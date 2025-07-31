"""
SCIN Dataset Demographic Search Service

This service provides demographic search capabilities using the SCIN (Skin Condition Image Network) dataset
for dermatological research and skin analysis recommendations.
"""
import logging
import numpy as np
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import tempfile
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import Google Cloud Storage for SCIN dataset access
try:
    from google.cloud import storage
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud Storage library not available. SCIN dataset access will be limited.")
    GOOGLE_CLOUD_AVAILABLE = False
    storage = None

# Try to import FAISS for vector similarity search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS library not available. Vector search will be disabled.")
    FAISS_AVAILABLE = False
    faiss = None


@dataclass
class DemographicProfile:
    """Demographic profile data structure"""
    profile_id: str
    age_range: str
    skin_type: str
    ethnicity: str
    geographic_region: str
    skin_conditions: List[str]
    similarity_score: float
    scin_data_reference: str
    metadata: Dict[str, Any]


@dataclass
class SkinConditionProfile:
    """Skin condition profile from SCIN dataset"""
    condition_id: str
    condition_name: str
    severity: str
    affected_areas: List[str]
    demographic_data: Dict[str, Any]
    treatment_recommendations: List[str]
    vector_embedding: Optional[np.ndarray]


class SCINDemographicSearchService:
    """
    Service for demographic search using the SCIN dataset with caching and optimization
    """
    
    def __init__(self, scin_config: Dict[str, Any]):
        """
        Initialize the SCIN demographic search service
        
        Args:
            scin_config: Configuration dictionary containing:
                - bucket_name: Google Cloud Storage bucket name
                - dataset_path: Path to SCIN dataset in bucket
                - cache_duration: Cache duration in hours (default: 24)
                - vector_dimension: Dimension of vector embeddings (default: 2048)
        """
        self.scin_config = scin_config
        self.bucket_name = scin_config.get('bucket_name', 'scin-dataset')
        self.dataset_path = scin_config.get('dataset_path', 'scin_data')
        self.cache_duration = scin_config.get('cache_duration', 24)  # hours
        self.vector_dimension = scin_config.get('vector_dimension', 2048)
        
        # Initialize Google Cloud Storage client
        self.storage_client = None
        self.bucket = None
        self._initialize_storage_client()
        
        # Initialize FAISS index for vector similarity search
        self.faiss_index = None
        self.profile_metadata = {}  # Maps FAISS index IDs to profile metadata
        self._initialize_faiss_index()
        
        # Cache for demographic profiles and search results
        self.profile_cache = {}
        self.search_cache = {}
        self.cache_timestamps = {}
        
        # Connection status
        self._connected = False
        self._last_connection_attempt = None
        
        logger.info(f"Initialized SCIN Demographic Search Service with bucket: {self.bucket_name}")
    
    def _initialize_storage_client(self):
        """Initialize Google Cloud Storage client with authentication"""
        if not GOOGLE_CLOUD_AVAILABLE:
            logger.warning("Google Cloud Storage not available")
            return
        
        try:
            # Try to authenticate using various methods
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                # Use JSON content from environment variable
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(credentials_json)
                    temp_credentials_path = f.name
                
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_credentials_path
                self.storage_client = storage.Client()
                logger.info("Authenticated with Google Cloud Storage using JSON credentials")
                
            elif credentials_path and os.path.exists(credentials_path):
                # Use file path
                self.storage_client = storage.Client()
                logger.info(f"Authenticated with Google Cloud Storage using file: {credentials_path}")
                
            else:
                # Try default authentication
                self.storage_client = storage.Client()
                logger.info("Authenticated with Google Cloud Storage using default credentials")
            
            # Get bucket reference
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage client: {e}")
            self.storage_client = None
            self.bucket = None
    
    def _initialize_faiss_index(self):
        """Initialize FAISS index for vector similarity search"""
        if not FAISS_AVAILABLE:
            logger.warning("FAISS not available for vector search")
            return
        
        try:
            # Create a flat index for exact similarity search
            self.faiss_index = faiss.IndexFlatIP(self.vector_dimension)  # Inner product for cosine similarity
            logger.info(f"Initialized FAISS index with dimension {self.vector_dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            self.faiss_index = None
    
    def connect_to_scin_dataset(self) -> bool:
        """
        Establish connection to the SCIN dataset and load initial data
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to SCIN dataset...")
            
            if not self.storage_client or not self.bucket:
                logger.error("Google Cloud Storage not properly initialized")
                return False
            
            # Test connection by listing dataset contents
            blobs = list(self.bucket.list_blobs(prefix=self.dataset_path, max_results=10))
            
            if not blobs:
                logger.warning(f"No data found in SCIN dataset path: {self.dataset_path}")
                return False
            
            logger.info(f"Successfully connected to SCIN dataset. Found {len(blobs)} files.")
            
            # Load demographic profiles and vector embeddings
            self._load_demographic_profiles()
            self._load_vector_embeddings()
            
            self._connected = True
            self._last_connection_attempt = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SCIN dataset: {e}")
            self._connected = False
            self._last_connection_attempt = datetime.utcnow()
            return False
    
    def _load_demographic_profiles(self):
        """Load demographic profiles from SCIN dataset"""
        try:
            # Look for demographic profiles file
            profiles_blob_name = f"{self.dataset_path}/demographic_profiles.json"
            
            try:
                blob = self.bucket.blob(profiles_blob_name)
                profiles_data = json.loads(blob.download_as_text())
                
                for profile_data in profiles_data.get('profiles', []):
                    profile = DemographicProfile(
                        profile_id=profile_data.get('id', ''),
                        age_range=profile_data.get('age_range', ''),
                        skin_type=profile_data.get('skin_type', ''),
                        ethnicity=profile_data.get('ethnicity', ''),
                        geographic_region=profile_data.get('geographic_region', ''),
                        skin_conditions=profile_data.get('skin_conditions', []),
                        similarity_score=0.0,  # Will be calculated during search
                        scin_data_reference=profile_data.get('reference', ''),
                        metadata=profile_data.get('metadata', {})
                    )
                    
                    self.profile_cache[profile.profile_id] = profile
                
                logger.info(f"Loaded {len(self.profile_cache)} demographic profiles from SCIN dataset")
                
            except Exception as e:
                logger.warning(f"Could not load demographic profiles: {e}")
                # Generate mock profiles for testing
                self._generate_mock_profiles()
                
        except Exception as e:
            logger.error(f"Error loading demographic profiles: {e}")
    
    def _load_vector_embeddings(self):
        """Load vector embeddings for demographic profiles"""
        if not self.faiss_index:
            logger.warning("FAISS index not available for loading embeddings")
            return
        
        try:
            # Look for vector embeddings file
            embeddings_blob_name = f"{self.dataset_path}/profile_embeddings.npy"
            
            try:
                blob = self.bucket.blob(embeddings_blob_name)
                
                # Download to temporary file
                with tempfile.NamedTemporaryFile() as temp_file:
                    blob.download_to_filename(temp_file.name)
                    embeddings = np.load(temp_file.name)
                
                # Add embeddings to FAISS index
                if embeddings.shape[1] == self.vector_dimension:
                    # Normalize vectors for cosine similarity
                    faiss.normalize_L2(embeddings)
                    self.faiss_index.add(embeddings)
                    
                    # Create mapping from FAISS index to profile IDs
                    profile_ids = list(self.profile_cache.keys())[:len(embeddings)]
                    for i, profile_id in enumerate(profile_ids):
                        self.profile_metadata[i] = profile_id
                    
                    logger.info(f"Loaded {len(embeddings)} vector embeddings into FAISS index")
                else:
                    logger.error(f"Embedding dimension mismatch: expected {self.vector_dimension}, got {embeddings.shape[1]}")
                    
            except Exception as e:
                logger.warning(f"Could not load vector embeddings: {e}")
                # Generate mock embeddings for testing
                self._generate_mock_embeddings()
                
        except Exception as e:
            logger.error(f"Error loading vector embeddings: {e}")
    
    def _generate_mock_profiles(self):
        """Generate mock demographic profiles for testing"""
        logger.info("Generating mock demographic profiles for testing")
        
        ethnicities = ['caucasian', 'african', 'asian', 'hispanic', 'middle_eastern', 'south_asian']
        skin_types = ['oily', 'dry', 'combination', 'sensitive', 'normal']
        age_ranges = ['18-25', '26-35', '36-45', '46-55', '55+']
        regions = ['north_america', 'europe', 'asia', 'africa', 'south_america', 'oceania']
        conditions = ['acne', 'dryness', 'hyperpigmentation', 'rosacea', 'eczema', 'aging']
        
        for i in range(50):  # Generate 50 mock profiles
            profile = DemographicProfile(
                profile_id=f"mock_profile_{i:03d}",
                age_range=age_ranges[i % len(age_ranges)],
                skin_type=skin_types[i % len(skin_types)],
                ethnicity=ethnicities[i % len(ethnicities)],
                geographic_region=regions[i % len(regions)],
                skin_conditions=[conditions[j % len(conditions)] for j in range(i % 3 + 1)],
                similarity_score=0.0,
                scin_data_reference=f"scin_ref_{i:03d}",
                metadata={
                    'data_source': 'mock',
                    'created_at': datetime.utcnow().isoformat(),
                    'confidence': 0.8
                }
            )
            
            self.profile_cache[profile.profile_id] = profile
        
        logger.info(f"Generated {len(self.profile_cache)} mock demographic profiles")
    
    def _generate_mock_embeddings(self):
        """Generate mock vector embeddings for testing"""
        if not self.faiss_index:
            return
        
        logger.info("Generating mock vector embeddings for testing")
        
        num_profiles = len(self.profile_cache)
        if num_profiles == 0:
            return
        
        # Generate random normalized embeddings
        embeddings = np.random.randn(num_profiles, self.vector_dimension).astype(np.float32)
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.faiss_index.add(embeddings)
        
        # Create mapping
        for i, profile_id in enumerate(self.profile_cache.keys()):
            self.profile_metadata[i] = profile_id
        
        logger.info(f"Generated {num_profiles} mock vector embeddings")
    
    def search_similar_profiles(self, features: Dict[str, Any], k: int = 10) -> List[DemographicProfile]:
        """
        Search for similar demographic profiles based on features
        
        Args:
            features: Dictionary containing:
                - skin_conditions: List of detected skin conditions
                - demographics: Dict with age_range, ethnicity, skin_type
                - vector_embedding: Optional numpy array for vector similarity
            k: Number of similar profiles to return
            
        Returns:
            List of similar demographic profiles with similarity scores
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(features, k)
            if self._is_cache_valid(cache_key):
                logger.debug("Returning cached search results")
                return self.search_cache[cache_key]
            
            similar_profiles = []
            
            # Use vector similarity if available
            if 'vector_embedding' in features and self.faiss_index and self.faiss_index.ntotal > 0:
                similar_profiles = self._vector_similarity_search(features['vector_embedding'], k)
            
            # If vector search didn't return enough results, use demographic matching
            if len(similar_profiles) < k:
                remaining_k = k - len(similar_profiles)
                demographic_profiles = self._demographic_similarity_search(features, remaining_k)
                
                # Merge results, avoiding duplicates
                existing_ids = {p.profile_id for p in similar_profiles}
                for profile in demographic_profiles:
                    if profile.profile_id not in existing_ids:
                        similar_profiles.append(profile)
                        if len(similar_profiles) >= k:
                            break
            
            # Sort by similarity score (descending)
            similar_profiles.sort(key=lambda p: p.similarity_score, reverse=True)
            
            # Cache results
            self.search_cache[cache_key] = similar_profiles[:k]
            self.cache_timestamps[cache_key] = datetime.utcnow()
            
            logger.info(f"Found {len(similar_profiles)} similar profiles")
            return similar_profiles[:k]
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def _vector_similarity_search(self, query_vector: np.ndarray, k: int) -> List[DemographicProfile]:
        """Perform vector similarity search using FAISS"""
        try:
            if not self.faiss_index or self.faiss_index.ntotal == 0:
                return []
            
            # Normalize query vector
            query_vector = query_vector.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search
            scores, indices = self.faiss_index.search(query_vector, min(k, self.faiss_index.ntotal))
            
            profiles = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                profile_id = self.profile_metadata.get(idx)
                if profile_id and profile_id in self.profile_cache:
                    profile = self.profile_cache[profile_id]
                    # Create a copy with updated similarity score
                    similar_profile = DemographicProfile(
                        profile_id=profile.profile_id,
                        age_range=profile.age_range,
                        skin_type=profile.skin_type,
                        ethnicity=profile.ethnicity,
                        geographic_region=profile.geographic_region,
                        skin_conditions=profile.skin_conditions,
                        similarity_score=float(score),
                        scin_data_reference=profile.scin_data_reference,
                        metadata=profile.metadata
                    )
                    profiles.append(similar_profile)
            
            logger.debug(f"Vector search returned {len(profiles)} profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            return []
    
    def _demographic_similarity_search(self, features: Dict[str, Any], k: int) -> List[DemographicProfile]:
        """Perform demographic similarity search based on categorical features"""
        try:
            demographics = features.get('demographics', {})
            skin_conditions = features.get('skin_conditions', [])
            
            scored_profiles = []
            
            for profile in self.profile_cache.values():
                similarity_score = self._calculate_demographic_similarity(
                    demographics, skin_conditions, profile
                )
                
                if similarity_score > 0:  # Only include profiles with some similarity
                    # Create a copy with similarity score
                    similar_profile = DemographicProfile(
                        profile_id=profile.profile_id,
                        age_range=profile.age_range,
                        skin_type=profile.skin_type,
                        ethnicity=profile.ethnicity,
                        geographic_region=profile.geographic_region,
                        skin_conditions=profile.skin_conditions,
                        similarity_score=similarity_score,
                        scin_data_reference=profile.scin_data_reference,
                        metadata=profile.metadata
                    )
                    scored_profiles.append(similar_profile)
            
            # Sort by similarity score and return top k
            scored_profiles.sort(key=lambda p: p.similarity_score, reverse=True)
            
            logger.debug(f"Demographic search returned {len(scored_profiles[:k])} profiles")
            return scored_profiles[:k]
            
        except Exception as e:
            logger.error(f"Error in demographic similarity search: {e}")
            return []
    
    def _calculate_demographic_similarity(self, user_demographics: Dict[str, Any], 
                                        user_conditions: List[str], 
                                        profile: DemographicProfile) -> float:
        """Calculate similarity score between user and profile demographics"""
        try:
            similarity = 0.0
            total_weight = 0.0
            
            # Ethnicity similarity (weight: 0.4)
            if user_demographics.get('ethnicity') and profile.ethnicity:
                weight = 0.4
                if user_demographics['ethnicity'].lower() == profile.ethnicity.lower():
                    similarity += weight
                total_weight += weight
            
            # Skin type similarity (weight: 0.3)
            if user_demographics.get('skin_type') and profile.skin_type:
                weight = 0.3
                if user_demographics['skin_type'].lower() == profile.skin_type.lower():
                    similarity += weight
                total_weight += weight
            
            # Age range similarity (weight: 0.2)
            if user_demographics.get('age_range') and profile.age_range:
                weight = 0.2
                if user_demographics['age_range'] == profile.age_range:
                    similarity += weight
                elif self._age_ranges_overlap(user_demographics['age_range'], profile.age_range):
                    similarity += weight * 0.5  # Partial match for overlapping ranges
                total_weight += weight
            
            # Skin conditions similarity (weight: 0.1)
            if user_conditions and profile.skin_conditions:
                weight = 0.1
                common_conditions = set(user_conditions) & set(profile.skin_conditions)
                if common_conditions:
                    condition_similarity = len(common_conditions) / max(len(user_conditions), len(profile.skin_conditions))
                    similarity += weight * condition_similarity
                total_weight += weight
            
            # Normalize similarity
            if total_weight > 0:
                similarity = similarity / total_weight
            
            return similarity
            
        except Exception as e:
            logger.error(f"Error calculating demographic similarity: {e}")
            return 0.0
    
    def _age_ranges_overlap(self, range1: str, range2: str) -> bool:
        """Check if two age ranges overlap"""
        try:
            # Parse age ranges (e.g., "25-35", "55+")
            def parse_range(age_range):
                if '+' in age_range:
                    return (int(age_range.replace('+', '')), 100)
                elif '-' in age_range:
                    parts = age_range.split('-')
                    return (int(parts[0]), int(parts[1]))
                else:
                    age = int(age_range)
                    return (age, age)
            
            min1, max1 = parse_range(range1)
            min2, max2 = parse_range(range2)
            
            # Check for overlap
            return not (max1 < min2 or max2 < min1)
            
        except Exception:
            return False
    
    def get_demographic_insights(self, profile_id: str) -> Dict[str, Any]:
        """
        Get detailed demographic insights for a specific profile
        
        Args:
            profile_id: ID of the demographic profile
            
        Returns:
            Dictionary with detailed demographic insights
        """
        try:
            if profile_id not in self.profile_cache:
                logger.warning(f"Profile {profile_id} not found in cache")
                return {}
            
            profile = self.profile_cache[profile_id]
            
            # Get additional insights from SCIN dataset if available
            insights = {
                'profile_id': profile.profile_id,
                'demographics': {
                    'age_range': profile.age_range,
                    'skin_type': profile.skin_type,
                    'ethnicity': profile.ethnicity,
                    'geographic_region': profile.geographic_region
                },
                'skin_conditions': profile.skin_conditions,
                'scin_reference': profile.scin_data_reference,
                'metadata': profile.metadata,
                'insights': self._generate_demographic_insights(profile)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting demographic insights for {profile_id}: {e}")
            return {}
    
    def _generate_demographic_insights(self, profile: DemographicProfile) -> Dict[str, Any]:
        """Generate insights based on demographic profile"""
        try:
            insights = {
                'common_conditions': [],
                'recommended_treatments': [],
                'demographic_prevalence': {},
                'risk_factors': []
            }
            
            # Analyze common conditions for this demographic
            similar_profiles = [p for p in self.profile_cache.values() 
                             if p.ethnicity == profile.ethnicity and p.age_range == profile.age_range]
            
            if similar_profiles:
                # Count condition prevalence
                condition_counts = {}
                for p in similar_profiles:
                    for condition in p.skin_conditions:
                        condition_counts[condition] = condition_counts.get(condition, 0) + 1
                
                # Calculate prevalence percentages
                total_profiles = len(similar_profiles)
                for condition, count in condition_counts.items():
                    prevalence = (count / total_profiles) * 100
                    insights['demographic_prevalence'][condition] = {
                        'prevalence_percentage': round(prevalence, 1),
                        'affected_count': count,
                        'total_population': total_profiles
                    }
                
                # Identify most common conditions
                insights['common_conditions'] = sorted(
                    condition_counts.keys(), 
                    key=lambda x: condition_counts[x], 
                    reverse=True
                )[:5]
            
            # Generate treatment recommendations based on conditions
            for condition in profile.skin_conditions:
                treatments = self._get_treatment_recommendations(condition, profile)
                insights['recommended_treatments'].extend(treatments)
            
            # Remove duplicates
            insights['recommended_treatments'] = list(set(insights['recommended_treatments']))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating demographic insights: {e}")
            return {}
    
    def _get_treatment_recommendations(self, condition: str, profile: DemographicProfile) -> List[str]:
        """Get treatment recommendations for a specific condition and demographic"""
        # This would typically query the SCIN dataset for evidence-based treatments
        # For now, return basic recommendations
        
        treatment_map = {
            'acne': ['salicylic acid cleanser', 'benzoyl peroxide treatment', 'retinoid therapy'],
            'dryness': ['hyaluronic acid serum', 'ceramide moisturizer', 'gentle cleanser'],
            'hyperpigmentation': ['vitamin C serum', 'niacinamide treatment', 'sunscreen'],
            'rosacea': ['gentle skincare routine', 'anti-inflammatory treatments', 'trigger avoidance'],
            'eczema': ['fragrance-free moisturizer', 'barrier repair cream', 'gentle cleansing'],
            'aging': ['retinoid treatment', 'peptide serum', 'antioxidant protection']
        }
        
        return treatment_map.get(condition.lower(), ['consult dermatologist'])
    
    def _generate_cache_key(self, features: Dict[str, Any], k: int) -> str:
        """Generate cache key for search results"""
        # Create a hash of the features and k value
        features_str = json.dumps(features, sort_keys=True, default=str)
        cache_data = f"{features_str}_{k}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        expiry_time = cache_time + timedelta(hours=self.cache_duration)
        
        return datetime.utcnow() < expiry_time
    
    def clear_cache(self):
        """Clear all cached data"""
        self.search_cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cleared all cached data")
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self._connected and len(self.profile_cache) > 0
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get detailed service status information"""
        return {
            'connected': self._connected,
            'last_connection_attempt': self._last_connection_attempt.isoformat() if self._last_connection_attempt else None,
            'profiles_loaded': len(self.profile_cache),
            'faiss_index_size': self.faiss_index.ntotal if self.faiss_index else 0,
            'cache_entries': len(self.search_cache),
            'google_cloud_available': GOOGLE_CLOUD_AVAILABLE,
            'faiss_available': FAISS_AVAILABLE,
            'bucket_name': self.bucket_name,
            'dataset_path': self.dataset_path
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current service configuration"""
        return {
            'bucket_name': self.bucket_name,
            'dataset_path': self.dataset_path,
            'cache_duration': self.cache_duration,
            'vector_dimension': self.vector_dimension,
            'service_status': self.get_service_status()
        }