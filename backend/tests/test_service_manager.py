import unittest
import os
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.service_manager import ServiceManager


class TestServiceManager(unittest.TestCase):
    """Test cases for the service manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service_manager = ServiceManager()
        
        # Test configuration
        self.test_config = {
            'faiss_dimension': 512,
            'faiss_index_path': 'test_index',
            'demographic_weight': 0.4,
            'ethnicity_weight': 0.7,
            'skin_type_weight': 0.2,
            'age_group_weight': 0.1,
            'supabase_url': 'https://test.supabase.co',
            'supabase_key': 'test_key'
        }
    
    def tearDown(self):
        """Clean up after tests"""
        if self.service_manager.is_initialized():
            self.service_manager.shutdown_services()
    
    @patch('app.service_manager.GoogleVisionService')
    @patch('app.service_manager.ImageVectorizationService')
    @patch('app.service_manager.FAISSService')
    @patch('app.service_manager.SupabaseService')
    @patch('app.service_manager.EnhancedSkinTypeClassifier')
    @patch('app.service_manager.DemographicWeightedSearch')
    def test_initialize_services_success(self, mock_demographic_search, mock_skin_classifier,
                                       mock_supabase, mock_faiss, mock_vectorization, mock_vision):
        """Test successful service initialization"""
        # Mock service instances
        mock_vision_instance = Mock()
        mock_vision_instance.is_available.return_value = True
        mock_vision.return_value = mock_vision_instance
        
        mock_vectorization_instance = Mock()
        mock_vectorization_instance.is_available.return_value = True
        mock_vectorization.return_value = mock_vectorization_instance
        
        mock_faiss_instance = Mock()
        mock_faiss_instance.is_available.return_value = True
        mock_faiss.return_value = mock_faiss_instance
        
        mock_supabase_instance = Mock()
        mock_supabase_instance.is_available.return_value = True
        mock_supabase.return_value = mock_supabase_instance
        
        mock_classifier_instance = Mock()
        mock_classifier_instance.is_available.return_value = True
        mock_skin_classifier.return_value = mock_classifier_instance
        
        mock_demographic_instance = Mock()
        mock_demographic_instance.is_available.return_value = True
        mock_demographic_instance.set_demographic_weight = Mock()
        mock_demographic_instance.set_demographic_component_weights = Mock()
        mock_demographic_search.return_value = mock_demographic_instance
        
        # Initialize services
        self.service_manager.initialize_services(self.test_config)
        
        # Verify initialization
        self.assertTrue(self.service_manager.is_initialized())
        
        # Verify service creation with correct parameters
        mock_faiss.assert_called_once_with(
            dimension=512,
            index_path='test_index'
        )
        mock_supabase.assert_called_once_with(
            url='https://test.supabase.co',
            key='test_key'
        )
        
        # Verify demographic search configuration
        mock_demographic_instance.set_demographic_weight.assert_called_once_with(0.4)
        mock_demographic_instance.set_demographic_component_weights.assert_called_once_with(
            0.7, 0.2, 0.1
        )
    
    def test_initialize_services_already_initialized(self):
        """Test that re-initialization is handled gracefully"""
        # Mock the initialization to avoid actual service creation
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            # First initialization
            self.service_manager.initialize_services()
            self.assertTrue(self.service_manager.is_initialized())
            
            # Second initialization should be ignored
            self.service_manager.initialize_services()
            self.assertTrue(self.service_manager.is_initialized())
    
    def test_get_service_success(self):
        """Test successful service retrieval"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Add a mock service
            mock_service = Mock()
            self.service_manager._services['test_service'] = mock_service
            
            # Retrieve service
            retrieved_service = self.service_manager.get_service('test_service')
            self.assertEqual(retrieved_service, mock_service)
    
    def test_get_service_not_initialized(self):
        """Test service retrieval when not initialized"""
        with self.assertRaises(ValueError) as context:
            self.service_manager.get_service('test_service')
        
        self.assertIn('not initialized', str(context.exception))
    
    def test_get_service_not_found(self):
        """Test service retrieval for non-existent service"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            with self.assertRaises(ValueError) as context:
                self.service_manager.get_service('non_existent_service')
            
            self.assertIn('not found', str(context.exception))
    
    def test_get_all_services(self):
        """Test getting all services"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Add mock services
            mock_service1 = Mock()
            mock_service2 = Mock()
            self.service_manager._services['service1'] = mock_service1
            self.service_manager._services['service2'] = mock_service2
            
            # Get all services
            all_services = self.service_manager.get_all_services()
            
            self.assertEqual(len(all_services), 2)
            self.assertEqual(all_services['service1'], mock_service1)
            self.assertEqual(all_services['service2'], mock_service2)
    
    def test_get_service_status(self):
        """Test getting service status"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Set mock status
            self.service_manager._service_status = {
                'service1': True,
                'service2': False
            }
            
            status = self.service_manager.get_service_status()
            self.assertEqual(status['service1'], True)
            self.assertEqual(status['service2'], False)
    
    def test_get_service_info(self):
        """Test getting service information"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Add mock services with info methods
            mock_faiss = Mock()
            mock_faiss.get_index_info.return_value = {'total_vectors': 100}
            self.service_manager._services['faiss'] = mock_faiss
            
            mock_vectorization = Mock()
            mock_vectorization.get_model_info.return_value = {'model': 'resnet50'}
            self.service_manager._services['vectorization'] = mock_vectorization
            
            mock_demographic = Mock()
            mock_demographic.get_configuration.return_value = {'weight': 0.3}
            self.service_manager._services['demographic_search'] = mock_demographic
            
            mock_classifier = Mock()
            mock_classifier.get_model_info.return_value = {'version': '1.0.0'}
            self.service_manager._services['skin_classifier'] = mock_classifier
            
            # Get service info
            info = self.service_manager.get_service_info()
            
            self.assertEqual(info['faiss']['total_vectors'], 100)
            self.assertEqual(info['vectorization']['model'], 'resnet50')
            self.assertEqual(info['demographic_search']['weight'], 0.3)
            self.assertEqual(info['skin_classifier']['version'], '1.0.0')
    
    def test_reconfigure_demographic_search_service(self):
        """Test reconfiguring demographic search service"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Add mock demographic search service
            mock_demographic = Mock()
            mock_demographic.set_demographic_weight = Mock()
            mock_demographic.set_demographic_component_weights = Mock()
            self.service_manager._services['demographic_search'] = mock_demographic
            
            # Reconfigure service
            self.service_manager.reconfigure_service(
                'demographic_search',
                demographic_weight=0.5,
                ethnicity_weight=0.8,
                skin_type_weight=0.15,
                age_group_weight=0.05
            )
            
            # Verify reconfiguration calls
            mock_demographic.set_demographic_weight.assert_called_once_with(0.5)
            mock_demographic.set_demographic_component_weights.assert_called_once_with(
                0.8, 0.15, 0.05
            )
    
    def test_reconfigure_skin_classifier_service(self):
        """Test reconfiguring skin classifier service"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            # Add mock skin classifier service
            mock_classifier = Mock()
            mock_classifier.set_confidence_threshold = Mock()
            self.service_manager._services['skin_classifier'] = mock_classifier
            
            # Reconfigure service
            self.service_manager.reconfigure_service(
                'skin_classifier',
                confidence_threshold=0.8
            )
            
            # Verify reconfiguration call
            mock_classifier.set_confidence_threshold.assert_called_once_with(0.8)
    
    def test_reconfigure_service_not_initialized(self):
        """Test reconfiguring service when not initialized"""
        with self.assertRaises(ValueError) as context:
            self.service_manager.reconfigure_service('test_service', param=123)
        
        self.assertIn('not initialized', str(context.exception))
    
    def test_reconfigure_service_not_found(self):
        """Test reconfiguring non-existent service"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            
            with self.assertRaises(ValueError) as context:
                self.service_manager.reconfigure_service('non_existent', param=123)
            
            self.assertIn('not found', str(context.exception))
    
    def test_shutdown_services(self):
        """Test service shutdown"""
        # Mock initialization
        with patch.object(self.service_manager, '_initialize_core_services'), \
             patch.object(self.service_manager, '_initialize_enhanced_services'), \
             patch.object(self.service_manager, '_validate_services'):
            
            self.service_manager.initialize_services()
            self.assertTrue(self.service_manager.is_initialized())
            
            # Shutdown services
            self.service_manager.shutdown_services()
            self.assertFalse(self.service_manager.is_initialized())
            self.assertEqual(len(self.service_manager._services), 0)
    
    @patch.dict(os.environ, {
        'FAISS_DIMENSION': '1024',
        'DEMOGRAPHIC_WEIGHT': '0.5',
        'SUPABASE_URL': 'https://env.supabase.co'
    })
    def test_environment_variable_configuration(self):
        """Test that environment variables are used for configuration"""
        # This test verifies that the Flask app would use environment variables
        # when creating the service configuration
        
        # Simulate what the Flask app does
        service_config = {
            'faiss_dimension': int(os.environ.get('FAISS_DIMENSION', '2048')),
            'demographic_weight': float(os.environ.get('DEMOGRAPHIC_WEIGHT', '0.3')),
            'supabase_url': os.environ.get('SUPABASE_URL')
        }
        
        self.assertEqual(service_config['faiss_dimension'], 1024)
        self.assertEqual(service_config['demographic_weight'], 0.5)
        self.assertEqual(service_config['supabase_url'], 'https://env.supabase.co')
    
    def test_service_availability_validation(self):
        """Test service availability validation during initialization"""
        # Mock services with mixed availability
        with patch('app.service_manager.GoogleVisionService') as mock_vision, \
             patch('app.service_manager.ImageVectorizationService') as mock_vectorization, \
             patch('app.service_manager.FAISSService') as mock_faiss, \
             patch('app.service_manager.SupabaseService') as mock_supabase, \
             patch('app.service_manager.EnhancedSkinTypeClassifier') as mock_classifier, \
             patch('app.service_manager.DemographicWeightedSearch') as mock_demographic:
            
            # Mock some services as available, others as not
            mock_vision.return_value.is_available.return_value = True
            mock_vectorization.return_value.is_available.return_value = False
            mock_faiss.return_value.is_available.return_value = True
            mock_supabase.return_value.is_available.return_value = False
            mock_classifier.return_value.is_available.return_value = True
            mock_demographic.return_value.is_available.return_value = False
            
            # Mock demographic search methods
            mock_demographic.return_value.set_demographic_weight = Mock()
            mock_demographic.return_value.set_demographic_component_weights = Mock()
            
            # Initialize services
            self.service_manager.initialize_services()
            
            # Verify initialization completed despite some services being unavailable
            self.assertTrue(self.service_manager.is_initialized())
            
            # Check service status
            status = self.service_manager.get_service_status()
            self.assertTrue(status['google_vision'])
            self.assertFalse(status['vectorization'])
            self.assertTrue(status['faiss'])
            self.assertFalse(status['supabase'])
            self.assertTrue(status['skin_classifier'])
            self.assertFalse(status['demographic_search'])


if __name__ == '__main__':
    unittest.main()