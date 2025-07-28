"""
Tests for InfrastructureManager - focused on deployment infrastructure.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.app.infrastructure_manager import InfrastructureManager


class TestInfrastructureManager:
    
    def setup_method(self):
        self.infrastructure_manager = InfrastructureManager()
    
    @patch('backend.app.infrastructure_manager.CredentialManager')
    def test_check_elastic_beanstalk_environment_found(self, mock_credential_manager):
        """Test checking existing Elastic Beanstalk environment."""
        # Mock AWS session and EB client
        mock_session = MagicMock()
        mock_eb_client = MagicMock()
        mock_eb_client.describe_environments.return_value = {
            'Environments': [{
                'Health': 'Ok',
                'Status': 'Ready',
                'CNAME': 'test-app.us-east-1.elasticbeanstalk.com',
                'VersionLabel': 'v1.0'
            }]
        }
        mock_session.client.return_value = mock_eb_client
        mock_credential_manager.return_value.get_aws_session.return_value = mock_session
        
        result = self.infrastructure_manager.check_elastic_beanstalk_environment()
        
        assert result['status'] == 'found'
        assert result['health'] == 'Ok'
        assert result['url'] == 'test-app.us-east-1.elasticbeanstalk.com'
    
    @patch('backend.app.infrastructure_manager.CredentialManager')
    def test_check_elastic_beanstalk_environment_not_found(self, mock_credential_manager):
        """Test checking non-existent Elastic Beanstalk environment."""
        # Mock AWS session and EB client
        mock_session = MagicMock()
        mock_eb_client = MagicMock()
        mock_eb_client.describe_environments.return_value = {'Environments': []}
        mock_session.client.return_value = mock_eb_client
        mock_credential_manager.return_value.get_aws_session.return_value = mock_session
        
        result = self.infrastructure_manager.check_elastic_beanstalk_environment()
        
        assert result['status'] == 'not_found'
    
    @patch('backend.app.infrastructure_manager.CredentialManager')
    def test_check_elastic_beanstalk_environment_no_credentials(self, mock_credential_manager):
        """Test checking environment without valid credentials."""
        mock_credential_manager.return_value.get_aws_session.return_value = None
        
        result = self.infrastructure_manager.check_elastic_beanstalk_environment()
        
        assert result['status'] == 'error'
        assert 'credentials not valid' in result['message']
    
    def test_create_deployment_package_info(self):
        """Test deployment package info creation."""
        info = self.infrastructure_manager.create_deployment_package_info()
        
        assert 'required_files' in info
        assert 'exclude_patterns' in info
        assert 'requirements-aws.txt' in info['required_files']
        assert '__pycache__/' in info['exclude_patterns']
    
    @patch('os.path.exists')
    def test_check_required_files_all_present(self, mock_exists):
        """Test checking required files when all are present."""
        mock_exists.return_value = True
        
        result = self.infrastructure_manager._check_required_files()
        
        assert result['all_present'] is True
        assert len(result['missing_files']) == 0
    
    @patch('os.path.exists')
    def test_check_required_files_some_missing(self, mock_exists):
        """Test checking required files when some are missing."""
        # Mock that some files exist, some don't
        def mock_exists_side_effect(path):
            return path != 'requirements-aws.txt'
        
        mock_exists.side_effect = mock_exists_side_effect
        
        result = self.infrastructure_manager._check_required_files()
        
        assert result['all_present'] is False
        assert 'requirements-aws.txt' in result['missing_files']
    
    def test_get_deployment_command(self):
        """Test getting deployment command."""
        command = self.infrastructure_manager.get_deployment_command()
        
        assert command == "eb deploy shine-backend-poc-env"
    
    @patch('backend.app.infrastructure_manager.InfrastructureManager.check_elastic_beanstalk_environment')
    def test_get_deployment_status_url(self, mock_check_env):
        """Test getting deployment status URL."""
        mock_check_env.return_value = {
            'status': 'found',
            'url': 'test-app.us-east-1.elasticbeanstalk.com'
        }
        
        url = self.infrastructure_manager.get_deployment_status_url()
        
        assert url == 'test-app.us-east-1.elasticbeanstalk.com'