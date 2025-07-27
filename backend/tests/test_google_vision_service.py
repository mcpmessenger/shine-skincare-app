"""
Unit tests for Google Vision API integration service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from datetime import datetime

# Import the service
from app.services.google_vision_service import GoogleVisionService


class TestGoogleVisionService(unittest.TestCase):
    """Test cases for Google Vision Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_image_data = b"fake_image_data"
        self.test_credentials_json = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "test-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_authenticate_client_with_json_credentials(self, mock_vision):
        """Test client authentication with JSON credentials"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            service = GoogleVisionService()
            self.assertIsNotNone(service.client)
            mock_vision.ImageAnnotatorClient.assert_called_once()
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_authenticate_client_with_file_credentials(self, mock_vision):
        """Test client authentication with file credentials"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_credentials_json, f)
            temp_path = f.name
        
        try:
            service = GoogleVisionService(credentials_path=temp_path)
            self.assertIsNotNone(service.client)
            mock_vision.ImageAnnotatorClient.assert_called_once()
        finally:
            os.unlink(temp_path)
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', False)
    def test_service_disabled_when_library_unavailable(self):
        """Test service is disabled when Google Vision library is not available"""
        service = GoogleVisionService()
        self.assertIsNone(service.client)
        self.assertFalse(service.is_available())
    
    def test_service_disabled_without_credentials(self):
        """Test service is disabled without proper credentials"""
        with patch.dict(os.environ, {}, clear=True):
            service = GoogleVisionService()
            self.assertIsNone(service.client)
            self.assertFalse(service.is_available())
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_analyze_image_from_bytes_success(self, mock_vision):
        """Test successful image analysis from bytes"""
        # Mock the client and responses
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock face detection response
        mock_face = Mock()
        mock_face.detection_confidence = 0.95
        mock_face.landmarking_confidence = 0.90
        mock_face.joy_likelihood.name = 'LIKELY'
        mock_face.sorrow_likelihood.name = 'UNLIKELY'
        mock_face.anger_likelihood.name = 'UNLIKELY'
        mock_face.surprise_likelihood.name = 'POSSIBLE'
        mock_face.under_exposed_likelihood.name = 'UNLIKELY'
        mock_face.blurred_likelihood.name = 'UNLIKELY'
        mock_face.headwear_likelihood.name = 'UNLIKELY'
        mock_face.roll_angle = 0.5
        mock_face.pan_angle = 1.2
        mock_face.tilt_angle = -0.3
        
        # Mock bounding polygons
        mock_vertex = Mock()
        mock_vertex.x = 100
        mock_vertex.y = 150
        mock_face.bounding_poly.vertices = [mock_vertex]
        mock_face.fd_bounding_poly.vertices = [mock_vertex]
        
        # Mock landmarks
        mock_landmark = Mock()
        mock_landmark.type_.name = 'NOSE_TIP'
        mock_landmark.position.x = 200
        mock_landmark.position.y = 250
        mock_landmark.position.z = 10
        mock_face.landmarks = [mock_landmark]
        
        mock_face_response = Mock()
        mock_face_response.face_annotations = [mock_face]
        mock_client.face_detection.return_value = mock_face_response
        
        # Mock image properties response
        mock_color = Mock()
        mock_color.color.red = 180
        mock_color.color.green = 150
        mock_color.color.blue = 120
        mock_color.score = 0.8
        mock_color.pixel_fraction = 0.3
        
        mock_properties = Mock()
        mock_properties.dominant_colors.colors = [mock_color]
        mock_properties_response = Mock()
        mock_properties_response.image_properties_annotation = mock_properties
        mock_client.image_properties.return_value = mock_properties_response
        
        # Mock label detection response
        mock_label = Mock()
        mock_label.description = 'Person'
        mock_label.score = 0.95
        mock_label.mid = '/m/01g317'
        
        mock_label_response = Mock()
        mock_label_response.label_annotations = [mock_label]
        mock_client.label_detection.return_value = mock_label_response
        
        # Mock safe search response
        mock_safe_search = Mock()
        mock_safe_search.adult = 'UNLIKELY'
        mock_safe_search.racy = 'UNLIKELY'
        mock_safe_search.violence = 'UNLIKELY'
        mock_safe_search.medical = 'POSSIBLE'
        mock_safe_search.spoof = 'UNLIKELY'
        
        mock_safe_response = Mock()
        mock_safe_response.safe_search_annotation = mock_safe_search
        mock_client.safe_search_detection.return_value = mock_safe_response
        
        # Create service and test
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            service = GoogleVisionService()
            result = service.analyze_image_from_bytes(self.mock_image_data)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('results', result)
            self.assertIn('face_detection', result['results'])
            self.assertIn('image_properties', result['results'])
            self.assertIn('label_detection', result['results'])
            self.assertIn('safe_search', result['results'])
            self.assertIn('timestamp', result)
            
            # Verify face detection results
            face_results = result['results']['face_detection']
            self.assertEqual(face_results['faces_found'], 1)
            self.assertEqual(len(face_results['faces']), 1)
            
            face_data = face_results['faces'][0]
            self.assertEqual(face_data['detection_confidence'], 0.95)
            self.assertIn('landmarks', face_data)
            self.assertIn('NOSE_TIP', face_data['landmarks'])
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_detect_faces_with_landmarks(self, mock_vision):
        """Test face detection with facial landmarks extraction"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock face with landmarks
        mock_face = Mock()
        mock_face.detection_confidence = 0.92
        mock_face.landmarking_confidence = 0.88
        
        # Mock landmark
        mock_landmark = Mock()
        mock_landmark.type_.name = 'LEFT_EYE'
        mock_landmark.position.x = 150
        mock_landmark.position.y = 200
        mock_landmark.position.z = 5
        mock_face.landmarks = [mock_landmark]
        
        # Mock other face properties
        mock_face.joy_likelihood.name = 'LIKELY'
        mock_face.sorrow_likelihood.name = 'UNLIKELY'
        mock_face.anger_likelihood.name = 'UNLIKELY'
        mock_face.surprise_likelihood.name = 'POSSIBLE'
        mock_face.under_exposed_likelihood.name = 'UNLIKELY'
        mock_face.blurred_likelihood.name = 'UNLIKELY'
        mock_face.headwear_likelihood.name = 'UNLIKELY'
        mock_face.roll_angle = 0.0
        mock_face.pan_angle = 0.0
        mock_face.tilt_angle = 0.0
        
        # Mock bounding polygons
        mock_vertex = Mock()
        mock_vertex.x = 100
        mock_vertex.y = 150
        mock_face.bounding_poly.vertices = [mock_vertex]
        mock_face.fd_bounding_poly.vertices = [mock_vertex]
        
        mock_response = Mock()
        mock_response.face_annotations = [mock_face]
        mock_client.face_detection.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            service = GoogleVisionService()
            faces = service.detect_faces(self.mock_image_data)
            
            self.assertEqual(len(faces), 1)
            face = faces[0]
            self.assertEqual(face['detection_confidence'], 0.92)
            self.assertEqual(face['landmarking_confidence'], 0.88)
            self.assertIn('landmarks', face)
            self.assertIn('LEFT_EYE', face['landmarks'])
            
            left_eye = face['landmarks']['LEFT_EYE']
            self.assertEqual(left_eye['x'], 150)
            self.assertEqual(left_eye['y'], 200)
            self.assertEqual(left_eye['z'], 5)
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_extract_image_properties_comprehensive(self, mock_vision):
        """Test comprehensive image properties extraction"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock multiple colors
        mock_color1 = Mock()
        mock_color1.color.red = 200
        mock_color1.color.green = 180
        mock_color1.color.blue = 160
        mock_color1.score = 0.7
        mock_color1.pixel_fraction = 0.4
        
        mock_color2 = Mock()
        mock_color2.color.red = 120
        mock_color2.color.green = 100
        mock_color2.color.blue = 80
        mock_color2.score = 0.5
        mock_color2.pixel_fraction = 0.3
        
        mock_properties = Mock()
        mock_properties.dominant_colors.colors = [mock_color1, mock_color2]
        
        mock_response = Mock()
        mock_response.image_properties_annotation = mock_properties
        mock_client.image_properties.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            service = GoogleVisionService()
            properties = service.extract_image_properties(self.mock_image_data)
            
            self.assertIn('dominant_colors', properties)
            self.assertIn('brightness', properties)
            self.assertIn('contrast', properties)
            self.assertIn('color_diversity', properties)
            self.assertEqual(properties['color_count'], 2)
            
            # Check brightness calculation
            self.assertIsInstance(properties['brightness'], float)
            self.assertGreaterEqual(properties['brightness'], 0.0)
            self.assertLessEqual(properties['brightness'], 1.0)
            
            # Check contrast calculation
            self.assertIsInstance(properties['contrast'], float)
            self.assertGreaterEqual(properties['contrast'], 0.0)
            self.assertLessEqual(properties['contrast'], 1.0)
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_detect_skin_related_labels(self, mock_vision):
        """Test skin-related label detection and filtering"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock labels - mix of skin-related and general
        mock_label1 = Mock()
        mock_label1.description = 'Person'
        mock_label1.score = 0.95
        mock_label1.mid = '/m/01g317'
        
        mock_label2 = Mock()
        mock_label2.description = 'Face'
        mock_label2.score = 0.90
        mock_label2.mid = '/m/0dzct'
        
        mock_label3 = Mock()
        mock_label3.description = 'Car'  # Not skin-related
        mock_label3.score = 0.85
        mock_label3.mid = '/m/0k4j'
        
        mock_label4 = Mock()
        mock_label4.description = 'Skin'
        mock_label4.score = 0.80
        mock_label4.mid = '/m/06z37_'
        
        mock_response = Mock()
        mock_response.label_annotations = [mock_label1, mock_label2, mock_label3, mock_label4]
        mock_client.label_detection.return_value = mock_response
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            service = GoogleVisionService()
            labels = service.detect_labels(self.mock_image_data)
            
            self.assertEqual(len(labels), 4)  # All labels returned
            
            # Check that skin-related labels are properly identified
            skin_related_descriptions = [label['description'] for label in labels 
                                       if label['description'] in ['Person', 'Face', 'Skin']]
            self.assertEqual(len(skin_related_descriptions), 3)
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_retry_logic_on_api_failure(self, mock_vision):
        """Test retry logic with exponential backoff on API failures"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock API failure then success
        mock_client.face_detection.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            Mock(face_annotations=[])  # Success on third attempt
        ]
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up test
                service = GoogleVisionService()
                faces = service.detect_faces(self.mock_image_data)
                
                # Should succeed after retries
                self.assertEqual(len(faces), 0)  # Empty result but no error
                
                # Verify retry attempts
                self.assertEqual(mock_client.face_detection.call_count, 3)
                self.assertEqual(mock_sleep.call_count, 2)  # 2 retries
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_retry_logic_exhausted(self, mock_vision):
        """Test behavior when all retry attempts are exhausted"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock consistent API failures
        mock_client.face_detection.side_effect = Exception("Persistent API Error")
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            with patch('time.sleep'):  # Mock sleep to speed up test
                service = GoogleVisionService()
                faces = service.detect_faces(self.mock_image_data)
                
                # Should return empty list after all retries exhausted
                self.assertEqual(len(faces), 0)
                
                # Verify all retry attempts were made
                self.assertEqual(mock_client.face_detection.call_count, 3)
    
    def test_service_unavailable_responses(self):
        """Test responses when service is unavailable"""
        service = GoogleVisionService()  # No credentials, service unavailable
        
        # Test all methods return appropriate responses when unavailable
        result = service.analyze_image_from_bytes(self.mock_image_data)
        self.assertEqual(result['status'], 'disabled')
        self.assertIn('error', result)
        
        faces = service.detect_faces(self.mock_image_data)
        self.assertEqual(len(faces), 0)
        
        properties = service.extract_image_properties(self.mock_image_data)
        self.assertEqual(len(properties), 0)
        
        labels = service.detect_labels(self.mock_image_data)
        self.assertEqual(len(labels), 0)
    
    def test_brightness_calculation_edge_cases(self):
        """Test brightness calculation with edge cases"""
        service = GoogleVisionService()
        
        # Test with empty colors
        brightness = service._calculate_brightness([])
        self.assertEqual(brightness, 0.5)  # Default value
        
        # Test with single color
        colors = [{
            'red': 255, 'green': 255, 'blue': 255,
            'pixel_fraction': 1.0
        }]
        brightness = service._calculate_brightness(colors)
        self.assertAlmostEqual(brightness, 1.0, places=6)  # White should be max brightness
        
        # Test with black color
        colors = [{
            'red': 0, 'green': 0, 'blue': 0,
            'pixel_fraction': 1.0
        }]
        brightness = service._calculate_brightness(colors)
        self.assertEqual(brightness, 0.0)  # Black should be min brightness
    
    def test_contrast_calculation_edge_cases(self):
        """Test contrast calculation with edge cases"""
        service = GoogleVisionService()
        
        # Test with single color (no contrast)
        colors = [{
            'red': 128, 'green': 128, 'blue': 128,
            'pixel_fraction': 1.0
        }]
        contrast = service._calculate_contrast(colors)
        self.assertEqual(contrast, 0.0)
        
        # Test with high contrast colors
        colors = [
            {'red': 255, 'green': 255, 'blue': 255, 'pixel_fraction': 0.5},
            {'red': 0, 'green': 0, 'blue': 0, 'pixel_fraction': 0.5}
        ]
        contrast = service._calculate_contrast(colors)
        self.assertAlmostEqual(contrast, 1.0, places=6)  # Maximum contrast
    
    @patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', True)
    @patch('app.services.google_vision_service.vision')
    def test_rate_limiting_handling(self, mock_vision):
        """Test handling of API rate limiting"""
        mock_client = Mock()
        mock_vision.ImageAnnotatorClient.return_value = mock_client
        
        # Mock rate limiting error
        from google.api_core.exceptions import ResourceExhausted
        mock_client.face_detection.side_effect = ResourceExhausted("Quota exceeded")
        
        with patch.dict(os.environ, {
            'GOOGLE_CREDENTIALS_JSON': json.dumps(self.test_credentials_json)
        }):
            with patch('time.sleep'):  # Mock sleep to speed up test
                service = GoogleVisionService()
                faces = service.detect_faces(self.mock_image_data)
                
                # Should handle rate limiting gracefully
                self.assertEqual(len(faces), 0)
                
                # Should attempt retries
                self.assertEqual(mock_client.face_detection.call_count, 3)


if __name__ == '__main__':
    unittest.main()