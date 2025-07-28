"""
Unit tests for FAISS Cache Optimizer
"""
import unittest
import tempfile
import shutil
import os
import time
import numpy as np
from unittest.mock import patch, Mock

from app.services.faiss_cache_optimizer import (
    FAISSCacheOptimizer, 
    CacheStrategy, 
    CacheEntry,
    CacheStats
)


class TestFAISSCacheOptimizer(unittest.TestCase):
    """Test cases for FAISS Cache Optimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        
        # Create test data
        self.test_data = {
            "key1": np.array([1, 2, 3], dtype=np.float32),
            "key2": "test_string",
            "key3": {"nested": "dict", "with": [1, 2, 3]},
            "key4": np.random.rand(100).astype(np.float32)
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cache_initialization(self):
        """Test cache initialization with different configurations"""
        # Test default initialization
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        self.assertEqual(cache.max_cache_size_bytes, 10 * 1024 * 1024)
        self.assertEqual(cache.cache_strategy, CacheStrategy.ADAPTIVE)
        self.assertEqual(cache.default_ttl_seconds, 3600)
        self.assertFalse(cache.enable_persistence)
        
        # Test custom initialization
        cache2 = FAISSCacheOptimizer(
            max_cache_size_mb=5,
            cache_strategy=CacheStrategy.LRU,
            default_ttl_seconds=1800,
            enable_compression=False,
            enable_persistence=True,
            cache_dir=self.cache_dir
        )
        
        self.assertEqual(cache2.max_cache_size_bytes, 5 * 1024 * 1024)
        self.assertEqual(cache2.cache_strategy, CacheStrategy.LRU)
        self.assertEqual(cache2.default_ttl_seconds, 1800)
        self.assertFalse(cache2.enable_compression)
        self.assertTrue(cache2.enable_persistence)
    
    def test_basic_cache_operations(self):
        """Test basic put and get operations"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Test put operation
        result = cache.put("test_key", self.test_data["key1"])
        self.assertTrue(result)
        
        # Test get operation
        retrieved_data = cache.get("test_key")
        self.assertIsNotNone(retrieved_data)
        np.testing.assert_array_equal(retrieved_data, self.test_data["key1"])
        
        # Test cache miss
        missing_data = cache.get("nonexistent_key")
        self.assertIsNone(missing_data)
        
        # Check statistics
        stats = cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['entry_count'], 1)
        self.assertGreater(stats['size_bytes'], 0)
    
    def test_cache_entry_expiration(self):
        """Test cache entry TTL expiration"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Add entry with short TTL
        cache.put("short_ttl_key", self.test_data["key1"], ttl_seconds=1)
        
        # Should be available immediately
        data = cache.get("short_ttl_key")
        self.assertIsNotNone(data)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        expired_data = cache.get("short_ttl_key")
        self.assertIsNone(expired_data)
        
        # Check that expired entry was removed
        stats = cache.get_stats()
        self.assertEqual(stats['entry_count'], 0)
    
    def test_lru_eviction_strategy(self):
        """Test LRU eviction strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=1,  # Small cache to trigger evictions
            cache_strategy=CacheStrategy.LRU,
            enable_persistence=False
        )
        
        # Fill cache beyond capacity
        large_data = {}
        for i in range(10):
            key = f"large_key_{i}"
            # Create large arrays to trigger evictions
            data = np.random.rand(10000).astype(np.float32)
            large_data[key] = data
            cache.put(key, data)
        
        # Check that evictions occurred
        stats = cache.get_stats()
        self.assertGreater(stats['evictions'], 0)
        self.assertLess(stats['entry_count'], 10)
        
        # Most recently added items should still be in cache
        recent_data = cache.get("large_key_9")
        self.assertIsNotNone(recent_data)
        
        # Older items should have been evicted
        old_data = cache.get("large_key_0")
        self.assertIsNone(old_data)
    
    def test_lfu_eviction_strategy(self):
        """Test LFU eviction strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=1,  # Small cache to trigger evictions
            cache_strategy=CacheStrategy.LFU,
            enable_persistence=False
        )
        
        # Add initial data
        for i in range(5):
            key = f"key_{i}"
            data = np.random.rand(5000).astype(np.float32)
            cache.put(key, data)
        
        # Access some keys more frequently
        for _ in range(5):
            cache.get("key_0")  # Most frequent
            cache.get("key_1")  # Second most frequent
        
        for _ in range(2):
            cache.get("key_2")  # Less frequent
        
        # Add more data to trigger evictions
        for i in range(5, 10):
            key = f"key_{i}"
            data = np.random.rand(5000).astype(np.float32)
            cache.put(key, data)
        
        # Frequently accessed items should still be in cache
        self.assertIsNotNone(cache.get("key_0"))
        self.assertIsNotNone(cache.get("key_1"))
        
        # Less frequently accessed items might be evicted
        stats = cache.get_stats()
        self.assertGreater(stats['evictions'], 0)
    
    def test_adaptive_eviction_strategy(self):
        """Test adaptive eviction strategy"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=1,
            cache_strategy=CacheStrategy.ADAPTIVE,
            enable_persistence=False
        )
        
        # Add data with different characteristics
        current_time = time.time()
        
        # Recent, frequently accessed data
        cache.put("hot_key", np.random.rand(3000).astype(np.float32))
        for _ in range(10):
            cache.get("hot_key")
        
        # Old, infrequently accessed data
        cache.put("cold_key", np.random.rand(3000).astype(np.float32))
        
        # Large, infrequently accessed data
        cache.put("large_cold_key", np.random.rand(8000).astype(np.float32))
        
        # Add more data to trigger adaptive eviction
        for i in range(5):
            key = f"new_key_{i}"
            data = np.random.rand(4000).astype(np.float32)
            cache.put(key, data)
        
        # Hot data should be preserved
        self.assertIsNotNone(cache.get("hot_key"))
        
        # Cold or large data more likely to be evicted
        stats = cache.get_stats()
        self.assertGreater(stats['evictions'], 0)
    
    def test_compression_functionality(self):
        """Test data compression and decompression"""
        # Test with compression enabled
        cache_compressed = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_compression=True,
            enable_persistence=False
        )
        
        # Test without compression
        cache_uncompressed = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_compression=False,
            enable_persistence=False
        )
        
        # Add same data to both caches
        test_data = np.random.rand(1000).astype(np.float32)
        
        cache_compressed.put("test_key", test_data)
        cache_uncompressed.put("test_key", test_data)
        
        # Retrieve and verify data integrity
        compressed_result = cache_compressed.get("test_key")
        uncompressed_result = cache_uncompressed.get("test_key")
        
        np.testing.assert_array_equal(compressed_result, test_data)
        np.testing.assert_array_equal(uncompressed_result, test_data)
        np.testing.assert_array_equal(compressed_result, uncompressed_result)
        
        # Compressed cache should use less memory
        compressed_stats = cache_compressed.get_stats()
        uncompressed_stats = cache_uncompressed.get_stats()
        
        self.assertLess(
            compressed_stats['size_bytes'], 
            uncompressed_stats['size_bytes']
        )
    
    def test_cache_statistics(self):
        """Test cache statistics tracking"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Perform various operations
        cache.put("key1", self.test_data["key1"])
        cache.put("key2", self.test_data["key2"])
        
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("key3")  # Miss
        
        stats = cache.get_stats()
        
        # Verify statistics
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['entry_count'], 2)
        self.assertAlmostEqual(stats['hit_rate'], 2/3, places=2)
        self.assertGreater(stats['size_bytes'], 0)
        self.assertGreater(stats['avg_access_time_ms'], 0)
        
        # Verify configuration info
        self.assertEqual(stats['cache_strategy'], 'adaptive')
        self.assertEqual(stats['max_size_mb'], 10)
        self.assertTrue(stats['compression_enabled'])
        self.assertFalse(stats['persistence_enabled'])
    
    def test_cache_cleanup(self):
        """Test automatic cleanup of expired entries"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Add entries with different TTLs
        cache.put("short_ttl", self.test_data["key1"], ttl_seconds=1)
        cache.put("long_ttl", self.test_data["key2"], ttl_seconds=3600)
        
        # Verify both entries exist
        self.assertIsNotNone(cache.get("short_ttl"))
        self.assertIsNotNone(cache.get("long_ttl"))
        
        # Wait for short TTL to expire
        time.sleep(1.1)
        
        # Trigger cleanup
        cache._cleanup_expired_entries()
        
        # Short TTL entry should be gone, long TTL should remain
        self.assertIsNone(cache.get("short_ttl"))
        self.assertIsNotNone(cache.get("long_ttl"))
        
        stats = cache.get_stats()
        self.assertEqual(stats['entry_count'], 1)
    
    def test_cache_optimization(self):
        """Test cache optimization functionality"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Create access patterns
        for i in range(20):
            key = f"key_{i}"
            cache.put(key, np.random.rand(100).astype(np.float32))
        
        # Create hot and cold access patterns
        hot_keys = [f"key_{i}" for i in range(5)]  # First 5 keys are hot
        cold_keys = [f"key_{i}" for i in range(15, 20)]  # Last 5 keys are cold
        
        # Access hot keys frequently
        for _ in range(10):
            for key in hot_keys:
                cache.get(key)
        
        # Access cold keys rarely
        for key in cold_keys:
            cache.get(key)
        
        # Run optimization
        cache.optimize_now()
        
        # Check that optimization identified patterns
        stats = cache.get_stats()
        self.assertGreater(stats['hot_entries'], 0)
        self.assertGreater(stats['cold_entries'], 0)
    
    def test_cache_persistence(self):
        """Test cache persistence functionality"""
        # Create cache with persistence enabled
        cache1 = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=True,
            cache_dir=self.cache_dir
        )
        
        # Add data
        for key, data in self.test_data.items():
            cache1.put(key, data)
        
        # Force save
        cache1._save_persistent_cache()
        
        # Create new cache instance (simulating restart)
        cache2 = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=True,
            cache_dir=self.cache_dir
        )
        
        # Verify data was loaded
        for key, expected_data in self.test_data.items():
            retrieved_data = cache2.get(key)
            if isinstance(expected_data, np.ndarray):
                np.testing.assert_array_equal(retrieved_data, expected_data)
            else:
                self.assertEqual(retrieved_data, expected_data)
    
    def test_cache_backup_and_restore(self):
        """Test cache backup and restore functionality"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Add data and create access patterns
        for key, data in self.test_data.items():
            cache.put(key, data)
            cache.get(key)  # Create access history
        
        # Create backup
        backup_path = os.path.join(self.temp_dir, "cache_backup.pkl.gz")
        result = cache.backup_cache(backup_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(backup_path))
        
        # Clear cache
        cache.clear()
        stats_after_clear = cache.get_stats()
        self.assertEqual(stats_after_clear['entry_count'], 0)
        
        # Restore from backup
        result = cache.restore_cache(backup_path)
        self.assertTrue(result)
        
        # Verify data was restored
        for key, expected_data in self.test_data.items():
            retrieved_data = cache.get(key)
            if isinstance(expected_data, np.ndarray):
                np.testing.assert_array_equal(retrieved_data, expected_data)
            else:
                self.assertEqual(retrieved_data, expected_data)
        
        # Verify statistics were restored
        stats_after_restore = cache.get_stats()
        self.assertGreater(stats_after_restore['entry_count'], 0)
    
    def test_cache_clear(self):
        """Test cache clearing functionality"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Add data
        for key, data in self.test_data.items():
            cache.put(key, data)
        
        # Verify data exists
        stats_before = cache.get_stats()
        self.assertGreater(stats_before['entry_count'], 0)
        self.assertGreater(stats_before['size_bytes'], 0)
        
        # Clear cache
        cache.clear()
        
        # Verify cache is empty
        stats_after = cache.get_stats()
        self.assertEqual(stats_after['entry_count'], 0)
        self.assertEqual(stats_after['size_bytes'], 0)
        self.assertEqual(stats_after['hits'], 0)
        self.assertEqual(stats_after['misses'], 0)
        
        # Verify data is gone
        for key in self.test_data.keys():
            self.assertIsNone(cache.get(key))
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Test key generation with different inputs
        key1 = cache._generate_cache_key("arg1", "arg2", param1="value1")
        key2 = cache._generate_cache_key("arg1", "arg2", param1="value1")
        key3 = cache._generate_cache_key("arg1", "arg2", param1="value2")
        key4 = cache._generate_cache_key("arg1", "arg3", param1="value1")
        
        # Same inputs should generate same key
        self.assertEqual(key1, key2)
        
        # Different inputs should generate different keys
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key1, key4)
        
        # Keys should be strings
        self.assertIsInstance(key1, str)
        self.assertGreater(len(key1), 0)
    
    def test_error_handling(self):
        """Test error handling in cache operations"""
        cache = FAISSCacheOptimizer(
            max_cache_size_mb=10,
            enable_persistence=False
        )
        
        # Test with invalid data that might cause serialization issues
        class UnserializableClass:
            def __init__(self):
                self.file_handle = open(__file__, 'r')  # Can't be pickled
        
        # This should handle the error gracefully
        result = cache.put("bad_key", UnserializableClass())
        # The result depends on implementation - it might succeed or fail
        # but it shouldn't crash
        
        # Test getting non-existent key
        result = cache.get("non_existent_key")
        self.assertIsNone(result)
        
        # Test with None key (should handle gracefully)
        try:
            cache.put(None, "some_data")
            cache.get(None)
        except Exception as e:
            # Should handle gracefully, not crash
            pass


if __name__ == '__main__':
    unittest.main()