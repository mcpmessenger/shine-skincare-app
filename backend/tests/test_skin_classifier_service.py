import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.skin_classifier_service import EnhancedSkinTypeClassifier


class TestEnhancedSkinTypeClassifier(unittest.TestCase):
    """Test cases for enhanced skin type classifier service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.classifier = EnhancedSkinTypeClassifier()
        
        # Test image data
        self.test_image_bytes = b"fake_image_data"
        self.test_image_array = np.random.rand(224, 224, 3)
    
    def test_initialization(self):
        """Test classifier initialization"""
        self.assertIsNotNone(self.classifier)
        self.assertEqual(self.classifier.confidence_threshold, 0.7)
        self.assertIn('african', self.classifier.ethnicity_adjustments)
        self.assertIn('caucasian', self.classifier.ethnicity_adjustments)
        self.assertTrue(self.classifier.is_available())
    
    def test_classify_skin_type_basic(self):
        """Test basic skin type classification"""
        result = self.classifier.classify_skin_type(self.test_image_array)
        
        # Check required fields
        required_fields = [
            'fitzpatrick_type', 'fitzpatrick_description', 'monk_tone', 'monk_description',
            'ethnicity_considered', 'confidence', 'high_confidence', 'original_classifications'
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check data types and ranges
        self.assertIn(result['fitzpatrick_type'], ['I', 'II', 'III', 'IV', 'V', 'VI'])
        self.assertIsInstance(result['monk_tone'], int)
        self.assertTrue(1 <= result['monk_tone'] <= 10)
        self.assertIsInstance(result['confidence'], float)
        self.assertTrue(0.0 <= result['confidence'] <= 1.0)
        self.assertFalse(result['ethnicity_considered'])  # No ethnicity provided
    
    def test_classify_skin_type_with_ethnicity(self):
        """Test skin type classification with ethnicity context"""
        result = self.classifier.classify_skin_type(
            self.test_image_array, 
            ethnicity='caucasian'
        )
        
        self.assertTrue(result['ethnicity_considered'])
        self.assertEqual(result['ethnicity'], 'caucasian')
        self.assertIn('adjustments_applied', result)
    
    def test_classify_skin_type_bytes_input(self):
        """Test classification with bytes input"""
        result = self.classifier.classify_skin_type(self.test_image_bytes)
        
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
    
    def test_extract_skin_regions_array_input(self):
        """Test skin region extraction with array input"""
        regions = self.classifier._extract_skin_regions(self.test_image_array)
        
        self.assertIsInstance(regions, np.ndarray)
        self.assertEqual(len(regions.shape), 3)  # Should be 3D array
    
    def test_extract_skin_regions_bytes_input(self):
        """Test skin region extraction with bytes input"""
        regions = self.classifier._extract_skin_regions(self.test_image_bytes)
        
        self.assertIsInstance(regions, np.ndarray)
        self.assertEqual(len(regions.shape), 3)  # Should be 3D array
    
    def test_extract_skin_regions_invalid_input(self):
        """Test skin region extraction with invalid input"""
        regions = self.classifier._extract_skin_regions("invalid_input")
        
        # Should return a default array
        self.assertIsInstance(regions, np.ndarray)
    
    def test_classify_fitzpatrick_range(self):
        """Test Fitzpatrick classification returns valid range"""
        # Test with different intensity levels
        test_cases = [
            np.ones((224, 224, 3)) * 0.1,   # Dark
            np.ones((224, 224, 3)) * 0.5,   # Medium
            np.ones((224, 224, 3)) * 0.9    # Light
        ]
        
        for skin_regions in test_cases:
            result = self.classifier._classify_fitzpatrick(skin_regions)
            self.assertIn(result, ['I', 'II', 'III', 'IV', 'V', 'VI'])
    
    def test_classify_monk_range(self):
        """Test Monk classification returns valid range"""
        # Test with different intensity levels
        test_cases = [
            np.ones((224, 224, 3)) * 0.1,   # Dark
            np.ones((224, 224, 3)) * 0.5,   # Medium
            np.ones((224, 224, 3)) * 0.9    # Light
        ]
        
        for skin_regions in test_cases:
            result = self.classifier._classify_monk(skin_regions)
            self.assertIsInstance(result, int)
            self.assertTrue(1 <= result <= 10)
    
    def test_apply_ethnicity_context_african(self):
        """Test ethnicity context application for African ethnicity"""
        original_fitz = 'III'
        original_monk = 4
        
        adjusted_fitz, adjusted_monk = self.classifier._apply_ethnicity_context(
            original_fitz, original_monk, 'african'
        )
        
        # Should adjust to minimum values for African ethnicity
        self.assertEqual(adjusted_fitz, 'V')  # Minimum for African
        self.assertEqual(adjusted_monk, 7)    # Minimum for African
    
    def test_apply_ethnicity_context_caucasian(self):
        """Test ethnicity context application for Caucasian ethnicity"""
        original_fitz = 'V'  # Too dark for typical Caucasian
        original_monk = 8    # Too dark for typical Caucasian
        
        adjusted_fitz, adjusted_monk = self.classifier._apply_ethnicity_context(
            original_fitz, original_monk, 'caucasian'
        )
        
        # Should adjust to maximum values for Caucasian range
        self.assertEqual(adjusted_fitz, 'III')  # Maximum for Caucasian
        self.assertEqual(adjusted_monk, 4)      # Maximum for Caucasian
    
    def test_apply_ethnicity_context_no_adjustment_needed(self):
        """Test ethnicity context when no adjustment is needed"""
        original_fitz = 'III'
        original_monk = 4
        
        adjusted_fitz, adjusted_monk = self.classifier._apply_ethnicity_context(
            original_fitz, original_monk, 'caucasian'
        )
        
        # Should remain unchanged as they're within range
        self.assertEqual(adjusted_fitz, original_fitz)
        self.assertEqual(adjusted_monk, original_monk)
    
    def test_apply_ethnicity_context_unknown_ethnicity(self):
        """Test ethnicity context with unknown ethnicity"""
        original_fitz = 'III'
        original_monk = 5
        
        adjusted_fitz, adjusted_monk = self.classifier._apply_ethnicity_context(
            original_fitz, original_monk, 'unknown_ethnicity'
        )
        
        # Should remain unchanged
        self.assertEqual(adjusted_fitz, original_fitz)
        self.assertEqual(adjusted_monk, original_monk)
    
    def test_compare_fitzpatrick_types(self):
        """Test Fitzpatrick type comparison"""
        # Test all comparison cases
        self.assertEqual(self.classifier._compare_fitzpatrick_types('I', 'III'), -1)
        self.assertEqual(self.classifier._compare_fitzpatrick_types('III', 'I'), 1)
        self.assertEqual(self.classifier._compare_fitzpatrick_types('II', 'II'), 0)
        
        # Test edge cases
        self.assertEqual(self.classifier._compare_fitzpatrick_types('I', 'VI'), -1)
        self.assertEqual(self.classifier._compare_fitzpatrick_types('VI', 'I'), 1)
    
    def test_compare_fitzpatrick_types_invalid(self):
        """Test Fitzpatrick type comparison with invalid types"""
        # Should handle invalid types gracefully
        result = self.classifier._compare_fitzpatrick_types('invalid', 'III')
        self.assertEqual(result, 0)
    
    def test_calculate_confidence_basic(self):
        """Test basic confidence calculation"""
        skin_regions = np.random.rand(224, 224, 3)
        
        confidence = self.classifier._calculate_confidence(skin_regions, None)
        
        self.assertIsInstance(confidence, float)
        self.assertTrue(0.0 <= confidence <= 1.0)
    
    def test_calculate_confidence_with_ethnicity(self):
        """Test confidence calculation with ethnicity bonus"""
        skin_regions = np.random.rand(224, 224, 3)
        
        confidence_without = self.classifier._calculate_confidence(skin_regions, None)
        confidence_with = self.classifier._calculate_confidence(skin_regions, 'caucasian')
        
        # Should be higher with ethnicity context
        self.assertGreater(confidence_with, confidence_without)
    
    def test_calculate_confidence_error_handling(self):
        """Test confidence calculation error handling"""
        # Mock numpy.std to raise an exception (which is used in the confidence calculation)
        with patch('app.services.skin_classifier_service.np.std', side_effect=Exception("Test error")):
            confidence = self.classifier._calculate_confidence(
                np.random.rand(224, 224, 3), None
            )
            
            # Should return default confidence
            self.assertEqual(confidence, 0.5)
    
    def test_get_supported_ethnicities(self):
        """Test getting supported ethnicities"""
        ethnicities = self.classifier.get_supported_ethnicities()
        
        self.assertIsInstance(ethnicities, list)
        self.assertIn('african', ethnicities)
        self.assertIn('caucasian', ethnicities)
        self.assertIn('east_asian', ethnicities)
    
    def test_get_fitzpatrick_info(self):
        """Test getting Fitzpatrick type information"""
        info = self.classifier.get_fitzpatrick_info('III')
        
        self.assertIn('description', info)
        self.assertIn('range', info)
        
        # Test invalid type
        invalid_info = self.classifier.get_fitzpatrick_info('invalid')
        self.assertEqual(invalid_info, {})
    
    def test_set_confidence_threshold_valid(self):
        """Test setting valid confidence threshold"""
        self.classifier.set_confidence_threshold(0.8)
        self.assertEqual(self.classifier.confidence_threshold, 0.8)
        
        self.classifier.set_confidence_threshold(0.0)
        self.assertEqual(self.classifier.confidence_threshold, 0.0)
        
        self.classifier.set_confidence_threshold(1.0)
        self.assertEqual(self.classifier.confidence_threshold, 1.0)
    
    def test_set_confidence_threshold_invalid(self):
        """Test setting invalid confidence threshold"""
        original_threshold = self.classifier.confidence_threshold
        
        # Test invalid thresholds
        self.classifier.set_confidence_threshold(-0.1)
        self.assertEqual(self.classifier.confidence_threshold, original_threshold)
        
        self.classifier.set_confidence_threshold(1.1)
        self.assertEqual(self.classifier.confidence_threshold, original_threshold)
    
    def test_get_model_info(self):
        """Test getting model information"""
        info = self.classifier.get_model_info()
        
        required_fields = [
            'fitzpatrick_model_loaded', 'monk_model_loaded', 'supported_ethnicities',
            'confidence_threshold', 'classifier_version'
        ]
        
        for field in required_fields:
            self.assertIn(field, info)
        
        self.assertIsInstance(info['supported_ethnicities'], list)
        self.assertEqual(info['confidence_threshold'], self.classifier.confidence_threshold)
    
    def test_classification_consistency(self):
        """Test that classification is consistent for the same input"""
        # Run classification multiple times with same input
        results = []
        for _ in range(3):
            result = self.classifier.classify_skin_type(self.test_image_array, 'caucasian')
            results.append((result['fitzpatrick_type'], result['monk_tone']))
        
        # All results should be the same
        self.assertTrue(all(r == results[0] for r in results))
    
    def test_ethnicity_adjustment_ranges(self):
        """Test that ethnicity adjustments work for all supported ethnicities"""
        test_cases = [
            ('african', 'I', 1),    # Should be adjusted up
            ('caucasian', 'VI', 10), # Should be adjusted down
            ('east_asian', 'III', 4), # Should remain in range
        ]
        
        for ethnicity, fitz_type, monk_tone in test_cases:
            adjusted_fitz, adjusted_monk = self.classifier._apply_ethnicity_context(
                fitz_type, monk_tone, ethnicity
            )
            
            # Verify adjustments are within expected ranges
            self.assertIn(adjusted_fitz, ['I', 'II', 'III', 'IV', 'V', 'VI'])
            self.assertTrue(1 <= adjusted_monk <= 10)
    
    def test_high_confidence_classification(self):
        """Test high confidence classification detection"""
        # Mock high confidence
        with patch.object(self.classifier, '_calculate_confidence', return_value=0.9):
            result = self.classifier.classify_skin_type(self.test_image_array)
            self.assertTrue(result['high_confidence'])
        
        # Mock low confidence
        with patch.object(self.classifier, '_calculate_confidence', return_value=0.5):
            result = self.classifier.classify_skin_type(self.test_image_array)
            self.assertFalse(result['high_confidence'])
    
    def test_classification_error_handling(self):
        """Test classification error handling"""
        # Mock an error in skin region extraction
        with patch.object(self.classifier, '_extract_skin_regions', 
                         side_effect=Exception("Test error")):
            result = self.classifier.classify_skin_type(self.test_image_array)
            
            self.assertIn('error', result)
            self.assertEqual(result['status'], 'error')
    
    def test_original_classifications_tracking(self):
        """Test that original classifications are tracked when adjustments are made"""
        # Use African ethnicity which will force adjustments
        result = self.classifier.classify_skin_type(
            self.test_image_array, 
            ethnicity='african'
        )
        
        self.assertIn('original_classifications', result)
        self.assertIn('fitzpatrick', result['original_classifications'])
        self.assertIn('monk', result['original_classifications'])
        
        # Check if adjustments were applied
        if result['adjustments_applied']:
            # Original should be different from final
            self.assertNotEqual(
                result['original_classifications']['fitzpatrick'],
                result['fitzpatrick_type']
            )


if __name__ == '__main__':
    unittest.main()