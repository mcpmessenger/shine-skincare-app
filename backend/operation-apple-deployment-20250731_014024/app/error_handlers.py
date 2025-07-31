import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

# Import monitoring components
try:
    from app.monitoring import metrics_collector, get_service_monitor
    MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Monitoring components not available")
    MONITORING_AVAILABLE = False
    metrics_collector = None


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


class GoogleVisionError(ServiceError):
    """Error specific to Google Vision API operations"""
    
    def __init__(self, message: str, api_error_code: str = None, 
                 quota_exceeded: bool = False, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details.update({
            'api_error_code': api_error_code,
            'quota_exceeded': quota_exceeded,
            'service_type': 'google_vision_api'
        })
        
        super().__init__(
            service_name="GoogleVision",
            message=message,
            details=enhanced_details
        )
        self.api_error_code = api_error_code
        self.quota_exceeded = quota_exceeded


class FAISSError(ServiceError):
    """Error specific to FAISS operations"""
    
    def __init__(self, message: str, operation: str = None, 
                 index_corrupted: bool = False, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details.update({
            'operation': operation,
            'index_corrupted': index_corrupted,
            'service_type': 'faiss_vector_search'
        })
        
        super().__init__(
            service_name="FAISS",
            message=message,
            details=enhanced_details
        )
        self.operation = operation
        self.index_corrupted = index_corrupted


class SkinClassificationError(ServiceError):
    """Error specific to skin classification operations"""
    
    def __init__(self, message: str, classification_stage: str = None,
                 confidence_too_low: bool = False, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details.update({
            'classification_stage': classification_stage,
            'confidence_too_low': confidence_too_low,
            'service_type': 'skin_classification'
        })
        
        super().__init__(
            service_name="SkinClassifier",
            message=message,
            details=enhanced_details
        )
        self.classification_stage = classification_stage
        self.confidence_too_low = confidence_too_low


class DemographicSearchError(ServiceError):
    """Error specific to demographic search operations"""
    
    def __init__(self, message: str, search_stage: str = None,
                 demographic_data_missing: bool = False, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details.update({
            'search_stage': search_stage,
            'demographic_data_missing': demographic_data_missing,
            'service_type': 'demographic_search'
        })
        
        super().__init__(
            service_name="DemographicSearch",
            message=message,
            details=enhanced_details
        )
        self.search_stage = search_stage
        self.demographic_data_missing = demographic_data_missing


class VectorProcessingError(ServiceError):
    """Error specific to vector processing operations"""
    
    def __init__(self, message: str, vector_operation: str = None,
                 dimension_mismatch: bool = False, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details.update({
            'vector_operation': vector_operation,
            'dimension_mismatch': dimension_mismatch,
            'service_type': 'vector_processing'
        })
        
        super().__init__(
            service_name="VectorProcessing",
            message=message,
            details=enhanced_details
        )
        self.vector_operation = vector_operation
        self.dimension_mismatch = dimension_mismatch


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
    Log error with appropriate level and context, including monitoring integration
    
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
    
    # Record error in monitoring system
    if MONITORING_AVAILABLE and metrics_collector:
        service_name = 'unknown'
        if isinstance(error, ServiceError):
            service_name = error.service_name.lower()
        elif hasattr(error, 'service_name'):
            service_name = error.service_name.lower()
        
        metrics_collector.record_error(
            service_name=service_name,
            error_type=type(error).__name__,
            error_message=str(error),
            tags=context
        )


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
    
    @app.errorhandler(GoogleVisionError)
    def handle_google_vision_error(error: GoogleVisionError):
        """Handle Google Vision API errors"""
        log_error(error, {
            'service_name': error.service_name,
            'api_error_code': error.api_error_code,
            'quota_exceeded': error.quota_exceeded
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(FAISSError)
    def handle_faiss_error(error: FAISSError):
        """Handle FAISS operation errors"""
        log_error(error, {
            'service_name': error.service_name,
            'operation': error.operation,
            'index_corrupted': error.index_corrupted
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(SkinClassificationError)
    def handle_skin_classification_error(error: SkinClassificationError):
        """Handle skin classification errors"""
        log_error(error, {
            'service_name': error.service_name,
            'classification_stage': error.classification_stage,
            'confidence_too_low': error.confidence_too_low
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(DemographicSearchError)
    def handle_demographic_search_error(error: DemographicSearchError):
        """Handle demographic search errors"""
        log_error(error, {
            'service_name': error.service_name,
            'search_stage': error.search_stage,
            'demographic_data_missing': error.demographic_data_missing
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
    @app.errorhandler(VectorProcessingError)
    def handle_vector_processing_error(error: VectorProcessingError):
        """Handle vector processing errors"""
        log_error(error, {
            'service_name': error.service_name,
            'vector_operation': error.vector_operation,
            'dimension_mismatch': error.dimension_mismatch
        })
        response = format_error_response(error)
        return jsonify(response), error.status_code
    
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


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0,
                    exceptions: tuple = (Exception,)):
    """
    Decorator to retry function calls on failure with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exceptions to retry on
        
    Returns:
        Decorated function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Last attempt failed, raise the exception
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                                 f"Retrying in {current_delay:.2f}s...")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def safe_service_call_with_retry(service_name: str, operation: str, func, *args, 
                                max_retries: int = 2, **kwargs):
    """
    Safely call a service method with retry logic for transient failures
    
    Args:
        service_name: Name of the service
        operation: Operation being performed
        func: Function to call
        max_retries: Maximum number of retry attempts
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        ServiceError: If service call fails after all retries
    """
    import time
    
    last_exception = None
    delay = 1.0
    
    for attempt in range(max_retries + 1):
        try:
            if attempt == 0:
                logger.debug(f"Calling {service_name}.{operation}")
            else:
                logger.info(f"Retrying {service_name}.{operation} (attempt {attempt + 1}/{max_retries + 1})")
            
            result = func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"Successfully completed {service_name}.{operation} after {attempt + 1} attempts")
            else:
                logger.debug(f"Successfully completed {service_name}.{operation}")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if this is a retryable error
            is_retryable = _is_retryable_error(e, service_name)
            
            if attempt == max_retries or not is_retryable:
                # Last attempt or non-retryable error
                error_context = create_error_context(
                    operation=f"{service_name}.{operation}",
                    service_name=service_name,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                    attempts=attempt + 1,
                    retryable=is_retryable
                )
                
                logger.error(f"Service call failed: {service_name}.{operation} after {attempt + 1} attempts", 
                           extra=error_context)
                
                # Raise appropriate service-specific error
                raise _create_service_specific_error(service_name, operation, e, error_context)
            
            # Wait before retry
            logger.warning(f"{service_name}.{operation} failed on attempt {attempt + 1}: {e}. "
                         f"Retrying in {delay:.2f}s...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    
    # This should never be reached
    raise last_exception


def _is_retryable_error(error: Exception, service_name: str) -> bool:
    """
    Determine if an error is retryable based on error type and service
    
    Args:
        error: The exception that occurred
        service_name: Name of the service
        
    Returns:
        True if the error is retryable, False otherwise
    """
    # Google Vision API retryable errors
    if service_name.lower() == 'googlevision':
        error_str = str(error).lower()
        retryable_patterns = [
            'timeout', 'connection', 'network', 'temporary', 'unavailable',
            'rate limit', 'quota', 'deadline exceeded', 'internal error'
        ]
        return any(pattern in error_str for pattern in retryable_patterns)
    
    # FAISS retryable errors
    elif service_name.lower() == 'faiss':
        error_str = str(error).lower()
        retryable_patterns = [
            'timeout', 'connection', 'lock', 'busy', 'temporary'
        ]
        return any(pattern in error_str for pattern in retryable_patterns)
    
    # Database connection errors are generally retryable
    elif service_name.lower() in ['supabase', 'database']:
        error_str = str(error).lower()
        retryable_patterns = [
            'connection', 'timeout', 'network', 'temporary', 'unavailable'
        ]
        return any(pattern in error_str for pattern in retryable_patterns)
    
    # General retryable error patterns
    error_str = str(error).lower()
    general_retryable = [
        'timeout', 'connection reset', 'network', 'temporary', 'unavailable'
    ]
    
    return any(pattern in error_str for pattern in general_retryable)


def _create_service_specific_error(service_name: str, operation: str, 
                                 original_error: Exception, context: Dict[str, Any]):
    """
    Create appropriate service-specific error based on service name and error
    
    Args:
        service_name: Name of the service
        operation: Operation that failed
        original_error: Original exception
        context: Error context
        
    Returns:
        Appropriate service-specific error
    """
    error_message = f"Failed to {operation}: {str(original_error)}"
    
    if service_name.lower() == 'googlevision':
        # Check for specific Google Vision errors
        error_str = str(original_error).lower()
        quota_exceeded = 'quota' in error_str or 'rate limit' in error_str
        
        return GoogleVisionError(
            message=error_message,
            api_error_code=getattr(original_error, 'code', None),
            quota_exceeded=quota_exceeded,
            details=context
        )
    
    elif service_name.lower() == 'faiss':
        # Check for FAISS-specific errors
        error_str = str(original_error).lower()
        index_corrupted = 'corrupt' in error_str or 'invalid' in error_str
        
        return FAISSError(
            message=error_message,
            operation=operation,
            index_corrupted=index_corrupted,
            details=context
        )
    
    elif service_name.lower() == 'skinclassifier':
        # Check for classification-specific errors
        error_str = str(original_error).lower()
        confidence_too_low = 'confidence' in error_str or 'uncertain' in error_str
        
        return SkinClassificationError(
            message=error_message,
            classification_stage=operation,
            confidence_too_low=confidence_too_low,
            details=context
        )
    
    elif service_name.lower() == 'demographicsearch':
        # Check for demographic search errors
        error_str = str(original_error).lower()
        demographic_data_missing = 'demographic' in error_str or 'missing' in error_str
        
        return DemographicSearchError(
            message=error_message,
            search_stage=operation,
            demographic_data_missing=demographic_data_missing,
            details=context
        )
    
    elif 'vector' in service_name.lower():
        # Vector processing errors
        error_str = str(original_error).lower()
        dimension_mismatch = 'dimension' in error_str or 'shape' in error_str
        
        return VectorProcessingError(
            message=error_message,
            vector_operation=operation,
            dimension_mismatch=dimension_mismatch,
            details=context
        )
    
    # Default to generic service error
    return ServiceError(
        service_name=service_name,
        message=error_message,
        details=context
    )