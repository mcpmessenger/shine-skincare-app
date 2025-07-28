"""
Unit tests for SCIN Demographic Search Service
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import json
import tempfile
import os
from datetime import datetime, timedelta

# Import the service
from app.services.scin_demographic_search_service import (
    SCINDemographicSearchService, 
    DemographicProfile, 
    SkinConditionProfile
)


class TestSCINDemographicSearchService(unittest.TestCase):
    """Test cases for SCIN Demographic Search Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config = {
            'bucket_name': 'test-scin-bucket',
            'dataset_path': 'test_scin_data',
            'cache_duration': 1,  # 1 hour for testing
            'vector_dimension': 128  # Smaller dimension for testing
        }
        
        self.test_features = {
            'demographics': {
                'ethnicity': 'caucasian',
                'skin_type': 'normal',
                'age_range': '25-35'
            },
            'skin_conditions': ['acne', 'dryness'],
            'vector_embedding': np.random.rand(128).astype(np.float32)
        }
    
    @patch('app.services.scin_demographic_search_service.GOOGLE_CLOUD_AVAILABLE', False)
    @patch('app.services.scin_demographic_search_service.FAISS_AVAILABLE', False)
    def test_initialization_without_dependencies(self):
        """Test initialization when dependencies are not available"""
        service = SCINDemographicSearchService(self.test_config)
        
        self.assertEqual(service.bucket_name, 'test-scin-bucket')
        self.assertEqual(service.dataset_path, 'test_scin_data')
        self.assertEqual(service.cache_duration, 1)
        self.assertEqual(service.vector_dimension, 128)
        self.assertIsNone(service.storage_client)
        self.assertIsNone(service.faiss_index)
    
    @patch('app.services.scin_demographic_search_service.GOOGLE_CLOUD_AVAILABLE', True)
    @patch('app.services.scin_demographic_search_service.FAISS_AVAILABLE', True)
    @patch('app.services.scin_demographic_search_service.storage')
    @patch('app.services.scin_demographic_search_service.faiss')
    def test_initialization_with_dependencies(self, mock_faiss, mock_storage):
        """Test initialization when all dependencies are available"""
        # Mock Google Cloud Storage
        mock_client = Mock()
        mock_bucket = Mock()
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        
        # Mock FAISS
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/fake/path/creds.json'}):
            with patch('os.path.exists', return_value=True):
                service = SCINDemographicSearchService(self.test_config)
                
                self.assertIsNotNone(service.storage_client)
                self.assertIsNotNone(service.bucket)
                self.assertIsNotNone(service.faiss_index)
                mock_faiss.IndexFlatIP.assert_called_once_with(128)
    
    @patch('app.services.scin_demographic_search_service.GOOGLE_CLOUD_AVAILABLE', True)
    @patch('app.services.scin_demographic_search_service.storage')
    def test_connect_to_scin_dataset_success(self, mock_storage):
        """Test successful connection to SCIN dataset"""
        # Mock Google Cloud Storage
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [mock_blob]  # Non-empty list
        
        service = SCINDemographicSearchService(self.test_config)
        service.storage_client = mock_client
        service.bucket = mock_bucket
        
        # Mock the loading methods
        service._load_demographic_profiles = Mock()
        service._load_vector_embeddings = Mock()
        
        result = service.connect_to_scin_dataset()
        
        self.assertTrue(result)
        self.assertTrue(service._connected)
        self.assertIsNotNone(service._last_connection_attempt)
        service._load_demographic_profiles.assert_called_once()
        service._load_vector_embeddings.assert_called_once()
    
    def test_connect_to_scin_dataset_no_storage(self):
        """Test connection failure when storage is not available"""
        service = SCINDemographicSearchService(self.test_config)
        service.storage_client = None
        service.bucket = None
        
        result = service.connect_to_scin_dataset()
        
        self.assertFalse(result)
        self.assertFalse(service._connected)
    
    def test_generate_mock_profiles(self):
        """Test generation of mock demographic profiles"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        
        self.assertEqual(len(service.profile_cache), 50)
        
        # Check first profile structure
        first_profile = list(service.profile_cache.values())[0]
        self.assertIsInstance(first_profile, DemographicProfile)
        self.assertTrue(first_profile.profile_id.startswith('mock_profile_'))
        self.assertIn(first_profile.ethnicity, ['caucasian', 'african', 'asian', 'hispanic', 'middle_eastern', 'south_asian'])
        self.assertIn(first_profile.skin_type, ['oily', 'dry', 'combination', 'sensitive', 'normal'])
        self.assertIsInstance(first_profile.skin_conditions, list)
        self.assertEqual(first_profile.metadata['data_source'], 'mock')
    
    @patch('app.services.scin_demographic_search_service.FAISS_AVAILABLE', True)
    @patch('app.services.scin_demographic_search_service.faiss')
    def test_generate_mock_embeddings(self, mock_faiss):
        """Test generation of mock vector embeddings"""
        # Mock FAISS
        mock_index = Mock()
        mock_faiss.IndexFlatIP.return_value = mock_index
        mock_faiss.normalize_L2 = Mock()
        
        service = SCINDemographicSearchService(self.test_config)
        service.faiss_index = mock_index
        
        # Add some profiles first
        service._generate_mock_profiles()
        service._generate_mock_embeddings()
        
        # Verify FAISS operations were called
        mock_faiss.normalize_L2.assert_called_once()
        mock_index.add.assert_called_once()
        
        # Verify metadata mapping
        self.assertEqual(len(service.profile_metadata), len(service.profile_cache))
    
    def test_demographic_similarity_search(self):
        """Test demographic similarity search"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        
        # Test search
        results = service._demographic_similarity_search(self.test_features, k=5)
        
        self.assertLessEqual(len(results), 5)
        
        if results:
            # Check that results are sorted by similarity score
            for i in range(len(results) - 1):
                self.assertGreaterEqual(results[i].similarity_score, results[i + 1].similarity_score)
            
            # Check that all results have similarity scores
            for profile in results:
                self.assertIsInstance(profile.similarity_score, float)
                self.assertGreaterEqual(profile.similarity_score, 0.0)
                self.assertLessEqual(profile.similarity_score, 1.0)
    
    def test_calculate_demographic_similarity_perfect_match(self):
        """Test demographic similarity calculation with perfect match"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Create a profile that matches user demographics exactly
        profile = DemographicProfile(
            profile_id='test_profile',
            age_range='25-35',
            skin_type='normal',
            ethnicity='caucasian',
            geographic_region='north_america',
            skin_conditions=['acne', 'dryness'],
            similarity_score=0.0,
            scin_data_reference='test_ref',
            metadata={}
        )
        
        user_demographics = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_range': '25-35'
        }
        user_conditions = ['acne', 'dryness']
        
        similarity = service._calculate_demographic_similarity(
            user_demographics, user_conditions, profile
        )
        
        # Should be 1.0 for perfect match
        self.assertAlmostEqual(similarity, 1.0, places=3)
    
    def test_calculate_demographic_similarity_no_match(self):
        """Test demographic similarity calculation with no match"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Create a profile that doesn't match user demographics
        profile = DemographicProfile(
            profile_id='test_profile',
            age_range='55+',
            skin_type='oily',
            ethnicity='african',
            geographic_region='africa',
            skin_conditions=['rosacea', 'aging'],
            similarity_score=0.0,
            scin_data_reference='test_ref',
            metadata={}
        )
        
        user_demographics = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_range': '25-35'
        }
        user_conditions = ['acne', 'dryness']
        
        similarity = service._calculate_demographic_similarity(
            user_demographics, user_conditions, profile
        )
        
        # Should be 0.0 for no match
        self.assertAlmostEqual(similarity, 0.0, places=3)
    
    def test_calculate_demographic_similarity_partial_match(self):
        """Test demographic similarity calculation with partial match"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Create a profile that partially matches user demographics
        profile = DemographicProfile(
            profile_id='test_profile',
            age_range='25-35',  # Match
            skin_type='oily',   # No match
            ethnicity='caucasian',  # Match
            geographic_region='europe',
            skin_conditions=['acne'],  # Partial match
            similarity_score=0.0,
            scin_data_reference='test_ref',
            metadata={}
        )
        
        user_demographics = {
            'ethnicity': 'caucasian',
            'skin_type': 'normal',
            'age_range': '25-35'
        }
        user_conditions = ['acne', 'dryness']
        
        similarity = service._calculate_demographic_similarity(
            user_demographics, user_conditions, profile
        )
        
        # Should be between 0 and 1
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)
    
    def test_age_ranges_overlap(self):
        """Test age range overlap detection"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Test overlapping ranges
        self.assertTrue(service._age_ranges_overlap('25-35', '30-40'))
        self.assertTrue(service._age_ranges_overlap('18-25', '25-35'))
        
        # Test non-overlapping ranges
        self.assertFalse(service._age_ranges_overlap('18-25', '35-45'))
        self.assertFalse(service._age_ranges_overlap('25-35', '45-55'))
        
        # Test with plus ranges
        self.assertTrue(service._age_ranges_overlap('55+', '45-55'))
        self.assertTrue(service._age_ranges_overlap('55+', '60-70'))
        
        # Test identical ranges
        self.assertTrue(service._age_ranges_overlap('25-35', '25-35'))
    
    @patch('app.services.scin_demographic_search_service.FAISS_AVAILABLE', True)
    @patch('app.services.scin_demographic_search_service.faiss')
    def test_vector_similarity_search(self, mock_faiss):
        """Test vector similarity search"""
        # Mock FAISS
        mock_index = Mock()
        mock_index.ntotal = 10
        mock_index.search.return_value = (
            np.array([[0.9, 0.8, 0.7]]),  # scores
            np.array([[0, 1, 2]])         # indices
        )
        mock_faiss.normalize_L2 = Mock()
        
        service = SCINDemographicSearchService(self.test_config)
        service.faiss_index = mock_index
        
        # Add some profiles and metadata
        service._generate_mock_profiles()
        profile_ids = list(service.profile_cache.keys())[:3]
        for i, profile_id in enumerate(profile_ids):
            service.profile_metadata[i] = profile_id
        
        # Test search
        query_vector = np.random.rand(128).astype(np.float32)
        results = service._vector_similarity_search(query_vector, k=3)
        
        self.assertEqual(len(results), 3)
        
        # Check that results are properly formatted
        for result in results:
            self.assertIsInstance(result, DemographicProfile)
            self.assertGreater(result.similarity_score, 0.0)
        
        # Verify FAISS operations
        mock_faiss.normalize_L2.assert_called_once()
        mock_index.search.assert_called_once()
    
    def test_search_similar_profiles_combined(self):
        """Test combined search using both vector and demographic similarity"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        
        # Test search without vector embedding (demographic only)
        features_no_vector = {
            'demographics': {
                'ethnicity': 'caucasian',
                'skin_type': 'normal',
                'age_range': '25-35'
            },
            'skin_conditions': ['acne']
        }
        
        results = service.search_similar_profiles(features_no_vector, k=5)
        
        self.assertLessEqual(len(results), 5)
        
        if results:
            # Check that results are sorted by similarity score
            for i in range(len(results) - 1):
                self.assertGreaterEqual(results[i].similarity_score, results[i + 1].similarity_score)
    
    def test_get_demographic_insights(self):
        """Test getting demographic insights for a profile"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        
        # Get insights for first profile
        profile_id = list(service.profile_cache.keys())[0]
        insights = service.get_demographic_insights(profile_id)
        
        self.assertIn('profile_id', insights)
        self.assertIn('demographics', insights)
        self.assertIn('skin_conditions', insights)
        self.assertIn('insights', insights)
        
        # Check insights structure
        profile_insights = insights['insights']
        self.assertIn('common_conditions', profile_insights)
        self.assertIn('recommended_treatments', profile_insights)
        self.assertIn('demographic_prevalence', profile_insights)
        self.assertIn('risk_factors', profile_insights)
    
    def test_get_demographic_insights_nonexistent_profile(self):
        """Test getting insights for non-existent profile"""
        service = SCINDemographicSearchService(self.test_config)
        
        insights = service.get_demographic_insights('nonexistent_profile')
        
        self.assertEqual(insights, {})
    
    def test_get_treatment_recommendations(self):
        """Test getting treatment recommendations for conditions"""
        service = SCINDemographicSearchService(self.test_config)
        
        profile = DemographicProfile(
            profile_id='test',
            age_range='25-35',
            skin_type='normal',
            ethnicity='caucasian',
            geographic_region='north_america',
            skin_conditions=[],
            similarity_score=0.0,
            scin_data_reference='test',
            metadata={}
        )
        
        # Test known conditions
        acne_treatments = service._get_treatment_recommendations('acne', profile)
        self.assertIn('salicylic acid cleanser', acne_treatments)
        
        dryness_treatments = service._get_treatment_recommendations('dryness', profile)
        self.assertIn('hyaluronic acid serum', dryness_treatments)
        
        # Test unknown condition
        unknown_treatments = service._get_treatment_recommendations('unknown_condition', profile)
        self.assertIn('consult dermatologist', unknown_treatments)
    
    def test_cache_functionality(self):
        """Test caching of search results"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        
        # Perform search
        results1 = service.search_similar_profiles(self.test_features, k=3)
        
        # Check that results are cached
        cache_key = service._generate_cache_key(self.test_features, 3)
        self.assertIn(cache_key, service.search_cache)
        self.assertIn(cache_key, service.cache_timestamps)
        
        # Perform same search again
        results2 = service.search_similar_profiles(self.test_features, k=3)
        
        # Results should be identical (from cache)
        self.assertEqual(len(results1), len(results2))
        if results1:
            self.assertEqual(results1[0].profile_id, results2[0].profile_id)
    
    def test_cache_expiry(self):
        """Test cache expiry functionality"""
        service = SCINDemographicSearchService(self.test_config)
        service.cache_duration = 0.001  # Very short cache duration (0.001 hours)
        
        cache_key = 'test_key'
        service.search_cache[cache_key] = []
        service.cache_timestamps[cache_key] = datetime.utcnow() - timedelta(hours=1)  # Expired
        
        self.assertFalse(service._is_cache_valid(cache_key))
        
        # Test valid cache
        service.cache_timestamps[cache_key] = datetime.utcnow()
        self.assertTrue(service._is_cache_valid(cache_key))
    
    def test_clear_cache(self):
        """Test clearing cache"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Add some cache data
        service.search_cache['test_key'] = []
        service.cache_timestamps['test_key'] = datetime.utcnow()
        
        service.clear_cache()
        
        self.assertEqual(len(service.search_cache), 0)
        self.assertEqual(len(service.cache_timestamps), 0)
    
    def test_is_available(self):
        """Test service availability check"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Initially not available (not connected, no profiles)
        self.assertFalse(service.is_available())
        
        # Add profiles and set connected
        service._generate_mock_profiles()
        service._connected = True
        
        self.assertTrue(service.is_available())
    
    def test_get_service_status(self):
        """Test getting service status"""
        service = SCINDemographicSearchService(self.test_config)
        service._generate_mock_profiles()
        service._connected = True
        service._last_connection_attempt = datetime.utcnow()
        
        status = service.get_service_status()
        
        self.assertIn('connected', status)
        self.assertIn('last_connection_attempt', status)
        self.assertIn('profiles_loaded', status)
        self.assertIn('faiss_index_size', status)
        self.assertIn('cache_entries', status)
        self.assertIn('google_cloud_available', status)
        self.assertIn('faiss_available', status)
        self.assertIn('bucket_name', status)
        self.assertIn('dataset_path', status)
        
        self.assertTrue(status['connected'])
        self.assertEqual(status['profiles_loaded'], 50)
        self.assertEqual(status['bucket_name'], 'test-scin-bucket')
    
    def test_get_configuration(self):
        """Test getting service configuration"""
        service = SCINDemographicSearchService(self.test_config)
        
        config = service.get_configuration()
        
        self.assertIn('bucket_name', config)
        self.assertIn('dataset_path', config)
        self.assertIn('cache_duration', config)
        self.assertIn('vector_dimension', config)
        self.assertIn('service_status', config)
        
        self.assertEqual(config['bucket_name'], 'test-scin-bucket')
        self.assertEqual(config['dataset_path'], 'test_scin_data')
        self.assertEqual(config['cache_duration'], 1)
        self.assertEqual(config['vector_dimension'], 128)
    
    def test_generate_cache_key(self):
        """Test cache key generation"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Same features should generate same key
        key1 = service._generate_cache_key(self.test_features, 5)
        key2 = service._generate_cache_key(self.test_features, 5)
        self.assertEqual(key1, key2)
        
        # Different k should generate different key
        key3 = service._generate_cache_key(self.test_features, 10)
        self.assertNotEqual(key1, key3)
        
        # Different features should generate different key
        different_features = self.test_features.copy()
        different_features['demographics']['ethnicity'] = 'asian'
        key4 = service._generate_cache_key(different_features, 5)
        self.assertNotEqual(key1, key4)
    
    def test_error_handling_in_search(self):
        """Test error handling during search operations"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Test search with invalid features
        invalid_features = {'invalid': 'data'}
        results = service.search_similar_profiles(invalid_features, k=5)
        
        # Should return empty list without crashing
        self.assertEqual(results, [])
    
    def test_error_handling_in_demographic_calculation(self):
        """Test error handling in demographic similarity calculation"""
        service = SCINDemographicSearchService(self.test_config)
        
        # Test with None values
        similarity = service._calculate_demographic_similarity(None, None, None)
        self.assertEqual(similarity, 0.0)
        
        # Test with invalid profile
        invalid_profile = "not_a_profile"
        similarity = service._calculate_demographic_similarity({}, [], invalid_profile)
        self.assertEqual(similarity, 0.0)


if __name__ == '__main__':
    unittest.main()