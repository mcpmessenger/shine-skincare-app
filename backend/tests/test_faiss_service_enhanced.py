import unittest
import numpy as np
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.faiss_service import FAISSService


class TestEnhancedFAISSService(unittest.TestCase):
    """Test cases for enhanced FAISS service with cosine similarity"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dimension = 128
        self.service = FAISSService(
            dimension=self.test_dimension,
            index_path=os.path.join(self.temp_dir, 'test_index')
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_vector_normalization_normal_case(self):
        """Test vector normalization with normal vectors"""
        # Test with a simple vector
        vector = np.array([3.0, 4.0])
        normalized = self.service._normalize_vector(vector)
        
        # Check that the normalized vector has unit length
        norm = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm, 1.0, places=6)
        
        # Check that the direction is preserved
        expected = np.array([0.6, 0.8])
        np.testing.assert_array_almost_equal(normalized, expected, decimal=6)
    
    def test_vector_normalization_zero_vector(self):
        """Test vector normalization with zero vector"""
        zero_vector = np.zeros(self.test_dimension)
        
        with patch('app.services.faiss_service.logger') as mock_logger:
            normalized = self.service._normalize_vector(zero_vector)
            
            # Should return the original zero vector
            np.testing.assert_array_equal(normalized, zero_vector)
            
            # Should log a warning
            mock_logger.warning.assert_called_once_with(
                "Encountered zero vector during normalization"
            )
    
    def test_vector_normalization_single_element(self):
        """Test vector normalization with single non-zero element"""
        vector = np.zeros(self.test_dimension)
        vector[0] = 5.0
        
        normalized = self.service._normalize_vector(vector)
        
        # Should have unit length
        norm = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm, 1.0, places=6)
        
        # First element should be 1.0, rest should be 0.0
        self.assertAlmostEqual(normalized[0], 1.0, places=6)
        np.testing.assert_array_almost_equal(normalized[1:], np.zeros(self.test_dimension - 1))
    
    def test_vector_normalization_negative_values(self):
        """Test vector normalization with negative values"""
        vector = np.array([-3.0, -4.0])
        normalized = self.service._normalize_vector(vector)
        
        # Check unit length
        norm = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm, 1.0, places=6)
        
        # Check correct normalization
        expected = np.array([-0.6, -0.8])
        np.testing.assert_array_almost_equal(normalized, expected, decimal=6)
    
    def test_add_vector_normalization(self):
        """Test that vectors are normalized when added to index"""
        # Create a non-normalized vector
        vector = np.random.rand(self.test_dimension) * 10  # Scale up to make it non-unit
        image_id = "test_image_1"
        
        # Add vector to index
        result = self.service.add_vector(vector, image_id)
        self.assertTrue(result)
        
        # Verify the vector was added
        self.assertEqual(len(self.service.image_ids), 1)
        self.assertEqual(self.service.image_ids[0], image_id)
        
        # Verify index has one vector
        self.assertEqual(self.service.index.ntotal, 1)
    
    def test_search_similar_normalization(self):
        """Test that query vectors are normalized during search"""
        # Add some test vectors
        vectors = []
        image_ids = []
        for i in range(3):
            vector = np.random.rand(self.test_dimension)
            image_id = f"test_image_{i}"
            vectors.append(vector)
            image_ids.append(image_id)
            self.service.add_vector(vector, image_id)
        
        # Create a query vector (non-normalized)
        query_vector = vectors[0] * 5.0  # Scale up the first vector
        
        # Search for similar vectors
        results = self.service.search_similar(query_vector, k=3)
        
        # Should return results
        self.assertEqual(len(results), 3)
        
        # First result should be the most similar (same direction as query)
        self.assertEqual(results[0][0], image_ids[0])
        
        # Distance should be very small (close to 0 for identical direction)
        self.assertLess(results[0][1], 0.1)
    
    def test_cosine_similarity_calculation(self):
        """Test that cosine similarity is correctly calculated"""
        # Create two identical vectors (should have similarity = 1, distance = 0)
        vector1 = np.array([1.0, 2.0, 3.0] + [0.0] * (self.test_dimension - 3))
        vector2 = vector1.copy()
        
        self.service.add_vector(vector1, "image1")
        self.service.add_vector(vector2, "image2")
        
        # Search with the same vector
        results = self.service.search_similar(vector1, k=2)
        
        # Both results should have very low distance (high similarity)
        for result in results:
            self.assertLess(result[1], 0.01)  # Distance should be near 0
    
    def test_orthogonal_vectors_similarity(self):
        """Test similarity between orthogonal vectors"""
        # Create orthogonal vectors
        vector1 = np.zeros(self.test_dimension)
        vector1[0] = 1.0
        
        vector2 = np.zeros(self.test_dimension)
        vector2[1] = 1.0
        
        self.service.add_vector(vector1, "image1")
        self.service.add_vector(vector2, "image2")
        
        # Search with first vector
        results = self.service.search_similar(vector1, k=2)
        
        # Find the result for the orthogonal vector
        orthogonal_result = next(r for r in results if r[0] == "image2")
        
        # Distance should be close to 2 (similarity = 0 for orthogonal vectors)
        self.assertAlmostEqual(orthogonal_result[1], 2.0, places=1)
    
    def test_opposite_vectors_similarity(self):
        """Test similarity between opposite vectors"""
        # Create opposite vectors
        vector1 = np.array([1.0, 0.0] + [0.0] * (self.test_dimension - 2))
        vector2 = np.array([-1.0, 0.0] + [0.0] * (self.test_dimension - 2))
        
        self.service.add_vector(vector1, "image1")
        self.service.add_vector(vector2, "image2")
        
        # Search with first vector
        results = self.service.search_similar(vector1, k=2)
        
        # Find the result for the opposite vector
        opposite_result = next(r for r in results if r[0] == "image2")
        
        # Distance should be close to 4 (similarity = -1 for opposite vectors)
        self.assertAlmostEqual(opposite_result[1], 4.0, places=1)
    
    def test_dimension_mismatch_handling(self):
        """Test handling of dimension mismatches"""
        # Try to add vector with wrong dimension
        wrong_vector = np.random.rand(self.test_dimension + 10)
        result = self.service.add_vector(wrong_vector, "wrong_dim")
        
        self.assertFalse(result)
        self.assertEqual(len(self.service.image_ids), 0)
        
        # Try to search with wrong dimension
        results = self.service.search_similar(wrong_vector, k=5)
        self.assertEqual(len(results), 0)
    
    def test_empty_index_search(self):
        """Test searching in empty index"""
        query_vector = np.random.rand(self.test_dimension)
        
        with patch('app.services.faiss_service.logger') as mock_logger:
            results = self.service.search_similar(query_vector, k=5)
            
            self.assertEqual(len(results), 0)
            mock_logger.warning.assert_called_once_with("FAISS index is empty")
    
    def test_vector_shape_handling(self):
        """Test handling of different vector shapes"""
        # Test 1D vector
        vector_1d = np.random.rand(self.test_dimension)
        result = self.service.add_vector(vector_1d, "test_1d")
        self.assertTrue(result)
        
        # Test 2D vector (1, dimension)
        vector_2d = np.random.rand(1, self.test_dimension)
        result = self.service.add_vector(vector_2d, "test_2d")
        self.assertTrue(result)
        
        # Both should be in the index
        self.assertEqual(len(self.service.image_ids), 2)
    
    def test_normalization_error_handling(self):
        """Test error handling in vector normalization"""
        # Mock numpy to raise an exception
        with patch('numpy.linalg.norm', side_effect=Exception("Test error")):
            with patch('app.services.faiss_service.logger') as mock_logger:
                vector = np.random.rand(self.test_dimension)
                result = self.service._normalize_vector(vector)
                
                # Should return original vector on error
                np.testing.assert_array_equal(result, vector)
                
                # Should log error
                mock_logger.error.assert_called_once()
    
    def test_similarity_to_distance_conversion(self):
        """Test the conversion from similarity to distance"""
        # Test known similarity values
        test_cases = [
            (1.0, 0.0),    # Perfect similarity -> distance 0
            (0.0, 2.0),    # No similarity -> distance 2
            (-1.0, 4.0),   # Opposite -> distance 4
            (0.5, 1.0),    # Half similarity -> distance 1
        ]
        
        for similarity, expected_distance in test_cases:
            # Formula: distance = 2 - 2 * similarity
            calculated_distance = 2 - 2 * similarity
            self.assertAlmostEqual(calculated_distance, expected_distance, places=6)


if __name__ == '__main__':
    unittest.main()