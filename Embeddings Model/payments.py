from flask import Blueprint, request, jsonify
import os
import stripe
import logging
from datetime import datetime, timedelta
import requests

payments_bp = Blueprint('payments', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

# Subscription plans
SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'Basic Plan',
        'price': 9.99,
        'stripe_price_id': os.environ.get('STRIPE_BASIC_PRICE_ID'),
        'api_calls_limit': 100,
        'features': ['Basic skin analysis', 'Product recommendations', 'Email support']
    },
    'premium': {
        'name': 'Premium Plan',
        'price': 19.99,
        'stripe_price_id': os.environ.get('STRIPE_PREMIUM_PRICE_ID'),
        'api_calls_limit': 500,
        'features': ['Advanced skin analysis', 'SCIN dataset access', 'Priority support', 'Custom API key']
    },
    'professional': {
        'name': 'Professional Plan',
        'price': 49.99,
        'stripe_price_id': os.environ.get('STRIPE_PROFESSIONAL_PRICE_ID'),
        'api_calls_limit': 2000,
        'features': ['All premium features', 'White-label API', 'Bulk analysis', 'Dedicated support']
    }
}

@payments_bp.route('/subscription/plans', methods=['GET'])
def get_subscription_plans():
    """
    Get available subscription plans
    """
    try:
        return jsonify({
            'success': True,
            'plans': SUBSCRIPTION_PLANS
        })
    except Exception as e:
        logger.error(f"Error getting plans: {str(e)}")
        return jsonify({'error': 'Failed to get plans'}), 500

@payments_bp.route('/subscription/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Create Stripe checkout session for subscription
    """
    try:
        data = request.get_json()
        
        if not data or 'plan' not in data or 'user_id' not in data:
            return jsonify({'error': 'Plan and user_id required'}), 400
        
        plan_name = data['plan']
        user_id = data['user_id']
        
        if plan_name not in SUBSCRIPTION_PLANS:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan = SUBSCRIPTION_PLANS[plan_name]
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=data.get('success_url', 'https://shineskincollective.com/success'),
            cancel_url=data.get('cancel_url', 'https://shineskincollective.com/cancel'),
            client_reference_id=user_id,
            metadata={
                'user_id': user_id,
                'plan': plan_name
            }
        )
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

@payments_bp.route('/subscription/portal', methods=['POST'])
def create_customer_portal():
    """
    Create Stripe customer portal session
    """
    try:
        data = request.get_json()
        
        if not data or 'customer_id' not in data:
            return jsonify({'error': 'Customer ID required'}), 400
        
        # Create customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=data['customer_id'],
            return_url=data.get('return_url', 'https://shineskincollective.com/account')
        )
        
        return jsonify({
            'success': True,
            'portal_url': portal_session.url
        })
        
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}")
        return jsonify({'error': 'Failed to create portal session'}), 500

@payments_bp.route('/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events
    """
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_cancelled(event['data']['object'])
        elif event['type'] == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        
        return jsonify({'success': True})
        
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

def handle_checkout_completed(session):
    """
    Handle successful checkout completion
    """
    try:
        user_id = session['metadata']['user_id']
        plan = session['metadata']['plan']
        customer_id = session['customer']
        subscription_id = session['subscription']
        
        # Update user subscription in Supabase
        update_user_subscription(user_id, {
            'subscription_type': plan,
            'stripe_customer_id': customer_id,
            'stripe_subscription_id': subscription_id,
            'subscription_status': 'active',
            'subscription_start_date': datetime.utcnow().isoformat(),
            'api_calls_limit': SUBSCRIPTION_PLANS[plan]['api_calls_limit'],
            'api_calls_used': 0
        })
        
        logger.info(f"Subscription activated for user {user_id}, plan {plan}")
        
    except Exception as e:
        logger.error(f"Error handling checkout completion: {str(e)}")

def handle_subscription_updated(subscription):
    """
    Handle subscription updates
    """
    try:
        customer_id = subscription['customer']
        subscription_status = subscription['status']
        
        # Find user by customer ID
        user = get_user_by_customer_id(customer_id)
        if user:
            update_user_subscription(user['id'], {
                'subscription_status': subscription_status,
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Subscription updated for customer {customer_id}, status {subscription_status}")
        
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")

def handle_subscription_cancelled(subscription):
    """
    Handle subscription cancellation
    """
    try:
        customer_id = subscription['customer']
        
        # Find user by customer ID
        user = get_user_by_customer_id(customer_id)
        if user:
            update_user_subscription(user['id'], {
                'subscription_status': 'cancelled',
                'subscription_end_date': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Subscription cancelled for customer {customer_id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {str(e)}")

def handle_payment_succeeded(invoice):
    """
    Handle successful payment
    """
    try:
        customer_id = invoice['customer']
        subscription_id = invoice['subscription']
        
        # Find user by customer ID
        user = get_user_by_customer_id(customer_id)
        if user:
            # Reset API usage for new billing period
            update_user_subscription(user['id'], {
                'api_calls_used': 0,
                'last_payment_date': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Payment succeeded for customer {customer_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    """
    Handle failed payment
    """
    try:
        customer_id = invoice['customer']
        
        # Find user by customer ID
        user = get_user_by_customer_id(customer_id)
        if user:
            update_user_subscription(user['id'], {
                'subscription_status': 'past_due',
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Payment failed for customer {customer_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")

def update_user_subscription(user_id, subscription_data):
    """
    Update user subscription in Supabase
    """
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}',
            headers=headers,
            json=subscription_data
        )
        
        if response.status_code == 200:
            logger.info(f"Updated subscription for user {user_id}")
        else:
            logger.error(f"Failed to update subscription: {response.text}")
            
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")

def get_user_by_customer_id(customer_id):
    """
    Get user by Stripe customer ID
    """
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/profiles?stripe_customer_id=eq.{customer_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json()
            return users[0] if users else None
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting user by customer ID: {str(e)}")
        return None

@payments_bp.route('/subscription/usage', methods=['GET'])
def get_usage():
    """
    Get current user's API usage
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user from token
        user_response = requests.get(
            f'{SUPABASE_URL}/auth/v1/user',
            headers={
                'apikey': os.environ.get('SUPABASE_ANON_KEY'),
                'Authorization': f'Bearer {token}'
            }
        )
        
        if user_response.status_code != 200:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_data = user_response.json()
        user_id = user_data['id']
        
        # Get user profile with subscription info
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile = profiles[0]
                return jsonify({
                    'success': True,
                    'usage': {
                        'api_calls_used': profile.get('api_calls_used', 0),
                        'api_calls_limit': profile.get('api_calls_limit', 10),
                        'subscription_type': profile.get('subscription_type', 'free'),
                        'subscription_status': profile.get('subscription_status', 'inactive')
                    }
                })
        
        return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return jsonify({'error': 'Failed to get usage'}), 500

@payments_bp.route('/subscription/increment-usage', methods=['POST'])
def increment_usage():
    """
    Increment API usage for user
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get current usage
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            profiles = response.json()
            if profiles:
                profile = profiles[0]
                current_usage = profile.get('api_calls_used', 0)
                
                # Increment usage
                update_response = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}',
                    headers=headers,
                    json={'api_calls_used': current_usage + 1}
                )
                
                if update_response.status_code == 200:
                    return jsonify({'success': True, 'new_usage': current_usage + 1})
        
        return jsonify({'error': 'Failed to increment usage'}), 500
        
    except Exception as e:
        logger.error(f"Error incrementing usage: {str(e)}")
        return jsonify({'error': 'Failed to increment usage'}), 500

