import unittest
import time
import threading
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.performance import (
    PerformanceMonitor, SimpleCache, measure_performance, cached,
    cache_key, optimize_for_cold_start, cleanup_resources,
    performance_monitor, vector_cache, demographic_cache, analysis_cache
)


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for performance monitoring"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_record_metric(self):
        """Test recording performance metrics"""
        self.monitor.record_metric('test_metric', 1.5, 'seconds', {'tag': 'value'})
        
        metrics = self.monitor.get_metrics('test_metric')
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]['value'], 1.5)
        self.assertEqual(metrics[0]['unit'], 'seconds')
        self.assertEqual(metrics[0]['tags']['tag'], 'value')
    
    def test_get_metrics_all(self):
        """Test getting all metrics"""
        self.monitor.record_metric('metric1', 1.0)
        self.monitor.record_metric('metric2', 2.0)
        
        all_metrics = self.monitor.get_metrics()
        self.assertIn('metric1', all_metrics)
        self.assertIn('metric2', all_metrics)
    
    def test_get_metrics_specific(self):
        """Test getting specific metric"""
        self.monitor.record_metric('test_metric', 1.0)
        
        metrics = self.monitor.get_metrics('test_metric')
        self.assertEqual(len(metrics), 1)
        
        # Test non-existent metric
        empty_metrics = self.monitor.get_metrics('non_existent')
        self.assertEqual(len(empty_metrics), 0)
    
    def test_get_average(self):
        """Test getting average metric value"""
        # Record multiple values
        for i in range(5):
            self.monitor.record_metric('test_avg', float(i))
        
        average = self.monitor.get_average('test_avg')
        self.assertEqual(average, 2.0)  # (0+1+2+3+4)/5 = 2.0
        
        # Test non-existent metric
        no_average = self.monitor.get_average('non_existent')
        self.assertIsNone(no_average)
    
    def test_metric_limit(self):
        """Test that metrics are limited to prevent memory bloat"""
        # Record more than 100 metrics
        for i in range(150):
            self.monitor.record_metric('test_limit', float(i))
        
        metrics = self.monitor.get_metrics('test_limit')
        self.assertEqual(len(metrics), 100)  # Should be limited to 100
        
        # Should contain the last 100 values (50-149)
        values = [m['value'] for m in metrics]
        self.assertEqual(min(values), 50.0)
        self.assertEqual(max(values), 149.0)
    
    def test_thread_safety(self):
        """Test thread safety of performance monitor"""
        def record_metrics():
            for i in range(10):
                self.monitor.record_metric('thread_test', float(i))
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=record_metrics)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 50 total metrics (5 threads * 10 metrics each)
        metrics = self.monitor.get_metrics('thread_test')
        self.assertEqual(len(metrics), 50)


class TestSimpleCache(unittest.TestCase):
    """Test cases for simple cache"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = SimpleCache(default_ttl=1)  # 1 second TTL for testing
    
    def test_set_and_get(self):
        """Test basic cache set and get operations"""
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        # Test non-existent key
        self.assertIsNone(self.cache.get('non_existent'))
    
    def test_ttl_expiration(self):
        """Test TTL expiration"""
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('key1'))
    
    def test_custom_ttl(self):
        """Test custom TTL"""
        # Set with custom TTL of 2 seconds
        self.cache.set('key1', 'value1', ttl=2)
        
        # Should still be available after 1 second
        time.sleep(1.1)
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        # Should expire after 2 seconds
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('key1'))
    
    def test_delete(self):
        """Test cache deletion"""
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        self.cache.delete('key1')
        self.assertIsNone(self.cache.get('key1'))
    
    def test_clear(self):
        """Test cache clearing"""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get('key1'))
        self.assertIsNone(self.cache.get('key2'))
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Add new entry
        self.cache.set('key3', 'value3')
        
        # Cleanup should remove 2 expired entries
        removed_count = self.cache.cleanup_expired()
        self.assertEqual(removed_count, 2)
        
        # Only key3 should remain
        self.assertIsNone(self.cache.get('key1'))
        self.assertIsNone(self.cache.get('key2'))
        self.assertEqual(self.cache.get('key3'), 'value3')
    
    def test_get_stats(self):
        """Test cache statistics"""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['active_entries'], 2)
        self.assertEqual(stats['expired_entries'], 0)
    
    def test_thread_safety(self):
        """Test thread safety of cache"""
        def cache_operations():
            for i in range(10):
                self.cache.set(f'key_{i}', f'value_{i}')
                self.cache.get(f'key_{i}')
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=cache_operations)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Cache should have entries from all threads
        stats = self.cache.get_stats()
        self.assertGreater(stats['total_entries'], 0)


class TestPerformanceDecorators(unittest.TestCase):
    """Test cases for performance decorators"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_monitor = PerformanceMonitor()
    
    def test_measure_performance_decorator(self):
        """Test measure_performance decorator"""
        @measure_performance('test_function')
        def test_function(duration=0.1):
            time.sleep(duration)
            return 'result'
        
        result = test_function(0.05)
        self.assertEqual(result, 'result')
        
        # Check that metric was recorded
        metrics = performance_monitor.get_metrics('test_function')
        self.assertGreater(len(metrics), 0)
        self.assertGreaterEqual(metrics[-1]['value'], 0.05)
    
    def test_measure_performance_with_exception(self):
        """Test measure_performance decorator with exception"""
        @measure_performance('test_function_error')
        def test_function_error():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            test_function_error()
        
        # Check that metric was still recorded
        metrics = performance_monitor.get_metrics('test_function_error')
        self.assertGreater(len(metrics), 0)
        self.assertEqual(metrics[-1]['tags']['success'], 'False')
    
    def test_cached_decorator(self):
        """Test cached decorator"""
        call_count = 0
        
        @cached(SimpleCache(default_ttl=60))
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Different argument should execute function again
        result3 = expensive_function(10)
        self.assertEqual(result3, 20)
        self.assertEqual(call_count, 2)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        # Test with simple arguments
        key1 = cache_key('arg1', 'arg2', kwarg1='value1')
        key2 = cache_key('arg1', 'arg2', kwarg1='value1')
        self.assertEqual(key1, key2)
        
        # Test with different arguments
        key3 = cache_key('arg1', 'arg3', kwarg1='value1')
        self.assertNotEqual(key1, key3)
        
        # Test with objects
        obj1 = Mock()
        obj2 = Mock()
        key4 = cache_key(obj1)
        key5 = cache_key(obj2)
        self.assertNotEqual(key4, key5)


class TestPerformanceOptimizations(unittest.TestCase):
    """Test cases for performance optimizations"""
    
    def test_optimize_for_cold_start(self):
        """Test cold start optimization"""
        # This should run without errors
        optimize_for_cold_start()
        
        # Check that caches are initialized
        self.assertIsNotNone(vector_cache)
        self.assertIsNotNone(demographic_cache)
        self.assertIsNotNone(analysis_cache)
    
    def test_cleanup_resources(self):
        """Test resource cleanup"""
        with patch('gc.collect', return_value=42) as mock_gc_collect:
            # Add some cache entries
            vector_cache.set('test1', 'value1')
            demographic_cache.set('test2', 'value2')
            
            cleanup_stats = cleanup_resources()
            
            self.assertIn('expired_cache_entries', cleanup_stats)
            self.assertIn('gc_collected', cleanup_stats)
            self.assertIn('memory_usage', cleanup_stats)
            self.assertEqual(cleanup_stats['gc_collected'], 42)
            
            # Verify garbage collection was called
            mock_gc_collect.assert_called_once()
    
    def test_get_memory_usage_with_psutil(self):
        """Test memory usage with psutil available"""
        try:
            import psutil
            psutil_available = True
        except ImportError:
            psutil_available = False
        
        if not psutil_available:
            self.skipTest("psutil not available")
        
        with patch('psutil.Process') as mock_process_class, \
             patch('psutil.virtual_memory') as mock_virtual_memory:
            
            # Mock psutil
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(rss=1024*1024*100, vms=1024*1024*200)
            mock_process.memory_percent.return_value = 15.5
            mock_process_class.return_value = mock_process
            mock_virtual_memory.return_value = Mock(available=1024*1024*1024)
            
            from app.performance import get_memory_usage
            usage = get_memory_usage()
            
            self.assertEqual(usage['rss_mb'], 100.0)
            self.assertEqual(usage['vms_mb'], 200.0)
            self.assertEqual(usage['percent'], 15.5)
            self.assertEqual(usage['available_mb'], 1024.0)
    
    def test_get_memory_usage_fallback(self):
        """Test memory usage fallback without psutil"""
        with patch.dict('sys.modules', {'psutil': None}):
            from app.performance import get_memory_usage
            usage = get_memory_usage()
            
            # Should have fallback fields (different on Windows vs Unix)
            if 'memory_info' in usage:
                # Windows fallback
                self.assertEqual(usage['memory_info'], 'unavailable')
                self.assertEqual(usage['platform'], 'windows_or_limited')
            else:
                # Unix fallback with resource module
                self.assertIn('max_rss_mb', usage)
                self.assertIn('user_time', usage)
                self.assertIn('system_time', usage)


class TestGlobalCaches(unittest.TestCase):
    """Test cases for global cache instances"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clear all caches before each test
        vector_cache.clear()
        demographic_cache.clear()
        analysis_cache.clear()
    
    def test_vector_cache(self):
        """Test vector cache functionality"""
        test_vector = [0.1, 0.2, 0.3]
        vector_cache.set('test_vector', test_vector)
        
        retrieved = vector_cache.get('test_vector')
        self.assertEqual(retrieved, test_vector)
    
    def test_demographic_cache(self):
        """Test demographic cache functionality"""
        test_demographics = {'ethnicity': 'caucasian', 'age': '25-35'}
        demographic_cache.set('user_123', test_demographics)
        
        retrieved = demographic_cache.get('user_123')
        self.assertEqual(retrieved, test_demographics)
    
    def test_analysis_cache(self):
        """Test analysis cache functionality"""
        test_analysis = {'skin_type': 'normal', 'concerns': ['acne']}
        analysis_cache.set('analysis_456', test_analysis)
        
        retrieved = analysis_cache.get('analysis_456')
        self.assertEqual(retrieved, test_analysis)
    
    def test_cache_isolation(self):
        """Test that caches are isolated from each other"""
        vector_cache.set('key1', 'vector_value')
        demographic_cache.set('key1', 'demographic_value')
        analysis_cache.set('key1', 'analysis_value')
        
        self.assertEqual(vector_cache.get('key1'), 'vector_value')
        self.assertEqual(demographic_cache.get('key1'), 'demographic_value')
        self.assertEqual(analysis_cache.get('key1'), 'analysis_value')


if __name__ == '__main__':
    unittest.main()