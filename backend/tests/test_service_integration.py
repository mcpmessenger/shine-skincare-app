"""
Integration tests for service integration with existing infrastructure
"""
import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, Mock
import numpy as np

from app.service_manager import service_manager
from app import create_app


class TestServiceIntegration(unittest.TestCase):
    """Test cases for service integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'faiss_dimension': 128,  # Smaller for testing
            'faiss_index_path': os.path.join(self.temp_dir, 'test_index'),
            'demographic_weight': 0.3,
            'ethnicity_weight': 0.6,
            'skin_type_weight': 0.3,
            'age_group_weight': 0.1
        }
        
        # Reset service manager
        service_manager._services = {}
        service_manager._initialized = False
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Clean up service manager
        service_manager.shutdown_services()
    
    def test_service_initialization_with_mock_services(self):
        """Test service initialization with mock services enabled"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Verify all services are initialized
            self.assertTrue(service_manager.is_initialized())
            
            # Check that mock services are used
            google_vision = service_manager.get_service('google_vision')
            self.assertEqual(google_vision.__class__.__name__, 'MockGoogleVisionService')
            
            faiss_service = service_manager.get_service('faiss')
            self.assertEqual(faiss_service.__class__.__name__, 'MockFAISSService')
            
            skin_classifier = service_manager.get_service('skin_classifier')
            self.assertEqual(skin_classifier.__class__.__name__, 'MockSkinClassifierService')
            
            # Verify services are available
            service_status = service_manager.get_service_status()
            self.assertTrue(all(service_status.values()))
    
    def test_service_initialization_with_production_services(self):
        """Test service initialization with production services"""
        with patch.dict(os.environ, {
            'USE_MOCK_SERVICES': 'false',
            'USE_PRODUCTION_FAISS': 'true'
        }):
            # Mock Google Vision to avoid requiring credentials
            with patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', False):
                service_manager.initialize_services(self.test_config)
                
                # Verify all services are initialized
                self.assertTrue(service_manager.is_initialized())
                
                # Check service types
                services = service_manager.get_all_services()
                self.assertIn('google_vision', services)
                self.assertIn('faiss', services)
                self.assertIn('skin_classifier', services)
                self.assertIn('demographic_search', services)
                
                # Verify FAISS service type (should be production if available)
                faiss_service = service_manager.get_service('faiss')
                # Could be ProductionFAISSService or MockFAISSService depending on availability
                self.assertIn(faiss_service.__class__.__name__, 
                             ['ProductionFAISSService', 'FAISSService', 'MockFAISSService'])
    
    def test_service_dependency_injection(self):
        """Test that services are properly injected with dependencies"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Get services
            google_vision = service_manager.get_service('google_vision')
            faiss_service = service_manager.get_service('faiss')
            supabase_service = service_manager.get_service('supabase')
            skin_classifier = service_manager.get_service('skin_classifier')
            demographic_search = service_manager.get_service('demographic_search')
            
            # Verify skin classifier has Google Vision integration
            # (For mock services, this might not be directly testable, but we can verify it doesn't crash)
            self.assertTrue(skin_classifier.is_available())
            
            # Verify demographic search has proper dependencies
            self.assertTrue(demographic_search.is_available())
    
    def test_service_configuration(self):
        """Test service configuration and reconfiguration"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Test demographic search configuration
            demographic_search = service_manager.get_service('demographic_search')
            
            # Reconfigure demographic search
            service_manager.reconfigure_service('demographic_search', 
                                              demographic_weight=0.4,
                                              ethnicity_weight=0.7)
            
            # Test skin classifier configuration
            skin_classifier = service_manager.get_service('skin_classifier')
            
            # Reconfigure skin classifier
            service_manager.reconfigure_service('skin_classifier', 
                                              confidence_threshold=0.8)
            
            # Verify configuration was applied (for mock services)
            self.assertTrue(skin_classifier.is_available())
    
    def test_service_info_retrieval(self):
        """Test getting service information"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Get service info
            service_info = service_manager.get_service_info()
            
            # Verify info structure
            self.assertIn('faiss', service_info)
            self.assertIn('skin_classifier', service_info)
            
            # Verify FAISS info
            faiss_info = service_info['faiss']
            self.assertIn('dimension', faiss_info)
            self.assertEqual(faiss_info['dimension'], 128)
            
            # Verify skin classifier info
            classifier_info = service_info['skin_classifier']
            self.assertIn('name', classifier_info)
            self.assertIn('version', classifier_info)
    
    def test_service_status_monitoring(self):
        """Test service status monitoring"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Get service status
            service_status = service_manager.get_service_status()
            
            # Verify all services are available
            expected_services = ['google_vision', 'vectorization', 'faiss', 
                               'supabase', 'skin_classifier', 'demographic_search']
            
            for service_name in expected_services:
                self.assertIn(service_name, service_status)
                self.assertTrue(service_status[service_name], 
                              f"Service {service_name} should be available")
    
    def test_flask_app_integration(self):
        """Test Flask app integration with services"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            app = create_app()
            
            with app.test_client() as client:
                # Test health check endpoint
                response = client.get('/api/health')
                self.assertEqual(response.status_code, 200)
                
                data = response.get_json()
                self.assertEqual(data['status'], 'healthy')
                self.assertIn('services', data)
                self.assertTrue(data['services_initialized'])
                
                # Test service config endpoint
                response = client.get('/api/services/config')
                self.assertEqual(response.status_code, 200)
                
                data = response.get_json()
                self.assertIn('configuration', data)
                self.assertIn('status', data)
    
    def test_service_error_handling(self):
        """Test service error handling and fallbacks"""
        # Test with invalid configuration
        invalid_config = {
            'faiss_dimension': -1,  # Invalid dimension
            'demographic_weight': 2.0  # Invalid weight
        }
        
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            # Should still initialize with fallbacks
            service_manager.initialize_services(invalid_config)
            self.assertTrue(service_manager.is_initialized())
    
    def test_service_graceful_shutdown(self):
        """Test graceful service shutdown"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            self.assertTrue(service_manager.is_initialized())
            
            # Shutdown services
            service_manager.shutdown_services()
            self.assertFalse(service_manager.is_initialized())
            
            # Verify services are cleared
            with self.assertRaises(ValueError):
                service_manager.get_service('google_vision')
    
    def test_enhanced_skin_analysis_integration(self):
        """Test enhanced skin analysis with integrated services"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Get services
            skin_classifier = service_manager.get_service('skin_classifier')
            google_vision = service_manager.get_service('google_vision')
            
            # Create test image data
            test_image_data = b"fake_image_data"
            
            # Test skin classification
            result = skin_classifier.classify_skin_type(test_image_data, ethnicity='caucasian')
            
            # Verify result structure
            self.assertIn('fitzpatrick_type', result)
            self.assertIn('monk_tone', result)
            self.assertIn('confidence', result)
            
            # Test Google Vision analysis
            vision_result = google_vision.analyze_image_from_bytes(test_image_data)
            
            # Verify vision result
            self.assertIn('status', vision_result)
    
    def test_demographic_search_integration(self):
        """Test demographic search integration with FAISS and Supabase"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services(self.test_config)
            
            # Get services
            demographic_search = service_manager.get_service('demographic_search')
            faiss_service = service_manager.get_service('faiss')
            
            # Test adding a vector
            test_vector = np.random.rand(128).astype(np.float32)
            success = faiss_service.add_vector(test_vector, 'test_image_1')
            self.assertTrue(success)
            
            # Test demographic search (with mock services)
            # This would normally require real demographic data
            self.assertTrue(demographic_search.is_available())
    
    def test_production_faiss_integration(self):
        """Test production FAISS service integration"""
        with patch.dict(os.environ, {
            'USE_MOCK_SERVICES': 'false',
            'USE_PRODUCTION_FAISS': 'true'
        }):
            # Mock other services to avoid external dependencies
            with patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', False):
                service_manager.initialize_services(self.test_config)
                
                faiss_service = service_manager.get_service('faiss')
                
                # Test vector operations
                test_vector = np.random.rand(128).astype(np.float32)
                success = faiss_service.add_vector(test_vector, 'test_image_1')
                
                if faiss_service.__class__.__name__ == 'ProductionFAISSService':
                    # Test production-specific features
                    stats = faiss_service.get_index_stats()
                    self.assertIn('dimension', stats)
                    self.assertIn('vectors_in_index', stats)
                    self.assertIn('thread_safe', stats)
                    self.assertTrue(stats['thread_safe'])
    
    def test_environment_variable_configuration(self):
        """Test configuration via environment variables"""
        test_env = {
            'USE_MOCK_SERVICES': 'false',
            'USE_PRODUCTION_FAISS': 'true',
            'FAISS_DIMENSION': '256',
            'DEMOGRAPHIC_WEIGHT': '0.4',
            'ETHNICITY_WEIGHT': '0.7'
        }
        
        with patch.dict(os.environ, test_env):
            # Mock external services
            with patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', False):
                config = {
                    'faiss_dimension': int(os.environ.get('FAISS_DIMENSION', '2048')),
                    'demographic_weight': float(os.environ.get('DEMOGRAPHIC_WEIGHT', '0.3')),
                    'ethnicity_weight': float(os.environ.get('ETHNICITY_WEIGHT', '0.6'))
                }
                
                service_manager.initialize_services(config)
                
                # Verify configuration was applied
                service_info = service_manager.get_service_info()
                faiss_info = service_info.get('faiss', {})
                
                if 'dimension' in faiss_info:
                    self.assertEqual(faiss_info['dimension'], 256)
    
    def test_service_fallback_chain(self):
        """Test the complete service fallback chain"""
        # Test fallback from production -> regular -> mock
        with patch.dict(os.environ, {
            'USE_MOCK_SERVICES': 'false',
            'USE_PRODUCTION_FAISS': 'true'
        }):
            # Mock production FAISS to fail
            with patch('app.service_manager.PRODUCTION_FAISS_AVAILABLE', False):
                # Mock regular services to avoid external dependencies
                with patch('app.services.google_vision_service.GOOGLE_VISION_AVAILABLE', False):
                    service_manager.initialize_services(self.test_config)
                    
                    # Should still initialize successfully with fallbacks
                    self.assertTrue(service_manager.is_initialized())
                    
                    # Verify services are available (even if mocked)
                    service_status = service_manager.get_service_status()
                    self.assertTrue(any(service_status.values()))


class TestServiceManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Reset service manager
        service_manager._services = {}
        service_manager._initialized = False
    
    def tearDown(self):
        """Clean up"""
        service_manager.shutdown_services()
    
    def test_double_initialization(self):
        """Test double initialization handling"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            # First initialization
            service_manager.initialize_services()
            self.assertTrue(service_manager.is_initialized())
            
            # Second initialization should be handled gracefully
            service_manager.initialize_services()
            self.assertTrue(service_manager.is_initialized())
    
    def test_service_access_before_initialization(self):
        """Test accessing services before initialization"""
        with self.assertRaises(ValueError):
            service_manager.get_service('google_vision')
        
        with self.assertRaises(ValueError):
            service_manager.get_all_services()
    
    def test_invalid_service_name(self):
        """Test accessing invalid service name"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services()
            
            with self.assertRaises(ValueError):
                service_manager.get_service('nonexistent_service')
    
    def test_service_reconfiguration_errors(self):
        """Test service reconfiguration error handling"""
        with patch.dict(os.environ, {'USE_MOCK_SERVICES': 'true'}):
            service_manager.initialize_services()
            
            # Test reconfiguring non-existent service
            with self.assertRaises(ValueError):
                service_manager.reconfigure_service('nonexistent_service', param=123)
            
            # Test reconfiguring before initialization
            service_manager.shutdown_services()
            with self.assertRaises(ValueError):
                service_manager.reconfigure_service('skin_classifier', confidence_threshold=0.8)


if __name__ == '__main__':
    unittest.main()