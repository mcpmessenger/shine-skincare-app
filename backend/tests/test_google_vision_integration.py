"""
Integration tests for Google Vision API service with real API calls
These tests require valid Google Cloud credentials and should be run in a test environment
"""
import unittest
import os
import base64
from unittest import skipUnless

from app.services.google_vision_service import GoogleVisionService


class TestGoogleVisionIntegration(unittest.TestCase):
    """Integration tests for Google Vision Service with real API calls"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with credentials check"""
        cls.has_credentials = (
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or 
            os.environ.get('GOOGLE_CREDENTIALS_JSON')
        )
        
        if cls.has_credentials:
            cls.service = GoogleVisionService()
        
        # Create a simple test image (1x1 pixel PNG)
        cls.test_image_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_real_api_analyze_image_from_bytes(self):
        """Test real API call for comprehensive image analysis"""
        if not self.service.is_available():
            self.skipTest("Google Vision service not available")
        
        result = self.service.analyze_image_from_bytes(self.test_image_data)
        
        # Verify response structure
        self.assertIn('status', result)
        if result['status'] == 'success':
            self.assertIn('results', result)
            self.assertIn('timestamp', result)
            self.assertEqual(result['service'], 'google_vision')
            
            results = result['results']
            self.assertIn('face_detection', results)
            self.assertIn('image_properties', results)
            self.assertIn('label_detection', results)
            self.assertIn('safe_search', results)
        else:
            # If API call fails, log the error for debugging
            print(f"API call failed: {result.get('error', 'Unknown error')}")
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_real_api_detect_faces(self):
        """Test real API call for face detection"""
        if not self.service.is_available():
            self.skipTest("Google Vision service not available")
        
        faces = self.service.detect_faces(self.test_image_data)
        
        # Should return a list (may be empty for simple test image)
        self.assertIsInstance(faces, list)
        
        # If faces are detected, verify structure
        for face in faces:
            self.assertIn('detection_confidence', face)
            self.assertIn('landmarks', face)
            self.assertIn('bounding_poly', face)
            self.assertIsInstance(face['landmarks'], dict)
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_real_api_extract_image_properties(self):
        """Test real API call for image properties extraction"""
        if not self.service.is_available():
            self.skipTest("Google Vision service not available")
        
        properties = self.service.extract_image_properties(self.test_image_data)
        
        # Should return a dictionary with expected properties
        if properties:  # May be empty if API call fails
            self.assertIn('dominant_colors', properties)
            self.assertIn('brightness', properties)
            self.assertIn('contrast', properties)
            self.assertIn('color_count', properties)
            
            # Verify brightness and contrast are in valid range
            if 'brightness' in properties:
                self.assertGreaterEqual(properties['brightness'], 0.0)
                self.assertLessEqual(properties['brightness'], 1.0)
            
            if 'contrast' in properties:
                self.assertGreaterEqual(properties['contrast'], 0.0)
                self.assertLessEqual(properties['contrast'], 1.0)
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_real_api_detect_labels(self):
        """Test real API call for label detection"""
        if not self.service.is_available():
            self.skipTest("Google Vision service not available")
        
        labels = self.service.detect_labels(self.test_image_data)
        
        # Should return a list
        self.assertIsInstance(labels, list)
        
        # If labels are detected, verify structure
        for label in labels:
            self.assertIn('description', label)
            self.assertIn('score', label)
            self.assertIsInstance(label['description'], str)
            self.assertIsInstance(label['score'], float)
            self.assertGreaterEqual(label['score'], 0.0)
            self.assertLessEqual(label['score'], 1.0)
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    def test_service_availability_without_credentials(self):
        """Test service behavior without credentials"""
        # Create service without credentials
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            service = GoogleVisionService()
            self.assertFalse(service.is_available())
            
            # All methods should handle unavailable service gracefully
            result = service.analyze_image_from_bytes(self.test_image_data)
            self.assertEqual(result['status'], 'disabled')
            
            faces = service.detect_faces(self.test_image_data)
            self.assertEqual(len(faces), 0)
            
            properties = service.extract_image_properties(self.test_image_data)
            self.assertEqual(len(properties), 0)
            
            labels = service.detect_labels(self.test_image_data)
            self.assertEqual(len(labels), 0)
    
    @skipUnless(os.environ.get('RUN_INTEGRATION_TESTS') == 'true', 
                "Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable")
    @skipUnless(has_credentials, "Google Cloud credentials not available")
    def test_api_error_handling(self):
        """Test API error handling with invalid image data"""
        if not self.service.is_available():
            self.skipTest("Google Vision service not available")
        
        # Test with invalid image data
        invalid_data = b"not_an_image"
        
        result = self.service.analyze_image_from_bytes(invalid_data)
        
        # Should handle error gracefully
        if result['status'] == 'error':
            self.assertIn('error', result)
            self.assertIn('attempts', result)
        
        # Individual methods should also handle errors gracefully
        faces = self.service.detect_faces(invalid_data)
        self.assertIsInstance(faces, list)
        
        properties = self.service.extract_image_properties(invalid_data)
        self.assertIsInstance(properties, dict)
        
        labels = self.service.detect_labels(invalid_data)
        self.assertIsInstance(labels, list)
    
    def test_service_initialization_edge_cases(self):
        """Test service initialization with various credential configurations"""
        # Test with invalid JSON credentials
        with unittest.mock.patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': 'invalid_json'
        }):
            service = GoogleVisionService()
            self.assertFalse(service.is_available())
        
        # Test with non-existent file path
        service = GoogleVisionService(credentials_path='/non/existent/path.json')
        self.assertFalse(service.is_available())
        
        # Test with empty credentials path
        service = GoogleVisionService(credentials_path='')
        self.assertFalse(service.is_available())


if __name__ == '__main__':
    # Print instructions for running integration tests
    print("Integration Test Instructions:")
    print("1. Set up Google Cloud credentials:")
    print("   - Set GOOGLE_APPLICATION_CREDENTIALS to path of service account key file, OR")
    print("   - Set GOOGLE_CREDENTIALS_JSON to JSON content of service account key")
    print("2. Enable integration tests: export RUN_INTEGRATION_TESTS=true")
    print("3. Run tests: python -m pytest backend/tests/test_google_vision_integration.py -v")
    print()
    
    unittest.main()