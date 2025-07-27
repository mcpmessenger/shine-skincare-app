"""
Vercel-specific performance optimizations for serverless deployment
"""
import os
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import pickle
import gzip
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.performance import (
    performance_monitor, vector_cache, demographic_cache, analysis_cache,
    measure_performance, cached, SimpleCache
)

logger = logging.getLogger(__name__)


class VercelOptimizer:
    """Optimizations specifically for Vercel serverless deployment"""
    
    def __init__(self):
        self.cold_start_time = time.time()
        self.initialization_complete = False
        self.service_cache = {}
        self.preloaded_data = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.Lock()
    
    def is_cold_start(self) -> bool:
        """Check if this is a cold start"""
        return time.time() - self.cold_start_time < 30  # Consider first 30s as cold start
    
    def optimize_cold_start(self):
        """Optimize for cold start performance"""
        start_time = time.time()
        logger.info("Starting cold start optimization...")
        
        try:
            # Pre-import critical modules in parallel
            self._preload_modules()
            
            # Initialize lightweight service instances
            self._initialize_lightweight_services()
            
            # Pre-warm caches with essential data
            self._prewarm_caches()
            
            # Set up memory-efficient configurations
            self._configure_memory_efficiency()
            
            self.initialization_complete = True
            duration = time.time() - start_time
            
            logger.info(f"Cold start optimization completed in {duration:.3f}s")
            performance_monitor.record_metric('cold_start_duration', duration, 'seconds')
            
        except Exception as e:
            logger.error(f"Cold start optimization failed: {e}")
            raise
    
    def _preload_modules(self):
        """Pre-load critical modules to reduce import time"""
        critical_modules = [
            'numpy',
            'faiss',
            'json',
            'base64',
            'hashlib',
            'threading',
            'concurrent.futures'
        ]
        
        for module_name in critical_modules:
            try:
                __import__(module_name)
                logger.debug(f"Pre-loaded module: {module_name}")
            except ImportError as e:
                logger.warning(f"Could not pre-load {module_name}: {e}")
    
    def _initialize_lightweight_services(self):
        """Initialize lightweight versions of services for cold starts"""
        try:
            # Initialize minimal FAISS service
            from app.services.production_faiss_service import ProductionFAISSService
            
            # Use smaller dimension for cold start
            cold_start_faiss = ProductionFAISSService(
                dimension=128,  # Smaller dimension for faster initialization
                index_file_path=None  # Don't load index on cold start
            )
            
            self.service_cache['faiss_lightweight'] = cold_start_faiss
            logger.debug("Initialized lightweight FAISS service")
            
        except Exception as e:
            logger.warning(f"Could not initialize lightweight services: {e}")
    
    def _prewarm_caches(self):
        """Pre-warm caches with frequently accessed data"""
        try:
            # Pre-warm with common demographic combinations
            common_demographics = [
                {'ethnicity': 'caucasian', 'skin_type': 'normal', 'age_group': '25-35'},
                {'ethnicity': 'african', 'skin_type': 'oily', 'age_group': '18-25'},
                {'ethnicity': 'east_asian', 'skin_type': 'sensitive', 'age_group': '35-45'},
            ]
            
            for demo in common_demographics:
                cache_key = f"demo_weights:{json.dumps(demo, sort_keys=True)}"
                # Cache empty placeholder to initialize cache structure
                demographic_cache.set(cache_key, {}, ttl=1800)
            
            logger.debug("Pre-warmed demographic cache")
            
        except Exception as e:
            logger.warning(f"Cache pre-warming failed: {e}")
    
    def _configure_memory_efficiency(self):
        """Configure memory-efficient settings"""
        try:
            # Set environment variables for memory efficiency
            os.environ.setdefault('PYTHONHASHSEED', '0')  # Consistent hashing
            os.environ.setdefault('PYTHONOPTIMIZE', '1')  # Enable optimizations
            
            # Configure numpy for memory efficiency
            try:
                import numpy as np
                # Limit numpy threads to reduce memory overhead
                os.environ.setdefault('OMP_NUM_THREADS', '2')
                os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
                os.environ.setdefault('MKL_NUM_THREADS', '2')
                logger.debug("Configured numpy for memory efficiency")
            except ImportError:
                pass
            
        except Exception as e:
            logger.warning(f"Memory efficiency configuration failed: {e}")
    
    def get_optimized_service(self, service_name: str, full_service_factory=None):
        """Get optimized service instance based on current state"""
        with self._lock:
            # During cold start, return lightweight version if available
            if self.is_cold_start() and f"{service_name}_lightweight" in self.service_cache:
                logger.debug(f"Returning lightweight {service_name} service for cold start")
                return self.service_cache[f"{service_name}_lightweight"]
            
            # Return full service if available
            if service_name in self.service_cache:
                return self.service_cache[service_name]
            
            # Create full service if factory provided
            if full_service_factory:
                logger.debug(f"Creating full {service_name} service")
                service = full_service_factory()
                self.service_cache[service_name] = service
                return service
            
            return None


class MemoryOptimizer:
    """Memory optimization utilities for Vercel deployment"""
    
    @staticmethod
    def compress_data(data: Any) -> bytes:
        """Compress data for efficient storage"""
        try:
            serialized = pickle.dumps(data)
            compressed = gzip.compress(serialized)
            return compressed
        except Exception as e:
            logger.error(f"Data compression failed: {e}")
            return pickle.dumps(data)  # Fallback to uncompressed
    
    @staticmethod
    def decompress_data(compressed_data: bytes) -> Any:
        """Decompress data"""
        try:
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
        except Exception:
            # Fallback: try direct pickle load (uncompressed)
            return pickle.loads(compressed_data)
    
    @staticmethod
    def optimize_numpy_array(array) -> Any:
        """Optimize numpy array for memory efficiency"""
        try:
            import numpy as np
            
            if not isinstance(array, np.ndarray):
                return array
            
            # Convert to most efficient dtype
            if array.dtype == np.float64:
                # Convert to float32 if precision loss is acceptable
                array = array.astype(np.float32)
            
            # Ensure array is contiguous for better cache performance
            if not array.flags['C_CONTIGUOUS']:
                array = np.ascontiguousarray(array)
            
            return array
            
        except ImportError:
            return array
    
    @staticmethod
    def get_memory_efficient_config() -> Dict[str, Any]:
        """Get memory-efficient configuration settings"""
        return {
            'faiss_dimension': 128,  # Reduced from 512 for memory efficiency
            'max_cache_size': 100,   # Limit cache entries
            'batch_size': 32,        # Smaller batch sizes
            'max_workers': 2,        # Limit concurrent workers
            'enable_compression': True,
            'gc_threshold': 50       # More frequent garbage collection
        }


class CacheOptimizer:
    """Advanced caching optimizations for Vercel"""
    
    def __init__(self):
        self.hit_counts = {}
        self.access_patterns = {}
        self._lock = threading.Lock()
    
    def smart_cache_key(self, *args, **kwargs) -> str:
        """Generate optimized cache key"""
        import hashlib
        
        # Create more efficient key representation
        key_parts = []
        
        for arg in args:
            if hasattr(arg, 'shape'):  # numpy array
                key_parts.append(f"array:{arg.shape}:{hash(arg.tobytes())}")
            elif isinstance(arg, dict):
                # Sort dict for consistent keys
                sorted_items = sorted(arg.items())
                key_parts.append(f"dict:{hash(str(sorted_items))}")
            else:
                key_parts.append(str(hash(str(arg))))
        
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{hash(str(v))}")
        
        # Use shorter hash for memory efficiency
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def adaptive_ttl(self, base_ttl: int, access_frequency: float) -> int:
        """Calculate adaptive TTL based on access patterns"""
        # More frequently accessed items get longer TTL
        if access_frequency > 0.8:
            return base_ttl * 2
        elif access_frequency > 0.5:
            return base_ttl
        else:
            return max(base_ttl // 2, 60)  # Minimum 1 minute
    
    def record_access(self, key: str):
        """Record cache access for pattern analysis"""
        with self._lock:
            self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
            self.access_patterns[key] = time.time()
    
    def get_cache_efficiency_stats(self) -> Dict[str, Any]:
        """Get cache efficiency statistics"""
        with self._lock:
            total_accesses = sum(self.hit_counts.values())
            unique_keys = len(self.hit_counts)
            
            if total_accesses == 0:
                return {'efficiency': 0, 'unique_keys': 0, 'total_accesses': 0}
            
            # Calculate efficiency metrics
            avg_accesses_per_key = total_accesses / unique_keys if unique_keys > 0 else 0
            
            return {
                'efficiency': avg_accesses_per_key,
                'unique_keys': unique_keys,
                'total_accesses': total_accesses,
                'cache_stats': {
                    'vector_cache': vector_cache.get_stats(),
                    'demographic_cache': demographic_cache.get_stats(),
                    'analysis_cache': analysis_cache.get_stats()
                }
            }


class RequestOptimizer:
    """Optimize request handling for Vercel"""
    
    def __init__(self):
        self.request_queue = []
        self.processing_times = {}
        self._lock = threading.Lock()
    
    def batch_similar_requests(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Batch similar requests for efficient processing"""
        batches = {}
        
        for request in requests:
            # Create batch key based on request type and parameters
            batch_key = self._get_batch_key(request)
            
            if batch_key not in batches:
                batches[batch_key] = []
            
            batches[batch_key].append(request)
        
        return list(batches.values())
    
    def _get_batch_key(self, request: Dict[str, Any]) -> str:
        """Generate batch key for similar requests"""
        # Group by endpoint and similar parameters
        endpoint = request.get('endpoint', 'unknown')
        method = request.get('method', 'GET')
        
        # Include relevant parameters for batching
        params = request.get('params', {})
        batch_params = {
            k: v for k, v in params.items()
            if k in ['skin_type', 'ethnicity', 'age_group']  # Demographic parameters
        }
        
        return f"{method}:{endpoint}:{json.dumps(batch_params, sort_keys=True)}"
    
    @measure_performance('request_optimization')
    def optimize_request_processing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize individual request processing"""
        start_time = time.time()
        
        try:
            # Pre-process request data
            optimized_data = self._preprocess_request(request_data)
            
            # Apply request-specific optimizations
            if 'image_data' in optimized_data:
                optimized_data['image_data'] = self._optimize_image_data(
                    optimized_data['image_data']
                )
            
            processing_time = time.time() - start_time
            
            with self._lock:
                self.processing_times[request_data.get('request_id', 'unknown')] = processing_time
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"Request optimization failed: {e}")
            return request_data  # Return original data on failure
    
    def _preprocess_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process request data for optimization"""
        optimized = request_data.copy()
        
        # Normalize demographic data
        if 'demographics' in optimized:
            optimized['demographics'] = self._normalize_demographics(
                optimized['demographics']
            )
        
        # Optimize vector data
        if 'vector' in optimized:
            optimized['vector'] = MemoryOptimizer.optimize_numpy_array(
                optimized['vector']
            )
        
        return optimized
    
    def _normalize_demographics(self, demographics: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize demographic data for consistent processing"""
        normalized = {}
        
        # Standardize ethnicity values
        ethnicity_mapping = {
            'white': 'caucasian',
            'black': 'african',
            'asian': 'east_asian',
            'hispanic': 'hispanic',
            'latino': 'hispanic'
        }
        
        ethnicity = demographics.get('ethnicity', '').lower()
        normalized['ethnicity'] = ethnicity_mapping.get(ethnicity, ethnicity)
        
        # Standardize skin type
        skin_type_mapping = {
            'dry': 'dry',
            'oily': 'oily',
            'combination': 'combination',
            'normal': 'normal',
            'sensitive': 'sensitive'
        }
        
        skin_type = demographics.get('skin_type', '').lower()
        normalized['skin_type'] = skin_type_mapping.get(skin_type, 'normal')
        
        # Standardize age group
        age = demographics.get('age', 0)
        if isinstance(age, (int, float)):
            if age < 18:
                normalized['age_group'] = 'under_18'
            elif age < 25:
                normalized['age_group'] = '18-25'
            elif age < 35:
                normalized['age_group'] = '25-35'
            elif age < 45:
                normalized['age_group'] = '35-45'
            elif age < 55:
                normalized['age_group'] = '45-55'
            else:
                normalized['age_group'] = '55+'
        else:
            normalized['age_group'] = demographics.get('age_group', '25-35')
        
        return normalized
    
    def _optimize_image_data(self, image_data: Any) -> Any:
        """Optimize image data for processing"""
        try:
            import numpy as np
            
            if isinstance(image_data, np.ndarray):
                # Ensure optimal dtype and memory layout
                return MemoryOptimizer.optimize_numpy_array(image_data)
            
            return image_data
            
        except ImportError:
            return image_data


# Global optimizer instances
vercel_optimizer = VercelOptimizer()
memory_optimizer = MemoryOptimizer()
cache_optimizer = CacheOptimizer()
request_optimizer = RequestOptimizer()


def optimize_for_vercel():
    """Main function to apply all Vercel optimizations"""
    logger.info("Applying Vercel-specific optimizations...")
    
    try:
        # Apply cold start optimizations
        vercel_optimizer.optimize_cold_start()
        
        # Configure memory efficiency
        config = memory_optimizer.get_memory_efficient_config()
        logger.info(f"Applied memory-efficient config: {config}")
        
        # Set up performance monitoring
        performance_monitor.record_metric(
            'vercel_optimization_complete',
            1,
            'boolean',
            {'timestamp': datetime.utcnow().isoformat()}
        )
        
        logger.info("Vercel optimizations applied successfully")
        
    except Exception as e:
        logger.error(f"Vercel optimization failed: {e}")
        raise


def vercel_performance_middleware(app):
    """Middleware specifically optimized for Vercel deployment"""
    
    @app.before_first_request
    def initialize_vercel_optimizations():
        """Initialize optimizations on first request"""
        if not vercel_optimizer.initialization_complete:
            optimize_for_vercel()
    
    @app.before_request
    def optimize_request():
        """Optimize each request"""
        from flask import g, request
        
        g.request_start_time = time.time()
        
        # Apply request-specific optimizations
        if request.is_json and request.json:
            g.optimized_request_data = request_optimizer.optimize_request_processing(
                request.json
            )
    
    @app.after_request
    def record_request_metrics(response):
        """Record request performance metrics"""
        from flask import g, request
        
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            
            # Record detailed metrics for Vercel
            performance_monitor.record_metric(
                'vercel_request_duration',
                duration,
                'seconds',
                {
                    'method': request.method,
                    'endpoint': request.endpoint or 'unknown',
                    'status_code': str(response.status_code),
                    'cold_start': str(vercel_optimizer.is_cold_start()),
                    'content_length': str(response.content_length or 0)
                }
            )
            
            # Log slow requests
            if duration > 5.0:  # Vercel has 10s timeout, warn at 5s
                logger.warning(
                    f"Slow Vercel request: {request.endpoint} took {duration:.3f}s",
                    extra={
                        'duration': duration,
                        'endpoint': request.endpoint,
                        'method': request.method
                    }
                )
        
        return response
    
    return app


def get_vercel_performance_stats() -> Dict[str, Any]:
    """Get comprehensive performance statistics for Vercel"""
    return {
        'vercel_optimizer': {
            'cold_start_time': vercel_optimizer.cold_start_time,
            'is_cold_start': vercel_optimizer.is_cold_start(),
            'initialization_complete': vercel_optimizer.initialization_complete,
            'cached_services': list(vercel_optimizer.service_cache.keys())
        },
        'memory_stats': {
            'config': memory_optimizer.get_memory_efficient_config(),
            'current_usage': get_memory_usage()
        },
        'cache_efficiency': cache_optimizer.get_cache_efficiency_stats(),
        'performance_metrics': performance_monitor.get_metrics(),
        'timestamp': datetime.utcnow().isoformat()
    }


def get_memory_usage():
    """Get current memory usage (imported from performance.py)"""
    from app.performance import get_memory_usage as _get_memory_usage
    return _get_memory_usage()


# Optimized decorators for Vercel
def vercel_cached(ttl: int = 300, compress: bool = True):
    """Vercel-optimized caching decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate optimized cache key
            cache_key = cache_optimizer.smart_cache_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = analysis_cache.get(cache_key)
            if cached_result is not None:
                cache_optimizer.record_access(cache_key)
                
                # Decompress if needed
                if compress and isinstance(cached_result, bytes):
                    cached_result = memory_optimizer.decompress_data(cached_result)
                
                logger.debug(f"Vercel cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Compress and cache result
            cache_data = result
            if compress:
                cache_data = memory_optimizer.compress_data(result)
            
            # Use adaptive TTL
            access_freq = cache_optimizer.hit_counts.get(cache_key, 0) / 100  # Normalize
            adaptive_ttl = cache_optimizer.adaptive_ttl(ttl, access_freq)
            
            analysis_cache.set(cache_key, cache_data, adaptive_ttl)
            cache_optimizer.record_access(cache_key)
            
            logger.debug(f"Vercel cache miss for {func.__name__}, cached with TTL {adaptive_ttl}s")
            return result
        
        return wrapper
    return decorator


@measure_performance('vercel_service_call')
def vercel_service_call(service_name: str, method_name: str, *args, **kwargs):
    """Optimized service call for Vercel deployment"""
    try:
        # Get optimized service instance
        service = vercel_optimizer.get_optimized_service(service_name)
        
        if service is None:
            raise Exception(f"Service {service_name} not available")
        
        # Call method with performance monitoring
        method = getattr(service, method_name)
        result = method(*args, **kwargs)
        
        return result
        
    except Exception as e:
        logger.error(f"Vercel service call failed: {service_name}.{method_name} - {e}")
        raise