import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import os
import pickle
import hashlib
from threading import Lock

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = Lock()
    
    def record_metric(self, name: str, value: float, unit: str = 'seconds', 
                     tags: Optional[Dict[str, str]] = None):
        """Record a performance metric"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = []
            
            metric_entry = {
                'value': value,
                'unit': unit,
                'timestamp': datetime.utcnow().isoformat(),
                'tags': tags or {}
            }
            
            self.metrics[name].append(metric_entry)
            
            # Keep only last 100 entries per metric to prevent memory bloat
            if len(self.metrics[name]) > 100:
                self.metrics[name] = self.metrics[name][-100:]
    
    def get_metrics(self, name: str = None) -> Dict[str, Any]:
        """Get performance metrics"""
        with self.lock:
            if name:
                return self.metrics.get(name, [])
            return self.metrics.copy()
    
    def get_average(self, name: str, window_minutes: int = 5) -> Optional[float]:
        """Get average metric value within time window"""
        with self.lock:
            if name not in self.metrics:
                return None
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_metrics = [
                m for m in self.metrics[name]
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
            
            if not recent_metrics:
                return None
            
            return sum(m['value'] for m in recent_metrics) / len(recent_metrics)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_performance(metric_name: str = None, tags: Optional[Dict[str, str]] = None):
    """Decorator to measure function execution time"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration = time.time() - start_time
                
                # Determine metric name
                name = metric_name or f"{func.__module__}.{func.__name__}"
                
                # Add success/failure to tags
                metric_tags = (tags or {}).copy()
                metric_tags['success'] = str(success)
                if error:
                    metric_tags['error_type'] = type(error).__name__
                
                # Record metric
                performance_monitor.record_metric(name, duration, 'seconds', metric_tags)
                
                # Log slow operations
                if duration > 2.0:  # Log operations taking more than 2 seconds
                    logger.warning(f"Slow operation: {name} took {duration:.3f}s", 
                                 extra={'duration': duration, 'function': name})
            
            return result
        return wrapper
    return decorator


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl
        self.lock = Lock()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        
        return time.time() - self.timestamps[key] > self.default_ttl
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        with self.lock:
            if key in self.cache and not self._is_expired(key):
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        with self.lock:
            self.cache[key] = value
            self.timestamps[key] = time.time()
            
            # Use custom TTL if provided
            if ttl is not None:
                # Store custom TTL by adjusting timestamp
                self.timestamps[key] = time.time() - (self.default_ttl - ttl)
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        with self.lock:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed"""
        with self.lock:
            expired_keys = [
                key for key in self.cache.keys()
                if self._is_expired(key)
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_entries = len(self.cache)
            expired_count = sum(1 for key in self.cache.keys() if self._is_expired(key))
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_count,
                'expired_entries': expired_count,
                'hit_ratio': getattr(self, '_hit_count', 0) / max(getattr(self, '_access_count', 1), 1)
            }


# Global cache instances
vector_cache = SimpleCache(default_ttl=1800)  # 30 minutes for vectors
demographic_cache = SimpleCache(default_ttl=600)  # 10 minutes for demographic data
analysis_cache = SimpleCache(default_ttl=300)  # 5 minutes for analysis results


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    # Create a string representation of arguments
    key_parts = []
    
    for arg in args:
        if hasattr(arg, '__dict__'):
            # For objects, use class name and relevant attributes
            key_parts.append(f"{type(arg).__name__}:{id(arg)}")
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    # Create hash of the key parts
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(cache_instance: SimpleCache, ttl: Optional[int] = None, 
          key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_instance.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache_instance.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator


class ConnectionPool:
    """Simple connection pool for managing service connections"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = []
        self.in_use = set()
        self.lock = Lock()
    
    def get_connection(self, factory_func: Callable):
        """Get a connection from the pool"""
        with self.lock:
            # Try to reuse existing connection
            for conn in self.connections:
                if conn not in self.in_use:
                    self.in_use.add(conn)
                    return conn
            
            # Create new connection if under limit
            if len(self.connections) < self.max_connections:
                conn = factory_func()
                self.connections.append(conn)
                self.in_use.add(conn)
                return conn
            
            # Wait for connection to become available (simplified)
            # In production, you might want to implement proper waiting/queuing
            raise Exception("Connection pool exhausted")
    
    def return_connection(self, conn):
        """Return connection to pool"""
        with self.lock:
            self.in_use.discard(conn)
    
    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in self.connections:
                if hasattr(conn, 'close'):
                    try:
                        conn.close()
                    except Exception as e:
                        logger.warning(f"Error closing connection: {e}")
            
            self.connections.clear()
            self.in_use.clear()


def optimize_for_cold_start():
    """Optimize application for serverless cold starts"""
    logger.info("Optimizing for cold start...")
    
    # Pre-import heavy modules
    try:
        import numpy as np
        import faiss
        logger.debug("Pre-imported numpy and faiss")
    except ImportError as e:
        logger.warning(f"Could not pre-import modules: {e}")
    
    # Pre-warm caches with empty entries to initialize data structures
    vector_cache.set("_warmup", None, ttl=1)
    demographic_cache.set("_warmup", None, ttl=1)
    analysis_cache.set("_warmup", None, ttl=1)
    
    # Clean up warmup entries
    vector_cache.delete("_warmup")
    demographic_cache.delete("_warmup")
    analysis_cache.delete("_warmup")
    
    logger.info("Cold start optimization complete")


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    except ImportError:
        # Fallback if psutil is not available
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return {
                'max_rss_mb': usage.ru_maxrss / 1024,  # Maximum RSS (Linux: KB, macOS: bytes)
                'user_time': usage.ru_utime,
                'system_time': usage.ru_stime
            }
        except ImportError:
            # Fallback for Windows or systems without resource module
            return {
                'memory_info': 'unavailable',
                'platform': 'windows_or_limited'
            }


def cleanup_resources():
    """Clean up resources to free memory"""
    logger.info("Cleaning up resources...")
    
    # Clean up caches
    expired_vector = vector_cache.cleanup_expired()
    expired_demographic = demographic_cache.cleanup_expired()
    expired_analysis = analysis_cache.cleanup_expired()
    
    logger.info(f"Cleaned up {expired_vector + expired_demographic + expired_analysis} expired cache entries")
    
    # Force garbage collection
    import gc
    collected = gc.collect()
    logger.info(f"Garbage collection freed {collected} objects")
    
    return {
        'expired_cache_entries': expired_vector + expired_demographic + expired_analysis,
        'gc_collected': collected,
        'memory_usage': get_memory_usage()
    }


class PerformanceMiddleware:
    """Middleware to track request performance"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        def new_start_response(status, response_headers, exc_info=None):
            duration = time.time() - start_time
            
            # Record request performance
            performance_monitor.record_metric(
                'request_duration',
                duration,
                'seconds',
                {
                    'method': environ.get('REQUEST_METHOD', 'UNKNOWN'),
                    'path': environ.get('PATH_INFO', '/'),
                    'status': status.split()[0] if status else 'unknown'
                }
            )
            
            return start_response(status, response_headers, exc_info)
        
        return self.app(environ, new_start_response)


def configure_performance_monitoring(app):
    """Configure performance monitoring for Flask app"""
    
    @app.before_request
    def before_request():
        """Set up request timing"""
        from flask import g
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Record request performance"""
        from flask import g, request
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            performance_monitor.record_metric(
                'flask_request_duration',
                duration,
                'seconds',
                {
                    'method': request.method,
                    'endpoint': request.endpoint or 'unknown',
                    'status_code': str(response.status_code)
                }
            )
        
        return response
    
    # Add performance endpoint
    @app.route('/api/performance/metrics')
    def get_performance_metrics():
        """Get performance metrics"""
        from flask import jsonify
        
        metrics = performance_monitor.get_metrics()
        cache_stats = {
            'vector_cache': vector_cache.get_stats(),
            'demographic_cache': demographic_cache.get_stats(),
            'analysis_cache': analysis_cache.get_stats()
        }
        
        return jsonify({
            'metrics': metrics,
            'cache_stats': cache_stats,
            'memory_usage': get_memory_usage(),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/performance/cleanup', methods=['POST'])
    def cleanup_performance():
        """Clean up resources"""
        from flask import jsonify
        
        cleanup_stats = cleanup_resources()
        return jsonify(cleanup_stats)