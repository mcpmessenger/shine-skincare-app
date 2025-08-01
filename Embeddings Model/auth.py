from flask import Blueprint, request, jsonify
import os
import jwt
import requests
from datetime import datetime, timedelta
import logging

auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

@auth_bp.route('/auth/google', methods=['POST'])
def google_auth():
    """
    Handle Google OAuth authentication via Supabase
    """
    try:
        data = request.get_json()
        
        if not data or 'id_token' not in data:
            return jsonify({'error': 'No Google ID token provided'}), 400
        
        # Verify Google ID token with Supabase
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        auth_data = {
            'provider': 'google',
            'id_token': data['id_token']
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/auth/v1/token?grant_type=id_token',
            headers=headers,
            json=auth_data
        )
        
        if response.status_code == 200:
            auth_result = response.json()
            
            # Create user profile if needed
            user_profile = create_or_update_user_profile(auth_result['user'])
            
            return jsonify({
                'success': True,
                'user': auth_result['user'],
                'access_token': auth_result['access_token'],
                'refresh_token': auth_result['refresh_token'],
                'profile': user_profile
            })
        else:
            logger.error(f"Supabase auth error: {response.text}")
            return jsonify({'error': 'Authentication failed'}), 401
            
    except Exception as e:
        logger.error(f"Google auth error: {str(e)}")
        return jsonify({'error': 'Authentication failed', 'details': str(e)}), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh authentication token
    """
    try:
        data = request.get_json()
        
        if not data or 'refresh_token' not in data:
            return jsonify({'error': 'No refresh token provided'}), 400
        
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        refresh_data = {
            'refresh_token': data['refresh_token']
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token',
            headers=headers,
            json=refresh_data
        )
        
        if response.status_code == 200:
            auth_result = response.json()
            return jsonify({
                'success': True,
                'access_token': auth_result['access_token'],
                'refresh_token': auth_result['refresh_token']
            })
        else:
            return jsonify({'error': 'Token refresh failed'}), 401
            
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Logout user and invalidate token
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 400
        
        token = auth_header.split(' ')[1]
        
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/auth/v1/logout',
            headers=headers
        )
        
        return jsonify({'success': True, 'message': 'Logged out successfully'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

@auth_bp.route('/auth/user', methods=['GET'])
def get_user():
    """
    Get current user information
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/auth/v1/user',
            headers=headers
        )
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Get user profile
            profile = get_user_profile(user_data['id'])
            
            return jsonify({
                'success': True,
                'user': user_data,
                'profile': profile
            })
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500

def create_or_update_user_profile(user_data):
    """
    Create or update user profile in Supabase
    """
    try:
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        profile_data = {
            'id': user_data['id'],
            'email': user_data['email'],
            'full_name': user_data.get('user_metadata', {}).get('full_name'),
            'avatar_url': user_data.get('user_metadata', {}).get('avatar_url'),
            'subscription_type': 'free',
            'api_key_usage': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Upsert user profile
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/profiles',
            headers=headers,
            json=profile_data
        )
        
        if response.status_code in [200, 201]:
            return profile_data
        else:
            logger.error(f"Profile creation error: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        return None

def get_user_profile(user_id):
    """
    Get user profile from Supabase
    """
    try:
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
            return profiles[0] if profiles else None
        else:
            return None
            
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return None

@auth_bp.route('/auth/settings', methods=['PUT'])
def update_settings():
    """
    Update user settings including API key preferences
    """
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        token = auth_header.split(' ')[1]
        data = request.get_json()
        
        # Get user from token
        user_response = requests.get(
            f'{SUPABASE_URL}/auth/v1/user',
            headers={
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {token}'
            }
        )
        
        if user_response.status_code != 200:
            return jsonify({'error': 'Invalid token'}), 401
        
        user_data = user_response.json()
        user_id = user_data['id']
        
        # Update profile settings
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add allowed settings
        allowed_fields = ['openai_api_key', 'use_own_api_key', 'subscription_type']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Settings updated'})
        else:
            return jsonify({'error': 'Failed to update settings'}), 500
            
    except Exception as e:
        logger.error(f"Update settings error: {str(e)}")
        return jsonify({'error': 'Failed to update settings', 'details': str(e)}), 500

