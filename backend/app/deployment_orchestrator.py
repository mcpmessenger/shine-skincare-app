"""
Deployment Orchestrator

Simple orchestration for AWS Elastic Beanstalk deployment.
"""

import subprocess
import os
import logging
import time
from typing import Dict, List
from .infrastructure_manager import InfrastructureManager

logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates the deployment process."""
    
    def __init__(self):
        self.infrastructure_manager = InfrastructureManager()
    
    def pre_deployment_check(self) -> Dict:
        """Run pre-deployment validation."""
        logger.info("Running pre-deployment checks...")
        
        readiness = self.infrastructure_manager.validate_deployment_readiness()
        
        if not readiness['overall_ready']:
            logger.error("Pre-deployment check failed")
            return {
                'success': False,
                'message': 'System not ready for deployment',
                'details': readiness
            }
        
        logger.info("Pre-deployment checks passed")
        return {
            'success': True,
            'message': 'Ready for deployment',
            'details': readiness
        }
    
    def deploy(self) -> Dict:
        """Execute the deployment."""
        logger.info("Starting deployment...")
        
        # Pre-deployment check
        pre_check = self.pre_deployment_check()
        if not pre_check['success']:
            return pre_check
        
        try:
            # Change to backend directory
            original_dir = os.getcwd()
            backend_dir = os.path.join(original_dir, 'backend')
            
            if not os.path.exists(backend_dir):
                return {
                    'success': False,
                    'message': 'Backend directory not found',
                    'details': {'current_dir': original_dir}
                }
            
            os.chdir(backend_dir)
            
            # Run deployment command
            cmd = self.infrastructure_manager.get_deployment_command()
            logger.info(f"Running deployment command: {cmd}")
            
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            # Return to original directory
            os.chdir(original_dir)
            
            if result.returncode == 0:
                logger.info("Deployment completed successfully")
                return {
                    'success': True,
                    'message': 'Deployment completed successfully',
                    'details': {
                        'stdout': result.stdout,
                        'deployment_url': self.infrastructure_manager.get_deployment_status_url()
                    }
                }
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                return {
                    'success': False,
                    'message': 'Deployment failed',
                    'details': {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'return_code': result.returncode
                    }
                }
                
        except subprocess.TimeoutExpired:
            os.chdir(original_dir)
            return {
                'success': False,
                'message': 'Deployment timed out after 10 minutes',
                'details': {}
            }
        except Exception as e:
            os.chdir(original_dir)
            logger.error(f"Deployment error: {str(e)}")
            return {
                'success': False,
                'message': f'Deployment error: {str(e)}',
                'details': {}
            }
    
    def check_deployment_health(self) -> Dict:
        """Check if the deployed application is healthy."""
        logger.info("Checking deployment health...")
        
        try:
            import requests
            
            url = self.infrastructure_manager.get_deployment_status_url()
            if not url:
                return {
                    'healthy': False,
                    'message': 'No deployment URL found'
                }
            
            # Add http:// if not present
            if not url.startswith('http'):
                url = f'http://{url}'
            
            # Try to hit the health endpoint
            response = requests.get(f'{url}/health', timeout=30)
            
            if response.status_code == 200:
                return {
                    'healthy': True,
                    'message': 'Application is healthy',
                    'url': url,
                    'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
            else:
                return {
                    'healthy': False,
                    'message': f'Health check failed with status {response.status_code}',
                    'url': url
                }
                
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            return {
                'healthy': False,
                'message': f'Health check error: {str(e)}'
            }
    
    def get_deployment_logs(self) -> Dict:
        """Get recent deployment logs."""
        try:
            result = subprocess.run(
                ['eb', 'logs', '--all'],
                capture_output=True,
                text=True,
                cwd='backend',
                timeout=60
            )
            
            return {
                'success': result.returncode == 0,
                'logs': result.stdout if result.returncode == 0 else result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'logs': f'Error getting logs: {str(e)}'
            }