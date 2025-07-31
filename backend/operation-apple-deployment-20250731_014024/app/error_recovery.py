"""
Error recovery mechanisms for transient failures and service resilience
"""
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

from app.error_handlers import (
    ServiceError, GoogleVisionError, FAISSError, 
    SkinClassificationError, DemographicSearchError, VectorProcessingError
)

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategies for different types of failures"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class RecoveryConfig:
    """Configuration for error recovery"""
    max_retries: int = 3
    base_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    fallback_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


class CircuitBreaker:
    """Circuit breaker pattern implementation for service resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                    logger.info("Circuit breaker transitioning to HALF_OPEN state")
                else:
                    raise ServiceError(
                        service_name="CircuitBreaker",
                        message=f"Circuit breaker is OPEN. Service unavailable.",
                        details={
                            'failure_count': self.failure_count,
                            'last_failure_time': self.last_failure_time,
                            'recovery_timeout': self.recovery_timeout
                        }
                    )
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            self.failure_count = 0
            logger.info("Circuit breaker reset to CLOSED state")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time,
            'recovery_timeout': self.recovery_timeout
        }


class ErrorRecoveryManager:
    """Manages error recovery strategies and mechanisms"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.recovery_configs: Dict[str, RecoveryConfig] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self._setup_default_configs()
    
    def _setup_default_configs(self):
        """Setup default recovery configurations for different services"""
        self.recovery_configs.update({
            'google_vision': RecoveryConfig(
                max_retries=3,
                base_delay=2.0,
                backoff_factor=2.0,
                strategy=RecoveryStrategy.RETRY,
                fallback_enabled=True,
                circuit_breaker_threshold=5,
                circuit_breaker_timeout=120
            ),
            'faiss': RecoveryConfig(
                max_retries=2,
                base_delay=1.0,
                backoff_factor=1.5,
                strategy=RecoveryStrategy.CIRCUIT_BREAKER,
                fallback_enabled=True,
                circuit_breaker_threshold=3,
                circuit_breaker_timeout=60
            ),
            'supabase': RecoveryConfig(
                max_retries=3,
                base_delay=1.5,
                backoff_factor=2.0,
                strategy=RecoveryStrategy.RETRY,
                fallback_enabled=False,
                circuit_breaker_threshold=5,
                circuit_breaker_timeout=90
            ),
            'skin_classifier': RecoveryConfig(
                max_retries=2,
                base_delay=1.0,
                backoff_factor=1.5,
                strategy=RecoveryStrategy.GRACEFUL_DEGRADATION,
                fallback_enabled=True,
                circuit_breaker_threshold=3,
                circuit_breaker_timeout=60
            ),
            'demographic_search': RecoveryConfig(
                max_retries=2,
                base_delay=1.0,
                backoff_factor=1.5,
                strategy=RecoveryStrategy.FALLBACK,
                fallback_enabled=True,
                circuit_breaker_threshold=3,
                circuit_breaker_timeout=60
            )
        })
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            config = self.recovery_configs.get(service_name, RecoveryConfig())
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                recovery_timeout=config.circuit_breaker_timeout
            )
        return self.circuit_breakers[service_name]
    
    def register_fallback_handler(self, service_name: str, handler: Callable):
        """Register fallback handler for a service"""
        self.fallback_handlers[service_name] = handler
        logger.info(f"Registered fallback handler for {service_name}")
    
    def execute_with_recovery(self, service_name: str, operation: str, 
                            func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with comprehensive error recovery
        
        Args:
            service_name: Name of the service
            operation: Operation being performed
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback result
        """
        config = self.recovery_configs.get(service_name, RecoveryConfig())
        
        # Apply recovery strategy
        if config.strategy == RecoveryStrategy.CIRCUIT_BREAKER:
            return self._execute_with_circuit_breaker(
                service_name, operation, func, config, *args, **kwargs
            )
        elif config.strategy == RecoveryStrategy.RETRY:
            return self._execute_with_retry(
                service_name, operation, func, config, *args, **kwargs
            )
        elif config.strategy == RecoveryStrategy.FALLBACK:
            return self._execute_with_fallback(
                service_name, operation, func, config, *args, **kwargs
            )
        elif config.strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return self._execute_with_degradation(
                service_name, operation, func, config, *args, **kwargs
            )
        else:
            # Default to retry
            return self._execute_with_retry(
                service_name, operation, func, config, *args, **kwargs
            )
    
    def _execute_with_circuit_breaker(self, service_name: str, operation: str,
                                    func: Callable, config: RecoveryConfig,
                                    *args, **kwargs) -> Any:
        """Execute with circuit breaker protection"""
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        try:
            return circuit_breaker.call(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Circuit breaker execution failed for {service_name}.{operation}: {e}")
            
            # Try fallback if available
            if config.fallback_enabled and service_name in self.fallback_handlers:
                logger.info(f"Attempting fallback for {service_name}.{operation}")
                try:
                    return self.fallback_handlers[service_name](*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed for {service_name}: {fallback_error}")
            
            raise self._create_service_error(service_name, operation, e)
    
    def _execute_with_retry(self, service_name: str, operation: str,
                          func: Callable, config: RecoveryConfig,
                          *args, **kwargs) -> Any:
        """Execute with retry logic"""
        last_exception = None
        delay = config.base_delay
        
        for attempt in range(config.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retrying {service_name}.{operation} (attempt {attempt + 1}/{config.max_retries + 1})")
                
                return func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == config.max_retries:
                    logger.error(f"All retry attempts failed for {service_name}.{operation}")
                    break
                
                if not self._is_retryable_error(e, service_name):
                    logger.warning(f"Non-retryable error for {service_name}.{operation}: {e}")
                    break
                
                logger.warning(f"{service_name}.{operation} failed on attempt {attempt + 1}: {e}. "
                             f"Retrying in {delay:.2f}s...")
                time.sleep(delay)
                delay = min(delay * config.backoff_factor, config.max_delay)
        
        # Try fallback if available
        if config.fallback_enabled and service_name in self.fallback_handlers:
            logger.info(f"Attempting fallback for {service_name}.{operation}")
            try:
                return self.fallback_handlers[service_name](*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed for {service_name}: {fallback_error}")
        
        raise self._create_service_error(service_name, operation, last_exception)
    
    def _execute_with_fallback(self, service_name: str, operation: str,
                             func: Callable, config: RecoveryConfig,
                             *args, **kwargs) -> Any:
        """Execute with immediate fallback on failure"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary execution failed for {service_name}.{operation}: {e}")
            
            if service_name in self.fallback_handlers:
                logger.info(f"Using fallback for {service_name}.{operation}")
                try:
                    return self.fallback_handlers[service_name](*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback failed for {service_name}: {fallback_error}")
                    raise self._create_service_error(service_name, operation, fallback_error)
            else:
                raise self._create_service_error(service_name, operation, e)
    
    def _execute_with_degradation(self, service_name: str, operation: str,
                                func: Callable, config: RecoveryConfig,
                                *args, **kwargs) -> Any:
        """Execute with graceful degradation"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Service degradation for {service_name}.{operation}: {e}")
            
            # Return degraded result instead of failing completely
            degraded_result = self._get_degraded_result(service_name, operation, e)
            if degraded_result is not None:
                logger.info(f"Returning degraded result for {service_name}.{operation}")
                return degraded_result
            
            # If no degraded result available, try fallback
            if service_name in self.fallback_handlers:
                try:
                    return self.fallback_handlers[service_name](*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback failed for {service_name}: {fallback_error}")
            
            raise self._create_service_error(service_name, operation, e)
    
    def _is_retryable_error(self, error: Exception, service_name: str) -> bool:
        """Determine if an error is retryable"""
        error_str = str(error).lower()
        
        # Google Vision API retryable errors
        if service_name == 'google_vision':
            retryable_patterns = [
                'timeout', 'connection', 'network', 'temporary', 'unavailable',
                'rate limit', 'quota', 'deadline exceeded', 'internal error',
                'service unavailable', 'bad gateway'
            ]
            return any(pattern in error_str for pattern in retryable_patterns)
        
        # FAISS retryable errors
        elif service_name == 'faiss':
            retryable_patterns = [
                'timeout', 'connection', 'lock', 'busy', 'temporary',
                'index not ready', 'concurrent access'
            ]
            return any(pattern in error_str for pattern in retryable_patterns)
        
        # Database connection errors
        elif service_name in ['supabase', 'database']:
            retryable_patterns = [
                'connection', 'timeout', 'network', 'temporary', 'unavailable',
                'connection reset', 'connection refused', 'connection timeout'
            ]
            return any(pattern in error_str for pattern in retryable_patterns)
        
        # General retryable patterns
        general_retryable = [
            'timeout', 'connection reset', 'network', 'temporary', 'unavailable',
            'service unavailable', 'bad gateway', 'gateway timeout'
        ]
        
        return any(pattern in error_str for pattern in general_retryable)
    
    def _get_degraded_result(self, service_name: str, operation: str, 
                           error: Exception) -> Optional[Any]:
        """Get degraded result for graceful degradation"""
        if service_name == 'skin_classifier':
            # Return basic classification result
            return {
                'fitzpatrick_type': 'III',
                'fitzpatrick_description': 'Sometimes burns, tans gradually',
                'monk_tone': 5,
                'monk_description': 'Monk Scale Tone 5',
                'confidence': 0.5,
                'degraded': True,
                'degradation_reason': str(error)
            }
        
        elif service_name == 'demographic_search':
            # Return empty demographic results (fall back to visual-only search)
            return {
                'demographic_matches': [],
                'visual_only': True,
                'degraded': True,
                'degradation_reason': str(error)
            }
        
        elif service_name == 'google_vision':
            # Return minimal analysis result
            return {
                'status': 'degraded',
                'results': {
                    'face_detection': {'faces_found': 0, 'faces': []},
                    'image_properties': {'dominant_colors': []},
                    'label_detection': {'labels_found': 0, 'labels': []}
                },
                'degraded': True,
                'degradation_reason': str(error)
            }
        
        return None
    
    def _create_service_error(self, service_name: str, operation: str, 
                            original_error: Exception) -> ServiceError:
        """Create appropriate service-specific error"""
        error_message = f"Failed to {operation}: {str(original_error)}"
        
        if service_name == 'google_vision':
            return GoogleVisionError(
                message=error_message,
                api_error_code=getattr(original_error, 'code', None),
                quota_exceeded='quota' in str(original_error).lower()
            )
        elif service_name == 'faiss':
            return FAISSError(
                message=error_message,
                operation=operation,
                index_corrupted='corrupt' in str(original_error).lower()
            )
        elif service_name == 'skin_classifier':
            return SkinClassificationError(
                message=error_message,
                classification_stage=operation,
                confidence_too_low='confidence' in str(original_error).lower()
            )
        elif service_name == 'demographic_search':
            return DemographicSearchError(
                message=error_message,
                search_stage=operation,
                demographic_data_missing='demographic' in str(original_error).lower()
            )
        else:
            return ServiceError(
                service_name=service_name,
                message=error_message
            )
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        stats = {
            'circuit_breakers': {},
            'recovery_configs': {},
            'fallback_handlers': list(self.fallback_handlers.keys())
        }
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            stats['circuit_breakers'][service_name] = circuit_breaker.get_state()
        
        for service_name, config in self.recovery_configs.items():
            stats['recovery_configs'][service_name] = {
                'max_retries': config.max_retries,
                'strategy': config.strategy.value,
                'fallback_enabled': config.fallback_enabled,
                'circuit_breaker_threshold': config.circuit_breaker_threshold
            }
        
        return stats
    
    def reset_circuit_breaker(self, service_name: str) -> bool:
        """Manually reset circuit breaker for a service"""
        if service_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[service_name]
            circuit_breaker.state = 'CLOSED'
            circuit_breaker.failure_count = 0
            circuit_breaker.last_failure_time = None
            logger.info(f"Circuit breaker reset for {service_name}")
            return True
        return False


# Global error recovery manager instance
error_recovery_manager = ErrorRecoveryManager()


def with_error_recovery(service_name: str, operation: str = None):
    """Decorator for automatic error recovery"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            return error_recovery_manager.execute_with_recovery(
                service_name, op_name, func, *args, **kwargs
            )
        return wrapper
    return decorator


def setup_fallback_handlers():
    """Setup default fallback handlers for services"""
    
    def google_vision_fallback(*args, **kwargs):
        """Fallback for Google Vision API failures"""
        return {
            'status': 'fallback',
            'results': {
                'face_detection': {'faces_found': 0, 'faces': []},
                'image_properties': {'dominant_colors': []},
                'label_detection': {'labels_found': 0, 'labels': []}
            },
            'fallback_reason': 'google_vision_unavailable'
        }
    
    def skin_classifier_fallback(*args, **kwargs):
        """Fallback for skin classifier failures"""
        return {
            'fitzpatrick_type': 'III',
            'fitzpatrick_description': 'Sometimes burns, tans gradually',
            'monk_tone': 5,
            'monk_description': 'Monk Scale Tone 5',
            'confidence': 0.5,
            'fallback': True,
            'fallback_reason': 'classifier_unavailable'
        }
    
    def demographic_search_fallback(*args, **kwargs):
        """Fallback for demographic search failures"""
        # Fall back to visual-only search
        return []
    
    # Register fallback handlers
    error_recovery_manager.register_fallback_handler('google_vision', google_vision_fallback)
    error_recovery_manager.register_fallback_handler('skin_classifier', skin_classifier_fallback)
    error_recovery_manager.register_fallback_handler('demographic_search', demographic_search_fallback)
    
    logger.info("Fallback handlers registered successfully")


# Initialize fallback handlers
setup_fallback_handlers()