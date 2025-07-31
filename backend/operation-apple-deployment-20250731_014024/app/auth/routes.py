from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.auth import auth_bp
from app.models.user import User, UserPreferences, UserSession
from app import db
import requests
import uuid
from datetime import datetime, timedelta
import secrets

@auth_bp.route('/login', methods=['POST'])
def login():
    """Initiate Google OAuth login"""
    try:
        data = request.get_json()
        client_type = data.get('client_type', 'web')
        
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Google OAuth authorization URL
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={current_app.config['GOOGLE_CLIENT_ID']}&"
            f"redirect_uri={current_app.config.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/callback')}&"
            f"scope=openid%20email%20profile&"
            f"response_type=code&"
            f"state={state}"
        )
        
        return jsonify({
            'authorization_url': google_auth_url,
            'state': state,
            'expires_in': 3600  # 1 hour
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/callback', methods=['POST'])
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        data = request.get_json()
        code = data.get('code')
        state = data.get('state')
        
        if not code:
            return jsonify({'error': 'Authorization code is required'}), 400
        
        # Exchange authorization code for tokens
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': current_app.config.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/callback')
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
        
        # Find or create user
        user = User.query.filter_by(google_id=user_info['id']).first()
        
        if not user:
            # Create new user
            user = User(
                google_id=user_info['id'],
                email=user_info['email'],
                name=user_info.get('name', ''),
                profile_picture_url=user_info.get('picture'),
                last_login_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create default preferences
            preferences = UserPreferences(user_id=user.id)
            db.session.add(preferences)
            
        else:
            # Update existing user
            user.last_login_at = datetime.utcnow()
            user.name = user_info.get('name', user.name)
            user.profile_picture_url = user_info.get('picture', user.profile_picture_url)
        
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_profile': user.to_dict(),
            'expires_in': 3600
        }), 200
        
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to authenticate with Google'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = user.to_dict()
        
        # Include preferences if they exist
        if user.preferences:
            profile_data['preferences'] = user.preferences.to_dict()
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile and preferences"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update user fields
        if 'name' in data:
            user.name = data['name']
        
        # Update or create preferences
        if 'preferences' in data:
            if not user.preferences:
                user.preferences = UserPreferences(user_id=user.id)
            
            prefs = user.preferences
            prefs_data = data['preferences']
            
            if 'skin_type' in prefs_data:
                prefs.skin_type = prefs_data['skin_type']
            if 'skin_concerns' in prefs_data:
                prefs.skin_concerns = prefs_data['skin_concerns']
            if 'allergies' in prefs_data:
                prefs.allergies = prefs_data['allergies']
            if 'preferred_brands' in prefs_data:
                prefs.preferred_brands = prefs_data['preferred_brands']
            if 'price_range_min' in prefs_data:
                prefs.price_range_min = prefs_data['price_range_min']
            if 'price_range_max' in prefs_data:
                prefs.price_range_max = prefs_data['price_range_max']
            if 'privacy_level' in prefs_data:
                prefs.privacy_level = prefs_data['privacy_level']
        
        db.session.commit()
        
        profile_data = user.to_dict()
        if user.preferences:
            profile_data['preferences'] = user.preferences.to_dict()
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and invalidate session"""
    try:
        user_id = get_jwt_identity()
        
        # Invalidate current session
        session = UserSession.query.filter_by(
            user_id=user_id,
            session_token=request.headers.get('Authorization', '').replace('Bearer ', ''),
            is_active=True
        ).first()
        
        if session:
            session.is_active = False
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token,
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 