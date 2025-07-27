"""
Unit tests for Production FAISS Service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import tempfile
import os
import shutil
import threading
import time

# Import the service
from app.services.production_faiss_service import ProductionFAISSService


class TestProductionFAISSService(unittest.TestCase):
    """Test cases for Production FAISS Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_index")
        self.dimension = 128  # Smaller dimension for faster tests
        
        # Create test vectors
        self.test_vectors = np.random.rand(5, self.dimension).astype(np.float32)
        self.test_image_ids = [f"image_{i}" for i in range(5)]
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_initialization_new_index(self, mock_faiss):
        """Test initialization with new index"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        self.assertIsNotNone(service.index)
        self.assertEqual(service.dimension, self.dimension)
        self.assertEqual(len(service.image_ids), 0)
        mock_faiss.IndexFlatIP.assert_called_once_with(self.dimension)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', False)
    def test_initialization_faiss_unavailable(self):
        """Test initialization when FAISS is not available"""
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        self.assertIsNone(service.index)
        self.assertFalse(service.is_available())
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_vector_normalization(self, mock_faiss):
        """Test vector normalization functionality"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Test normal vector normalization
        vector = np.array([3.0, 4.0, 0.0], dtype=np.float32)
        normalized = service._normalize_vector(vector)
        
        # Should be unit length
        self.assertAlmostEqual(np.linalg.norm(normalized), 1.0, places=6)
        
        # Test zero vector handling
        zero_vector = np.zeros(self.dimension, dtype=np.float32)
        normalized_zero = service._normalize_vector(zero_vector)
        
        # Should return a normalized vector (not zero)
        self.assertAlmostEqual(np.linalg.norm(normalized_zero), 1.0, places=6)
        self.assertFalse(np.allclose(normalized_zero, 0))
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_vector_dimension_validation(self, mock_faiss):
        """Test vector dimension validation"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Test correct dimension
        correct_vector = np.random.rand(self.dimension).astype(np.float32)
        self.assertTrue(service._validate_vector_dimension(correct_vector))
        
        # Test incorrect dimension
        wrong_vector = np.random.rand(self.dimension + 10).astype(np.float32)
        self.assertFalse(service._validate_vector_dimension(wrong_vector))
        
        # Test 2D vector with correct dimension
        correct_2d_vector = np.random.rand(1, self.dimension).astype(np.float32)
        self.assertTrue(service._validate_vector_dimension(correct_2d_vector))
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_add_vector_success(self, mock_faiss):
        """Test successful vector addition"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False  # Disable auto-save for testing
        
        # Add a vector
        vector = self.test_vectors[0]
        image_id = self.test_image_ids[0]
        
        result = service.add_vector(vector, image_id)
        
        self.assertTrue(result)
        self.assertIn(image_id, service.image_ids)
        self.assertIn(image_id, service.metadata)
        self.assertEqual(service._stats['add_count'], 1)
        mock_index.add.assert_called_once()
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_add_vector_duplicate_id(self, mock_faiss):
        """Test adding vector with duplicate image ID"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add first vector
        vector = self.test_vectors[0]
        image_id = self.test_image_ids[0]
        
        result1 = service.add_vector(vector, image_id)
        self.assertTrue(result1)
        
        # Try to add same ID again
        result2 = service.add_vector(vector, image_id)
        self.assertFalse(result2)
        
        # Should only be called once
        self.assertEqual(mock_index.add.call_count, 1)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_add_vector_wrong_dimension(self, mock_faiss):
        """Test adding vector with wrong dimension"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Create vector with wrong dimension
        wrong_vector = np.random.rand(self.dimension + 10).astype(np.float32)
        image_id = self.test_image_ids[0]
        
        result = service.add_vector(wrong_vector, image_id)
        
        self.assertFalse(result)
        self.assertNotIn(image_id, service.image_ids)
        mock_index.add.assert_not_called()
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_search_similar_success(self, mock_faiss):
        """Test successful similarity search"""
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        # Mock search results
        similarities = np.array([[0.9, 0.7]])
        indices = np.array([[0, 1]])
        mock_index.search.return_value = (similarities, indices)
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add some test data
        service.image_ids = ["image_0", "image_1"]
        
        # Search
        query_vector = self.test_vectors[0]
        results = service.search_similar(query_vector, k=2)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "image_0")  # First result should be image_0
        self.assertEqual(results[1][0], "image_1")  # Second result should be image_1
        self.assertIsInstance(results[0][1], float)  # Similarity score
        self.assertEqual(service._stats['search_count'], 1)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_search_similar_empty_index(self, mock_faiss):
        """Test search on empty index"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        query_vector = self.test_vectors[0]
        results = service.search_similar(query_vector, k=5)
        
        self.assertEqual(len(results), 0)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_search_similar_wrong_dimension(self, mock_faiss):
        """Test search with wrong dimension query vector"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Create query vector with wrong dimension
        wrong_query = np.random.rand(self.dimension + 10).astype(np.float32)
        results = service.search_similar(wrong_query, k=5)
        
        self.assertEqual(len(results), 0)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_save_and_load_index(self, mock_faiss):
        """Test saving and loading index"""
        mock_index = Mock()
        mock_index.ntotal = 1
        mock_faiss.IndexFlatIP.return_value = mock_index
        mock_faiss.write_index = Mock()
        mock_faiss.read_index = Mock(return_value=mock_index)
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Reset call count after initialization (which may trigger a save)
        mock_faiss.write_index.reset_mock()
        
        # Add some test data
        service.image_ids = ["test_image"]
        service.metadata = {"test_image": {"added_at": "2023-01-01"}}
        
        # Test save
        result = service.save_index()
        self.assertTrue(result)
        mock_faiss.write_index.assert_called_once()
        
        # Test load
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                # Mock file operations
                mock_open.return_value.__enter__.return_value.read.return_value = '{"test": "data"}'
                
                result = service.load_index()
                # Note: This test is simplified - in reality, pickle loading would be mocked
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_index_consistency_validation(self, mock_faiss):
        """Test index consistency validation"""
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Test consistent state
        service.image_ids = ["image_0", "image_1"]
        service.metadata = {
            "image_0": {"index_position": 0},
            "image_1": {"index_position": 1}
        }
        
        self.assertTrue(service._validate_index_consistency())
        
        # Test inconsistent state (wrong number of IDs)
        service.image_ids = ["image_0"]  # Only one ID but index has 2 vectors
        self.assertFalse(service._validate_index_consistency())
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_rebuild_index(self, mock_faiss):
        """Test index rebuilding"""
        mock_old_index = Mock()
        mock_old_index.ntotal = 2
        mock_old_index.reconstruct.side_effect = [
            np.random.rand(self.dimension).astype(np.float32),
            np.random.rand(self.dimension).astype(np.float32)
        ]
        
        mock_new_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_new_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        service.index = mock_old_index
        
        result = service.rebuild_index()
        
        self.assertTrue(result)
        self.assertEqual(service._stats['rebuild_count'], 1)
        self.assertFalse(service._stats['corruption_detected'])
        # New index should be used
        self.assertEqual(service.index, mock_new_index)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_batch_vector_addition(self, mock_faiss):
        """Test batch vector addition"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add vectors in batch
        vectors = self.test_vectors[:3]
        image_ids = self.test_image_ids[:3]
        
        results = service.add_vectors_batch(vectors, image_ids)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))  # All should succeed
        self.assertEqual(len(service.image_ids), 3)
        self.assertEqual(service._stats['add_count'], 3)
        mock_index.add.assert_called_once()  # Should be called once for batch
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_batch_vector_addition_mismatched_lengths(self, mock_faiss):
        """Test batch vector addition with mismatched lengths"""
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Mismatched lengths
        vectors = self.test_vectors[:3]
        image_ids = self.test_image_ids[:2]  # One less ID
        
        results = service.add_vectors_batch(vectors, image_ids)
        
        self.assertEqual(len(results), 2)  # Should return results for image_ids length
        self.assertTrue(all(not r for r in results))  # All should fail
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_get_index_stats(self, mock_faiss):
        """Test getting index statistics"""
        mock_index = Mock()
        mock_index.ntotal = 5
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Add some test data
        service.image_ids = ["img1", "img2", "img3"]
        service._stats['search_count'] = 10
        service._stats['add_count'] = 3
        
        stats = service.get_index_stats()
        
        self.assertEqual(stats['dimension'], self.dimension)
        self.assertEqual(stats['vectors_in_index'], 5)
        self.assertEqual(stats['image_ids_count'], 3)
        self.assertEqual(stats['search_count'], 10)
        self.assertEqual(stats['add_count'], 3)
        self.assertTrue(stats['thread_safe'])
        self.assertIn('estimated_memory_mb', stats)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_clear_index(self, mock_faiss):
        """Test clearing the index"""
        mock_index = Mock()
        mock_new_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_new_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add some test data
        service.image_ids = ["img1", "img2"]
        service.metadata = {"img1": {}, "img2": {}}
        service._stats['add_count'] = 2
        
        service.clear_index()
        
        self.assertEqual(len(service.image_ids), 0)
        self.assertEqual(len(service.metadata), 0)
        self.assertEqual(service._stats['total_vectors'], 0)
        self.assertEqual(service._stats['add_count'], 0)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_thread_safety(self, mock_faiss):
        """Test thread safety of operations"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        results = []
        errors = []
        
        def add_vectors_thread(start_idx):
            try:
                for i in range(start_idx, start_idx + 10):
                    vector = np.random.rand(self.dimension).astype(np.float32)
                    result = service.add_vector(vector, f"thread_image_{i}")
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_vectors_thread, args=(i * 10,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0)  # No errors should occur
        self.assertEqual(len(results), 30)  # 3 threads * 10 vectors each
        self.assertTrue(all(results))  # All additions should succeed
        self.assertEqual(len(service.image_ids), 30)  # All vectors should be added
    
    def test_service_unavailable_responses(self):
        """Test responses when service is unavailable"""
        # Test with FAISS unavailable
        with patch('app.services.production_faiss_service.FAISS_AVAILABLE', False):
            service = ProductionFAISSService(
                dimension=self.dimension,
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
            self.assertFalse(service.rebuild_index())
            
            # Batch operations
            results = service.add_vectors_batch([vector], [image_id])
            self.assertEqual(results, [False])
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_auto_save_functionality(self, mock_faiss):
        """Test auto-save functionality"""
        mock_index = Mock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatIP.return_value = mock_index
        mock_faiss.write_index = Mock()
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.save_interval = 2  # Save every 2 operations
        
        # Reset call count after initialization (which may trigger a save)
        mock_faiss.write_index.reset_mock()
        
        # Add vectors - should trigger auto-save after 2 additions
        vector1 = self.test_vectors[0]
        vector2 = self.test_vectors[1]
        
        with patch('builtins.open', create=True):
            service.add_vector(vector1, "img1")  # Operation 1
            self.assertEqual(mock_faiss.write_index.call_count, 0)  # No save yet
            
            service.add_vector(vector2, "img2")  # Operation 2
            self.assertEqual(mock_faiss.write_index.call_count, 1)  # Should save now
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_get_vector_by_id(self, mock_faiss):
        """Test retrieving vector by ID"""
        mock_index = Mock()
        mock_index.ntotal = 1
        test_vector = np.random.rand(self.dimension).astype(np.float32)
        mock_index.reconstruct.return_value = test_vector
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Add test data
        service.image_ids = ["test_image"]
        
        # Retrieve vector
        retrieved_vector = service.get_vector_by_id("test_image")
        
        self.assertIsNotNone(retrieved_vector)
        np.testing.assert_array_equal(retrieved_vector, test_vector)
        mock_index.reconstruct.assert_called_once_with(0)
        
        # Test non-existent ID
        non_existent = service.get_vector_by_id("non_existent")
        self.assertIsNone(non_existent)
    
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    @patch('app.services.production_faiss_service.faiss')
    def test_remove_vector(self, mock_faiss):
        """Test vector removal"""
        mock_index = Mock()
        mock_index.ntotal = 2
        mock_new_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_new_index
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        service.index = mock_index
        
        # Add test data
        service.image_ids = ["img1", "img2"]
        service.metadata = {
            "img1": {"index_position": 0},
            "img2": {"index_position": 1}
        }
        
        # Mock the rebuild process
        with patch.object(service, 'rebuild_index', return_value=True) as mock_rebuild:
            result = service.remove_vector("img1")
            
            self.assertTrue(result)
            self.assertNotIn("img1", service.image_ids)
            self.assertNotIn("img1", service.metadata)
            self.assertIn("img2", service.image_ids)
            mock_rebuild.assert_called_once()
        
        # Test removing non-existent vector
        result = service.remove_vector("non_existent")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()