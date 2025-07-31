"""
Comprehensive monitoring and metrics collection for AI services
"""
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceHealth:
    """Service health status"""
    service_name: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    response_time: float
    error_rate: float
    success_rate: float
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self, max_points_per_metric: int = 1000):
        self.max_points_per_metric = max_points_per_metric
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points_per_metric))
        self.service_health: Dict[str, ServiceHealth] = {}
        self._lock = threading.RLock()
        
        # Performance counters
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        
        # Error tracking
        self.error_counts = defaultdict(int)
        self.error_details = defaultdict(list)
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None,
                     metadata: Dict[str, Any] = None):
        """Record a metric data point"""
        with self._lock:
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                tags=tags or {},
                metadata=metadata or {}
            )
            self.metrics[name].append(point)
    
    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        with self._lock:
            counter_key = f"{name}:{json.dumps(tags or {}, sort_keys=True)}"
            self.counters[counter_key] += value
            
            # Also record as time series
            self.record_metric(f"{name}_count", value, tags)
    
    def record_timing(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timing information"""
        with self._lock:
            timer_key = f"{name}:{json.dumps(tags or {}, sort_keys=True)}"
            self.timers[timer_key].append(duration)
            
            # Keep only recent timings
            if len(self.timers[timer_key]) > 100:
                self.timers[timer_key] = self.timers[timer_key][-100:]
            
            # Record as metric
            self.record_metric(f"{name}_duration", duration, tags)
    
    def record_error(self, service_name: str, error_type: str, error_message: str,
                    tags: Dict[str, str] = None):
        """Record error information"""
        with self._lock:
            error_key = f"{service_name}:{error_type}"
            self.error_counts[error_key] += 1
            
            error_detail = {
                'timestamp': datetime.utcnow().isoformat(),
                'service_name': service_name,
                'error_type': error_type,
                'error_message': error_message,
                'tags': tags or {}
            }
            
            self.error_details[error_key].append(error_detail)
            
            # Keep only recent errors
            if len(self.error_details[error_key]) > 50:
                self.error_details[error_key] = self.error_details[error_key][-50:]
            
            # Record as metric
            error_tags = (tags or {}).copy()
            error_tags['error_type'] = error_type
            self.record_metric(f"{service_name}_errors", 1, error_tags)
    
    def update_service_health(self, service_name: str, status: str, 
                            response_time: float, error_rate: float,
                            details: Dict[str, Any] = None):
        """Update service health status"""
        with self._lock:
            success_rate = max(0.0, 1.0 - error_rate)
            
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                status=status,
                last_check=datetime.utcnow(),
                response_time=response_time,
                error_rate=error_rate,
                success_rate=success_rate,
                details=details or {}
            )
            
            # Record as metrics
            self.record_metric(f"{service_name}_response_time", response_time)
            self.record_metric(f"{service_name}_error_rate", error_rate)
            self.record_metric(f"{service_name}_success_rate", success_rate)
    
    def get_metric_summary(self, name: str, window_minutes: int = 5) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        with self._lock:
            if name not in self.metrics:
                return {}
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_points = [
                point for point in self.metrics[name]
                if point.timestamp > cutoff_time
            ]
            
            if not recent_points:
                return {}
            
            values = [point.value for point in recent_points]
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'latest': values[-1] if values else 0,
                'window_minutes': window_minutes
            }
    
    def get_service_health_summary(self) -> Dict[str, Any]:
        """Get overall service health summary"""
        with self._lock:
            summary = {
                'overall_status': 'healthy',
                'services': {},
                'total_services': len(self.service_health),
                'healthy_services': 0,
                'degraded_services': 0,
                'unhealthy_services': 0
            }
            
            for service_name, health in self.service_health.items():
                summary['services'][service_name] = {
                    'status': health.status,
                    'response_time': health.response_time,
                    'error_rate': health.error_rate,
                    'success_rate': health.success_rate,
                    'last_check': health.last_check.isoformat(),
                    'details': health.details
                }
                
                if health.status == 'healthy':
                    summary['healthy_services'] += 1
                elif health.status == 'degraded':
                    summary['degraded_services'] += 1
                else:
                    summary['unhealthy_services'] += 1
            
            # Determine overall status
            if summary['unhealthy_services'] > 0:
                summary['overall_status'] = 'unhealthy'
            elif summary['degraded_services'] > 0:
                summary['overall_status'] = 'degraded'
            
            return summary
    
    def get_error_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get error summary for recent time window"""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            recent_errors = {}
            total_errors = 0
            
            for error_key, error_list in self.error_details.items():
                recent_error_list = [
                    error for error in error_list
                    if datetime.fromisoformat(error['timestamp']) > cutoff_time
                ]
                
                if recent_error_list:
                    recent_errors[error_key] = {
                        'count': len(recent_error_list),
                        'latest_error': recent_error_list[-1],
                        'error_types': list(set(error['error_type'] for error in recent_error_list))
                    }
                    total_errors += len(recent_error_list)
            
            return {
                'total_errors': total_errors,
                'error_types': len(recent_errors),
                'window_minutes': window_minutes,
                'errors_by_service': recent_errors
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all services"""
        with self._lock:
            summary = {
                'counters': dict(self.counters),
                'timing_stats': {},
                'active_metrics': len(self.metrics),
                'total_data_points': sum(len(points) for points in self.metrics.values())
            }
            
            # Calculate timing statistics
            for timer_key, timings in self.timers.items():
                if timings:
                    summary['timing_stats'][timer_key] = {
                        'count': len(timings),
                        'min': min(timings),
                        'max': max(timings),
                        'avg': sum(timings) / len(timings),
                        'p95': sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 1 else timings[0]
                    }
            
            return summary
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old metric data"""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for metric_name, points in self.metrics.items():
                original_length = len(points)
                # Filter out old points
                while points and points[0].timestamp < cutoff_time:
                    points.popleft()
                cleaned_count += original_length - len(points)
            
            # Clean up error details
            for error_key, error_list in self.error_details.items():
                original_length = len(error_list)
                self.error_details[error_key] = [
                    error for error in error_list
                    if datetime.fromisoformat(error['timestamp']) > cutoff_time
                ]
                cleaned_count += original_length - len(self.error_details[error_key])
            
            logger.info(f"Cleaned up {cleaned_count} old metric data points")
            return cleaned_count


class ServiceMonitor:
    """Monitors individual service health and performance"""
    
    def __init__(self, service_name: str, metrics_collector: MetricsCollector):
        self.service_name = service_name
        self.metrics_collector = metrics_collector
        self.last_health_check = None
        self.health_check_interval = 60  # seconds
        
        # Performance tracking
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.last_reset = datetime.utcnow()
    
    def record_request(self, duration: float, success: bool = True, 
                      error_type: str = None, error_message: str = None):
        """Record a service request"""
        self.request_count += 1
        self.total_response_time += duration
        
        if not success:
            self.error_count += 1
            if error_type and error_message:
                self.metrics_collector.record_error(
                    self.service_name, error_type, error_message
                )
        
        # Record timing
        self.metrics_collector.record_timing(
            f"{self.service_name}_request",
            duration,
            {'success': str(success)}
        )
        
        # Record counter
        self.metrics_collector.increment_counter(
            f"{self.service_name}_requests",
            tags={'success': str(success)}
        )
    
    def check_health(self) -> ServiceHealth:
        """Perform health check and update metrics"""
        now = datetime.utcnow()
        
        # Calculate metrics since last reset
        if self.request_count > 0:
            avg_response_time = self.total_response_time / self.request_count
            error_rate = self.error_count / self.request_count
        else:
            avg_response_time = 0.0
            error_rate = 0.0
        
        # Determine health status
        if error_rate > 0.5:
            status = 'unhealthy'
        elif error_rate > 0.1 or avg_response_time > 5.0:
            status = 'degraded'
        else:
            status = 'healthy'
        
        # Update service health
        self.metrics_collector.update_service_health(
            self.service_name,
            status,
            avg_response_time,
            error_rate,
            details={
                'request_count': self.request_count,
                'error_count': self.error_count,
                'uptime_seconds': (now - self.last_reset).total_seconds()
            }
        )
        
        self.last_health_check = now
        return self.metrics_collector.service_health[self.service_name]
    
    def reset_counters(self):
        """Reset performance counters"""
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.last_reset = datetime.utcnow()


class AlertManager:
    """Manages alerts based on metrics and thresholds"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules: List[Dict[str, Any]] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = [
            {
                'name': 'high_error_rate',
                'condition': lambda health: health.error_rate > 0.1,
                'severity': 'warning',
                'message': 'High error rate detected'
            },
            {
                'name': 'very_high_error_rate',
                'condition': lambda health: health.error_rate > 0.5,
                'severity': 'critical',
                'message': 'Very high error rate detected'
            },
            {
                'name': 'slow_response_time',
                'condition': lambda health: health.response_time > 5.0,
                'severity': 'warning',
                'message': 'Slow response time detected'
            },
            {
                'name': 'service_unhealthy',
                'condition': lambda health: health.status == 'unhealthy',
                'severity': 'critical',
                'message': 'Service is unhealthy'
            }
        ]
    
    def check_alerts(self):
        """Check all alert rules against current metrics"""
        with self._lock:
            current_time = datetime.utcnow()
            
            for service_name, health in self.metrics_collector.service_health.items():
                for rule in self.alert_rules:
                    alert_key = f"{service_name}:{rule['name']}"
                    
                    if rule['condition'](health):
                        # Alert condition is met
                        if alert_key not in self.active_alerts:
                            # New alert
                            alert = {
                                'service_name': service_name,
                                'rule_name': rule['name'],
                                'severity': rule['severity'],
                                'message': rule['message'],
                                'started_at': current_time,
                                'last_seen': current_time,
                                'health_snapshot': health
                            }
                            
                            self.active_alerts[alert_key] = alert
                            self.alert_history.append(alert.copy())
                            
                            logger.warning(f"ALERT: {rule['severity'].upper()} - {service_name}: {rule['message']}")
                        else:
                            # Update existing alert
                            self.active_alerts[alert_key]['last_seen'] = current_time
                            self.active_alerts[alert_key]['health_snapshot'] = health
                    else:
                        # Alert condition is not met
                        if alert_key in self.active_alerts:
                            # Resolve alert
                            resolved_alert = self.active_alerts.pop(alert_key)
                            resolved_alert['resolved_at'] = current_time
                            
                            logger.info(f"RESOLVED: {service_name}: {rule['message']}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        with self._lock:
            return self.alert_history[-limit:]


# Global monitoring instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager(metrics_collector)

# Service monitors
service_monitors: Dict[str, ServiceMonitor] = {}


def get_service_monitor(service_name: str) -> ServiceMonitor:
    """Get or create service monitor"""
    if service_name not in service_monitors:
        service_monitors[service_name] = ServiceMonitor(service_name, metrics_collector)
    return service_monitors[service_name]


def monitor_service_call(service_name: str):
    """Decorator to monitor service calls"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            monitor = get_service_monitor(service_name)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_request(duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_request(
                    duration, 
                    success=False,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def start_monitoring_thread():
    """Start background monitoring thread"""
    def monitoring_loop():
        while True:
            try:
                # Check service health
                for monitor in service_monitors.values():
                    monitor.check_health()
                
                # Check alerts
                alert_manager.check_alerts()
                
                # Clean up old data periodically
                if datetime.utcnow().minute == 0:  # Once per hour
                    metrics_collector.cleanup_old_data()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    logger.info("Monitoring thread started")


def get_monitoring_dashboard() -> Dict[str, Any]:
    """Get comprehensive monitoring dashboard data"""
    return {
        'service_health': metrics_collector.get_service_health_summary(),
        'performance': metrics_collector.get_performance_summary(),
        'errors': metrics_collector.get_error_summary(),
        'active_alerts': alert_manager.get_active_alerts(),
        'alert_history': alert_manager.get_alert_history(20),
        'timestamp': datetime.utcnow().isoformat()
    }


# Initialize monitoring
start_monitoring_thread()