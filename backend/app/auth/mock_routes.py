from flask import jsonify, request
from app.auth import auth_bp
from app.models.user import User, UserPreferences, UserSession
from app import db
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta

@auth_bp.route('/mock-login', methods=['POST'])
def mock_login():
    """Mock OAuth login for development"""
    try:
        # Create a mock authorization URL that redirects to our callback
        mock_auth_url = "http://localhost:3000/auth/callback?code=mock_code&state=mock_state"
        
        return jsonify({
            'authorization_url': mock_auth_url,
            'state': 'mock_state',
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mock-callback', methods=['POST'])
def mock_callback():
    """Mock OAuth callback for development"""
    try:
        # Create a mock user
        user = User.query.filter_by(email='test@example.com').first()
        
        if not user:
            user = User(
                google_id='mock_google_id_123',
                email='test@example.com',
                name='Test User',
                profile_picture_url='https://via.placeholder.com/150',
                last_login_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            
            # Create default preferences
            preferences = UserPreferences(user_id=user.id)
            db.session.add(preferences)
        
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_profile': user.to_dict(),
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 