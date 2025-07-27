"""
Tests for enhanced service wrappers with error handling and monitoring
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.enhanced_service_wrappers import (
    EnhancedGoogleVisionWrapper, EnhancedFAISSWrapper,
    EnhancedSkinClassifierWrapper, EnhancedDemographicSearchWrapper,
    create_enhanced_service_wrappers, health_check_all_services
)
from app.error_handlers import (
    GoogleVisionError, FAISSError, SkinClassificationError, DemographicSearchError
)


class TestEnhancedGoogleVisionWrapper:
    """Test enhanced Google Vision service wrapper"""
    
    def test_successful_image_analysis(self):
        """Test successful image analysis"""
        # Mock the underlying service
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.analyze_image_from_bytes.return_value = {
            'status': 'success',
            'results': {'face_detection': {'faces_found': 1}}
        }
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        # Test analysis
        image_data = b"fake_image_data"
        result = wrapper.analyze_image_from_bytes(image_data)
        
        assert result['status'] == 'success'
        assert 'results' in result
        mock_service.analyze_image_from_bytes.assert_called_once_with(image_data)
    
    def test_empty_image_data_validation(self):
        """Test validation of empty image data"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        # Test with empty data
        with pytest.raises(GoogleVisionError) as exc_info:
            wrapper.analyze_image_from_bytes(b"")
        
        assert "Empty image data" in str(exc_info.value)
        assert exc_info.value.details['data_length'] == 0
    
    def test_service_unavailable_handling(self):
        """Test handling when service is unavailable"""
        mock_service = Mock()
        mock_service.is_available.return_value = False
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        with pytest.raises(GoogleVisionError) as exc_info:
            wrapper.analyze_image_from_bytes(b"fake_data")
        
        assert "not available" in str(exc_info.value)
    
    def test_analysis_failure_handling(self):
        """Test handling of analysis failures"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.analyze_image_from_bytes.return_value = {
            'status': 'error',
            'error': 'Analysis failed'
        }
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        with pytest.raises(GoogleVisionError) as exc_info:
            wrapper.analyze_image_from_bytes(b"fake_data")
        
        assert "Analysis failed" in str(exc_info.value)
    
    def test_face_detection(self):
        """Test face detection functionality"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.detect_faces.return_value = [
            {'confidence': 0.9, 'bounding_box': [0, 0, 100, 100]}
        ]
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        faces = wrapper.detect_faces(b"fake_data")
        
        assert len(faces) == 1
        assert faces[0]['confidence'] == 0.9
        mock_service.detect_faces.assert_called_once_with(b"fake_data")
    
    def test_service_exception_handling(self):
        """Test handling of service exceptions"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.analyze_image_from_bytes.side_effect = Exception("Service error")
        
        wrapper = EnhancedGoogleVisionWrapper(mock_service)
        
        with pytest.raises(GoogleVisionError) as exc_info:
            wrapper.analyze_image_from_bytes(b"fake_data")
        
        assert "Service error" in str(exc_info.value)
        assert 'original_error' in exc_info.value.details


class TestEnhancedFAISSWrapper:
    """Test enhanced FAISS service wrapper"""
    
    def test_successful_vector_addition(self):
        """Test successful vector addition"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.add_vector.return_value = True
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        vector = np.array([1.0, 2.0, 3.0])
        result = wrapper.add_vector(vector, "test_image_id")
        
        assert result is True
        mock_service.add_vector.assert_called_once_with(vector, "test_image_id")
    
    def test_none_vector_validation(self):
        """Test validation of None vector"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        with pytest.raises(FAISSError) as exc_info:
            wrapper.add_vector(None, "test_image_id")
        
        assert "Vector is None" in str(exc_info.value)
        assert exc_info.value.operation == "add_vector"
    
    def test_invalid_image_id_validation(self):
        """Test validation of invalid image ID"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        vector = np.array([1.0, 2.0, 3.0])
        
        # Test with None image_id
        with pytest.raises(FAISSError) as exc_info:
            wrapper.add_vector(vector, None)
        
        assert "Invalid image_id" in str(exc_info.value)
        
        # Test with non-string image_id
        with pytest.raises(FAISSError) as exc_info:
            wrapper.add_vector(vector, 123)
        
        assert "Invalid image_id" in str(exc_info.value)
    
    def test_service_unavailable_handling(self):
        """Test handling when FAISS service is unavailable"""
        mock_service = Mock()
        mock_service.is_available.return_value = False
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        vector = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(FAISSError) as exc_info:
            wrapper.add_vector(vector, "test_id")
        
        assert "not available" in str(exc_info.value)
    
    def test_vector_addition_failure(self):
        """Test handling of vector addition failure"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.add_vector.return_value = False  # Service returns False
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        vector = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(FAISSError) as exc_info:
            wrapper.add_vector(vector, "test_id")
        
        assert "returned False" in str(exc_info.value)
    
    def test_successful_similarity_search(self):
        """Test successful similarity search"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        mock_service.search_similar.return_value = [
            ("image1", 0.9),
            ("image2", 0.8),
            ("image3", 0.7)
        ]
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        query_vector = np.array([1.0, 2.0, 3.0])
        results = wrapper.search_similar(query_vector, k=3)
        
        assert len(results) == 3
        assert results[0] == ("image1", 0.9)
        mock_service.search_similar.assert_called_once_with(query_vector, 3)
    
    def test_search_parameter_validation(self):
        """Test validation of search parameters"""
        mock_service = Mock()
        mock_service.is_available.return_value = True
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        # Test with None query vector
        with pytest.raises(FAISSError) as exc_info:
            wrapper.search_similar(None, k=5)
        
        assert "Query vector is None" in str(exc_info.value)
        
        # Test with invalid k values
        query_vector = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(FAISSError) as exc_info:
            wrapper.search_similar(query_vector, k=0)
        
        assert "Invalid k value" in str(exc_info.value)
        
        with pytest.raises(FAISSError) as exc_info:
            wrapper.search_similar(query_vector, k=101)
        
        assert "Invalid k value" in str(exc_info.value)
    
    def test_index_stats_retrieval(self):
        """Test index statistics retrieval"""
        mock_service = Mock()
        mock_service.get_index_stats.return_value = {
            'total_vectors': 1000,
            'dimension': 2048
        }
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        stats = wrapper.get_index_stats()
        
        assert stats['total_vectors'] == 1000
        assert stats['dimension'] == 2048
    
    def test_index_stats_error_handling(self):
        """Test error handling in index stats retrieval"""
        mock_service = Mock()
        mock_service.get_index_stats.side_effect = Exception("Stats error")
        
        wrapper = EnhancedFAISSWrapper(mock_service)
        
        stats = wrapper.get_index_stats()
        
        assert 'error' in stats
        assert stats['available'] is False


class TestEnhancedSkinClassifierWrapper:
    """Test enhanced skin classifier service wrapper"""
    
    def test_successful_classification(self):
        """Test successful skin type classification"""
        mock_service = Mock()
        mock_service.classify_skin_type.return_value = {
            'fitzpatrick_type': 'III',
            'monk_tone': 5,
            'confidence': 0.85,
            'ethnicity_considered': True
        }
        
        wrapper = EnhancedSkinClassifierWrapper(mock_service)
        
        image_data = b"fake_image_data"
        result = wrapper.classify_skin_type(image_data, ethnicity="caucasian")
        
        assert result['fitzpatrick_type'] == 'III'
        assert result['monk_tone'] == 5
        assert result['confidence'] == 0.85
        mock_service.classify_skin_type.assert_called_once_with(image_data, "caucasian")
    
    def test_empty_image_data_validation(self):
        """Test validation of empty image data"""
        mock_service = Mock()
        
        wrapper = EnhancedSkinClassifierWrapper(mock_service)
        
        with pytest.raises(SkinClassificationError) as exc_info:
            wrapper.classify_skin_type(None, ethnicity="caucasian")
        
        assert "No image data provided" in str(exc_info.value)
        assert exc_info.value.classification_stage == "input_validation"
    
    def test_classification_failure_handling(self):
        """Test handling of classification failures"""
        mock_service = Mock()
        mock_service.classify_skin_type.return_value = {
            'error': 'Classification failed',
            'status': 'error'
        }
        
        wrapper = EnhancedSkinClassifierWrapper(mock_service)
        
        with pytest.raises(SkinClassificationError) as exc_info:
            wrapper.classify_skin_type(b"fake_data")
        
        assert "Classification failed" in str(exc_info.value)
        assert exc_info.value.classification_stage == "classification"
    
    def test_service_exception_handling(self):
        """Test handling of service exceptions"""
        mock_service = Mock()
        mock_service.classify_skin_type.side_effect = Exception("Service error")
        
        wrapper = EnhancedSkinClassifierWrapper(mock_service)
        
        with pytest.raises(SkinClassificationError) as exc_info:
            wrapper.classify_skin_type(b"fake_data")
        
        assert "Service error" in str(exc_info.value)
        assert exc_info.value.classification_stage == "execution"


class TestEnhancedDemographicSearchWrapper:
    """Test enhanced demographic search service wrapper"""
    
    def test_successful_demographic_search(self):
        """Test successful demographic search"""
        mock_service = Mock()
        mock_service.search_with_demographics.return_value = [
            ("image1", 0.95),
            ("image2", 0.88),
            ("image3", 0.82)
        ]
        
        wrapper = EnhancedDemographicSearchWrapper(mock_service)
        
        query_vector = np.array([1.0, 2.0, 3.0])
        demographics = {'ethnicity': 'caucasian', 'age_group': '25-35'}
        
        results = wrapper.search_with_demographics(query_vector, demographics, k=3)
        
        assert len(results) == 3
        assert results[0] == ("image1", 0.95)
        mock_service.search_with_demographics.assert_called_once_with(query_vector, demographics, 3)
    
    def test_none_vector_validation(self):
        """Test validation of None query vector"""
        mock_service = Mock()
        
        wrapper = EnhancedDemographicSearchWrapper(mock_service)
        
        demographics = {'ethnicity': 'caucasian'}
        
        with pytest.raises(DemographicSearchError) as exc_info:
            wrapper.search_with_demographics(None, demographics, k=5)
        
        assert "Query vector is None" in str(exc_info.value)
        assert exc_info.value.search_stage == "input_validation"
    
    def test_invalid_demographics_validation(self):
        """Test validation of invalid demographics"""
        mock_service = Mock()
        
        wrapper = EnhancedDemographicSearchWrapper(mock_service)
        
        query_vector = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(DemographicSearchError) as exc_info:
            wrapper.search_with_demographics(query_vector, "invalid_demographics", k=5)
        
        assert "Invalid user demographics format" in str(exc_info.value)
        assert exc_info.value.demographic_data_missing is True
    
    def test_service_exception_handling(self):
        """Test handling of service exceptions"""
        mock_service = Mock()
        mock_service.search_with_demographics.side_effect = Exception("Search error")
        
        wrapper = EnhancedDemographicSearchWrapper(mock_service)
        
        query_vector = np.array([1.0, 2.0, 3.0])
        demographics = {'ethnicity': 'caucasian'}
        
        with pytest.raises(DemographicSearchError) as exc_info:
            wrapper.search_with_demographics(query_vector, demographics, k=5)
        
        assert "Search error" in str(exc_info.value)
        assert exc_info.value.search_stage == "execution"


class TestServiceWrapperCreation:
    """Test service wrapper creation and management"""
    
    def test_create_enhanced_service_wrappers(self):
        """Test creation of enhanced service wrappers"""
        # Mock service manager
        mock_service_manager = Mock()
        
        # Mock services
        mock_google_vision = Mock()
        mock_faiss = Mock()
        mock_skin_classifier = Mock()
        mock_demographic_search = Mock()
        
        mock_service_manager.get_service.side_effect = lambda name: {
            'google_vision': mock_google_vision,
            'faiss': mock_faiss,
            'skin_classifier': mock_skin_classifier,
            'demographic_search': mock_demographic_search
        }.get(name)
        
        wrappers = create_enhanced_service_wrappers(mock_service_manager)
        
        assert 'google_vision' in wrappers
        assert 'faiss' in wrappers
        assert 'skin_classifier' in wrappers
        assert 'demographic_search' in wrappers
        
        assert isinstance(wrappers['google_vision'], EnhancedGoogleVisionWrapper)
        assert isinstance(wrappers['faiss'], EnhancedFAISSWrapper)
        assert isinstance(wrappers['skin_classifier'], EnhancedSkinClassifierWrapper)
        assert isinstance(wrappers['demographic_search'], EnhancedDemographicSearchWrapper)
    
    def test_create_wrappers_with_missing_services(self):
        """Test wrapper creation with missing services"""
        mock_service_manager = Mock()
        mock_service_manager.get_service.return_value = None
        
        wrappers = create_enhanced_service_wrappers(mock_service_manager)
        
        # Should handle missing services gracefully
        assert len(wrappers) == 0
    
    def test_create_wrappers_with_exception(self):
        """Test wrapper creation with service manager exception"""
        mock_service_manager = Mock()
        mock_service_manager.get_service.side_effect = Exception("Service manager error")
        
        # Should not raise exception
        wrappers = create_enhanced_service_wrappers(mock_service_manager)
        assert len(wrappers) == 0


class TestHealthChecking:
    """Test health checking functionality"""
    
    def test_health_check_all_services_healthy(self):
        """Test health check with all services healthy"""
        # Create mock wrappers
        mock_wrapper1 = Mock()
        mock_wrapper1.is_available.return_value = True
        mock_wrapper1.get_index_stats.return_value = {'total_vectors': 100}
        
        mock_wrapper2 = Mock()
        mock_wrapper2.is_available.return_value = True
        
        wrappers = {
            'service1': mock_wrapper1,
            'service2': mock_wrapper2
        }
        
        health_results = health_check_all_services(wrappers)
        
        assert health_results['overall_status'] == 'healthy'
        assert health_results['healthy_services'] == 2
        assert health_results['unhealthy_services'] == 0
        assert health_results['total_services'] == 2
        
        assert health_results['services']['service1']['status'] == 'healthy'
        assert health_results['services']['service1']['available'] is True
        assert 'stats' in health_results['services']['service1']
    
    def test_health_check_with_unhealthy_services(self):
        """Test health check with some unhealthy services"""
        mock_wrapper1 = Mock()
        mock_wrapper1.is_available.return_value = True
        
        mock_wrapper2 = Mock()
        mock_wrapper2.is_available.return_value = False
        
        wrappers = {
            'service1': mock_wrapper1,
            'service2': mock_wrapper2
        }
        
        health_results = health_check_all_services(wrappers)
        
        assert health_results['overall_status'] == 'degraded'
        assert health_results['healthy_services'] == 1
        assert health_results['unhealthy_services'] == 1
        
        assert health_results['services']['service1']['status'] == 'healthy'
        assert health_results['services']['service2']['status'] == 'unhealthy'
    
    def test_health_check_with_all_unhealthy_services(self):
        """Test health check with all services unhealthy"""
        mock_wrapper1 = Mock()
        mock_wrapper1.is_available.return_value = False
        
        mock_wrapper2 = Mock()
        mock_wrapper2.is_available.return_value = False
        
        wrappers = {
            'service1': mock_wrapper1,
            'service2': mock_wrapper2
        }
        
        health_results = health_check_all_services(wrappers)
        
        assert health_results['overall_status'] == 'unhealthy'
        assert health_results['healthy_services'] == 0
        assert health_results['unhealthy_services'] == 2
    
    def test_health_check_with_service_exception(self):
        """Test health check with service throwing exception"""
        mock_wrapper1 = Mock()
        mock_wrapper1.is_available.side_effect = Exception("Service error")
        
        wrappers = {'service1': mock_wrapper1}
        
        health_results = health_check_all_services(wrappers)
        
        assert health_results['overall_status'] == 'unhealthy'
        assert health_results['services']['service1']['status'] == 'error'
        assert health_results['services']['service1']['available'] is False
        assert 'error' in health_results['services']['service1']


if __name__ == '__main__':
    pytest.main([__file__])