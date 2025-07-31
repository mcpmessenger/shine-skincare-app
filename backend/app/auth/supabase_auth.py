import os
import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    """Service for Supabase authentication integration"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize the Supabase auth service
        
        Args:
            url: Supabase project URL
            key: Supabase service key
        """
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_SERVICE_KEY')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        try:
            if self.url and self.key:
                self.client = create_client(self.url, self.key)
                logger.info("Supabase auth client initialized successfully")
            else:
                logger.warning("Supabase credentials not found. Auth service will be disabled.")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase auth client: {e}")
            self.client = None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user data
        
        Args:
            token: JWT token from request header
            
        Returns:
            User data if valid, None otherwise
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            # Verify token with Supabase
            user = self.client.auth.get_user(token)
            if user.user:
                return {
                    'id': user.user.id,
                    'email': user.user.email,
                    'name': user.user.user_metadata.get('name', ''),
                    'is_guest': user.user.user_metadata.get('is_guest', False)
                }
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def create_user(self, email: str, password: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Create a new user in Supabase
        
        Args:
            email: User email
            password: User password
            name: User name
            
        Returns:
            User data if successful, None otherwise
        """
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.auth.admin.create_user({
                'email': email,
                'password': password,
                'user_metadata': {
                    'name': name
                }
            })
            
            if response.user:
                return {
                    'id': response.user.id,
                    'email': response.user.email,
                    'name': name
                }
            return None
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    def create_guest_user(self) -> Optional[Dict[str, Any]]:
        """
        Create a guest user for anonymous access
        
        Returns:
            Guest user data if successful, None otherwise
        """
        guest_email = f"guest_{datetime.now().timestamp()}@shine.app"
        guest_password = f"guest_{datetime.now().timestamp()}"
        
        return self.create_user(guest_email, guest_password, "Guest User")
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.client is not None

# Global auth service instance
auth_service = SupabaseAuthService()

def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = auth_service.verify_token(token)
        
        if not user_data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user data to request context
        request.user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication - allows guest access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user_data = auth_service.verify_token(token)
            if user_data:
                request.user = user_data
            else:
                request.user = None
        else:
            request.user = None
        
        return f(*args, **kwargs)
    
    return decorated_function 