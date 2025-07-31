import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any


class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def filter(self, record):
        # Add timestamp in ISO format
        record.iso_timestamp = datetime.utcnow().isoformat()
        
        # Add service context if available
        if not hasattr(record, 'service_name'):
            record.service_name = 'unknown'
        
        # Add request ID if available (would be set by middleware)
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        
        return True


class ServiceLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds service context to all log messages"""
    
    def __init__(self, logger, service_name: str):
        super().__init__(logger, {'service_name': service_name})
        self.service_name = service_name
    
    def process(self, msg, kwargs):
        # Add service name to extra context
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        kwargs['extra']['service_name'] = self.service_name
        return msg, kwargs


def get_logging_config(log_level: str = None, log_file: str = None) -> Dict[str, Any]:
    """
    Get logging configuration dictionary
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Logging configuration dictionary
    """
    # Determine log level
    log_level = log_level or os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # Determine log file
    if log_file is None:
        log_file = os.environ.get('LOG_FILE')
    
    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '[{iso_timestamp}] {levelname:8} [{service_name}] {name}: {message}',
                'style': '{'
            },
            'simple': {
                'format': '{levelname:8} {name}: {message}',
                'style': '{'
            },
            'json': {
                'format': '{{"timestamp": "{iso_timestamp}", "level": "{levelname}", "service": "{service_name}", "logger": "{name}", "message": "{message}", "request_id": "{request_id}"}}',
                'style': '{'
            }
        },
        'filters': {
            'context_filter': {
                '()': ContextFilter
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filters': ['context_filter'],
                'stream': sys.stdout
            }
        },
        'loggers': {
            # Application loggers
            'app': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app.services': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app.enhanced_image_analysis': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app.service_manager': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'app.error_handlers': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            # Third-party loggers (reduce verbosity)
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'urllib3': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            },
            'requests': {
                'level': 'WARNING',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['context_filter'],
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        
        # Add file handler to all loggers
        for logger_config in config['loggers'].values():
            if 'file' not in logger_config['handlers']:
                logger_config['handlers'].append('file')
        
        config['root']['handlers'].append('file')
    
    return config


def setup_logging(log_level: str = None, log_file: str = None) -> None:
    """
    Setup application logging
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    config = get_logging_config(log_level, log_file)
    logging.config.dictConfig(config)
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level or 'INFO'}, File: {log_file or 'None'}")


def get_service_logger(service_name: str) -> ServiceLoggerAdapter:
    """
    Get a logger adapter for a specific service
    
    Args:
        service_name: Name of the service
        
    Returns:
        ServiceLoggerAdapter instance
    """
    logger = logging.getLogger(f'app.services.{service_name}')
    return ServiceLoggerAdapter(logger, service_name)


def log_service_operation(service_name: str, operation: str, 
                         success: bool = True, duration: float = None,
                         details: Dict[str, Any] = None) -> None:
    """
    Log service operation with structured information
    
    Args:
        service_name: Name of the service
        operation: Operation performed
        success: Whether operation was successful
        duration: Operation duration in seconds
        details: Additional operation details
    """
    logger = get_service_logger(service_name)
    
    log_data = {
        'operation': operation,
        'success': success,
        'service_name': service_name
    }
    
    if duration is not None:
        log_data['duration_seconds'] = round(duration, 3)
    
    if details:
        log_data.update(details)
    
    if success:
        message = f"Operation completed: {operation}"
        if duration is not None:
            message += f" ({duration:.3f}s)"
        logger.info(message, extra=log_data)
    else:
        message = f"Operation failed: {operation}"
        logger.error(message, extra=log_data)


def log_api_request(endpoint: str, method: str, status_code: int,
                   duration: float = None, user_id: str = None,
                   details: Dict[str, Any] = None) -> None:
    """
    Log API request with structured information
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration: Request duration in seconds
        user_id: User ID if authenticated
        details: Additional request details
    """
    logger = logging.getLogger('app.api')
    
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code
    }
    
    if duration is not None:
        log_data['duration_seconds'] = round(duration, 3)
    
    if user_id:
        log_data['user_id'] = user_id
    
    if details:
        log_data.update(details)
    
    # Determine log level based on status code
    if status_code >= 500:
        log_level = logging.ERROR
    elif status_code >= 400:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    
    message = f"{method} {endpoint} -> {status_code}"
    if duration is not None:
        message += f" ({duration:.3f}s)"
    
    logger.log(log_level, message, extra=log_data)


def log_performance_metric(metric_name: str, value: float, unit: str = None,
                          service_name: str = None, details: Dict[str, Any] = None) -> None:
    """
    Log performance metric
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        service_name: Service name if applicable
        details: Additional metric details
    """
    logger = logging.getLogger('app.performance')
    
    log_data = {
        'metric_name': metric_name,
        'value': value
    }
    
    if unit:
        log_data['unit'] = unit
    
    if service_name:
        log_data['service_name'] = service_name
    
    if details:
        log_data.update(details)
    
    message = f"Performance metric: {metric_name} = {value}"
    if unit:
        message += f" {unit}"
    
    logger.info(message, extra=log_data)


class LoggingMiddleware:
    """Middleware to add request logging and context"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # This would be implemented as WSGI middleware
        # For now, we'll use Flask's before/after request hooks
        return self.app(environ, start_response)


def configure_flask_logging(app):
    """
    Configure Flask-specific logging
    
    Args:
        app: Flask application instance
    """
    import time
    import uuid
    from flask import g, request
    
    @app.before_request
    def before_request():
        """Set up request context for logging"""
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]
        
        # Add request ID to logging context
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'filters'):
                for filter_obj in handler.filters:
                    if hasattr(filter_obj, 'request_id'):
                        filter_obj.request_id = g.request_id
    
    @app.after_request
    def after_request(response):
        """Log request completion"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            log_api_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                details={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'content_length': response.content_length,
                    'user_agent': request.headers.get('User-Agent', 'unknown')[:100]
                }
            )
        
        return response
    
    # Disable default Flask request logging to avoid duplication
    logging.getLogger('werkzeug').setLevel(logging.WARNING)