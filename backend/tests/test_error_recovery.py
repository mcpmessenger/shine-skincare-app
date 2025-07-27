"""
Tests for error recovery mechanisms
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.error_recovery import (
    CircuitBreaker, ErrorRecoveryManager, RecoveryConfig, RecoveryStrategy,
    error_recovery_manager, with_error_recovery
)
from app.error_handlers import ServiceError, GoogleVisionError, FAISSError


class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        # Should be closed initially
        assert cb.state == 'CLOSED'
        assert cb.failure_count == 0
        
        # Successful calls should keep it closed
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == 'CLOSED'
    
    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        
        # First failure
        with pytest.raises(Exception):
            cb.call(lambda: exec('raise Exception("test error")'))
        
        assert cb.state == 'CLOSED'
        assert cb.failure_count == 1
        
        # Second failure should open the circuit
        with pytest.raises(Exception):
            cb.call(lambda: exec('raise Exception("test error")'))
        
        assert cb.state == 'OPEN'
        assert cb.failure_count == 2
    
    def test_circuit_breaker_blocks_calls_when_open(self):
        """Test circuit breaker blocks calls when open"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        
        # Trigger failure to open circuit
        with pytest.raises(Exception):
            cb.call(lambda: exec('raise Exception("test error")'))
        
        assert cb.state == 'OPEN'
        
        # Should block subsequent calls
        with pytest.raises(ServiceError) as exc_info:
            cb.call(lambda: "should not execute")
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    def test_circuit_breaker_half_open_transition(self):
        """Test circuit breaker transitions to half-open after timeout"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)  # Short timeout for testing
        
        # Open the circuit
        with pytest.raises(Exception):
            cb.call(lambda: exec('raise Exception("test error")'))
        
        assert cb.state == 'OPEN'
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Next call should transition to half-open
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == 'CLOSED'  # Should reset to closed on success
    
    def test_circuit_breaker_state_info(self):
        """Test circuit breaker state information"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        state = cb.get_state()
        assert state['state'] == 'CLOSED'
        assert state['failure_count'] == 0
        assert state['failure_threshold'] == 3
        assert state['recovery_timeout'] == 60


class TestErrorRecoveryManager:
    """Test error recovery manager"""
    
    def test_recovery_manager_initialization(self):
        """Test recovery manager initializes with default configs"""
        manager = ErrorRecoveryManager()
        
        assert 'google_vision' in manager.recovery_configs
        assert 'faiss' in manager.recovery_configs
        assert 'supabase' in manager.recovery_configs
        
        # Check default config
        google_config = manager.recovery_configs['google_vision']
        assert google_config.max_retries == 3
        assert google_config.strategy == RecoveryStrategy.RETRY
    
    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation for services"""
        manager = ErrorRecoveryManager()
        
        cb1 = manager.get_circuit_breaker('test_service')
        cb2 = manager.get_circuit_breaker('test_service')
        
        # Should return same instance
        assert cb1 is cb2
        assert 'test_service' in manager.circuit_breakers
    
    def test_fallback_handler_registration(self):
        """Test fallback handler registration"""
        manager = ErrorRecoveryManager()
        
        def test_fallback():
            return "fallback_result"
        
        manager.register_fallback_handler('test_service', test_fallback)
        assert 'test_service' in manager.fallback_handlers
        assert manager.fallback_handlers['test_service'] is test_fallback
    
    def test_retry_strategy_execution(self):
        """Test retry strategy execution"""
        manager = ErrorRecoveryManager()
        
        # Mock function that fails twice then succeeds
        call_count = 0
        def mock_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("temporary failure")
            return "success"
        
        # Configure retry strategy
        manager.recovery_configs['test_service'] = RecoveryConfig(
            max_retries=3,
            base_delay=0.01,  # Short delay for testing
            strategy=RecoveryStrategy.RETRY
        )
        
        result = manager.execute_with_recovery('test_service', 'test_op', mock_function)
        assert result == "success"
        assert call_count == 3
    
    def test_fallback_strategy_execution(self):
        """Test fallback strategy execution"""
        manager = ErrorRecoveryManager()
        
        # Register fallback handler
        def fallback_handler():
            return "fallback_result"
        
        manager.register_fallback_handler('test_service', fallback_handler)
        
        # Configure fallback strategy
        manager.recovery_configs['test_service'] = RecoveryConfig(
            strategy=RecoveryStrategy.FALLBACK,
            fallback_enabled=True
        )
        
        # Function that always fails
        def failing_function():
            raise Exception("always fails")
        
        result = manager.execute_with_recovery('test_service', 'test_op', failing_function)
        assert result == "fallback_result"
    
    def test_graceful_degradation_strategy(self):
        """Test graceful degradation strategy"""
        manager = ErrorRecoveryManager()
        
        # Configure degradation strategy
        manager.recovery_configs['skin_classifier'] = RecoveryConfig(
            strategy=RecoveryStrategy.GRACEFUL_DEGRADATION
        )
        
        # Function that fails
        def failing_function():
            raise Exception("classification failed")
        
        result = manager.execute_with_recovery('skin_classifier', 'classify', failing_function)
        
        # Should return degraded result
        assert result['degraded'] is True
        assert result['fitzpatrick_type'] == 'III'
        assert 'degradation_reason' in result
    
    def test_recovery_stats(self):
        """Test recovery statistics"""
        manager = ErrorRecoveryManager()
        
        # Create some circuit breakers
        manager.get_circuit_breaker('service1')
        manager.get_circuit_breaker('service2')
        
        # Register fallback handler
        manager.register_fallback_handler('service1', lambda: "fallback")
        
        stats = manager.get_recovery_stats()
        
        assert 'circuit_breakers' in stats
        assert 'recovery_configs' in stats
        assert 'fallback_handlers' in stats
        
        assert 'service1' in stats['circuit_breakers']
        assert 'service2' in stats['circuit_breakers']
        assert 'service1' in stats['fallback_handlers']
    
    def test_circuit_breaker_reset(self):
        """Test manual circuit breaker reset"""
        manager = ErrorRecoveryManager()
        
        # Get circuit breaker and open it
        cb = manager.get_circuit_breaker('test_service')
        cb.state = 'OPEN'
        cb.failure_count = 5
        
        # Reset it
        success = manager.reset_circuit_breaker('test_service')
        assert success is True
        assert cb.state == 'CLOSED'
        assert cb.failure_count == 0
        
        # Try to reset non-existent service
        success = manager.reset_circuit_breaker('non_existent')
        assert success is False


class TestErrorRecoveryDecorator:
    """Test error recovery decorator"""
    
    def test_decorator_success(self):
        """Test decorator with successful function"""
        @with_error_recovery('test_service', 'test_operation')
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_decorator_with_retry(self):
        """Test decorator with retry on failure"""
        call_count = 0
        
        @with_error_recovery('test_service', 'test_operation')
        def retry_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("temporary failure")
            return "success"
        
        # Configure retry for test service
        error_recovery_manager.recovery_configs['test_service'] = RecoveryConfig(
            max_retries=3,
            base_delay=0.01,
            strategy=RecoveryStrategy.RETRY
        )
        
        result = retry_function()
        assert result == "success"
        assert call_count == 2
    
    def test_decorator_with_fallback(self):
        """Test decorator with fallback"""
        # Register fallback
        def fallback_handler():
            return "fallback_result"
        
        error_recovery_manager.register_fallback_handler('test_service', fallback_handler)
        error_recovery_manager.recovery_configs['test_service'] = RecoveryConfig(
            strategy=RecoveryStrategy.FALLBACK,
            fallback_enabled=True
        )
        
        @with_error_recovery('test_service', 'test_operation')
        def failing_function():
            raise Exception("always fails")
        
        result = failing_function()
        assert result == "fallback_result"


class TestRetryableErrorDetection:
    """Test retryable error detection"""
    
    def test_google_vision_retryable_errors(self):
        """Test Google Vision retryable error detection"""
        manager = ErrorRecoveryManager()
        
        # Retryable errors
        retryable_errors = [
            Exception("timeout occurred"),
            Exception("connection failed"),
            Exception("rate limit exceeded"),
            Exception("service unavailable"),
            Exception("internal error")
        ]
        
        for error in retryable_errors:
            assert manager._is_retryable_error(error, 'google_vision') is True
        
        # Non-retryable errors
        non_retryable_errors = [
            Exception("invalid api key"),
            Exception("malformed request"),
            Exception("permission denied")
        ]
        
        for error in non_retryable_errors:
            assert manager._is_retryable_error(error, 'google_vision') is False
    
    def test_faiss_retryable_errors(self):
        """Test FAISS retryable error detection"""
        manager = ErrorRecoveryManager()
        
        # Retryable errors
        retryable_errors = [
            Exception("timeout occurred"),
            Exception("connection busy"),
            Exception("index not ready"),
            Exception("concurrent access")
        ]
        
        for error in retryable_errors:
            assert manager._is_retryable_error(error, 'faiss') is True
        
        # Non-retryable errors
        non_retryable_errors = [
            Exception("invalid dimension"),
            Exception("corrupted index"),
            Exception("out of memory")
        ]
        
        for error in non_retryable_errors:
            assert manager._is_retryable_error(error, 'faiss') is False
    
    def test_database_retryable_errors(self):
        """Test database retryable error detection"""
        manager = ErrorRecoveryManager()
        
        # Retryable errors
        retryable_errors = [
            Exception("connection timeout"),
            Exception("connection reset"),
            Exception("network unavailable"),
            Exception("temporary failure")
        ]
        
        for error in retryable_errors:
            assert manager._is_retryable_error(error, 'supabase') is True
        
        # Non-retryable errors
        non_retryable_errors = [
            Exception("authentication failed"),
            Exception("invalid query"),
            Exception("permission denied")
        ]
        
        for error in non_retryable_errors:
            assert manager._is_retryable_error(error, 'supabase') is False


class TestServiceSpecificErrors:
    """Test service-specific error creation"""
    
    def test_google_vision_error_creation(self):
        """Test Google Vision error creation"""
        manager = ErrorRecoveryManager()
        
        original_error = Exception("quota exceeded")
        service_error = manager._create_service_specific_error(
            'google_vision', 'analyze_image', original_error, {}
        )
        
        assert isinstance(service_error, GoogleVisionError)
        assert service_error.quota_exceeded is True
        assert 'analyze_image' in service_error.message
    
    def test_faiss_error_creation(self):
        """Test FAISS error creation"""
        manager = ErrorRecoveryManager()
        
        original_error = Exception("index corrupted")
        service_error = manager._create_service_specific_error(
            'faiss', 'search_similar', original_error, {}
        )
        
        assert isinstance(service_error, FAISSError)
        assert service_error.index_corrupted is True
        assert service_error.operation == 'search_similar'
    
    def test_generic_service_error_creation(self):
        """Test generic service error creation"""
        manager = ErrorRecoveryManager()
        
        original_error = Exception("unknown error")
        service_error = manager._create_service_specific_error(
            'unknown_service', 'unknown_operation', original_error, {}
        )
        
        assert isinstance(service_error, ServiceError)
        assert service_error.service_name == 'unknown_service'


if __name__ == '__main__':
    pytest.main([__file__])