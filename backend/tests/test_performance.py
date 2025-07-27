"""
Performance tests for Vercel deployment optimization
"""
import pytest
import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import numpy as np

from app.vercel_optimizations import (
    VercelOptimizer, MemoryOptimizer, CacheOptimizer, RequestOptimizer,
    vercel_optimizer, memory_optimizer, cache_optimizer, request_optimizer,
    vercel_cached, vercel_service_call
)
from app.performance import performance_monitor, vector_cache, demographic_cache


class TestVercelOptimizer:
    """Test Vercel-specific optimizations"""
    
    def test_cold_start_detection(self):
        """Test cold start detection"""
        optimizer = VercelOptimizer()
        
        # Should be cold start initially
        assert optimizer.is_cold_start() is True
        
        # Simulate time passing
        optimizer.cold_start_time = time.time() - 35  # 35 seconds ago
        assert optimizer.is_cold_start() is False
    
    def test_cold_start_optimization(self):
        """Test cold start optimization process"""
        optimizer = VercelOptimizer()
        
        start_time = time.time()
        optimizer.optimize_cold_start()
        duration = time.time() - start_time
        
        assert optimizer.initialization_complete is True
        assert duration < 5.0  # Should complete quickly
        assert 'faiss_lightweight' in optimizer.service_cache
    
    def test_lightweight_service_retrieval(self):
        """Test retrieval of lightweight services during cold start"""
        optimizer = VercelOptimizer()
        optimizer.optimize_cold_start()
        
        # During cold start, should return lightweight service
        service = optimizer.get_optimized_service('faiss')
        assert service is not None
        
        # After cold start period, should create full service if factory provided
        optimizer.cold_start_time = time.time() - 35  # Simulate end of cold start
        
        def mock_factory():
            return Mock()
        
        full_service = optimizer.get_optimized_service('faiss', mock_factory)
        assert full_service is not None
        assert full_service != service  # Should be different instance
    
    def test_service_caching(self):
        """Test service instance caching"""
        optimizer = VercelOptimizer()
        
        mock_service = Mock()
        def factory():
            return mock_service
        
        # First call should create service
        service1 = optimizer.get_optimized_service('test_service', factory)
        assert service1 is mock_service
        
        # Second call should return cached service
        service2 = optimizer.get_optimized_service('test_service')
        assert service2 is mock_service
        assert service1 is service2


class TestMemoryOptimizer:
    """Test memory optimization utilities"""
    
    def test_data_compression(self):
        """Test data compression and decompression"""
        test_data = {
            'vectors': np.random.rand(100, 128).tolist(),
            'metadata': {'test': 'data', 'numbers': [1, 2, 3, 4, 5]}
        }
        
        # Compress data
        compressed = MemoryOptimizer.compress_data(test_data)
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        
        # Decompress data
        decompressed = MemoryOptimizer.decompress_data(compressed)
        assert decompressed == test_data
    
    def test_numpy_array_optimization(self):
        """Test numpy array optimization"""
        # Test float64 to float32 conversion
        array_64 = np.random.rand(100, 128).astype(np.float64)
        optimized = MemoryOptimizer.optimize_numpy_array(array_64)
        
        assert optimized.dtype == np.float32
        assert optimized.flags['C_CONTIGUOUS'] is True
        
        # Test non-contiguous array
        non_contiguous = np.random.rand(100, 128)[::2, ::2]
        assert non_contiguous.flags['C_CONTIGUOUS'] is False
        
        optimized_contiguous = MemoryOptimizer.optimize_numpy_array(non_contiguous)
        assert optimized_contiguous.flags['C_CONTIGUOUS'] is True
    
    def test_memory_efficient_config(self):
        """Test memory-efficient configuration"""
        config = MemoryOptimizer.get_memory_efficient_config()
        
        assert isinstance(config, dict)
        assert 'faiss_dimension' in config
        assert 'max_cache_size' in config
        assert 'batch_size' in config
        assert config['faiss_dimension'] <= 128  # Should be memory-efficient
        assert config['max_cache_size'] <= 100
    
    def test_non_numpy_data_passthrough(self):
        """Test that non-numpy data passes through unchanged"""
        test_data = [1, 2, 3, 4, 5]
        result = MemoryOptimizer.optimize_numpy_array(test_data)
        assert result == test_data


class TestCacheOptimizer:
    """Test cache optimization functionality"""
    
    def test_smart_cache_key_generation(self):
        """Test smart cache key generation"""
        optimizer = CacheOptimizer()
        
        # Test with various data types
        key1 = optimizer.smart_cache_key("test", 123, {"key": "value"})
        key2 = optimizer.smart_cache_key("test", 123, {"key": "value"})
        key3 = optimizer.smart_cache_key("test", 124, {"key": "value"})
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different inputs should generate different keys
        assert len(key1) == 16  # Should be shortened hash
    
    def test_numpy_array_cache_key(self):
        """Test cache key generation with numpy arrays"""
        optimizer = CacheOptimizer()
        
        array1 = np.array([1, 2, 3, 4, 5])
        array2 = np.array([1, 2, 3, 4, 5])
        array3 = np.array([1, 2, 3, 4, 6])
        
        key1 = optimizer.smart_cache_key(array1)
        key2 = optimizer.smart_cache_key(array2)
        key3 = optimizer.smart_cache_key(array3)
        
        assert key1 == key2  # Same arrays should generate same key
        assert key1 != key3  # Different arrays should generate different keys
    
    def test_adaptive_ttl(self):
        """Test adaptive TTL calculation"""
        optimizer = CacheOptimizer()
        base_ttl = 300
        
        # High frequency access should get longer TTL
        high_freq_ttl = optimizer.adaptive_ttl(base_ttl, 0.9)
        assert high_freq_ttl == base_ttl * 2
        
        # Medium frequency should get base TTL
        med_freq_ttl = optimizer.adaptive_ttl(base_ttl, 0.6)
        assert med_freq_ttl == base_ttl
        
        # Low frequency should get shorter TTL
        low_freq_ttl = optimizer.adaptive_ttl(base_ttl, 0.3)
        assert low_freq_ttl == base_ttl // 2
        
        # Very low frequency should have minimum TTL
        very_low_ttl = optimizer.adaptive_ttl(base_ttl, 0.1)
        assert very_low_ttl >= 60  # Minimum 1 minute
    
    def test_access_recording(self):
        """Test access pattern recording"""
        optimizer = CacheOptimizer()
        
        # Record some accesses
        optimizer.record_access("key1")
        optimizer.record_access("key1")
        optimizer.record_access("key2")
        
        assert optimizer.hit_counts["key1"] == 2
        assert optimizer.hit_counts["key2"] == 1
        assert "key1" in optimizer.access_patterns
        assert "key2" in optimizer.access_patterns
    
    def test_cache_efficiency_stats(self):
        """Test cache efficiency statistics"""
        optimizer = CacheOptimizer()
        
        # Record some accesses
        optimizer.record_access("key1")
        optimizer.record_access("key1")
        optimizer.record_access("key2")
        
        stats = optimizer.get_cache_efficiency_stats()
        
        assert stats['unique_keys'] == 2
        assert stats['total_accesses'] == 3
        assert stats['efficiency'] == 1.5  # 3 accesses / 2 keys
        assert 'cache_stats' in stats


class TestRequestOptimizer:
    """Test request optimization functionality"""
    
    def test_request_batching(self):
        """Test batching of similar requests"""
        optimizer = RequestOptimizer()
        
        requests = [
            {'endpoint': '/analyze', 'method': 'POST', 'params': {'skin_type': 'oily'}},
            {'endpoint': '/analyze', 'method': 'POST', 'params': {'skin_type': 'oily'}},
            {'endpoint': '/analyze', 'method': 'POST', 'params': {'skin_type': 'dry'}},
            {'endpoint': '/classify', 'method': 'POST', 'params': {'ethnicity': 'caucasian'}},
        ]
        
        batches = optimizer.batch_similar_requests(requests)
        
        # Should have 3 batches: 2 oily skin, 1 dry skin, 1 classify
        assert len(batches) == 3
        
        # Find the oily skin batch
        oily_batch = None
        for batch in batches:
            if len(batch) == 2:  # The batch with 2 requests
                oily_batch = batch
                break
        
        assert oily_batch is not None
        assert all(req['params']['skin_type'] == 'oily' for req in oily_batch)
    
    def test_demographic_normalization(self):
        """Test demographic data normalization"""
        optimizer = RequestOptimizer()
        
        # Test ethnicity normalization
        demographics1 = {'ethnicity': 'white', 'skin_type': 'DRY', 'age': 30}
        normalized1 = optimizer._normalize_demographics(demographics1)
        
        assert normalized1['ethnicity'] == 'caucasian'
        assert normalized1['skin_type'] == 'dry'
        assert normalized1['age_group'] == '25-35'
        
        # Test age group calculation
        demographics2 = {'ethnicity': 'black', 'age': 22}
        normalized2 = optimizer._normalize_demographics(demographics2)
        
        assert normalized2['ethnicity'] == 'african'
        assert normalized2['age_group'] == '18-25'
        assert normalized2['skin_type'] == 'normal'  # Default
    
    def test_request_optimization(self):
        """Test complete request optimization"""
        optimizer = RequestOptimizer()
        
        request_data = {
            'request_id': 'test_123',
            'demographics': {'ethnicity': 'white', 'skin_type': 'OILY'},
            'vector': np.random.rand(128).astype(np.float64),
            'other_data': 'unchanged'
        }
        
        optimized = optimizer.optimize_request_processing(request_data)
        
        # Check demographic normalization
        assert optimized['demographics']['ethnicity'] == 'caucasian'
        assert optimized['demographics']['skin_type'] == 'oily'
        
        # Check vector optimization
        assert optimized['vector'].dtype == np.float32
        
        # Check other data unchanged
        assert optimized['other_data'] == 'unchanged'
        
        # Check processing time recorded
        assert 'test_123' in optimizer.processing_times
    
    def test_image_data_optimization(self):
        """Test image data optimization"""
        optimizer = RequestOptimizer()
        
        # Test with numpy array
        image_array = np.random.rand(224, 224, 3).astype(np.float64)
        optimized_image = optimizer._optimize_image_data(image_array)
        
        assert optimized_image.dtype == np.float32
        assert optimized_image.flags['C_CONTIGUOUS'] is True
        
        # Test with non-numpy data
        other_data = "not an array"
        optimized_other = optimizer._optimize_image_data(other_data)
        assert optimized_other == other_data


class TestVercelCaching:
    """Test Vercel-optimized caching decorator"""
    
    def test_vercel_cached_decorator(self):
        """Test the vercel_cached decorator"""
        call_count = 0
        
        @vercel_cached(ttl=60, compress=True)
        def test_function(x, y):
            nonlocal call_count
            call_count += 1
            return {'result': x + y, 'data': list(range(100))}
        
        # First call should execute function
        result1 = test_function(1, 2)
        assert call_count == 1
        assert result1['result'] == 3
        
        # Second call should use cache
        result2 = test_function(1, 2)
        assert call_count == 1  # Should not increment
        assert result2 == result1
        
        # Different parameters should execute function again
        result3 = test_function(2, 3)
        assert call_count == 2
        assert result3['result'] == 5
    
    def test_cache_compression(self):
        """Test cache compression functionality"""
        @vercel_cached(ttl=60, compress=True)
        def large_data_function():
            return {'large_data': list(range(1000)), 'nested': {'data': list(range(500))}}
        
        # First call
        result1 = large_data_function()
        
        # Second call should decompress correctly
        result2 = large_data_function()
        assert result1 == result2
        assert len(result2['large_data']) == 1000
        assert len(result2['nested']['data']) == 500


class TestConcurrentPerformance:
    """Test concurrent request handling performance"""
    
    def test_concurrent_cache_access(self):
        """Test concurrent cache access performance"""
        @vercel_cached(ttl=300)
        def cached_computation(x):
            time.sleep(0.1)  # Simulate computation
            return x * x
        
        def worker(thread_id):
            results = []
            for i in range(10):
                result = cached_computation(i % 5)  # Reuse some values
                results.append(result)
            return results
        
        # Run concurrent workers
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        duration = time.time() - start_time
        
        # Should complete faster than sequential execution due to caching
        assert duration < 2.0  # Should be much faster than 5 * 10 * 0.1 = 5s
        assert len(results) == 5
        assert all(len(result) == 10 for result in results)
    
    def test_concurrent_request_optimization(self):
        """Test concurrent request optimization"""
        def optimize_request(request_id):
            request_data = {
                'request_id': f'req_{request_id}',
                'demographics': {'ethnicity': 'caucasian', 'skin_type': 'normal'},
                'vector': np.random.rand(128)
            }
            return request_optimizer.optimize_request_processing(request_data)
        
        # Run concurrent optimizations
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(optimize_request, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        duration = time.time() - start_time
        
        assert len(results) == 50
        assert duration < 5.0  # Should complete reasonably quickly
        
        # Check that all requests were processed correctly
        for result in results:
            assert 'demographics' in result
            assert result['demographics']['ethnicity'] == 'caucasian'
            assert result['demographics']['skin_type'] == 'normal'
    
    def test_memory_usage_under_load(self):
        """Test memory usage under concurrent load"""
        from app.vercel_optimizations import get_memory_usage
        
        initial_memory = get_memory_usage()
        
        @vercel_cached(ttl=60, compress=True)
        def memory_intensive_function(size):
            # Create large data structure
            data = {
                'vectors': np.random.rand(size, 128).tolist(),
                'metadata': {'id': i for i in range(size)}
            }
            return data
        
        def worker(worker_id):
            results = []
            for i in range(5):
                result = memory_intensive_function(100)  # Same size for caching
                results.append(len(result['vectors']))
            return results
        
        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(worker, i) for i in range(8)]
            results = [future.result() for future in as_completed(futures)]
        
        final_memory = get_memory_usage()
        
        # Memory usage should not grow excessively due to caching and compression
        if 'rss_mb' in initial_memory and 'rss_mb' in final_memory:
            memory_growth = final_memory['rss_mb'] - initial_memory['rss_mb']
            assert memory_growth < 100  # Should not grow by more than 100MB
        
        assert len(results) == 8
        assert all(len(result) == 5 for result in results)
    
    def test_performance_monitoring_under_load(self):
        """Test performance monitoring under concurrent load"""
        @measure_performance('concurrent_test')
        def monitored_function(x):
            time.sleep(0.01)  # Small delay
            return x * 2
        
        def worker(worker_id):
            return [monitored_function(i) for i in range(10)]
        
        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        # Check performance metrics were recorded
        metrics = performance_monitor.get_metrics('concurrent_test')
        assert len(metrics) == 50  # 5 workers * 10 calls each
        
        # Check average performance
        avg_duration = performance_monitor.get_average('concurrent_test')
        assert avg_duration is not None
        assert avg_duration > 0.005  # Should be at least 5ms due to sleep
        assert avg_duration < 0.1   # Should be less than 100ms


class TestVercelServiceCall:
    """Test optimized service calls for Vercel"""
    
    def test_service_call_with_mock_service(self):
        """Test service call with mock service"""
        # Set up mock service
        mock_service = Mock()
        mock_service.test_method.return_value = "test_result"
        
        vercel_optimizer.service_cache['test_service'] = mock_service
        
        # Call service method
        result = vercel_service_call('test_service', 'test_method', 'arg1', kwarg1='value1')
        
        assert result == "test_result"
        mock_service.test_method.assert_called_once_with('arg1', kwarg1='value1')
    
    def test_service_call_with_missing_service(self):
        """Test service call with missing service"""
        with pytest.raises(Exception) as exc_info:
            vercel_service_call('nonexistent_service', 'test_method')
        
        assert "Service nonexistent_service not available" in str(exc_info.value)
    
    def test_service_call_performance_monitoring(self):
        """Test that service calls are monitored for performance"""
        # Set up mock service
        mock_service = Mock()
        mock_service.slow_method.side_effect = lambda: time.sleep(0.1) or "result"
        
        vercel_optimizer.service_cache['test_service'] = mock_service
        
        # Call service method
        result = vercel_service_call('test_service', 'slow_method')
        
        assert result == "result"
        
        # Check that performance was monitored
        metrics = performance_monitor.get_metrics('vercel_service_call')
        assert len(metrics) > 0
        
        latest_metric = metrics[-1]
        assert latest_metric['value'] >= 0.1  # Should record the sleep time


if __name__ == '__main__':
    pytest.main([__file__])