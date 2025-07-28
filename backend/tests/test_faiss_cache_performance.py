"""
Performance tests for FAISS Cache Optimizer
"""
import unittest
import time
import threading
import tempfile
import shutil
import os
import numpy as np
from unittest.mock import patch

from app.services.faiss_cache_optimizer import (
    FAISSCacheOptimizer, 
    CacheStrategy, 
    CacheEntry
)


class TestFAISSCachePerformance(unittest.TestCase):
    """Performance test cases for FAISS Cache Optimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        
        # Create test data
        self.test_data = {
            f"key_{i}": np.random.rand(100).astype(np.float32) 
            for i in range(100)
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cache_performance_lru(self):
        """Test cache performance with LRU strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            cache_strategy=CacheStrategy.LRU,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Measure put performance
        start_time = time.time()
        for key, data in self.test_data.items():
            cache.put(key, data)
        put_time = time.time() - start_time
        
        # Measure get performance
        start_time = time.time()
        hits = 0
        for key in self.test_data.keys():
            if cache.get(key) is not None:
                hits += 1
        get_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(put_time, 5.0, "Put operations should complete within 5 seconds")
        self.assertLess(get_time, 2.0, "Get operations should complete within 2 seconds")
        self.assertGreater(hits, 50, "Should have at least 50% hit rate")
        
        # Check statistics
        stats = cache.get_stats()
        self.assertGreater(stats['hit_rate'], 0.5)
        self.assertLess(stats['avg_access_time_ms'], 10.0)
        
        print(f"LRU Performance: Put={put_time:.3f}s, Get={get_time:.3f}s, Hits={hits}")
    
    def test_cache_performance_lfu(self):
        """Test cache performance with LFU strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            cache_strategy=CacheStrategy.LFU,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Add data with varying access patterns
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        # Access some keys more frequently
        frequent_keys = list(self.test_data.keys())[:20]
        for _ in range(5):
            for key in frequent_keys:
                cache.get(key)
        
        # Measure performance after establishing access patterns
        start_time = time.time()
        for key in frequent_keys:
            cache.get(key)
        frequent_access_time = time.time() - start_time
        
        start_time = time.time()
        for key in list(self.test_data.keys())[20:40]:
            cache.get(key)
        infrequent_access_time = time.time() - start_time
        
        # Frequent keys should be faster to access
        self.assertLess(frequent_access_time, infrequent_access_time * 1.5)
        
        print(f"LFU Performance: Frequent={frequent_access_time:.3f}s, Infrequent={infrequent_access_time:.3f}s")
    
    def test_cache_performance_adaptive(self):
        """Test cache performance with adaptive strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            cache_strategy=CacheStrategy.ADAPTIVE,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Simulate realistic access patterns
        start_time = time.time()
        
        # Phase 1: Initial loading
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        # Phase 2: Mixed access pattern
        for i in range(200):
            # 80% access to 20% of keys (hot data)
            if i % 5 < 4:
                key = f"key_{i % 20}"
            else:
                key = f"key_{20 + (i % 80)}"
            
            cache.get(key)
        
        total_time = time.time() - start_time
        
        # Check adaptive performance
        stats = cache.get_stats()
        self.assertGreater(stats['hit_rate'], 0.7, "Adaptive strategy should achieve high hit rate")
        self.assertGreater(stats['hot_entries'], 0, "Should identify hot entries")
        
        print(f"Adaptive Performance: Total={total_time:.3f}s, Hit Rate={stats['hit_rate']:.3f}")
    
    def test_concurrent_access_performance(self):
        """Test cache performance under concurrent access"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=20,
            cache_strategy=CacheStrategy.LRU,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Pre-populate cache
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        results = []
        errors = []
        
        def worker_thread(thread_id, operations):
            try:
                start_time = time.time()
                hits = 0
                
                for i in range(operations):
                    key = f"key_{(thread_id * operations + i) % len(self.test_data)}"
                    if cache.get(key) is not None:
                        hits += 1
                    
                    # Occasionally add new data
                    if i % 20 == 0:
                        new_key = f"thread_{thread_id}_key_{i}"
                        new_data = np.random.rand(50).astype(np.float32)
                        cache.put(new_key, new_data)
                
                elapsed_time = time.time() - start_time
                results.append({
                    'thread_id': thread_id,
                    'operations': operations,
                    'hits': hits,
                    'time': elapsed_time,
                    'ops_per_sec': operations / elapsed_time
                })
                
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        operations_per_thread = 500
        num_threads = 4
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=worker_thread, 
                args=(i, operations_per_thread)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Analyze results
        self.assertEqual(len(errors), 0, "No errors should occur during concurrent access")
        self.assertEqual(len(results), num_threads, "All threads should complete")
        
        total_operations = sum(r['operations'] for r in results)
        total_hits = sum(r['hits'] for r in results)
        avg_ops_per_sec = sum(r['ops_per_sec'] for r in results) / len(results)
        
        # Performance assertions
        self.assertGreater(avg_ops_per_sec, 100, "Should handle at least 100 ops/sec per thread")
        self.assertGreater(total_hits / total_operations, 0.5, "Should maintain reasonable hit rate")
        
        print(f"Concurrent Performance: {avg_ops_per_sec:.1f} ops/sec/thread, "
              f"Hit Rate: {total_hits/total_operations:.3f}")
    
    def test_memory_usage_performance(self):
        """Test memory usage and cleanup performance"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=5,  # Small cache to trigger evictions
            cache_strategy=CacheStrategy.LRU,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Generate large data to test memory management
        large_data = {}
        for i in range(50):
            # Create progressively larger arrays
            size = 1000 + i * 100
            large_data[f"large_key_{i}"] = np.random.rand(size).astype(np.float32)
        
        start_time = time.time()
        evictions_start = 0
        
        # Add data and monitor evictions
        for key, data in large_data.items():
            cache.put(key, data)
            
            stats = cache.get_stats()
            if evictions_start == 0 and stats['evictions'] > 0:
                evictions_start = time.time()
        
        total_time = time.time() - start_time
        
        # Check final state
        final_stats = cache.get_stats()
        
        # Performance assertions
        self.assertLess(total_time, 10.0, "Memory management should be efficient")
        self.assertGreater(final_stats['evictions'], 0, "Should have performed evictions")
        self.assertLess(final_stats['memory_usage_mb'], 6.0, "Should stay within memory limits")
        self.assertGreater(final_stats['cache_utilization'], 50, "Should utilize cache space efficiently")
        
        print(f"Memory Performance: Total={total_time:.3f}s, "
              f"Evictions={final_stats['evictions']}, "
              f"Memory={final_stats['memory_usage_mb']:.1f}MB")
    
    def test_compression_performance(self):
        """Test performance impact of compression"""
        # Test without compression
        cache_no_compression = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_compression=False,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        start_time = time.time()
        for key, data in self.test_data.items():
            cache_no_compression.put(key, data)
        no_compression_put_time = time.time() - start_time
        
        start_time = time.time()
        for key in self.test_data.keys():
            cache_no_compression.get(key)
        no_compression_get_time = time.time() - start_time
        
        no_compression_stats = cache_no_compression.get_stats()
        
        # Test with compression
        cache_with_compression = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_compression=True,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        start_time = time.time()
        for key, data in self.test_data.items():
            cache_with_compression.put(key, data)
        compression_put_time = time.time() - start_time
        
        start_time = time.time()
        for key in self.test_data.keys():
            cache_with_compression.get(key)
        compression_get_time = time.time() - start_time
        
        compression_stats = cache_with_compression.get_stats()
        
        # Compression should reduce memory usage but may increase CPU time
        self.assertLess(
            compression_stats['memory_usage_mb'], 
            no_compression_stats['memory_usage_mb'],
            "Compression should reduce memory usage"
        )
        
        # CPU overhead should be reasonable (less than 3x slower)
        self.assertLess(
            compression_put_time, 
            no_compression_put_time * 3,
            "Compression overhead should be reasonable for puts"
        )
        
        self.assertLess(
            compression_get_time, 
            no_compression_get_time * 3,
            "Compression overhead should be reasonable for gets"
        )
        
        print(f"Compression Impact: "
              f"Memory: {no_compression_stats['memory_usage_mb']:.1f}MB -> {compression_stats['memory_usage_mb']:.1f}MB, "
              f"Put: {no_compression_put_time:.3f}s -> {compression_put_time:.3f}s, "
              f"Get: {no_compression_get_time:.3f}s -> {compression_get_time:.3f}s")
    
    def test_persistence_performance(self):
        """Test performance impact of persistence"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=True,
            cache_dir=self.cache_dir
        )
        
        # Measure time to populate cache with persistence
        start_time = time.time()
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        # Force a save
        cache._save_persistent_cache()
        persistence_time = time.time() - start_time
        
        # Measure time to load from persistence
        cache2 = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=True,
            cache_dir=self.cache_dir
        )
        
        start_time = time.time()
        # Access some data to trigger loading
        hits = 0
        for key in list(self.test_data.keys())[:20]:
            if cache2.get(key) is not None:
                hits += 1
        load_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(persistence_time, 15.0, "Persistence should complete within reasonable time")
        self.assertLess(load_time, 5.0, "Loading should be fast")
        self.assertGreater(hits, 0, "Should successfully load persisted data")
        
        print(f"Persistence Performance: Save={persistence_time:.3f}s, Load={load_time:.3f}s, Hits={hits}")
    
    def test_optimization_performance(self):
        """Test performance of cache optimization"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            cache_strategy=CacheStrategy.ADAPTIVE,
            enable_persistence=False,
            cache_dir=self.cache_dir
        )
        
        # Create varied access patterns
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        # Create access pattern (some keys accessed more than others)
        for i in range(300):
            key_index = i % len(self.test_data)
            # Access first 20 keys more frequently
            if key_index < 20:
                for _ in range(3):  # Access 3 times
                    cache.get(f"key_{key_index}")
            else:
                cache.get(f"key_{key_index}")
        
        # Measure optimization performance
        start_time = time.time()
        cache.optimize_now()
        optimization_time = time.time() - start_time
        
        # Get stats after optimization
        stats = cache.get_stats()
        
        # Performance assertions
        self.assertLess(optimization_time, 2.0, "Optimization should complete quickly")
        self.assertGreater(stats['hot_entries'], 0, "Should identify hot entries")
        
        print(f"Optimization Performance: Time={optimization_time:.3f}s, "
              f"Hot Entries={stats['hot_entries']}, Cold Entries={stats['cold_entries']}")


if __name__ == '__main__':
    # Run performance tests
    unittest.main(verbosity=2)