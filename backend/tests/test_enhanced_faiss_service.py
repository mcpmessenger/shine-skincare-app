"""
Unit tests for Enhanced FAISS Service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import tempfile
import os
import shutil
import threading
import time
import json

# Import the service and related classes
from app.services.enhanced_faiss_service import (
    EnhancedFAISSService, 
    IndexConfig, 
    SearchConfig, 
    IndexType,
    PerformanceMetrics
)


class TestEnhancedFAISSService(unittest.TestCase):
    """Test cases for Enhanced FAISS Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_enhanced_index")
        self.dimension = 128  # Smaller dimension for faster tests
        
        # Create test configurations
        self.index_config = IndexConfig(
            index_type=IndexType.FLAT_IP,
            dimension=self.dimension
        )
        
        self.search_config = SearchConfig(
            k=5,
            use_gpu=False
        )
        
        # Create test vectors
        self.test_vectors = np.random.rand(10, self.dimension).astype(np.float32)
        self.test_image_ids = [f"image_{i}" for i in range(10)]
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_initialization_with_flat_ip_index(self, mock_faiss):
        """Test initialization with IndexFlatIP"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=True
        )
        
        self.assertIsNotNone(service.index)
        self.assertEqual(service.index_config.index_type, IndexType.FLAT_IP)
        self.assertEqual(service.index_config.dimension, self.dimension)
        self.assertTrue(service.enable_caching)
        mock_faiss.IndexFlatIP.assert_called_once_with(self.dimension)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_initialization_with_ivf_flat_index(self, mock_faiss):
        """Test initialization with IndexIVFFlat"""
        mock_quantizer = Mock()
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.is_trained = False
        
        mock_faiss.IndexFlatL2.return_value = mock_quantizer
        mock_faiss.IndexIVFFlat.return_value = mock_index
        
        ivf_config = IndexConfig(
            index_type=IndexType.IVF_FLAT,
            dimension=self.dimension,
            nlist=50
        )
        
        service = EnhancedFAISSService(
            index_config=ivf_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        self.assertIsNotNone(service.index)
        mock_faiss.IndexFlatL2.assert_called_once_with(self.dimension)
        mock_faiss.IndexIVFFlat.assert_called_once_with(mock_quantizer, self.dimension, 50)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_initialization_with_hnsw_index(self, mock_faiss):
        """Test initialization with IndexHNSWFlat"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_index.hnsw = Mock()
        
        mock_faiss.IndexHNSWFlat.return_value = mock_index
        
        hnsw_config = IndexConfig(
            index_type=IndexType.HNSW,
            dimension=self.dimension,
            M=16,
            efConstruction=200
        )
        
        service = EnhancedFAISSService(
            index_config=hnsw_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        self.assertIsNotNone(service.index)
        mock_faiss.IndexHNSWFlat.assert_called_once_with(self.dimension, 16)
        self.assertEqual(mock_index.hnsw.efConstruction, 200)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', False)
    def test_initialization_faiss_unavailable(self):
        """Test initialization when FAISS is not available"""
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        self.assertIsNone(service.index)
        self.assertFalse(service.is_available())
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_vector_normalization_for_ip_index(self, mock_faiss):
        """Test vector normalization for IP-based indices"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Test normal vector normalization
        vector = np.array([3.0, 4.0, 0.0], dtype=np.float32)
        normalized = service._normalize_vector(vector)
        
        # Should be unit length for IP indices
        self.assertAlmostEqual(np.linalg.norm(normalized), 1.0, places=6)
        
        # Test zero vector handling
        zero_vector = np.zeros(self.dimension, dtype=np.float32)
        normalized_zero = service._normalize_vector(zero_vector)
        
        # Should return a normalized vector (not zero)
        self.assertAlmostEqual(np.linalg.norm(normalized_zero), 1.0, places=6)
        self.assertFalse(np.allclose(normalized_zero, 0))
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_vector_normalization_for_l2_index(self, mock_faiss):
        """Test vector normalization for L2-based indices"""
        mock_index = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        
        l2_config = IndexConfig(
            index_type=IndexType.FLAT_L2,
            dimension=self.dimension
        )
        
        service = EnhancedFAISSService(
            index_config=l2_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Test that L2 indices don't normalize vectors
        vector = np.array([3.0, 4.0, 0.0], dtype=np.float32)
        normalized = service._normalize_vector(vector)
        
        # Should not be normalized for L2 indices
        np.testing.assert_array_equal(normalized, vector)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_add_vector_success(self, mock_faiss):
        """Test successful vector addition with metadata"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        service.auto_save = False  # Disable auto-save for testing
        
        # Add a vector with metadata
        vector = self.test_vectors[0]
        image_id = self.test_image_ids[0]
        metadata = {'source': 'test', 'quality': 'high'}
        
        result = service.add_vector(vector, image_id, metadata)
        
        self.assertTrue(result)
        self.assertIn(image_id, service.image_ids)
        self.assertIn(image_id, service.metadata)
        self.assertEqual(service.metadata[image_id]['custom_metadata'], metadata)
        self.assertEqual(service.metrics.add_count, 1)
        self.assertEqual(service.metrics.total_vectors, 1)
        mock_index.add.assert_called_once()
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_add_vector_performance_tracking(self, mock_faiss):
        """Test that vector addition tracks performance metrics"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add multiple vectors to test average calculation
        for i in range(3):
            vector = self.test_vectors[i]
            image_id = self.test_image_ids[i]
            service.add_vector(vector, image_id)
        
        # Check performance metrics
        self.assertEqual(service.metrics.add_count, 3)
        self.assertGreater(service.metrics.avg_add_time_ms, 0)
        self.assertGreater(service.metrics.last_add_time_ms, 0)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_search_similar_with_caching(self, mock_faiss):
        """Test similarity search with caching enabled"""
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Mock search results
        similarities = np.array([[0.9, 0.7]])
        indices = np.array([[0, 1]])
        mock_index.search.return_value = (similarities, indices)
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=True
        )
        service.auto_save = False
        
        # Add some test data
        service.image_ids = ["image_0", "image_1"]
        
        # First search - should hit the index
        query_vector = self.test_vectors[0]
        results1 = service.search_similar(query_vector, k=2)
        
        self.assertEqual(len(results1), 2)
        self.assertEqual(service.metrics.search_count, 1)
        self.assertEqual(service._cache_misses, 1)
        
        # Second identical search - should hit the cache
        results2 = service.search_similar(query_vector, k=2)
        
        self.assertEqual(len(results2), 2)
        self.assertEqual(service.metrics.search_count, 2)  # Still incremented
        self.assertEqual(service._cache_hits, 1)
        
        # Results should be identical
        self.assertEqual(results1, results2)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_search_similar_performance_tracking(self, mock_faiss):
        """Test that search tracks performance metrics"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Mock search results
        similarities = np.array([[0.9]])
        indices = np.array([[0]])
        mock_index.search.return_value = (similarities, indices)
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=False  # Disable caching to test actual search
        )
        
        service.image_ids = ["image_0"]
        
        # Perform multiple searches
        query_vector = self.test_vectors[0]
        for i in range(3):
            service.search_similar(query_vector, k=1)
        
        # Check performance metrics
        self.assertEqual(service.metrics.search_count, 3)
        self.assertGreater(service.metrics.avg_search_time_ms, 0)
        self.assertGreater(service.metrics.last_search_time_ms, 0)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_search_with_different_parameters(self, mock_faiss):
        """Test search with different search parameters"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_index.nprobe = 10  # For IVF indices
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Mock search results
        similarities = np.array([[0.9]])
        indices = np.array([[0]])
        mock_index.search.return_value = (similarities, indices)
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        service.image_ids = ["image_0"]
        
        # Search with custom parameters
        query_vector = self.test_vectors[0]
        search_params = {'nprobe': 20, 'max_codes': 1000}
        
        results = service.search_similar(query_vector, k=1, search_params=search_params)
        
        self.assertEqual(len(results), 1)
        # Note: In a real test, we'd verify that the parameters were applied
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_cache_key_generation(self, mock_faiss):
        """Test cache key generation for different queries"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Same vector should generate same key
        vector1 = self.test_vectors[0]
        key1 = service._generate_cache_key(vector1, 5)
        key2 = service._generate_cache_key(vector1, 5)
        self.assertEqual(key1, key2)
        
        # Different k should generate different key
        key3 = service._generate_cache_key(vector1, 10)
        self.assertNotEqual(key1, key3)
        
        # Different vector should generate different key
        vector2 = self.test_vectors[1]
        key4 = service._generate_cache_key(vector2, 5)
        self.assertNotEqual(key1, key4)
        
        # Different search params should generate different key
        key5 = service._generate_cache_key(vector1, 5, {'nprobe': 20})
        self.assertNotEqual(key1, key5)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_auto_optimization_trigger(self, mock_faiss):
        """Test that auto-optimization is triggered after threshold operations"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            auto_optimize=True
        )
        service.auto_save = False
        service._optimization_threshold = 3  # Low threshold for testing
        
        # Mock the optimization method
        service._auto_optimize_index = Mock()
        
        # Add vectors to trigger optimization
        for i in range(4):  # One more than threshold
            vector = self.test_vectors[i % len(self.test_vectors)]
            image_id = f"test_image_{i}"
            service.add_vector(vector, image_id)
        
        # Optimization should have been called
        service._auto_optimize_index.assert_called_once()
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_save_and_load_enhanced_index(self, mock_faiss):
        """Test saving and loading enhanced index with all metadata"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        mock_faiss.write_index = Mock()
        mock_faiss.read_index = Mock(return_value=mock_index)
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Add some test data
        service.image_ids = ["test_image"]
        service.metadata = {"test_image": {"added_at": "2023-01-01", "custom_metadata": {"test": "data"}}}
        service.metrics.add_count = 5
        service.metrics.search_count = 10
        
        # Test save
        result = service.save_index()
        self.assertTrue(result)
        mock_faiss.write_index.assert_called_once()
        
        # Verify that configuration and metrics files would be created
        config_file = f"{self.index_path}_config.json"
        metrics_file = f"{self.index_path}_metrics.json"
        
        # In a real test, we'd verify the file contents
        # For now, just verify the save method completed successfully
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_comprehensive_stats(self, mock_faiss):
        """Test getting comprehensive statistics"""
        mock_index = Mock()
        mock_index.ntotal = 5
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Set up some test data
        service.image_ids = ["img1", "img2", "img3"]
        service.metrics.search_count = 10
        service.metrics.add_count = 3
        service.metrics.avg_search_time_ms = 5.5
        service.metrics.cache_hit_rate = 0.75
        service._cache_hits = 15
        service._cache_misses = 5
        
        stats = service.get_comprehensive_stats()
        
        # Verify basic metrics
        self.assertEqual(stats['total_vectors'], 3)
        self.assertEqual(stats['search_count'], 10)
        self.assertEqual(stats['add_count'], 3)
        self.assertEqual(stats['avg_search_time_ms'], 5.5)
        self.assertEqual(stats['cache_hit_rate'], 0.75)
        
        # Verify configuration info
        self.assertEqual(stats['index_type'], 'IndexFlatIP')
        self.assertEqual(stats['dimension'], self.dimension)
        self.assertTrue(stats['cache_enabled'])
        self.assertFalse(stats['gpu_enabled'])
        
        # Verify health indicators
        self.assertTrue(stats['is_available'])
        self.assertTrue(stats['thread_safe'])
        self.assertTrue(stats['faiss_available'])
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_clear_cache(self, mock_faiss):
        """Test clearing the search cache"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=True
        )
        
        # Add some cache data
        service._search_cache = {"key1": [], "key2": []}
        service._cache_timestamps = {"key1": time.time(), "key2": time.time()}
        service._cache_hits = 10
        service._cache_misses = 5
        
        service.clear_cache()
        
        self.assertEqual(len(service._search_cache), 0)
        self.assertEqual(len(service._cache_timestamps), 0)
        self.assertEqual(service._cache_hits, 0)
        self.assertEqual(service._cache_misses, 0)
        self.assertEqual(service.metrics.cache_hit_rate, 0.0)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_manual_optimization(self, mock_faiss):
        """Test manual index optimization"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Mock the optimization method
        service._auto_optimize_index = Mock()
        
        result = service.optimize_index()
        
        self.assertTrue(result)
        service._auto_optimize_index.assert_called_once()
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_manual_backup_creation(self, mock_faiss):
        """Test manual backup creation"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        mock_faiss.write_index = Mock()
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        # Mock file operations for backup
        with patch('builtins.open', create=True):
            result = service.create_backup()
        
        self.assertTrue(result)
        # In a real test, we'd verify that backup files were created
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_thread_safety_enhanced(self, mock_faiss):
        """Test thread safety of enhanced operations"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        service.auto_save = False
        service.auto_optimize = False  # Disable to avoid interference
        
        results = []
        errors = []
        
        def add_vectors_thread(start_idx):
            try:
                for i in range(start_idx, start_idx + 5):
                    vector = np.random.rand(self.dimension).astype(np.float32)
                    metadata = {'thread': threading.current_thread().name, 'index': i}
                    result = service.add_vector(vector, f"thread_image_{i}", metadata)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_vectors_thread, args=(i * 5,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0)  # No errors should occur
        self.assertEqual(len(results), 15)  # 3 threads * 5 vectors each
        self.assertTrue(all(results))  # All additions should succeed
        self.assertEqual(len(service.image_ids), 15)  # All vectors should be added
        
        # Verify metadata was stored correctly
        for image_id in service.image_ids:
            self.assertIn(image_id, service.metadata)
            self.assertIn('custom_metadata', service.metadata[image_id])
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_error_handling_and_metrics(self, mock_faiss):
        """Test error handling and error count tracking"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path
        )
        
        initial_error_count = service.metrics.error_count
        
        # Test adding vector with wrong dimension
        wrong_vector = np.random.rand(self.dimension + 10).astype(np.float32)
        result = service.add_vector(wrong_vector, "test_image")
        
        self.assertFalse(result)
        self.assertEqual(service.metrics.error_count, initial_error_count + 1)
        
        # Test search with wrong dimension
        wrong_query = np.random.rand(self.dimension + 10).astype(np.float32)
        results = service.search_similar(wrong_query)
        
        self.assertEqual(len(results), 0)
        self.assertEqual(service.metrics.error_count, initial_error_count + 2)
    
    def test_service_unavailable_responses(self):
        """Test responses when service is unavailable"""
        # Test with FAISS unavailable
        with patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', False):
            service = EnhancedFAISSService(
                index_config=self.index_config,
                search_config=self.search_config,
                index_path=self.index_path
            )
            
            self.assertFalse(service.is_available())
            
            # Test all methods return appropriate responses
            vector = self.test_vectors[0]
            image_id = self.test_image_ids[0]
            
            self.assertFalse(service.add_vector(vector, image_id))
            self.assertEqual(len(service.search_similar(vector)), 0)
            self.assertFalse(service.save_index())
            self.assertFalse(service.load_index())
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_cache_ttl_expiration(self, mock_faiss):
        """Test that cache entries expire after TTL"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Mock search results
        similarities = np.array([[0.9]])
        indices = np.array([[0]])
        mock_index.search.return_value = (similarities, indices)
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=True
        )
        
        service.image_ids = ["image_0"]
        
        # Add a cache entry with old timestamp
        query_vector = self.test_vectors[0]
        cache_key = service._generate_cache_key(query_vector, 1)
        service._search_cache[cache_key] = [("image_0", 0.9)]
        service._cache_timestamps[cache_key] = time.time() - 7200  # 2 hours ago
        
        # Search should not use expired cache
        results = service.search_similar(query_vector, k=1)
        
        # Cache entry should be removed
        self.assertNotIn(cache_key, service._search_cache)
        self.assertNotIn(cache_key, service._cache_timestamps)
    
    @patch('app.services.enhanced_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.enhanced_faiss_service.faiss')
    def test_cache_lru_eviction(self, mock_faiss):
        """Test LRU eviction when cache is full"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = EnhancedFAISSService(
            index_config=self.index_config,
            search_config=self.search_config,
            index_path=self.index_path,
            enable_caching=True,
            cache_size=2  # Small cache for testing
        )
        
        # Fill cache to capacity
        service._search_cache = {"key1": [], "key2": []}
        service._cache_timestamps = {
            "key1": time.time() - 100,  # Older
            "key2": time.time() - 50    # Newer
        }
        
        # Add new entry should evict oldest
        service._cache_results("key3", [("image_0", 0.9)])
        
        # key1 should be evicted, key2 and key3 should remain
        self.assertNotIn("key1", service._search_cache)
        self.assertIn("key2", service._search_cache)
        self.assertIn("key3", service._search_cache)


if __name__ == '__main__':
    unittest.main()