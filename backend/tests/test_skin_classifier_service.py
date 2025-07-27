"""
Unit tests for Enhanced Skin Type Classifier Service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import io
from PIL import Image

# Import the service
from app.services.skin_classifier_service import EnhancedSkinTypeClassifier


class TestEnhancedSkinTypeClassifier(unittest.TestCase):
    """Test cases for Enhanced Skin Type Classifier"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test image data
        self.test_image_array = np.random.rand(224, 224, 3)
        
        # Convert to bytes
        pil_image = Image.fromarray((self.test_image_array * 255).astype(np.uint8))
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        self.test_image_bytes = img_byte_arr.getvalue()
        
        # Mock Google Vision service
        self.mock_google_vision = Mock()
        self.mock_google_vision.is_available.return_value = True
    
    def test_initialization_with_google_vision(self):
        """Test initialization with Google Vision service"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        self.assertEqual(classifier.google_vision_service, self.mock_google_vision)
        self.assertEqual(classifier.confidence_threshold, 0.7)
        self.assertIsNotNone(classifier.ethnicity_adjustments)
        self.assertTrue(classifier.is_available())
    
    def test_initialization_without_google_vision(self):
        """Test initialization without Google Vision service"""
        with patch('app.services.skin_classifier_service.GOOGLE_VISION_AVAILABLE', False):
            classifier = EnhancedSkinTypeClassifier()
            
            self.assertIsNone(classifier.google_vision_service)
            self.assertTrue(classifier.is_available())
    
    def test_classify_skin_type_with_google_vision(self):
        """Test skin type classification with Google Vision integration"""
        # Mock Google Vision responses
        mock_faces = [{
            'detection_confidence': 0.95,
            'landmarks': {
                'LEFT_CHEEK_CENTER': {'x': 100, 'y': 150, 'z': 5},
                'RIGHT_CHEEK_CENTER': {'x': 200, 'y': 150, 'z': 5},
                'NOSE_TIP': {'x': 150, 'y': 180, 'z': 10}
            },
            'bounding_poly': [{'x': 50, 'y': 100}, {'x': 250, 'y': 100}],
            'roll_angle': 0.5,
            'pan_angle': 1.2,
            'tilt_angle': -0.3,
            'blurred_likelihood': 'UNLIKELY',
            'under_exposed_likelihood': 'UNLIKELY'
        }]
        
        mock_image_properties = {
            'dominant_colors': [
                {'red': 180, 'green': 150, 'blue': 120, 'pixel_fraction': 0.4},
                {'red': 160, 'green': 130, 'blue': 100, 'pixel_fraction': 0.3}
            ],
            'brightness': 0.6,
            'contrast': 0.4
        }
        
        self.mock_google_vision.detect_faces.return_value = mock_faces
        self.mock_google_vision.extract_image_properties.return_value = mock_image_properties
        
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        result = classifier.classify_skin_type(self.test_image_bytes, ethnicity='caucasian')
        
        # Verify result structure
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('fitzpatrick_description', result)
        self.assertIn('monk_tone', result)
        self.assertIn('monk_description', result)
        self.assertIn('confidence', result)
        self.assertIn('ethnicity_considered', result)
        self.assertIn('classification_timestamp', result)
        
        # Verify values
        self.assertTrue(result['ethnicity_considered'])
        self.assertEqual(result['ethnicity'], 'caucasian')
        self.assertIsInstance(result['confidence'], float)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
        # Verify Fitzpatrick type is valid
        self.assertIn(result['fitzpatrick_type'], ['I', 'II', 'III', 'IV', 'V', 'VI'])
        
        # Verify Monk tone is valid
        self.assertIsInstance(result['monk_tone'], int)
        self.assertGreaterEqual(result['monk_tone'], 1)
        self.assertLessEqual(result['monk_tone'], 10)
    
    def test_classify_skin_type_without_google_vision(self):
        """Test skin type classification without Google Vision (fallback)"""
        # Mock Google Vision as unavailable
        self.mock_google_vision.is_available.return_value = False
        
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        result = classifier.classify_skin_type(self.test_image_bytes)
        
        # Should still return valid result
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
        self.assertIn('confidence', result)
        self.assertFalse(result['ethnicity_considered'])
        
        # Confidence should be lower without Google Vision
        self.assertLess(result['confidence'], 0.8)
    
    def test_classify_skin_type_no_faces_detected(self):
        """Test classification when no faces are detected"""
        # Mock no faces detected
        self.mock_google_vision.detect_faces.return_value = []
        self.mock_google_vision.extract_image_properties.return_value = {
            'dominant_colors': [
                {'red': 150, 'green': 120, 'blue': 100, 'pixel_fraction': 0.5}
            ]
        }
        
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        result = classifier.classify_skin_type(self.test_image_bytes)
        
        # Should still return valid result using fallback
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
        self.assertIn('confidence', result)
        
        # Confidence should be lower without face detection
        self.assertLess(result['confidence'], 0.7)
    
    def test_extract_skin_analysis_points(self):
        """Test extraction of skin analysis points from landmarks"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        landmarks = {
            'LEFT_CHEEK_CENTER': {'x': 100, 'y': 150, 'z': 5},
            'RIGHT_CHEEK_CENTER': {'x': 200, 'y': 150, 'z': 5},
            'NOSE_TIP': {'x': 150, 'y': 180, 'z': 10},
            'CHIN_GNATHION': {'x': 150, 'y': 220, 'z': 8}
        }
        
        analysis_points = classifier._extract_skin_analysis_points(landmarks)
        
        self.assertIn('LEFT_CHEEK_CENTER', analysis_points)
        self.assertIn('RIGHT_CHEEK_CENTER', analysis_points)
        self.assertIn('NOSE_TIP', analysis_points)
        self.assertIn('CHIN_GNATHION', analysis_points)
        self.assertIn('skin_center', analysis_points)
        
        # Verify skin center calculation
        skin_center = analysis_points['skin_center']
        self.assertEqual(skin_center['x'], 150.0)  # Average of x coordinates
        self.assertEqual(skin_center['point_count'], 4)
    
    def test_fitzpatrick_classification_with_vision(self):
        """Test Fitzpatrick classification using Google Vision data"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Test with light skin (should be Type I or II)
        light_skin_data = {
            'face_detected': True,
            'image_properties': {
                'dominant_colors': [
                    {'red': 240, 'green': 220, 'blue': 200, 'pixel_fraction': 0.6}
                ]
            },
            'face_quality': {
                'under_exposed_likelihood': 'UNLIKELY'
            }
        }
        
        result = classifier._classify_fitzpatrick_with_vision(light_skin_data)
        self.assertIn(result, ['I', 'II'])
        
        # Test with dark skin (should be Type V or VI)
        dark_skin_data = {
            'face_detected': True,
            'image_properties': {
                'dominant_colors': [
                    {'red': 80, 'green': 60, 'blue': 40, 'pixel_fraction': 0.6}
                ]
            },
            'face_quality': {
                'under_exposed_likelihood': 'UNLIKELY'
            }
        }
        
        result = classifier._classify_fitzpatrick_with_vision(dark_skin_data)
        self.assertIn(result, ['V', 'VI'])
    
    def test_monk_classification_with_vision(self):
        """Test Monk scale classification using Google Vision data"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Test with light skin (should be tone 1-3)
        light_skin_data = {
            'face_detected': True,
            'image_properties': {
                'dominant_colors': [
                    {'red': 240, 'green': 220, 'blue': 200, 'pixel_fraction': 0.6}
                ]
            }
        }
        
        result = classifier._classify_monk_with_vision(light_skin_data)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 3)
        
        # Test with dark skin (should be tone 8-10)
        dark_skin_data = {
            'face_detected': True,
            'image_properties': {
                'dominant_colors': [
                    {'red': 60, 'green': 40, 'blue': 30, 'pixel_fraction': 0.6}
                ]
            }
        }
        
        result = classifier._classify_monk_with_vision(dark_skin_data)
        self.assertGreaterEqual(result, 8)
        self.assertLessEqual(result, 10)
    
    def test_ethnicity_context_application(self):
        """Test application of ethnicity-based adjustments"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Test African ethnicity adjustment (should enforce minimum Type V)
        adjusted_fitz, adjusted_monk = classifier._apply_ethnicity_context('III', 4, 'african')
        self.assertEqual(adjusted_fitz, 'V')  # Should be adjusted to minimum
        self.assertGreaterEqual(adjusted_monk, 7)  # Should be adjusted to minimum
        
        # Test Caucasian ethnicity adjustment (should stay within range)
        adjusted_fitz, adjusted_monk = classifier._apply_ethnicity_context('V', 8, 'caucasian')
        self.assertIn(adjusted_fitz, ['I', 'II', 'III'])  # Should be adjusted to range
        self.assertLessEqual(adjusted_monk, 4)  # Should be adjusted to range
        
        # Test unknown ethnicity (should not change)
        adjusted_fitz, adjusted_monk = classifier._apply_ethnicity_context('III', 5, 'unknown')
        self.assertEqual(adjusted_fitz, 'III')
        self.assertEqual(adjusted_monk, 5)
    
    def test_fitzpatrick_type_comparison(self):
        """Test Fitzpatrick type comparison logic"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Test comparisons
        self.assertEqual(classifier._compare_fitzpatrick_types('I', 'I'), 0)
        self.assertEqual(classifier._compare_fitzpatrick_types('I', 'III'), -1)
        self.assertEqual(classifier._compare_fitzpatrick_types('VI', 'IV'), 1)
        
        # Test invalid types
        self.assertEqual(classifier._compare_fitzpatrick_types('X', 'I'), 0)
    
    def test_confidence_calculation_with_google_vision(self):
        """Test confidence calculation with Google Vision data"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # High quality data
        high_quality_data = {
            'face_detected': True,
            'face_confidence': 0.95,
            'face_quality': {
                'blurred_likelihood': 'UNLIKELY',
                'under_exposed_likelihood': 'UNLIKELY'
            },
            'image_properties': {
                'dominant_colors': [
                    {'red': 180, 'green': 150, 'blue': 120, 'pixel_fraction': 0.4},
                    {'red': 160, 'green': 130, 'blue': 100, 'pixel_fraction': 0.3},
                    {'red': 140, 'green': 110, 'blue': 80, 'pixel_fraction': 0.2}
                ]
            },
            'landmarks': {'LEFT_CHEEK_CENTER': {}, 'RIGHT_CHEEK_CENTER': {}},
            'skin_analysis_points': {
                'LEFT_CHEEK_CENTER': {}, 'RIGHT_CHEEK_CENTER': {}, 'NOSE_TIP': {}
            }
        }
        
        confidence = classifier._calculate_confidence(high_quality_data, 'caucasian')
        self.assertGreater(confidence, 0.8)  # Should be high confidence
        
        # Low quality data
        low_quality_data = {
            'face_detected': True,
            'face_confidence': 0.3,
            'face_quality': {
                'blurred_likelihood': 'LIKELY',
                'under_exposed_likelihood': 'LIKELY'
            },
            'image_properties': {
                'dominant_colors': []
            },
            'landmarks': {},
            'skin_analysis_points': {}
        }
        
        confidence = classifier._calculate_confidence(low_quality_data, None)
        self.assertLess(confidence, 0.6)  # Should be lower confidence
    
    def test_confidence_calculation_fallback(self):
        """Test confidence calculation with fallback data"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        fallback_data = {
            'face_detected': False,
            'fallback_analysis': {
                'mean_color': [150, 120, 100],
                'color_std': [25, 20, 15]
            }
        }
        
        confidence = classifier._calculate_confidence(fallback_data, 'east_asian')
        
        # Should be lower than Google Vision confidence but still reasonable
        self.assertGreater(confidence, 0.3)
        self.assertLess(confidence, 0.7)
    
    def test_supported_ethnicities(self):
        """Test getting supported ethnicities"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        ethnicities = classifier.get_supported_ethnicities()
        
        self.assertIn('african', ethnicities)
        self.assertIn('caucasian', ethnicities)
        self.assertIn('east_asian', ethnicities)
        self.assertIn('south_asian', ethnicities)
        self.assertIn('hispanic', ethnicities)
        self.assertIn('middle_eastern', ethnicities)
    
    def test_fitzpatrick_info(self):
        """Test getting Fitzpatrick type information"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        info = classifier.get_fitzpatrick_info('III')
        
        self.assertIn('description', info)
        self.assertIn('range', info)
        self.assertIn('burns', info['description'].lower())
    
    def test_confidence_threshold_setting(self):
        """Test setting confidence threshold"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Valid threshold
        classifier.set_confidence_threshold(0.8)
        self.assertEqual(classifier.confidence_threshold, 0.8)
        
        # Invalid threshold (too high)
        classifier.set_confidence_threshold(1.5)
        self.assertEqual(classifier.confidence_threshold, 0.8)  # Should not change
        
        # Invalid threshold (too low)
        classifier.set_confidence_threshold(-0.1)
        self.assertEqual(classifier.confidence_threshold, 0.8)  # Should not change
    
    def test_model_info(self):
        """Test getting model information"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        info = classifier.get_model_info()
        
        self.assertIn('fitzpatrick_model_loaded', info)
        self.assertIn('monk_model_loaded', info)
        self.assertIn('supported_ethnicities', info)
        self.assertIn('confidence_threshold', info)
        self.assertIn('classifier_version', info)
        
        self.assertEqual(info['confidence_threshold'], 0.7)
        self.assertEqual(info['classifier_version'], '1.0.0')
    
    def test_error_handling_in_classification(self):
        """Test error handling during classification"""
        # Mock Google Vision to raise an exception
        self.mock_google_vision.detect_faces.side_effect = Exception("API Error")
        
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        result = classifier.classify_skin_type(self.test_image_bytes)
        
        # Should handle error gracefully and return fallback classification
        # (The service gracefully falls back instead of returning an error)
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
        self.assertIn('confidence', result)
        
        # Confidence should be lower due to error fallback
        self.assertLess(result['confidence'], 0.6)
    
    def test_fallback_skin_region_extraction(self):
        """Test fallback skin region extraction"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=None)
        
        result = classifier._extract_skin_regions_fallback(self.test_image_bytes)
        
        self.assertFalse(result['face_detected'])
        self.assertEqual(result['face_confidence'], 0.0)
        self.assertIn('fallback_analysis', result)
        self.assertIn('mean_color', result['fallback_analysis'])
        self.assertIn('color_std', result['fallback_analysis'])
    
    def test_numpy_array_input(self):
        """Test classification with numpy array input"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Mock Google Vision responses for array input
        self.mock_google_vision.detect_faces.return_value = []
        self.mock_google_vision.extract_image_properties.return_value = {
            'dominant_colors': [
                {'red': 150, 'green': 120, 'blue': 100, 'pixel_fraction': 0.5}
            ]
        }
        
        result = classifier.classify_skin_type(self.test_image_array)
        
        # Should handle numpy array input
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
    
    def test_classification_consistency(self):
        """Test that classification results are consistent for same input"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=self.mock_google_vision)
        
        # Mock consistent responses
        mock_faces = [{
            'detection_confidence': 0.9,
            'landmarks': {'LEFT_CHEEK_CENTER': {'x': 100, 'y': 150, 'z': 5}},
            'blurred_likelihood': 'UNLIKELY',
            'under_exposed_likelihood': 'UNLIKELY'
        }]
        
        mock_properties = {
            'dominant_colors': [
                {'red': 180, 'green': 150, 'blue': 120, 'pixel_fraction': 0.6}
            ]
        }
        
        self.mock_google_vision.detect_faces.return_value = mock_faces
        self.mock_google_vision.extract_image_properties.return_value = mock_properties
        
        # Run classification multiple times
        results = []
        for _ in range(3):
            result = classifier.classify_skin_type(self.test_image_bytes, ethnicity='caucasian')
            results.append((result['fitzpatrick_type'], result['monk_tone']))
        
        # Results should be consistent
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])


if __name__ == '__main__':
    unittest.main()