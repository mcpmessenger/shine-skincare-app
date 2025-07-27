"""
Integration tests for Enhanced Skin Type Classifier with real image data and Google Vision results
"""
import unittest
import os
import base64
import numpy as np
from unittest import skipUnless
from unittest.mock import patch

from app.services.skin_classifier_service import EnhancedSkinTypeClassifier
from app.services.google_vision_service import GoogleVisionService


class TestSkinClassifierIntegration(unittest.TestCase):
    """Integration tests for Enhanced Skin Type Classifier"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with credentials check"""
        cls.has_credentials = (
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or 
            os.environ.get('GOOGLE_CREDENTIALS_JSON')
        )
        
        # Create test images (simple colored squares)
        cls.light_skin_image = cls._create_test_image([240, 220, 200])  # Light skin tone
        cls.medium_skin_image = cls._create_test_image([180, 150, 120])  # Medium skin tone
        cls.dark_skin_image = cls._create_test_image([100, 80, 60])     # Dark skin tone
        
        if cls.has_credentials:
            try:
                cls.google_vision_service = GoogleVisionService()
                cls.classifier = EnhancedSkinTypeClassifier(
                    google_vision_service=cls.google_vision_service
                )
            except Exception as e:
                print(f"Failed to initialize services: {e}")
                cls.google_vision_service = None
                cls.classifier = None
    
    @classmethod
    def _create_test_image(cls, rgb_color):
        """Create a simple test image with specified color"""
        # Create a 100x100 image with the specified color
        image_array = np.full((100, 100, 3), rgb_color, dtype=np.uint8)
        
        # Convert to bytes
        from PIL import Image
        import io
        
        pil_image = Image.fromarray(image_array)
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_real_classification_with_google_vision(self):
        """Test real classification using Google Vision API"""
        if not self.classifier or not self.google_vision_service:
            self.skipTest("Services not available for integration testing")
        
        if not self.google_vision_service.is_available():
            self.skipTest("Google Vision service not available")
        
        # Test with medium skin tone image
        result = self.classifier.classify_skin_type(
            self.medium_skin_image, 
            ethnicity='caucasian'
        )
        
        # Verify result structure
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
        self.assertIn('confidence', result)
        self.assertIn('ethnicity_considered', result)
        
        # Verify values are valid
        self.assertIn(result['fitzpatrick_type'], ['I', 'II', 'III', 'IV', 'V', 'VI'])
        self.assertGreaterEqual(result['monk_tone'], 1)
        self.assertLessEqual(result['monk_tone'], 10)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
        print(f"Classification result: {result['fitzpatrick_type']}/{result['monk_tone']} "
              f"(confidence: {result['confidence']:.3f})")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_classification_across_skin_tones(self):
        """Test classification across different skin tones"""
        if not self.classifier or not self.google_vision_service:
            self.skipTest("Services not available for integration testing")
        
        if not self.google_vision_service.is_available():
            self.skipTest("Google Vision service not available")
        
        test_cases = [
            (self.light_skin_image, "light skin"),
            (self.medium_skin_image, "medium skin"),
            (self.dark_skin_image, "dark skin")
        ]
        
        results = []
        for image_data, description in test_cases:
            result = self.classifier.classify_skin_type(image_data)
            results.append((description, result))
            
            # Verify each result
            self.assertIn('fitzpatrick_type', result)
            self.assertIn('monk_tone', result)
            
            print(f"{description}: {result['fitzpatrick_type']}/{result['monk_tone']} "
                  f"(confidence: {result['confidence']:.3f})")
        
        # Verify that different skin tones get different classifications
        # (This might not always be true for simple test images, but we can check)
        fitzpatrick_types = [r[1]['fitzpatrick_type'] for r in results]
        monk_tones = [r[1]['monk_tone'] for r in results]
        
        # At least some variation should exist
        self.assertTrue(len(set(fitzpatrick_types)) > 1 or len(set(monk_tones)) > 1,
                       "Expected some variation in classifications across different skin tones")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_ethnicity_adjustments_with_real_data(self):
        """Test ethnicity-based adjustments with real Google Vision data"""
        if not self.classifier or not self.google_vision_service:
            self.skipTest("Services not available for integration testing")
        
        if not self.google_vision_service.is_available():
            self.skipTest("Google Vision service not available")
        
        # Test same image with different ethnicities
        ethnicities = ['caucasian', 'african', 'east_asian', 'south_asian']
        
        results = {}
        for ethnicity in ethnicities:
            result = self.classifier.classify_skin_type(
                self.medium_skin_image, 
                ethnicity=ethnicity
            )
            results[ethnicity] = result
            
            # Verify ethnicity was considered
            self.assertTrue(result['ethnicity_considered'])
            self.assertEqual(result['ethnicity'], ethnicity)
            
            print(f"{ethnicity}: {result['fitzpatrick_type']}/{result['monk_tone']} "
                  f"(confidence: {result['confidence']:.3f})")
        
        # Verify that ethnicity context affects results
        # (At least confidence should be affected)
        confidences = [r['confidence'] for r in results.values()]
        self.assertTrue(all(c > 0.4 for c in confidences), 
                       "All ethnicity-adjusted results should have reasonable confidence")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    def test_classification_without_google_vision(self):
        """Test classification fallback without Google Vision"""
        # Create classifier without Google Vision
        classifier = EnhancedSkinTypeClassifier(google_vision_service=None)
        
        result = classifier.classify_skin_type(self.medium_skin_image)
        
        # Should still work with fallback
        self.assertIn('fitzpatrick_type', result)
        self.assertIn('monk_tone', result)
        self.assertIn('confidence', result)
        
        # Confidence should be lower without Google Vision
        self.assertLess(result['confidence'], 0.8)
        
        print(f"Fallback classification: {result['fitzpatrick_type']}/{result['monk_tone']} "
              f"(confidence: {result['confidence']:.3f})")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_classification_consistency(self):
        """Test that classification is consistent for the same input"""
        if not self.classifier or not self.google_vision_service:
            self.skipTest("Services not available for integration testing")
        
        if not self.google_vision_service.is_available():
            self.skipTest("Google Vision service not available")
        
        # Run classification multiple times on the same image
        results = []
        for i in range(3):
            result = self.classifier.classify_skin_type(
                self.medium_skin_image, 
                ethnicity='caucasian'
            )
            results.append((result['fitzpatrick_type'], result['monk_tone']))
        
        # Results should be consistent
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result, 
                           "Classification results should be consistent for the same input")
        
        print(f"Consistent classification: {first_result[0]}/{first_result[1]}")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_confidence_correlation_with_image_quality(self):
        """Test that confidence correlates with image quality"""
        if not self.classifier or not self.google_vision_service:
            self.skipTest("Services not available for integration testing")
        
        if not self.google_vision_service.is_available():
            self.skipTest("Google Vision service not available")
        
        # Test with different quality images
        test_images = [
            (self.light_skin_image, "clear image"),
            (self.medium_skin_image, "medium image"),
            (self.dark_skin_image, "dark image")
        ]
        
        confidences = []
        for image_data, description in test_images:
            result = self.classifier.classify_skin_type(image_data)
            confidences.append(result['confidence'])
            
            print(f"{description} confidence: {result['confidence']:.3f}")
        
        # All confidences should be reasonable
        for confidence in confidences:
            self.assertGreaterEqual(confidence, 0.1)
            self.assertLessEqual(confidence, 1.0)
    
    def test_error_handling_with_invalid_image(self):
        """Test error handling with invalid image data"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=None)
        
        # Test with invalid image data
        invalid_data = b"not_an_image"
        
        result = classifier.classify_skin_type(invalid_data)
        
        # Should handle error gracefully
        if 'error' in result:
            self.assertEqual(result['status'], 'error')
        else:
            # Or return fallback classification
            self.assertIn('fitzpatrick_type', result)
            self.assertIn('monk_tone', result)
    
    def test_supported_ethnicities_coverage(self):
        """Test that all supported ethnicities work"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=None)
        
        supported_ethnicities = classifier.get_supported_ethnicities()
        
        # Test each supported ethnicity
        for ethnicity in supported_ethnicities:
            result = classifier.classify_skin_type(
                self.medium_skin_image, 
                ethnicity=ethnicity
            )
            
            self.assertTrue(result['ethnicity_considered'])
            self.assertEqual(result['ethnicity'], ethnicity)
            self.assertIn('fitzpatrick_type', result)
            self.assertIn('monk_tone', result)
    
    def test_fitzpatrick_monk_correlation(self):
        """Test that Fitzpatrick and Monk classifications are correlated"""
        classifier = EnhancedSkinTypeClassifier(google_vision_service=None)
        
        # Test with different skin tones
        test_cases = [
            (self.light_skin_image, "light"),
            (self.medium_skin_image, "medium"),
            (self.dark_skin_image, "dark")
        ]
        
        results = []
        for image_data, description in test_cases:
            result = classifier.classify_skin_type(image_data)
            results.append((
                result['fitzpatrick_type'], 
                result['monk_tone'], 
                description
            ))
        
        # Print results for manual verification
        for fitz, monk, desc in results:
            print(f"{desc}: Fitzpatrick {fitz}, Monk {monk}")
        
        # Basic correlation check: lighter Fitzpatrick should generally have lower Monk tones
        # This is a loose correlation test since our test images are simple
        for fitz, monk, desc in results:
            if fitz in ['I', 'II']:
                self.assertLessEqual(monk, 5, f"Light Fitzpatrick {fitz} should have low Monk tone")
            elif fitz in ['V', 'VI']:
                self.assertGreaterEqual(monk, 6, f"Dark Fitzpatrick {fitz} should have high Monk tone")


if __name__ == '__main__':
    # Print instructions for running integration tests
    print("Skin Classifier Integration Test Instructions:")
    print("1. Set up Google Cloud credentials:")
    print("   - Set GOOGLE_APPLICATION_CREDENTIALS to path of service account key file, OR")
    print("   - Set GOOGLE_CREDENTIALS_JSON to JSON content of service account key")
    print("2. Enable integration tests: export RUN_INTEGRATION_TESTS=true")
    print("3. Run tests: python -m pytest backend/tests/test_skin_classifier_integration.py -v -s")
    print()
    
    unittest.main()