"""
Infrastructure Manager for AWS Deployment

Simple, practical infrastructure management focused on getting the app deployed.
"""

import boto3
import json
import logging
from typing import Dict, Optional, List
from .credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class InfrastructureManager:
    """Manages AWS infrastructure for deployment."""
    
    def __init__(self):
        self.credential_manager = CredentialManager()
        self.region = 'us-east-1'  # Default region
    
    def check_elastic_beanstalk_environment(self, app_name: str = 'shine-backend', env_name: str = 'shine-backend-poc-env') -> Dict:
        """Check if Elastic Beanstalk environment exists and is healthy."""
        try:
            session = self.credential_manager.get_aws_session()
            if not session:
                return {'status': 'error', 'message': 'AWS credentials not valid'}
            
            eb_client = session.client('elasticbeanstalk', region_name=self.region)
            
            # Check if environment exists
            try:
                response = eb_client.describe_environments(
                    ApplicationName=app_name,
                    EnvironmentNames=[env_name]
                )
                
                if not response['Environments']:
                    return {'status': 'not_found', 'message': f'Environment {env_name} not found'}
                
                env = response['Environments'][0]
                return {
                    'status': 'found',
                    'health': env.get('Health', 'Unknown'),
                    'status_detail': env.get('Status', 'Unknown'),
                    'url': env.get('CNAME', 'No URL'),
                    'version': env.get('VersionLabel', 'Unknown')
                }
                
            except Exception as e:
                return {'status': 'error', 'message': f'Error checking environment: {str(e)}'}
                
        except Exception as e:
            logger.error(f"Infrastructure check failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_deployment_package_info(self) -> Dict:
        """Get info needed for deployment package creation."""
        return {
            'required_files': [
                'requirements-aws.txt',
                '.ebextensions/',
                'simple_app.py',
                'app/',
                '.env'
            ],
            'exclude_patterns': [
                '__pycache__/',
                '*.pyc',
                'venv/',
                '.pytest_cache/',
                'tests/',
                '*.log'
            ]
        }
    
    def validate_deployment_readiness(self) -> Dict:
        """Check if everything is ready for deployment."""
        readiness = {
            'credentials': self.credential_manager.get_deployment_status(),
            'infrastructure': self.check_elastic_beanstalk_environment(),
            'files': self._check_required_files(),
            'overall_ready': False
        }
        
        # Determine if ready for deployment
        creds_ok = readiness['credentials']['aws_valid']
        infra_ok = readiness['infrastructure']['status'] in ['found', 'not_found']  # Either exists or can be created
        files_ok = readiness['files']['all_present']
        
        readiness['overall_ready'] = creds_ok and infra_ok and files_ok
        
        return readiness
    
    def _check_required_files(self) -> Dict:
        """Check if required deployment files exist."""
        import os
        
        required_files = [
            'requirements-aws.txt',
            'simple_app.py',
            '.env',
            '.ebextensions/01_python.config'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        return {
            'all_present': len(missing_files) == 0,
            'missing_files': missing_files,
            'required_files': required_files
        }
    
    def get_deployment_command(self) -> str:
        """Get the deployment command to run."""
        return "eb deploy shine-backend-poc-env"
    
    def get_deployment_status_url(self) -> Optional[str]:
        """Get URL to check deployment status."""
        env_info = self.check_elastic_beanstalk_environment()
        if env_info['status'] == 'found':
            return env_info.get('url')
        return None