"""
Tests for monitoring and metrics collection
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.monitoring import (
    MetricsCollector, ServiceMonitor, AlertManager, ServiceHealth,
    MetricPoint, metrics_collector, get_service_monitor, monitor_service_call
)


class TestMetricsCollector:
    """Test metrics collection functionality"""
    
    def test_metric_recording(self):
        """Test basic metric recording"""
        collector = MetricsCollector()
        
        collector.record_metric('test_metric', 1.5, {'tag1': 'value1'})
        collector.record_metric('test_metric', 2.0, {'tag1': 'value2'})
        
        assert 'test_metric' in collector.metrics
        assert len(collector.metrics['test_metric']) == 2
        
        # Check first metric point
        first_point = collector.metrics['test_metric'][0]
        assert first_point.value == 1.5
        assert first_point.tags == {'tag1': 'value1'}
        assert isinstance(first_point.timestamp, datetime)
    
    def test_counter_increment(self):
        """Test counter increment functionality"""
        collector = MetricsCollector()
        
        collector.increment_counter('test_counter', 1, {'service': 'test'})
        collector.increment_counter('test_counter', 2, {'service': 'test'})
        collector.increment_counter('test_counter', 1, {'service': 'other'})
        
        # Check counters
        test_key = 'test_counter:{"service": "test"}'
        other_key = 'test_counter:{"service": "other"}'
        
        assert collector.counters[test_key] == 3
        assert collector.counters[other_key] == 1
        
        # Should also record as time series
        assert 'test_counter_count' in collector.metrics
    
    def test_timing_recording(self):
        """Test timing recording"""
        collector = MetricsCollector()
        
        collector.record_timing('test_operation', 1.5, {'service': 'test'})
        collector.record_timing('test_operation', 2.0, {'service': 'test'})
        
        timer_key = 'test_operation:{"service": "test"}'
        assert timer_key in collector.timers
        assert len(collector.timers[timer_key]) == 2
        assert collector.timers[timer_key] == [1.5, 2.0]
        
        # Should also record as metric
        assert 'test_operation_duration' in collector.metrics
    
    def test_error_recording(self):
        """Test error recording"""
        collector = MetricsCollector()
        
        collector.record_error('test_service', 'ValueError', 'Test error message')
        collector.record_error('test_service', 'ValueError', 'Another error')
        collector.record_error('test_service', 'TypeError', 'Type error')
        
        # Check error counts
        value_error_key = 'test_service:ValueError'
        type_error_key = 'test_service:TypeError'
        
        assert collector.error_counts[value_error_key] == 2
        assert collector.error_counts[type_error_key] == 1
        
        # Check error details
        assert len(collector.error_details[value_error_key]) == 2
        assert len(collector.error_details[type_error_key]) == 1
        
        # Should also record as metric
        assert 'test_service_errors' in collector.metrics
    
    def test_service_health_update(self):
        """Test service health status updates"""
        collector = MetricsCollector()
        
        collector.update_service_health(
            'test_service', 'healthy', 0.5, 0.01,
            {'additional': 'info'}
        )
        
        assert 'test_service' in collector.service_health
        health = collector.service_health['test_service']
        
        assert health.service_name == 'test_service'
        assert health.status == 'healthy'
        assert health.response_time == 0.5
        assert health.error_rate == 0.01
        assert health.success_rate == 0.99
        assert health.details == {'additional': 'info'}
        assert isinstance(health.last_check, datetime)
    
    def test_metric_summary(self):
        """Test metric summary calculation"""
        collector = MetricsCollector()
        
        # Add some metrics
        collector.record_metric('test_metric', 1.0)
        collector.record_metric('test_metric', 2.0)
        collector.record_metric('test_metric', 3.0)
        collector.record_metric('test_metric', 4.0)
        collector.record_metric('test_metric', 5.0)
        
        summary = collector.get_metric_summary('test_metric', window_minutes=60)
        
        assert summary['count'] == 5
        assert summary['min'] == 1.0
        assert summary['max'] == 5.0
        assert summary['avg'] == 3.0
        assert summary['latest'] == 5.0
    
    def test_service_health_summary(self):
        """Test service health summary"""
        collector = MetricsCollector()
        
        # Add some service health data
        collector.update_service_health('service1', 'healthy', 0.5, 0.01)
        collector.update_service_health('service2', 'degraded', 2.0, 0.15)
        collector.update_service_health('service3', 'unhealthy', 5.0, 0.8)
        
        summary = collector.get_service_health_summary()
        
        assert summary['total_services'] == 3
        assert summary['healthy_services'] == 1
        assert summary['degraded_services'] == 1
        assert summary['unhealthy_services'] == 1
        assert summary['overall_status'] == 'unhealthy'  # Any unhealthy service makes overall unhealthy
        
        assert 'service1' in summary['services']
        assert summary['services']['service1']['status'] == 'healthy'
    
    def test_error_summary(self):
        """Test error summary"""
        collector = MetricsCollector()
        
        # Add some errors
        collector.record_error('service1', 'ValueError', 'Error 1')
        collector.record_error('service1', 'TypeError', 'Error 2')
        collector.record_error('service2', 'ValueError', 'Error 3')
        
        summary = collector.get_error_summary(window_minutes=60)
        
        assert summary['total_errors'] == 3
        assert summary['error_types'] == 2  # service1:ValueError, service1:TypeError, service2:ValueError
        assert 'service1:ValueError' in summary['errors_by_service']
        assert 'service1:TypeError' in summary['errors_by_service']
        assert 'service2:ValueError' in summary['errors_by_service']
    
    def test_performance_summary(self):
        """Test performance summary"""
        collector = MetricsCollector()
        
        # Add some performance data
        collector.increment_counter('requests', 10)
        collector.record_timing('response_time', 1.5)
        collector.record_timing('response_time', 2.0)
        collector.record_metric('cpu_usage', 75.0)
        
        summary = collector.get_performance_summary()
        
        assert 'counters' in summary
        assert 'timing_stats' in summary
        assert summary['active_metrics'] > 0
        assert summary['total_data_points'] > 0
        
        # Check timing stats
        timing_key = 'response_time:{}'
        if timing_key in summary['timing_stats']:
            timing_stats = summary['timing_stats'][timing_key]
            assert timing_stats['count'] == 2
            assert timing_stats['min'] == 1.5
            assert timing_stats['max'] == 2.0
            assert timing_stats['avg'] == 1.75
    
    def test_cleanup_old_data(self):
        """Test cleanup of old metric data"""
        collector = MetricsCollector()
        
        # Add some old metrics (simulate by modifying timestamps)
        old_time = datetime.utcnow() - timedelta(hours=25)
        recent_time = datetime.utcnow()
        
        # Manually add old and recent points
        old_point = MetricPoint(timestamp=old_time, value=1.0)
        recent_point = MetricPoint(timestamp=recent_time, value=2.0)
        
        collector.metrics['test_metric'].append(old_point)
        collector.metrics['test_metric'].append(recent_point)
        
        # Add old error
        collector.error_details['service:error'].append({
            'timestamp': old_time.isoformat(),
            'service_name': 'service',
            'error_type': 'error',
            'error_message': 'old error',
            'tags': {}
        })
        
        collector.error_details['service:error'].append({
            'timestamp': recent_time.isoformat(),
            'service_name': 'service',
            'error_type': 'error',
            'error_message': 'recent error',
            'tags': {}
        })
        
        # Cleanup old data
        cleaned_count = collector.cleanup_old_data(max_age_hours=24)
        
        assert cleaned_count >= 2  # At least old metric and old error
        assert len(collector.metrics['test_metric']) == 1  # Only recent point remains
        assert len(collector.error_details['service:error']) == 1  # Only recent error remains


class TestServiceMonitor:
    """Test service monitoring functionality"""
    
    def test_service_monitor_initialization(self):
        """Test service monitor initialization"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        assert monitor.service_name == 'test_service'
        assert monitor.metrics_collector is collector
        assert monitor.request_count == 0
        assert monitor.error_count == 0
        assert monitor.total_response_time == 0.0
    
    def test_request_recording(self):
        """Test request recording"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        # Record successful request
        monitor.record_request(1.5, success=True)
        assert monitor.request_count == 1
        assert monitor.error_count == 0
        assert monitor.total_response_time == 1.5
        
        # Record failed request
        monitor.record_request(2.0, success=False, error_type='ValueError', error_message='Test error')
        assert monitor.request_count == 2
        assert monitor.error_count == 1
        assert monitor.total_response_time == 3.5
    
    def test_health_check(self):
        """Test health check functionality"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        # Record some requests
        monitor.record_request(1.0, success=True)
        monitor.record_request(2.0, success=True)
        monitor.record_request(3.0, success=False)
        
        # Perform health check
        health = monitor.check_health()
        
        assert isinstance(health, ServiceHealth)
        assert health.service_name == 'test_service'
        assert health.response_time == 2.0  # Average of 1.0, 2.0, 3.0
        assert health.error_rate == 1/3  # 1 error out of 3 requests
        assert health.success_rate == 2/3  # 2 successes out of 3 requests
        
        # Status should be degraded (error rate > 0.1)
        assert health.status == 'degraded'
    
    def test_health_status_determination(self):
        """Test health status determination logic"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        # Test healthy status (low error rate, fast response)
        monitor.record_request(0.5, success=True)
        monitor.record_request(0.6, success=True)
        health = monitor.check_health()
        assert health.status == 'healthy'
        
        # Reset and test degraded status (high error rate)
        monitor.reset_counters()
        for _ in range(8):
            monitor.record_request(1.0, success=True)
        for _ in range(2):
            monitor.record_request(1.0, success=False)
        
        health = monitor.check_health()
        assert health.status == 'degraded'  # 20% error rate
        
        # Reset and test unhealthy status (very high error rate)
        monitor.reset_counters()
        for _ in range(3):
            monitor.record_request(1.0, success=True)
        for _ in range(7):
            monitor.record_request(1.0, success=False)
        
        health = monitor.check_health()
        assert health.status == 'unhealthy'  # 70% error rate
    
    def test_counter_reset(self):
        """Test counter reset functionality"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        # Record some data
        monitor.record_request(1.0, success=True)
        monitor.record_request(2.0, success=False)
        
        assert monitor.request_count == 2
        assert monitor.error_count == 1
        assert monitor.total_response_time == 3.0
        
        # Reset counters
        monitor.reset_counters()
        
        assert monitor.request_count == 0
        assert monitor.error_count == 0
        assert monitor.total_response_time == 0.0


class TestAlertManager:
    """Test alert management functionality"""
    
    def test_alert_manager_initialization(self):
        """Test alert manager initialization"""
        collector = MetricsCollector()
        alert_manager = AlertManager(collector)
        
        assert alert_manager.metrics_collector is collector
        assert len(alert_manager.alert_rules) > 0
        assert len(alert_manager.active_alerts) == 0
        assert len(alert_manager.alert_history) == 0
    
    def test_alert_rule_evaluation(self):
        """Test alert rule evaluation"""
        collector = MetricsCollector()
        alert_manager = AlertManager(collector)
        
        # Add service with high error rate
        collector.update_service_health('test_service', 'degraded', 1.0, 0.6)  # 60% error rate
        
        # Check alerts
        alert_manager.check_alerts()
        
        # Should trigger high error rate alerts
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) > 0
        
        # Check for specific alert
        high_error_alerts = [a for a in active_alerts if a['rule_name'] == 'very_high_error_rate']
        assert len(high_error_alerts) == 1
        
        alert = high_error_alerts[0]
        assert alert['service_name'] == 'test_service'
        assert alert['severity'] == 'critical'
    
    def test_alert_resolution(self):
        """Test alert resolution"""
        collector = MetricsCollector()
        alert_manager = AlertManager(collector)
        
        # Add service with high error rate
        collector.update_service_health('test_service', 'unhealthy', 1.0, 0.6)
        alert_manager.check_alerts()
        
        # Should have active alerts
        assert len(alert_manager.get_active_alerts()) > 0
        
        # Fix the service
        collector.update_service_health('test_service', 'healthy', 0.5, 0.01)
        alert_manager.check_alerts()
        
        # Alerts should be resolved
        active_alerts = alert_manager.get_active_alerts()
        high_error_alerts = [a for a in active_alerts if a['rule_name'] == 'very_high_error_rate']
        assert len(high_error_alerts) == 0
    
    def test_alert_history(self):
        """Test alert history tracking"""
        collector = MetricsCollector()
        alert_manager = AlertManager(collector)
        
        # Trigger an alert
        collector.update_service_health('test_service', 'unhealthy', 1.0, 0.6)
        alert_manager.check_alerts()
        
        # Check alert history
        history = alert_manager.get_alert_history()
        assert len(history) > 0
        
        # Should contain the triggered alert
        high_error_alerts = [a for a in history if a['rule_name'] == 'very_high_error_rate']
        assert len(high_error_alerts) == 1


class TestMonitoringDecorator:
    """Test monitoring decorator functionality"""
    
    def test_monitor_service_call_success(self):
        """Test monitoring decorator with successful call"""
        @monitor_service_call('test_service')
        def successful_function():
            time.sleep(0.1)  # Simulate some work
            return "success"
        
        result = successful_function()
        assert result == "success"
        
        # Check that monitoring was recorded
        monitor = get_service_monitor('test_service')
        assert monitor.request_count > 0
        assert monitor.error_count == 0
    
    def test_monitor_service_call_failure(self):
        """Test monitoring decorator with failed call"""
        @monitor_service_call('test_service')
        def failing_function():
            time.sleep(0.1)  # Simulate some work
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        # Check that monitoring was recorded
        monitor = get_service_monitor('test_service')
        assert monitor.request_count > 0
        assert monitor.error_count > 0
    
    def test_get_service_monitor(self):
        """Test service monitor retrieval"""
        monitor1 = get_service_monitor('test_service')
        monitor2 = get_service_monitor('test_service')
        
        # Should return same instance
        assert monitor1 is monitor2
        assert monitor1.service_name == 'test_service'


class TestThreadSafety:
    """Test thread safety of monitoring components"""
    
    def test_metrics_collector_thread_safety(self):
        """Test metrics collector thread safety"""
        collector = MetricsCollector()
        results = []
        
        def record_metrics():
            for i in range(100):
                collector.record_metric('test_metric', i)
                collector.increment_counter('test_counter')
                collector.record_timing('test_timing', i * 0.01)
        
        # Run multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=record_metrics)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(collector.metrics['test_metric']) == 500  # 5 threads * 100 metrics
        assert 'test_counter:{}' in collector.counters
        assert collector.counters['test_counter:{}'] == 500
    
    def test_service_monitor_thread_safety(self):
        """Test service monitor thread safety"""
        collector = MetricsCollector()
        monitor = ServiceMonitor('test_service', collector)
        
        def record_requests():
            for i in range(100):
                success = i % 10 != 0  # 10% failure rate
                monitor.record_request(0.1, success=success)
        
        # Run multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=record_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert monitor.request_count == 300  # 3 threads * 100 requests
        assert monitor.error_count == 30  # 10% of 300


if __name__ == '__main__':
    pytest.main([__file__])