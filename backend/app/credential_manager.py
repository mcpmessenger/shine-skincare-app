"""
Simple Credential Management for Deployment

Focused on practical credential validation for AWS and Google Cloud deployment.
"""

import os
import json
import boto3
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CredentialManager:
    """Simple credential manager focused on deployment needs."""
    
    def __init__(self):
        self.aws_session = None
    
    def validate_aws_credentials(self) -> bool:
        """Quick AWS credential validation for deployment."""
        try:
            # Try to create session and test with STS
            session = boto3.Session()
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            
            self.aws_session = session
            logger.info(f"AWS credentials valid for account: {identity.get('Account')}")
            return True
            
        except Exception as e:
            logger.error(f"AWS credential validation failed: {str(e)}")
            return False
    
    def validate_google_credentials(self) -> bool:
        """Quick Google credential validation."""
        try:
            credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if not credentials_json:
                logger.error("GOOGLE_CREDENTIALS_JSON not found")
                return False
            
            # Just validate JSON format
            json.loads(credentials_json)
            logger.info("Google credentials JSON format valid")
            return True
            
        except Exception as e:
            logger.error(f"Google credential validation failed: {str(e)}")
            return False
    
    def get_deployment_status(self) -> Dict[str, any]:
        """Get simple deployment credential status."""
        return {
            'aws_valid': self.validate_aws_credentials(),
            'google_valid': self.validate_google_credentials(),
            'environment_ready': bool(os.getenv('SECRET_KEY') and os.getenv('SUPABASE_URL'))
        }
    
    def get_aws_session(self):
        """Get AWS session for deployment operations."""
        if not self.aws_session:
            self.validate_aws_credentials()
        return self.aws_session