import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom API error class for structured error handling"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize API error
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"API_ERROR_{status_code}"
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()


class ServiceError(APIError):
    """Error related to service operations"""
    
    def __init__(self, service_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service_name} service error: {message}",
            status_code=503,
            error_code=f"{service_name.upper()}_SERVICE_ERROR",
            details=details
        )
        self.service_name = service_name


class ValidationError(APIError):
    """Error related to input validation"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation error: {message}",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )
        self.field = field


class AuthenticationError(APIError):
    """Error related to authentication"""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(APIError):
    """Error related to authorization"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ResourceNotFoundError(APIError):
    """Error when requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: str = None, 
                 details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


def format_error_response(error: Exception, request_id: str = None) -> Dict[str, Any]:
    """
    Format error response in a consistent structure
    
    Args:
        error: Exception instance
        request_id: Optional request ID for tracking
        
    Returns:
        Formatted error response dictionary
    """
    if isinstance(error, APIError):
        response = {
            'error': {
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp,
                'status_code': error.status_code
            }
        }
        
        if error.details:
            response['error']['details'] = error.details
            
    elif isinstance(error, HTTPException):
        response = {
            'error': {
                'code': f"HTTP_{error.code}",
                'message': error.description or str(error),
                'timestamp': datetime.utcnow().isoformat(),
                'status_code': error.code
            }
        }
        
    else:
        # Generic error handling
        response = {
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'timestamp': datetime.utcnow().isoformat(),
                'status_code': 500
            }
        }
    
    # Add request context
    if request:
        response['error']['request'] = {
            'method': request.method,
            'url': request.url,
            'endpoint': request.endpoint
        }
    
    if request_id:
        response['error']['request_id'] = request_id
    
    return response


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log error with appropriate level and context
    
    Args:
        error: Exception instance
        context: Additional context information
    """
    context = context or {}
    
    # Determine log level based on error type
    if isinstance(error, APIError):
        if error.status_code >= 500:
            log_level = logging.ERROR
        elif error.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
    else:
        log_level = logging.ERROR
    
    # Prepare log message
    log_message = f"Error occurred: {str(error)}"
    
    # Add context information
    log_context = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        **context
    }
    
    if isinstance(error, APIError):
        log_context.update({
            'error_code': error.error_code,
            'status_code': error.status_code,
            'details': error.details
        })
    
    # Add request context if available
    if request:
        log_context.update({
            'method': request.method,
            'url': request.url,
            'endpoint': request.endpoint,
            'user_agent': request.headers.get('User-Agent'),
            'remote_addr': request.remote_addr
        })
    
    # Log with appropriate level
    logger.log(log_level, log_message, extra=log_context)
    
    # Log stack trace for server errors
    if log_level == logging.ERROR:
        logger.error(f"Stack trace: {traceback.format_exc()}")


def register_error_handlers(app):
    """
    Register comprehensive error handlers for the Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle validation errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(ServiceError)
    def handle_service_error(error: ServiceError):
        """Handle service errors"""
        log_error(error, {'service_name': error.service_name})
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError):
        """Handle authentication errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error: AuthorizationError):
        """Handle authorization errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(ResourceNotFoundError)
    def handle_resource_not_found_error(error: ResourceNotFoundError):
        """Handle resource not found errors"""
        log_error(error, {
            'resource_type': error.resource_type,
            'resource_id': error.resource_id
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle method not allowed errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), 405
    
    @app.errorhandler(413)
    def handle_request_entity_too_large(error):
        """Handle request entity too large errors"""
        log_error(error)
        response = format_error_response(error)
        response['error']['message'] = 'Request entity too large. Please reduce file size.'
        return jsonify(response), 413
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """Handle rate limit exceeded errors"""
        log_error(error)
        response = format_error_response(error)
        response['error']['message'] = 'Rate limit exceeded. Please try again later.'
        return jsonify(response), 429
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle internal server errors"""
        log_error(error)
        response = format_error_response(error)
        return jsonify(response), 500
    
    @app.errorhandler(502)
    def handle_bad_gateway(error):
        """Handle bad gateway errors"""
        log_error(error)
        response = format_error_response(error)
        response['error']['message'] = 'Service temporarily unavailable'
        return jsonify(response), 502
    
    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Handle service unavailable errors"""
        log_error(error)
        response = format_error_response(error)
        response['error']['message'] = 'Service temporarily unavailable'
        return jsonify(response), 503
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        log_error(error, {'unexpected': True})
        response = format_error_response(error)
        return jsonify(response), 500


def create_error_context(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create error context for logging
    
    Args:
        operation: Operation being performed
        **kwargs: Additional context
        
    Returns:
        Error context dictionary
    """
    context = {
        'operation': operation,
        'timestamp': datetime.utcnow().isoformat()
    }
    context.update(kwargs)
    return context


def safe_service_call(service_name: str, operation: str, func, *args, **kwargs):
    """
    Safely call a service method with proper error handling
    
    Args:
        service_name: Name of the service
        operation: Operation being performed
        func: Function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        ServiceError: If service call fails
    """
    try:
        logger.debug(f"Calling {service_name}.{operation}")
        result = func(*args, **kwargs)
        logger.debug(f"Successfully completed {service_name}.{operation}")
        return result
        
    except Exception as e:
        error_context = create_error_context(
            operation=f"{service_name}.{operation}",
            service_name=service_name,
            args_count=len(args),
            kwargs_keys=list(kwargs.keys())
        )
        
        logger.error(f"Service call failed: {service_name}.{operation}", extra=error_context)
        
        raise ServiceError(
            service_name=service_name,
            message=f"Failed to {operation}: {str(e)}",
            details=error_context
        ) from e