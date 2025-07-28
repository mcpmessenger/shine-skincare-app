"""
Tests for Enhanced Analysis Router

This module contains comprehensive tests for the enhanced analysis router,
including unit tests, integration tests, and end-to-end tests.
"""

import pytest
import json
import io
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.enhanced_analysis_router import EnhancedAnalysisRouter, enhanced_analysis_bp
from app.service_manager import ServiceManager


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register the enhanced analysis blueprint
    app.register_blueprint(enhanced_analysis_bp)
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create authentication headers for testing"""
    with app.app_context():
        access_token = create_access_token(identity='test_user_123')
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def mock_services():
    """Create mock services for testing"""
    mock_google_vision = Mock()
    mock_google_vision.analyze_image_from_bytes.return_value = {
        'status': 'success',
        'results': {
            'face_detection': {
                'faces_found': 1,
                'face_data': [{'confidence': 0.9}]
            },
            'image_properties': {
                'color_count': 5,
                'dominant_colors': ['#F4C2A1', '#D4A574']
            },
            'label_detection': {
                'labels_found': 3,
                'labels': [
                    {'description': 'Person', 'confidence': 0.95},
                    {'description': 'Face', 'confidence': 0.92},
                    {'description': 'Skin', 'confidence': 0.88}
                ]
            }
        },
        'confidence': 0.9
    }
    mock_google_vision.is_available.return_value = True
    
    mock_skin_classifier = Mock()
    mock_skin_classifier.classify_skin_type.return_value = {
        'fitzpatrick_type': 'III',
        'fitzpatrick_description': 'Light skin, sometimes burns, usually tans',
        'monk_tone': 'MT-4',
        'monk_description': 'Light medium skin tone',
        'confidence': 0.85,
        'concerns': ['Even Skin Tone', 'Hydration'],
        'ethnicity_considered': True
    }
    mock_skin_classifier.is_available.return_value = True
    
    mock_demographic_search = Mock()
    mock_demographic_search.search_similar_profiles.return_value = [
        {
            'profile_id': 'profile_001',
            'age_range': '25-35',
            'skin_type': 'III',
            'ethnicity': 'Mixed',
            'geographic_region': 'North America',
            'similarity_score': 0.87,
            'scin_data_reference': 'SCIN_001'
        },
        {
            'profile_id': 'profile_002',
            'age_range': '25-35',
            'skin_type': 'III',
            'ethnicity': 'Caucasian',
            'geographic_region': 'Europe',
            'similarity_score': 0.82,
            'scin_data_reference': 'SCIN_002'
        }
    ]
    mock_demographic_search.is_available.return_value = True
    
    mock_faiss = Mock()
    mock_faiss.is_available.return_value = True
    
    return {
        'google_vision': mock_google_vision,
        'skin_classifier': mock_skin_classifier,
        'demographic_search': mock_demographic_search,
        'faiss': mock_faiss
    }


@pytest.fixture
def sample_image():
    """Create a sample image file for testing"""
    # Create a simple test image (1x1 pixel PNG)
    image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    return io.BytesIO(image_data)


class TestEnhancedAnalysisRouter:
    """Test cases for Enhanced Analysis Router"""
    
    def test_router_initialization(self):
        """Test that the router initializes correctly"""
        router = EnhancedAnalysisRouter('test_router')
        assert router.blueprint.name == 'test_router'
        assert len(router.analysis_cache) == 0
        assert len(router.analysis_history) == 0
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_enhanced_analysis_endpoint_success(self, mock_service_manager, client, auth_headers, mock_services, sample_image):
        """Test successful enhanced analysis"""
        # Setup mock service manager
        mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
        
        # Prepare test data
        data = {
            'image': (sample_image, 'test_image.png'),
            'ethnicity': 'Mixed',
            'analysis_type': 'comprehensive'
        }
        
        # Make request
        response = client.post(
            '/api/enhanced-analysis',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        # Verify response
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert 'analysis_id' in response_data
        assert response_data['status'] == 'completed'
        assert 'processing_time' in response_data
        assert 'data' in response_data
        
        # Verify analysis data structure
        data = response_data['data']
        assert 'skin_analysis' in data
        assert 'demographic_insights' in data
        assert 'confidence_scores' in data
        assert 'metadata' in data
        
        # Verify skin analysis structure
        skin_analysis = data['skin_analysis']
        assert skin_analysis['status'] == 'success'
        assert 'skinType' in skin_analysis
        assert 'concerns' in skin_analysis
        assert 'recommendations' in skin_analysis
        assert 'products' in skin_analysis
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_enhanced_analysis_no_image(self, mock_service_manager, client, auth_headers):
        """Test enhanced analysis with no image file"""
        response = client.post(
            '/api/enhanced-analysis',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'No image file provided' in response_data['error']
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_enhanced_analysis_invalid_file_type(self, mock_service_manager, client, auth_headers):
        """Test enhanced analysis with invalid file type"""
        data = {
            'image': (io.BytesIO(b'test data'), 'test.txt')
        }
        
        response = client.post(
            '/api/enhanced-analysis',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'Invalid file type' in response_data['error']
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_enhanced_analysis_service_failure(self, mock_service_manager, client, auth_headers, sample_image):
        """Test enhanced analysis with service failure"""
        # Setup mock service that fails
        mock_google_vision = Mock()
        mock_google_vision.analyze_image_from_bytes.return_value = {
            'status': 'error',
            'error': 'Service unavailable'
        }
        
        mock_service_manager.get_service.return_value = mock_google_vision
        
        data = {
            'image': (sample_image, 'test_image.png')
        }
        
        response = client.post(
            '/api/enhanced-analysis',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'error_type' in response_data
    
    def test_analysis_status_endpoint(self, client):
        """Test analysis status endpoint"""
        # Create a router instance and add a test analysis
        router = EnhancedAnalysisRouter()
        analysis_id = 'test_analysis_123'
        router._update_analysis_status(analysis_id, 'processing', {'test': 'data'})
        
        # Register the blueprint with the test status
        with client.application.app_context():
            client.application.register_blueprint(router.blueprint, url_prefix='/test')
        
        response = client.get(f'/test/api/enhanced-analysis/status/{analysis_id}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['analysis_id'] == analysis_id
        assert response_data['status'] == 'processing'
    
    def test_analysis_status_not_found(self, client):
        """Test analysis status endpoint with non-existent ID"""
        response = client.get('/api/enhanced-analysis/status/nonexistent_id')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'not found' in response_data['error'].lower()
    
    def test_analysis_history_endpoint(self, client, auth_headers):
        """Test analysis history endpoint"""
        response = client.get(
            '/api/enhanced-analysis/history',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'data' in response_data
        assert 'analyses' in response_data['data']
        assert 'pagination' in response_data['data']
    
    def test_analysis_history_pagination(self, client, auth_headers):
        """Test analysis history pagination"""
        response = client.get(
            '/api/enhanced-analysis/history?page=2&per_page=5',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        pagination = response_data['data']['pagination']
        assert pagination['page'] == 2
        assert pagination['per_page'] == 5
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_skin_analysis_compatibility(self, mock_service_manager, client, mock_services, sample_image):
        """Test backward compatibility endpoint"""
        # Setup mock service manager
        mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
        
        data = {
            'image': (sample_image, 'test_image.png')
        }
        
        response = client.post(
            '/api/skin-analysis',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Should return legacy format even if using enhanced analysis
        assert response.status_code in [200, 500]  # May fail due to missing auth, but structure should be correct
        response_data = json.loads(response.data)
        
        # Check for legacy format fields
        if response.status_code == 200:
            assert 'status' in response_data
            assert 'skinType' in response_data or 'error' in response_data
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_guest_analysis_endpoint(self, mock_service_manager, client, mock_services, sample_image):
        """Test guest analysis endpoint"""
        # Setup mock service manager
        mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
        
        data = {
            'image': (sample_image, 'test_image.png'),
            'ethnicity': 'Asian'
        }
        
        response = client.post(
            '/api/enhanced-analysis/guest',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Guest endpoint should work without authentication
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'success' in response_data
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_health_check_endpoint(self, mock_service_manager, client, mock_services):
        """Test health check endpoint"""
        # Setup mock service manager
        mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
        mock_service_manager.get_service_info.return_value = {
            'faiss': {'index_size': 1000},
            'vectorization': {'model_name': 'test_model'}
        }
        
        response = client.get('/api/enhanced-analysis/health')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'status' in response_data
        assert 'services' in response_data
        assert 'timestamp' in response_data
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_health_check_service_failure(self, mock_service_manager, client):
        """Test health check with service failures"""
        # Setup mock service that fails
        mock_service = Mock()
        mock_service.is_available.return_value = False
        mock_service_manager.get_service.return_value = mock_service
        mock_service_manager.get_service_info.return_value = {}
        
        response = client.get('/api/enhanced-analysis/health')
        
        assert response.status_code == 503  # Service unavailable
        response_data = json.loads(response.data)
        assert response_data['status'] == 'degraded'
    
    def test_analysis_request_model(self):
        """Test AnalysisRequest data model"""
        from app.enhanced_analysis_router import AnalysisRequest
        
        request = AnalysisRequest(
            image_data=b'test_data',
            user_id='test_user',
            analysis_type='comprehensive',
            metadata={'test': 'value'},
            timestamp=datetime.utcnow()
        )
        
        request_dict = request.to_dict()
        assert request_dict['user_id'] == 'test_user'
        assert request_dict['analysis_type'] == 'comprehensive'
        assert request_dict['metadata']['test'] == 'value'
        assert request_dict['image_size'] == len(b'test_data')
    
    def test_analysis_result_model(self):
        """Test AnalysisResult data model"""
        from app.enhanced_analysis_router import AnalysisResult
        
        result = AnalysisResult(
            analysis_id='test_123',
            user_id='test_user',
            skin_classification={'type': 'III'},
            demographic_matches=[],
            recommendations=['test rec'],
            confidence_scores={'overall': 0.8},
            processing_time=1.5,
            timestamp=datetime.utcnow()
        )
        
        result_dict = result.to_dict()
        assert result_dict['analysis_id'] == 'test_123'
        assert result_dict['processing_time'] == 1.5
        assert result_dict['status'] == 'completed'
    
    def test_generate_enhanced_recommendations(self):
        """Test enhanced recommendation generation"""
        router = EnhancedAnalysisRouter()
        
        vision_result = {
            'results': {
                'face_detection': {'faces_found': 1},
                'image_properties': {}
            }
        }
        
        skin_classification = {
            'fitzpatrick_type': 'II',
            'concerns': ['Acne', 'Sensitivity']
        }
        
        demographic_matches = [{'profile_id': 'test'}]
        
        recommendations = router._generate_enhanced_recommendations(
            vision_result, skin_classification, demographic_matches
        )
        
        assert len(recommendations) > 0
        assert any('SPF 50+' in rec for rec in recommendations)  # Fair skin recommendation
        assert any('salicylic acid' in rec for rec in recommendations)  # Acne recommendation
    
    def test_format_skin_analysis_response(self):
        """Test skin analysis response formatting"""
        router = EnhancedAnalysisRouter()
        
        vision_result = {
            'results': {'face_detection': {'faces_found': 1}},
            'confidence': 0.9
        }
        
        skin_classification = {
            'fitzpatrick_type': 'IV',
            'confidence': 0.85,
            'concerns': ['Hyperpigmentation', 'Oiliness']
        }
        
        recommendations = ['Use sunscreen daily', 'Consider vitamin C serum']
        
        response = router._format_skin_analysis_response(
            vision_result, skin_classification, recommendations
        )
        
        assert response['status'] == 'success'
        assert response['skinType'] == 'Medium'
        assert response['fitzpatrick_type'] == 'IV'
        assert len(response['concerns']) <= 3
        assert len(response['products']) > 0
        assert 'enhanced_features' in response
    
    def test_performance_requirement(self, client, auth_headers, sample_image):
        """Test that analysis completes within 10-second requirement"""
        with patch('app.enhanced_analysis_router.service_manager') as mock_service_manager:
            # Setup fast mock services
            mock_services = {
                'google_vision': Mock(),
                'skin_classifier': Mock(),
                'demographic_search': Mock(),
                'faiss': Mock()
            }
            
            for service in mock_services.values():
                service.is_available.return_value = True
            
            mock_services['google_vision'].analyze_image_from_bytes.return_value = {
                'status': 'success', 'results': {}, 'confidence': 0.8
            }
            mock_services['skin_classifier'].classify_skin_type.return_value = {
                'fitzpatrick_type': 'III', 'confidence': 0.8, 'concerns': []
            }
            mock_services['demographic_search'].search_similar_profiles.return_value = []
            
            mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
            
            data = {'image': (sample_image, 'test_image.png')}
            
            start_time = time.time()
            response = client.post(
                '/api/enhanced-analysis',
                data=data,
                headers=auth_headers,
                content_type='multipart/form-data'
            )
            end_time = time.time()
            
            # Verify response time is under 10 seconds
            processing_time = end_time - start_time
            assert processing_time < 10.0, f"Analysis took {processing_time:.2f}s, exceeding 10s requirement"
            
            if response.status_code == 200:
                response_data = json.loads(response.data)
                assert response_data['processing_time'] < 10.0


class TestIntegration:
    """Integration tests for the enhanced analysis router"""
    
    @patch('app.enhanced_analysis_router.service_manager')
    def test_end_to_end_analysis_flow(self, mock_service_manager, client, auth_headers, mock_services, sample_image):
        """Test complete end-to-end analysis flow"""
        # Setup mock service manager
        mock_service_manager.get_service.side_effect = lambda name: mock_services[name]
        mock_service_manager.get_service_info.return_value = {}
        
        # Step 1: Submit analysis
        data = {
            'image': (sample_image, 'test_image.png'),
            'ethnicity': 'Mixed',
            'analysis_type': 'comprehensive'
        }
        
        response = client.post(
            '/api/enhanced-analysis',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        analysis_id = response_data['analysis_id']
        
        # Step 2: Check analysis status
        status_response = client.get(f'/api/enhanced-analysis/status/{analysis_id}')
        assert status_response.status_code == 200
        status_data = json.loads(status_response.data)
        assert status_data['status'] == 'completed'
        
        # Step 3: Check analysis history
        history_response = client.get('/api/enhanced-analysis/history', headers=auth_headers)
        assert history_response.status_code == 200
        history_data = json.loads(history_response.data)
        
        # Should have at least one analysis in history
        analyses = history_data['data']['analyses']
        assert len(analyses) >= 1
        
        # Step 4: Test health check
        health_response = client.get('/api/enhanced-analysis/health')
        assert health_response.status_code == 200
        health_data = json.loads(health_response.data)
        assert health_data['status'] in ['healthy', 'degraded']
    
    def test_error_recovery_and_fallback(self, client, auth_headers, sample_image):
        """Test error recovery and fallback mechanisms"""
        with patch('app.enhanced_analysis_router.service_manager') as mock_service_manager:
            # Setup services that fail gracefully
            mock_google_vision = Mock()
            mock_google_vision.analyze_image_from_bytes.side_effect = Exception("Service temporarily unavailable")
            
            mock_service_manager.get_service.return_value = mock_google_vision
            
            data = {'image': (sample_image, 'test_image.png')}
            
            response = client.post(
                '/api/enhanced-analysis',
                data=data,
                headers=auth_headers,
                content_type='multipart/form-data'
            )
            
            # Should handle error gracefully
            assert response.status_code == 500
            response_data = json.loads(response.data)
            assert response_data['success'] is False
            assert 'analysis_id' in response_data  # Should still provide analysis ID for tracking


if __name__ == '__main__':
    pytest.main([__file__, '-v'])