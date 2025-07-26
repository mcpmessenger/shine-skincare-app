from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.payments import payments_bp
from app.models.payments import Order, OrderItem, Payment
from app.models.products import Product
from app.models.user import User
from app import db
import stripe
from datetime import datetime
import uuid
import json

# Initialize Stripe
# stripe.api_key will be set when the app context is available

def generate_order_number():
    """Generate unique order number"""
    return f"SHINE-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

@payments_bp.route('/create-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create Stripe payment intent for order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        payment_method = data.get('payment_method')
        order_items = data.get('order_items', [])
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Create order in database
        order = Order(
            user_id=user_id,
            order_number=generate_order_number(),
            total_amount=amount / 100,  # Convert from cents
            currency=currency.upper(),
            order_status='pending',
            payment_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for item_data in order_items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'error': f'Product {product_id} not found'}), 404
            
            unit_price = product.price or 0
            total_price = unit_price * quantity
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Create Stripe payment intent
        intent_data = {
            'amount': amount,
            'currency': currency,
            'metadata': {
                'order_id': order.id,
                'order_number': order.order_number,
                'user_id': user_id
            }
        }
        
        if payment_method:
            intent_data['payment_method'] = payment_method
        
        payment_intent = stripe.PaymentIntent.create(**intent_data)
        
        # Create payment record
        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            stripe_payment_intent_id=payment_intent.id,
            payment_method=payment_method,
            amount=amount / 100,  # Convert from cents
            currency=currency.upper(),
            payment_status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret,
            'status': payment_intent.status,
            'amount': payment_intent.amount,
            'order_id': order.id,
            'order_number': order.order_number
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_payment():
    """Confirm payment completion"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        payment_intent_id = data.get('payment_intent_id')
        payment_method_id = data.get('payment_method_id')
        
        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID is required'}), 400
        
        # Retrieve payment intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Find payment record
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=payment_intent_id,
            user_id=user_id
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update payment status based on Stripe status
        if payment_intent.status == 'succeeded':
            payment.payment_status = 'completed'
            payment.processed_at = datetime.utcnow()
            
            # Update order status
            order = payment.order
            order.payment_status = 'completed'
            order.order_status = 'confirmed'
            
            db.session.commit()
            
            return jsonify({
                'payment_status': 'completed',
                'order_id': order.id,
                'order_number': order.order_number,
                'receipt_url': payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else None,
                'fulfillment_status': 'pending'
            }), 200
            
        elif payment_intent.status == 'requires_payment_method':
            payment.payment_status = 'failed'
            db.session.commit()
            
            return jsonify({
                'payment_status': 'failed',
                'error': 'Payment method required'
            }), 400
            
        else:
            return jsonify({
                'payment_status': payment_intent.status,
                'error': f'Payment status: {payment_intent.status}'
            }), 400
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get user payment history"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 10, type=int), 50)
        status_filter = request.args.get('status_filter')
        
        # Build query
        query = Payment.query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter(Payment.payment_status == status_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(Payment.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=limit, error_out=False
        )
        
        payments = []
        total_amount = 0
        
        for payment in pagination.items:
            payment_data = payment.to_dict()
            # Include order info
            if payment.order:
                payment_data['order'] = {
                    'id': payment.order.id,
                    'order_number': payment.order.order_number,
                    'order_status': payment.order.order_status
                }
            payments.append(payment_data)
            total_amount += payment.amount or 0
        
        return jsonify({
            'payments': payments,
            'total_amount': total_amount,
            'total_count': pagination.total,
            'has_more': pagination.has_next
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        if not sig_header:
            return jsonify({'error': 'No signature header'}), 400
        
        # Verify webhook signature (in production, use your webhook secret)
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        # For development, parse without verification
        event = stripe.Event.construct_from(json.loads(payload), sig_header)
        
        # Handle different event types
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            
            # Update payment status
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if payment:
                payment.payment_status = 'completed'
                payment.processed_at = datetime.utcnow()
                
                # Update order status
                order = payment.order
                order.payment_status = 'completed'
                order.order_status = 'confirmed'
                
                db.session.commit()
                
        elif event.type == 'payment_intent.payment_failed':
            payment_intent = event.data.object
            
            # Update payment status
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if payment:
                payment.payment_status = 'failed'
                db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/orders/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        user_id = get_jwt_identity()
        
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 