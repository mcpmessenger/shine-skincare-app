import unittest
import json
import io
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.services import (
    GoogleVisionService, 
    ImageVectorizationService, 
    FAISSService, 
    SupabaseService,
    DemographicWeightedSearch,
    EnhancedSkinTypeClassifier
)


class TestEnhancedAPIEndpoints(unittest.TestCase):
    """Test cases for enhanced API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock services
        self.mock_services()
        
        # Test data
        self.test_image_data = b"fake_image_data"
        self.test_demographics = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_group': '25-35'
        }
        
        # Mock JWT token
        self.mock_jwt_token = "mock_jwt_token"
    
    def mock_services(self):
        """Mock all services for testing"""
        # Mock service responses
        self.mock_vision_result = {
            'status': 'success',
            'results': {
                'face_detection': {'faces_found': 1},
                'image_properties': {'color_count': 5},
                'label_detection': {'labels': []}
            }
        }
        
        self.mock_skin_classification = {
            'fitzpatrick_type': 'III',
            'fitzpatrick_description': 'Sometimes burns, tans gradually',
            'monk_tone': 4,
            'monk_description': 'Monk Scale Tone 4',
            'ethnicity_considered': True,
            'ethnicity': 'caucasian',
            'confidence': 0.85,
            'high_confidence': True,
            'original_classifications': {'fitzpatrick': 'III', 'monk': 4},
            'adjustments_applied': False
        }
    
    def create_mock_image_file(self):
        """Create a mock image file for testing"""
        return (io.BytesIO(self.test_image_data), 'test_image.jpg')
    
    @patch('app.enhanced_image_analysis.routes.google_vision_service')
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_analyze_guest_enhanced(self, mock_skin_classifier, mock_vision_service):
        """Test enhanced guest analysis endpoint"""
        # Mock service responses
        mock_vision_service.analyze_image_from_bytes.return_value = self.mock_vision_result
        mock_skin_classifier.classify_skin_type.return_value = self.mock_skin_classification
        
        # Prepare request data
        data = {
            'image': self.create_mock_image_file(),
            'ethnicity': 'caucasian'
        }
        
        # Make request
        response = self.client.post('/api/enhanced/analyze/guest', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertTrue(response_data['success'])
        self.assertIn('data', response_data)
        self.assertIn('analysis', response_data['data'])
        self.assertIn('skin_classification', response_data['data'])
        
        # Verify service calls
        mock_vision_service.analyze_image_from_bytes.assert_called_once()
        mock_skin_classifier.classify_skin_type.assert_called_once()
    
    @patch('app.enhanced_image_analysis.routes.google_vision_service')
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_analyze_guest_no_ethnicity(self, mock_skin_classifier, mock_vision_service):
        """Test guest analysis without ethnicity"""
        # Mock service responses
        mock_vision_service.analyze_image_from_bytes.return_value = self.mock_vision_result
        mock_skin_classifier.classify_skin_type.return_value = self.mock_skin_classification
        
        # Prepare request data without ethnicity
        data = {'image': self.create_mock_image_file()}
        
        # Make request
        response = self.client.post('/api/enhanced/analyze/guest', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify skin classifier was called with None ethnicity
        mock_skin_classifier.classify_skin_type.assert_called_once()
        args, kwargs = mock_skin_classifier.classify_skin_type.call_args
        self.assertIsNone(kwargs.get('ethnicity'))
    
    def test_analyze_guest_no_image(self):
        """Test guest analysis without image"""
        response = self.client.post('/api/enhanced/analyze/guest')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_analyze_guest_invalid_file_type(self):
        """Test guest analysis with invalid file type"""
        data = {
            'image': (io.BytesIO(b"fake_data"), 'test.txt')
        }
        
        response = self.client.post('/api/enhanced/analyze/guest', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_classify_skin_type_enhanced(self, mock_skin_classifier):
        """Test enhanced skin type classification endpoint"""
        # Mock service response
        mock_skin_classifier.classify_skin_type.return_value = self.mock_skin_classification
        mock_skin_classifier.get_supported_ethnicities.return_value = ['caucasian', 'african', 'asian']
        mock_skin_classifier.get_model_info.return_value = {'version': '1.0.0'}
        
        # Prepare request data
        data = {
            'image': self.create_mock_image_file(),
            'ethnicity': 'caucasian'
        }
        
        # Make request
        response = self.client.post('/api/enhanced/classify/skin-type', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertTrue(response_data['success'])
        self.assertIn('classification', response_data)
        self.assertIn('supported_ethnicities', response_data)
        self.assertIn('classifier_info', response_data)
        
        # Verify service call
        mock_skin_classifier.classify_skin_type.assert_called_once()
    
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_classify_skin_type_error(self, mock_skin_classifier):
        """Test skin type classification with error"""
        # Mock service to return error
        mock_skin_classifier.classify_skin_type.return_value = {
            'error': 'Classification failed',
            'status': 'error'
        }
        
        # Prepare request data
        data = {'image': self.create_mock_image_file()}
        
        # Make request
        response = self.client.post('/api/enhanced/classify/skin-type', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    @patch('flask_jwt_extended.get_jwt_identity')
    @patch('app.enhanced_image_analysis.routes.supabase_service')
    @patch('app.enhanced_image_analysis.routes.demographic_search_service')
    def test_similarity_search_demographic(self, mock_demographic_search, mock_supabase, mock_jwt):
        """Test demographic similarity search endpoint"""
        # Mock JWT
        mock_jwt.return_value = 'test_user_id'
        
        # Mock services
        mock_supabase.get_image_by_id.return_value = {
            'id': 'test_image_id',
            'user_id': 'test_user_id',
            'image_url': 'http://example.com/image.jpg'
        }
        mock_supabase.get_vector_by_image_id.return_value = {
            'vector_data': [0.1, 0.2, 0.3] * 100  # Mock vector
        }
        
        mock_demographic_search.search_with_demographics.return_value = [
            ('similar_image_1', 0.5),
            ('similar_image_2', 0.8)
        ]
        mock_demographic_search._extract_demographics.return_value = {'ethnicity': 'caucasian'}
        mock_demographic_search.demographic_weight = 0.3
        
        # Mock similar image records
        def mock_get_image_by_id(image_id):
            return {
                'id': image_id,
                'image_url': f'http://example.com/{image_id}.jpg'
            }
        mock_supabase.get_image_by_id.side_effect = mock_get_image_by_id
        mock_supabase.get_analysis_by_image_id.return_value = {'google_vision_result': {}}
        
        # Prepare request data
        request_data = {
            'image_id': 'test_image_id',
            'demographics': self.test_demographics,
            'k': 5
        }
        
        # Make request with JWT token
        headers = {'Authorization': f'Bearer {self.mock_jwt_token}'}
        response = self.client.post('/api/enhanced/similarity/demographic',
                                  data=json.dumps(request_data),
                                  content_type='application/json',
                                  headers=headers)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertIn('similar_images', response_data)
        self.assertIn('user_demographics', response_data)
        self.assertIn('search_type', response_data)
        self.assertEqual(response_data['search_type'], 'demographic_weighted')
    
    @patch('flask_jwt_extended.get_jwt_identity')
    def test_similarity_search_demographic_no_data(self, mock_jwt):
        """Test demographic search without JSON data"""
        mock_jwt.return_value = 'test_user_id'
        
        headers = {'Authorization': f'Bearer {self.mock_jwt_token}'}
        response = self.client.post('/api/enhanced/similarity/demographic',
                                  headers=headers)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    @patch('flask_jwt_extended.get_jwt_identity')
    def test_similarity_search_demographic_missing_image_id(self, mock_jwt):
        """Test demographic search without image_id"""
        mock_jwt.return_value = 'test_user_id'
        
        request_data = {'demographics': self.test_demographics}
        headers = {'Authorization': f'Bearer {self.mock_jwt_token}'}
        
        response = self.client.post('/api/enhanced/similarity/demographic',
                                  data=json.dumps(request_data),
                                  content_type='application/json',
                                  headers=headers)
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    @patch('app.enhanced_image_analysis.routes.google_vision_service')
    @patch('app.enhanced_image_analysis.routes.vectorization_service')
    @patch('app.enhanced_image_analysis.routes.faiss_service')
    @patch('app.enhanced_image_analysis.routes.supabase_service')
    @patch('app.enhanced_image_analysis.routes.demographic_search_service')
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_enhanced_health_check(self, mock_skin_classifier, mock_demographic_search,
                                 mock_supabase, mock_faiss, mock_vectorization, mock_vision):
        """Test enhanced health check endpoint"""
        # Mock service availability
        mock_vision.is_available.return_value = True
        mock_vectorization.is_available.return_value = True
        mock_faiss.is_available.return_value = True
        mock_supabase.is_available.return_value = True
        mock_demographic_search.is_available.return_value = True
        mock_skin_classifier.is_available.return_value = True
        
        # Mock service info
        mock_faiss.get_index_info.return_value = {'total_vectors': 100}
        mock_vectorization.get_model_info.return_value = {'model': 'resnet50'}
        mock_demographic_search.get_configuration.return_value = {'demographic_weight': 0.3}
        mock_skin_classifier.get_model_info.return_value = {'version': '1.0.0'}
        
        # Make request
        response = self.client.get('/api/enhanced/health/enhanced')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        self.assertEqual(response_data['status'], 'healthy')
        self.assertIn('services', response_data)
        self.assertIn('service_info', response_data)
        self.assertIn('enhanced_features', response_data)
        
        # Verify all services are checked
        services = response_data['services']
        expected_services = [
            'google_vision', 'vectorization', 'faiss', 
            'supabase', 'demographic_search', 'skin_classifier'
        ]
        for service in expected_services:
            self.assertIn(service, services)
            self.assertTrue(services[service])
        
        # Verify enhanced features
        features = response_data['enhanced_features']
        self.assertTrue(features['cosine_similarity'])
        self.assertTrue(features['demographic_weighting'])
        self.assertTrue(features['enhanced_skin_classification'])
        self.assertTrue(features['ethnicity_context'])
    
    def test_input_validation_edge_cases(self):
        """Test various input validation edge cases"""
        # Test empty file
        data = {'image': (io.BytesIO(b""), 'empty.jpg')}
        response = self.client.post('/api/enhanced/analyze/guest', 
                                  data=data, 
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        # Test very long ethnicity string
        data = {
            'image': self.create_mock_image_file(),
            'ethnicity': 'a' * 1000  # Very long string
        }
        response = self.client.post('/api/enhanced/classify/skin-type', 
                                  data=data, 
                                  content_type='multipart/form-data')
        # Should still work but might be handled by the service
        self.assertIn(response.status_code, [200, 400, 500])
    
    @patch('app.enhanced_image_analysis.routes.skin_classifier_service')
    def test_service_exception_handling(self, mock_skin_classifier):
        """Test handling of service exceptions"""
        # Mock service to raise exception
        mock_skin_classifier.classify_skin_type.side_effect = Exception("Service error")
        
        data = {'image': self.create_mock_image_file()}
        response = self.client.post('/api/enhanced/classify/skin-type', 
                                  data=data, 
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()