import unittest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.demographic_search_service import DemographicWeightedSearch


class TestDemographicWeightedSearch(unittest.TestCase):
    """Test cases for demographic weighted search service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock services
        self.mock_faiss_service = Mock()
        self.mock_supabase_service = Mock()
        
        # Configure mock services as available
        self.mock_faiss_service.is_available.return_value = True
        self.mock_supabase_service.is_available.return_value = True
        
        # Create the service
        self.service = DemographicWeightedSearch(
            self.mock_faiss_service,
            self.mock_supabase_service
        )
        
        # Test data
        self.test_vector = np.random.rand(128)
        self.test_demographics = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service.demographic_weight, 0.3)
        self.assertEqual(self.service.visual_weight, 0.7)
        self.assertEqual(self.service.ethnicity_weight, 0.6)
        self.assertEqual(self.service.skin_type_weight, 0.3)
        self.assertEqual(self.service.age_group_weight, 0.1)
    
    def test_search_with_demographics_basic(self):
        """Test basic demographic weighted search"""
        # Mock FAISS results
        faiss_results = [
            ('image1', 0.5),
            ('image2', 0.8),
            ('image3', 1.0)
        ]
        self.mock_faiss_service.search_similar.return_value = faiss_results
        
        # Mock Supabase analysis data
        def mock_get_analysis(image_id):
            return {
                'google_vision_result': {
                    'ethnicity': 'caucasian' if image_id == 'image1' else 'african',
                    'skin_type': 'normal',
                    'age_group': '25-35'
                }
            }
        
        self.mock_supabase_service.get_analysis_by_image_id.side_effect = mock_get_analysis
        
        # Perform search
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=3
        )
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results, list)
        
        # First result should be image1 (matching ethnicity)
        self.assertEqual(results[0][0], 'image1')
        
        # Verify FAISS was called with larger k
        self.mock_faiss_service.search_similar.assert_called_once_with(self.test_vector, 9)
    
    def test_search_faiss_unavailable(self):
        """Test search when FAISS service is unavailable"""
        self.mock_faiss_service.is_available.return_value = False
        
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=5
        )
        
        self.assertEqual(results, [])
    
    def test_search_supabase_unavailable_fallback(self):
        """Test fallback to visual-only search when Supabase is unavailable"""
        self.mock_supabase_service.is_available.return_value = False
        
        faiss_results = [('image1', 0.5), ('image2', 0.8)]
        self.mock_faiss_service.search_similar.return_value = faiss_results
        
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=2
        )
        
        # Should return FAISS results directly
        self.assertEqual(results, faiss_results)
        self.mock_faiss_service.search_similar.assert_called_once_with(self.test_vector, 2)
    
    def test_extract_demographics_basic(self):
        """Test basic demographic extraction"""
        analysis = {
            'google_vision_result': {
                'ethnicity': 'asian',
                'skin_type': 'oily',
                'age_group': '18-25'
            }
        }
        
        demographics = self.service._extract_demographics(analysis)
        
        expected = {
            'ethnicity': 'asian',
            'skin_type': 'oily',
            'age_group': '18-25'
        }
        self.assertEqual(demographics, expected)
    
    def test_extract_demographics_nested_structure(self):
        """Test demographic extraction from nested results structure"""
        analysis = {
            'google_vision_result': {
                'results': {
                    'face_detection': {
                        'demographic_info': {
                            'ethnicity': 'hispanic',
                            'age_group': '35-45'
                        }
                    }
                }
            }
        }
        
        demographics = self.service._extract_demographics(analysis)
        
        expected = {
            'ethnicity': 'hispanic',
            'age_group': '35-45'
        }
        self.assertEqual(demographics, expected)
    
    def test_extract_demographics_empty_values(self):
        """Test demographic extraction with empty values"""
        analysis = {
            'google_vision_result': {
                'ethnicity': '',
                'skin_type': 'normal',
                'age_group': None
            }
        }
        
        demographics = self.service._extract_demographics(analysis)
        
        # Should only include non-empty values
        expected = {'skin_type': 'normal'}
        self.assertEqual(demographics, expected)
    
    def test_extract_demographics_error_handling(self):
        """Test demographic extraction error handling"""
        # Test with malformed data
        analysis = {'invalid': 'data'}
        
        demographics = self.service._extract_demographics(analysis)
        
        self.assertEqual(demographics, {})
    
    def test_calculate_demographic_similarity_perfect_match(self):
        """Test demographic similarity calculation with perfect match"""
        user_demo = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
        
        result_demo = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should be 1.0 for perfect match
        self.assertAlmostEqual(similarity, 1.0, places=3)
    
    def test_calculate_demographic_similarity_no_match(self):
        """Test demographic similarity calculation with no match"""
        user_demo = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
        
        result_demo = {
            'ethnicity': 'african',
            'skin_type': 'oily',
            'age_group': '45-55'
        }
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should be 0.0 for no match
        self.assertAlmostEqual(similarity, 0.0, places=3)
    
    def test_calculate_demographic_similarity_partial_match(self):
        """Test demographic similarity calculation with partial match"""
        user_demo = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
        
        result_demo = {
            'ethnicity': 'caucasian',  # Match (weight 0.6)
            'skin_type': 'oily',       # No match
            'age_group': '25-35'       # Match (weight 0.1)
        }
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should be (0.6 + 0.1) / 1.0 = 0.7
        expected = (0.6 + 0.1) / 1.0
        self.assertAlmostEqual(similarity, expected, places=3)
    
    def test_calculate_demographic_similarity_ethnicity_only(self):
        """Test demographic similarity with only ethnicity data"""
        user_demo = {'ethnicity': 'asian'}
        result_demo = {'ethnicity': 'asian'}
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should be 1.0 since ethnicity matches and it's the only available data
        self.assertAlmostEqual(similarity, 1.0, places=3)
    
    def test_calculate_demographic_similarity_no_common_fields(self):
        """Test demographic similarity with no common fields"""
        user_demo = {'ethnicity': 'caucasian'}
        result_demo = {'skin_type': 'normal'}
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should be 0.0 since no common fields to compare
        self.assertAlmostEqual(similarity, 0.0, places=3)
    
    def test_calculate_demographic_similarity_case_insensitive(self):
        """Test that demographic similarity is case insensitive"""
        user_demo = {'ethnicity': 'CAUCASIAN'}
        result_demo = {'ethnicity': 'caucasian'}
        
        similarity = self.service._calculate_demographic_similarity(user_demo, result_demo)
        
        # Should match despite different cases
        self.assertAlmostEqual(similarity, 1.0, places=3)
    
    def test_set_demographic_weight_valid(self):
        """Test setting valid demographic weight"""
        self.service.set_demographic_weight(0.5)
        
        self.assertEqual(self.service.demographic_weight, 0.5)
        self.assertEqual(self.service.visual_weight, 0.5)
    
    def test_set_demographic_weight_invalid(self):
        """Test setting invalid demographic weight"""
        original_weight = self.service.demographic_weight
        
        # Test invalid weights
        self.service.set_demographic_weight(-0.1)
        self.assertEqual(self.service.demographic_weight, original_weight)
        
        self.service.set_demographic_weight(1.1)
        self.assertEqual(self.service.demographic_weight, original_weight)
    
    def test_set_demographic_component_weights(self):
        """Test setting demographic component weights"""
        self.service.set_demographic_component_weights(0.5, 0.3, 0.2)
        
        self.assertEqual(self.service.ethnicity_weight, 0.5)
        self.assertEqual(self.service.skin_type_weight, 0.3)
        self.assertEqual(self.service.age_group_weight, 0.2)
    
    def test_set_demographic_component_weights_normalization(self):
        """Test that component weights are normalized if they don't sum to 1"""
        self.service.set_demographic_component_weights(0.8, 0.6, 0.4)  # Sum = 1.8
        
        # Should be normalized
        self.assertAlmostEqual(self.service.ethnicity_weight, 0.8/1.8, places=3)
        self.assertAlmostEqual(self.service.skin_type_weight, 0.6/1.8, places=3)
        self.assertAlmostEqual(self.service.age_group_weight, 0.4/1.8, places=3)
    
    def test_get_configuration(self):
        """Test getting configuration parameters"""
        config = self.service.get_configuration()
        
        expected_keys = [
            'demographic_weight', 'visual_weight', 'ethnicity_weight',
            'skin_type_weight', 'age_group_weight'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config)
        
        self.assertEqual(config['demographic_weight'], 0.3)
        self.assertEqual(config['visual_weight'], 0.7)
    
    def test_is_available_both_services_available(self):
        """Test availability when both services are available"""
        self.assertTrue(self.service.is_available())
    
    def test_is_available_faiss_unavailable(self):
        """Test availability when FAISS is unavailable"""
        self.mock_faiss_service.is_available.return_value = False
        
        self.assertFalse(self.service.is_available())
    
    def test_is_available_supabase_unavailable(self):
        """Test availability when Supabase is unavailable"""
        self.mock_supabase_service.is_available.return_value = False
        
        self.assertFalse(self.service.is_available())
    
    def test_search_with_missing_analysis_data(self):
        """Test search when some images have missing analysis data"""
        faiss_results = [
            ('image1', 0.5),
            ('image2', 0.8),
            ('image3', 1.0)
        ]
        self.mock_faiss_service.search_similar.return_value = faiss_results
        
        # Mock Supabase to return None for some images
        def mock_get_analysis(image_id):
            if image_id == 'image2':
                return None  # Missing analysis data
            return {
                'google_vision_result': {
                    'ethnicity': 'caucasian',
                    'skin_type': 'normal'
                }
            }
        
        self.mock_supabase_service.get_analysis_by_image_id.side_effect = mock_get_analysis
        
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=3
        )
        
        # Should still return all results, using visual similarity for missing data
        self.assertEqual(len(results), 3)
    
    def test_search_with_error_in_processing(self):
        """Test search when there's an error processing individual results"""
        faiss_results = [('image1', 0.5), ('image2', 0.8)]
        self.mock_faiss_service.search_similar.return_value = faiss_results
        
        # Mock Supabase to raise exception for one image
        def mock_get_analysis(image_id):
            if image_id == 'image1':
                raise Exception("Database error")
            return {
                'google_vision_result': {
                    'ethnicity': 'caucasian'
                }
            }
        
        self.mock_supabase_service.get_analysis_by_image_id.side_effect = mock_get_analysis
        
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=2
        )
        
        # Should still return results, handling the error gracefully
        self.assertEqual(len(results), 2)
    
    def test_weighted_distance_calculation(self):
        """Test that weighted distance is calculated correctly"""
        # Set known weights for predictable calculation
        self.service.demographic_weight = 0.4
        self.service.visual_weight = 0.6
        
        faiss_results = [('image1', 1.0)]  # Visual distance = 1.0
        self.mock_faiss_service.search_similar.return_value = faiss_results
        
        # Perfect demographic match (similarity = 1.0)
        self.mock_supabase_service.get_analysis_by_image_id.return_value = {
            'google_vision_result': {
                'ethnicity': 'caucasian',
                'skin_type': 'normal',
                'age_group': '25-35'
            }
        }
        
        results = self.service.search_with_demographics(
            self.test_vector, self.test_demographics, k=1
        )
        
        # Weighted distance = 0.6 * 1.0 - 0.4 * 1.0 = 0.2
        expected_distance = 0.6 * 1.0 - 0.4 * 1.0
        self.assertAlmostEqual(results[0][1], expected_distance, places=3)


if __name__ == '__main__':
    unittest.main()