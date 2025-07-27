import unittest
import json
import logging
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.error_handlers import (
    APIError, ServiceError, ValidationError, AuthenticationError,
    AuthorizationError, ResourceNotFoundError, format_error_response,
    log_error, safe_service_call, create_error_context
)


class TestErrorHandlers(unittest.TestCase):
    """Test cases for error handling system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_api_error_creation(self):
        """Test APIError creation and properties"""
        error = APIError(
            message="Test error",
            status_code=400,
            error_code="TEST_ERROR",
            details={'field': 'test_field'}
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.error_code, "TEST_ERROR")
        self.assertEqual(error.details['field'], 'test_field')
        self.assertIsNotNone(error.timestamp)
    
    def test_service_error_creation(self):
        """Test ServiceError creation"""
        error = ServiceError(
            service_name="test_service",
            message="Service failed",
            details={'operation': 'test_op'}
        )
        
        self.assertEqual(error.service_name, "test_service")
        self.assertEqual(error.status_code, 503)
        self.assertEqual(error.error_code, "TEST_SERVICE_SERVICE_ERROR")
        self.assertIn("test_service service error", error.message)
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError(
            message="Invalid input",
            field="email",
            details={'expected': 'email format'}
        )
        
        self.assertEqual(error.field, "email")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.error_code, "VALIDATION_ERROR")
        self.assertIn("Validation error", error.message)
    
    def test_authentication_error_creation(self):
        """Test AuthenticationError creation"""
        error = AuthenticationError()
        
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.error_code, "AUTHENTICATION_ERROR")
        self.assertEqual(error.message, "Authentication required")
    
    def test_authorization_error_creation(self):
        """Test AuthorizationError creation"""
        error = AuthorizationError()
        
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.error_code, "AUTHORIZATION_ERROR")
        self.assertEqual(error.message, "Access denied")
    
    def test_resource_not_found_error_creation(self):
        """Test ResourceNotFoundError creation"""
        error = ResourceNotFoundError(
            resource_type="User",
            resource_id="123"
        )
        
        self.assertEqual(error.resource_type, "User")
        self.assertEqual(error.resource_id, "123")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.error_code, "RESOURCE_NOT_FOUND")
        self.assertIn("User not found: 123", error.message)
    
    def test_format_error_response_api_error(self):
        """Test formatting APIError response"""
        error = APIError(
            message="Test error",
            status_code=400,
            error_code="TEST_ERROR",
            details={'field': 'test'}
        )
        
        with self.app.test_request_context('/test', method='POST'):
            response = format_error_response(error, request_id="req123")
        
        self.assertIn('error', response)
        self.assertEqual(response['error']['code'], 'TEST_ERROR')
        self.assertEqual(response['error']['message'], 'Test error')
        self.assertEqual(response['error']['status_code'], 400)
        self.assertIn('details', response['error'])
        self.assertIn('request', response['error'])
        self.assertEqual(response['error']['request_id'], 'req123')
    
    def test_format_error_response_generic_error(self):
        """Test formatting generic error response"""
        error = Exception("Generic error")
        
        response = format_error_response(error)
        
        self.assertIn('error', response)
        self.assertEqual(response['error']['code'], 'INTERNAL_SERVER_ERROR')
        self.assertEqual(response['error']['message'], 'An unexpected error occurred')
        self.assertEqual(response['error']['status_code'], 500)
    
    def test_create_error_context(self):
        """Test creating error context"""
        context = create_error_context(
            operation="test_operation",
            service="test_service",
            user_id="user123"
        )
        
        self.assertEqual(context['operation'], 'test_operation')
        self.assertEqual(context['service'], 'test_service')
        self.assertEqual(context['user_id'], 'user123')
        self.assertIn('timestamp', context)
    
    def test_safe_service_call_success(self):
        """Test successful safe service call"""
        def mock_function(arg1, arg2, kwarg1=None):
            return f"result: {arg1}, {arg2}, {kwarg1}"
        
        result = safe_service_call(
            'test_service', 'test_operation',
            mock_function, 'value1', 'value2', kwarg1='kwvalue'
        )
        
        self.assertEqual(result, "result: value1, value2, kwvalue")
    
    def test_safe_service_call_failure(self):
        """Test safe service call with failure"""
        def mock_function():
            raise Exception("Service failed")
        
        with self.assertRaises(ServiceError) as context:
            safe_service_call('test_service', 'test_operation', mock_function)
        
        error = context.exception
        self.assertEqual(error.service_name, 'test_service')
        self.assertIn('Failed to test_operation', error.message)
    
    @patch('app.error_handlers.logger')
    def test_log_error_api_error(self, mock_logger):
        """Test logging APIError"""
        error = APIError("Test error", status_code=400)
        
        with self.app.test_request_context('/test'):
            log_error(error, {'extra': 'context'})
        
        # Verify logger was called with WARNING level (400 status)
        mock_logger.log.assert_called()
        # Check that log was called with WARNING level (30)
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.WARNING)
    
    @patch('app.error_handlers.logger')
    def test_log_error_server_error(self, mock_logger):
        """Test logging server error"""
        error = Exception("Server error")
        
        log_error(error)
        
        # Verify logger was called with ERROR level
        mock_logger.log.assert_called()
        mock_logger.error.assert_called()  # Should log stack trace
    
    def test_error_handler_integration_validation_error(self):
        """Test ValidationError handling in Flask app"""
        # Create a test route that raises ValidationError
        @self.app.route('/test-validation-error')
        def test_validation_error():
            raise ValidationError("Invalid input", field="email")
        
        response = self.client.get('/test-validation-error')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'VALIDATION_ERROR')
    
    def test_error_handler_integration_service_error(self):
        """Test ServiceError handling in Flask app"""
        # Create a test route that raises ServiceError
        @self.app.route('/test-service-error')
        def test_service_error():
            raise ServiceError("test_service", "Service unavailable")
        
        response = self.client.get('/test-service-error')
        
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'TEST_SERVICE_SERVICE_ERROR')
    
    def test_error_handler_integration_authentication_error(self):
        """Test AuthenticationError handling in Flask app"""
        # Create a test route that raises AuthenticationError
        @self.app.route('/test-auth-error')
        def test_auth_error():
            raise AuthenticationError()
        
        response = self.client.get('/test-auth-error')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'AUTHENTICATION_ERROR')
    
    def test_error_handler_integration_authorization_error(self):
        """Test AuthorizationError handling in Flask app"""
        # Create a test route that raises AuthorizationError
        @self.app.route('/test-authz-error')
        def test_authz_error():
            raise AuthorizationError()
        
        response = self.client.get('/test-authz-error')
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'AUTHORIZATION_ERROR')
    
    def test_error_handler_integration_resource_not_found_error(self):
        """Test ResourceNotFoundError handling in Flask app"""
        # Create a test route that raises ResourceNotFoundError
        @self.app.route('/test-not-found-error')
        def test_not_found_error():
            raise ResourceNotFoundError("User", "123")
        
        response = self.client.get('/test-not-found-error')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'RESOURCE_NOT_FOUND')
    
    def test_error_handler_integration_generic_exception(self):
        """Test generic exception handling in Flask app"""
        # Create a test route that raises generic exception
        @self.app.route('/test-generic-error')
        def test_generic_error():
            raise Exception("Unexpected error")
        
        response = self.client.get('/test-generic-error')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'INTERNAL_SERVER_ERROR')
    
    def test_error_handler_404(self):
        """Test 404 error handling"""
        response = self.client.get('/non-existent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'HTTP_404')
    
    def test_error_handler_405(self):
        """Test 405 method not allowed error handling"""
        # Try POST to a GET-only endpoint
        response = self.client.post('/api/health')
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'HTTP_405')
    
    def test_error_response_structure(self):
        """Test that error responses have consistent structure"""
        # Create a test route that raises APIError
        @self.app.route('/test-error-structure')
        def test_error_structure():
            raise APIError("Test error", status_code=400, error_code="TEST_ERROR")
        
        response = self.client.get('/test-error-structure')
        data = json.loads(response.data)
        
        # Verify required fields
        self.assertIn('error', data)
        error = data['error']
        
        required_fields = ['code', 'message', 'timestamp', 'status_code']
        for field in required_fields:
            self.assertIn(field, error)
        
        # Verify request context is included
        self.assertIn('request', error)
        request_info = error['request']
        self.assertIn('method', request_info)
        self.assertIn('url', request_info)
        self.assertIn('endpoint', request_info)
    
    def test_error_logging_context(self):
        """Test that error logging includes proper context"""
        with patch('app.error_handlers.logger') as mock_logger:
            error = ServiceError("test_service", "Test error")
            
            with self.app.test_request_context('/test', method='POST'):
                log_error(error, {'custom_context': 'test_value'})
            
            # Verify logger was called with proper context
            mock_logger.log.assert_called()
            call_args = mock_logger.log.call_args
            
            # Check that extra context was passed
            self.assertIn('extra', call_args[1])
            extra_context = call_args[1]['extra']
            self.assertIn('error_type', extra_context)
            self.assertIn('custom_context', extra_context)
            self.assertEqual(extra_context['custom_context'], 'test_value')


if __name__ == '__main__':
    unittest.main()