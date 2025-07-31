"""
Advanced caching strategies for demographic data and search results
"""
import logging
import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
import threading
from dataclasses import dataclass, field

from app.performance import demographic_cache, SimpleCache
from app.vercel_optimizations import MemoryOptimizer, cache_optimizer

logger = logging.getLogger(__name__)


@dataclass
class DemographicProfile:
    """Structured demographic profile for caching"""
    ethnicity: str
    skin_type: str
    age_group: str
    additional_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_cache_key(self) -> str:
        """Generate cache key from profile"""
        profile_dict = {
            'ethnicity': self.ethnicity,
            'skin_type': self.skin_type,
            'age_group': self.age_group,
            **self.additional_attributes
        }
        
        # Sort for consistent keys
        sorted_items = sorted(profile_dict.items())
        key_string = json.dumps(sorted_items, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def similarity_score(self, other: 'DemographicProfile') -> float:
        """Calculate similarity score with another profile"""
        score = 0.0
        total_weight = 0.0
        
        # Ethnicity weight: 0.4
        if self.ethnicity == other.ethnicity:
            score += 0.4
        total_weight += 0.4
        
        # Skin type weight: 0.3
        if self.skin_type == other.skin_type:
            score += 0.3
        total_weight += 0.3
        
        # Age group weight: 0.3
        if self.age_group == other.age_group:
            score += 0.3
        total_weight += 0.3
        
        return score / total_weight if total_weight > 0 else 0.0


class DemographicWeightingCache:
    """Cache for demographic weighting calculations"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 1800):  # 30 minutes
        self.cache = OrderedDict()
        self.timestamps = {}
        self.access_counts = defaultdict(int)
        self.max_size = max_size
        self.ttl = ttl
        self._lock = threading.RLock()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    def _evict_lru(self):
        """Evict least recently used items"""
        while len(self.cache) >= self.max_size:
            # Remove least recently used item
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]
            self.timestamps.pop(lru_key, None)
            self.access_counts.pop(lru_key, None)
    
    def get_weighting(self, query_profile: DemographicProfile, 
                     target_profile: DemographicProfile) -> Optional[float]:
        """Get cached demographic weighting"""
        with self._lock:
            # Create bidirectional key (order doesn't matter for similarity)
            key1 = f"{query_profile.to_cache_key()}:{target_profile.to_cache_key()}"
            key2 = f"{target_profile.to_cache_key()}:{query_profile.to_cache_key()}"
            
            for key in [key1, key2]:
                if key in self.cache and not self._is_expired(key):
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    self.access_counts[key] += 1
                    return self.cache[key]
            
            return None
    
    def set_weighting(self, query_profile: DemographicProfile,
                     target_profile: DemographicProfile, weighting: float):
        """Cache demographic weighting"""
        with self._lock:
            key = f"{query_profile.to_cache_key()}:{target_profile.to_cache_key()}"
            
            # Evict if necessary
            self._evict_lru()
            
            self.cache[key] = weighting
            self.timestamps[key] = time.time()
            self.access_counts[key] = 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self.cache)
            expired_count = sum(1 for key in self.cache.keys() if self._is_expired(key))
            total_accesses = sum(self.access_counts.values())
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_count,
                'expired_entries': expired_count,
                'total_accesses': total_accesses,
                'hit_ratio': total_accesses / max(total_entries, 1),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self._lock:
            expired_keys = [key for key in self.cache.keys() if self._is_expired(key)]
            
            for key in expired_keys:
                del self.cache[key]
                self.timestamps.pop(key, None)
                self.access_counts.pop(key, None)
            
            return len(expired_keys)


class SearchResultCache:
    """Cache for search results with demographic context"""
    
    def __init__(self, max_size: int = 500, ttl: int = 600):  # 10 minutes
        self.cache = SimpleCache(default_ttl=ttl)
        self.result_metadata = {}
        self.max_size = max_size
        self._lock = threading.RLock()
    
    def _generate_search_key(self, query_vector_hash: str, demographics: Dict[str, Any],
                           search_params: Dict[str, Any]) -> str:
        """Generate cache key for search results"""
        key_components = {
            'vector_hash': query_vector_hash,
            'demographics': demographics,
            'params': search_params
        }
        
        key_string = json.dumps(key_components, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def get_search_results(self, query_vector_hash: str, demographics: Dict[str, Any],
                          search_params: Dict[str, Any]) -> Optional[List[Tuple[str, float]]]:
        """Get cached search results"""
        with self._lock:
            cache_key = self._generate_search_key(query_vector_hash, demographics, search_params)
            
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                # Update metadata
                if cache_key in self.result_metadata:
                    self.result_metadata[cache_key]['access_count'] += 1
                    self.result_metadata[cache_key]['last_accessed'] = time.time()
                
                logger.debug(f"Search result cache hit for key: {cache_key[:8]}...")
                return cached_result
            
            return None
    
    def set_search_results(self, query_vector_hash: str, demographics: Dict[str, Any],
                          search_params: Dict[str, Any], results: List[Tuple[str, float]]):
        """Cache search results"""
        with self._lock:
            cache_key = self._generate_search_key(query_vector_hash, demographics, search_params)
            
            # Check cache size and evict if necessary
            if len(self.result_metadata) >= self.max_size:
                self._evict_least_valuable()
            
            # Cache the results
            self.cache.set(cache_key, results)
            
            # Store metadata
            self.result_metadata[cache_key] = {
                'created_at': time.time(),
                'last_accessed': time.time(),
                'access_count': 1,
                'result_count': len(results),
                'demographics': demographics.copy()
            }
            
            logger.debug(f"Cached search results for key: {cache_key[:8]}... ({len(results)} results)")
    
    def _evict_least_valuable(self):
        """Evict least valuable cache entries"""
        if not self.result_metadata:
            return
        
        # Calculate value score for each entry
        current_time = time.time()
        entry_scores = {}
        
        for key, metadata in self.result_metadata.items():
            age = current_time - metadata['created_at']
            recency = current_time - metadata['last_accessed']
            access_frequency = metadata['access_count'] / max(age / 3600, 1)  # accesses per hour
            
            # Lower score = less valuable (will be evicted first)
            score = access_frequency / (1 + recency / 3600)  # Favor recent and frequent access
            entry_scores[key] = score
        
        # Sort by score and remove lowest 20%
        sorted_entries = sorted(entry_scores.items(), key=lambda x: x[1])
        evict_count = max(1, len(sorted_entries) // 5)  # Remove at least 1, up to 20%
        
        for key, _ in sorted_entries[:evict_count]:
            self.cache.delete(key)
            self.result_metadata.pop(key, None)
        
        logger.debug(f"Evicted {evict_count} least valuable search result cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            cache_stats = self.cache.get_stats()
            
            if self.result_metadata:
                total_accesses = sum(meta['access_count'] for meta in self.result_metadata.values())
                avg_result_count = sum(meta['result_count'] for meta in self.result_metadata.values()) / len(self.result_metadata)
                
                # Demographic distribution
                demographic_dist = defaultdict(int)
                for meta in self.result_metadata.values():
                    ethnicity = meta['demographics'].get('ethnicity', 'unknown')
                    demographic_dist[ethnicity] += 1
            else:
                total_accesses = 0
                avg_result_count = 0
                demographic_dist = {}
            
            return {
                **cache_stats,
                'metadata_entries': len(self.result_metadata),
                'total_accesses': total_accesses,
                'avg_result_count': avg_result_count,
                'demographic_distribution': dict(demographic_dist),
                'max_size': self.max_size
            }


class VectorSimilarityCache:
    """Cache for vector similarity calculations"""
    
    def __init__(self, max_size: int = 2000, ttl: int = 3600):  # 1 hour
        self.cache = SimpleCache(default_ttl=ttl)
        self.max_size = max_size
        self.similarity_stats = defaultdict(list)
        self._lock = threading.RLock()
    
    def _vector_hash(self, vector) -> str:
        """Generate hash for vector"""
        try:
            import numpy as np
            if isinstance(vector, np.ndarray):
                return hashlib.md5(vector.tobytes()).hexdigest()[:12]
            else:
                # Convert to numpy array first
                arr = np.array(vector)
                return hashlib.md5(arr.tobytes()).hexdigest()[:12]
        except Exception:
            # Fallback for non-numpy vectors
            vector_str = str(vector)
            return hashlib.md5(vector_str.encode()).hexdigest()[:12]
    
    def get_similarity(self, vector1, vector2) -> Optional[float]:
        """Get cached similarity between two vectors"""
        with self._lock:
            hash1 = self._vector_hash(vector1)
            hash2 = self._vector_hash(vector2)
            
            # Try both orders (similarity is symmetric)
            key1 = f"{hash1}:{hash2}"
            key2 = f"{hash2}:{hash1}"
            
            for key in [key1, key2]:
                similarity = self.cache.get(key)
                if similarity is not None:
                    logger.debug(f"Vector similarity cache hit: {key[:16]}...")
                    return similarity
            
            return None
    
    def set_similarity(self, vector1, vector2, similarity: float):
        """Cache similarity between two vectors"""
        with self._lock:
            hash1 = self._vector_hash(vector1)
            hash2 = self._vector_hash(vector2)
            key = f"{hash1}:{hash2}"
            
            self.cache.set(key, similarity)
            
            # Track similarity statistics
            self.similarity_stats['all'].append(similarity)
            if len(self.similarity_stats['all']) > 1000:
                self.similarity_stats['all'] = self.similarity_stats['all'][-1000:]
            
            logger.debug(f"Cached vector similarity: {key[:16]}... = {similarity:.4f}")
    
    def get_similarity_stats(self) -> Dict[str, Any]:
        """Get similarity statistics"""
        with self._lock:
            cache_stats = self.cache.get_stats()
            
            if self.similarity_stats['all']:
                similarities = self.similarity_stats['all']
                stats = {
                    'count': len(similarities),
                    'mean': sum(similarities) / len(similarities),
                    'min': min(similarities),
                    'max': max(similarities),
                    'std': self._calculate_std(similarities)
                }
            else:
                stats = {'count': 0, 'mean': 0, 'min': 0, 'max': 0, 'std': 0}
            
            return {
                **cache_stats,
                'similarity_stats': stats,
                'max_size': self.max_size
            }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5


class DemographicCacheManager:
    """Manages all demographic-related caches"""
    
    def __init__(self):
        self.weighting_cache = DemographicWeightingCache()
        self.search_cache = SearchResultCache()
        self.similarity_cache = VectorSimilarityCache()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def get_demographic_weighting(self, query_profile: DemographicProfile,
                                target_profile: DemographicProfile) -> float:
        """Get demographic weighting with caching"""
        # Try cache first
        cached_weight = self.weighting_cache.get_weighting(query_profile, target_profile)
        if cached_weight is not None:
            return cached_weight
        
        # Calculate weighting
        weighting = query_profile.similarity_score(target_profile)
        
        # Cache the result
        self.weighting_cache.set_weighting(query_profile, target_profile, weighting)
        
        return weighting
    
    def get_search_results(self, query_vector, demographics: Dict[str, Any],
                          search_params: Dict[str, Any]) -> Optional[List[Tuple[str, float]]]:
        """Get cached search results"""
        vector_hash = self.similarity_cache._vector_hash(query_vector)
        return self.search_cache.get_search_results(vector_hash, demographics, search_params)
    
    def cache_search_results(self, query_vector, demographics: Dict[str, Any],
                           search_params: Dict[str, Any], results: List[Tuple[str, float]]):
        """Cache search results"""
        vector_hash = self.similarity_cache._vector_hash(query_vector)
        self.search_cache.set_search_results(vector_hash, demographics, search_params, results)
    
    def get_vector_similarity(self, vector1, vector2) -> Optional[float]:
        """Get cached vector similarity"""
        return self.similarity_cache.get_similarity(vector1, vector2)
    
    def cache_vector_similarity(self, vector1, vector2, similarity: float):
        """Cache vector similarity"""
        self.similarity_cache.set_similarity(vector1, vector2, similarity)
    
    def periodic_cleanup(self):
        """Perform periodic cleanup of all caches"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        logger.info("Starting demographic cache cleanup...")
        
        # Cleanup expired entries
        weighting_cleaned = self.weighting_cache.cleanup_expired()
        search_cleaned = self.search_cache.cache.cleanup_expired()
        similarity_cleaned = self.similarity_cache.cache.cleanup_expired()
        
        total_cleaned = weighting_cleaned + search_cleaned + similarity_cleaned
        
        logger.info(f"Demographic cache cleanup complete: {total_cleaned} entries removed")
        
        self._last_cleanup = current_time
        
        return {
            'weighting_cleaned': weighting_cleaned,
            'search_cleaned': search_cleaned,
            'similarity_cleaned': similarity_cleaned,
            'total_cleaned': total_cleaned
        }
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all caches"""
        return {
            'weighting_cache': self.weighting_cache.get_stats(),
            'search_cache': self.search_cache.get_stats(),
            'similarity_cache': self.similarity_cache.get_similarity_stats(),
            'last_cleanup': self._last_cleanup,
            'cleanup_interval': self._cleanup_interval,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def clear_all_caches(self):
        """Clear all demographic caches"""
        self.weighting_cache.cache.clear()
        self.weighting_cache.timestamps.clear()
        self.weighting_cache.access_counts.clear()
        
        self.search_cache.cache.clear()
        self.search_cache.result_metadata.clear()
        
        self.similarity_cache.cache.clear()
        self.similarity_cache.similarity_stats.clear()
        
        logger.info("All demographic caches cleared")


# Global demographic cache manager
demographic_cache_manager = DemographicCacheManager()


def cached_demographic_search(ttl: int = 600):
    """Decorator for caching demographic search results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract relevant parameters for caching
            if len(args) >= 2:
                query_vector = args[0]
                demographics = args[1] if len(args) > 1 else kwargs.get('demographics', {})
                search_params = kwargs.copy()
                
                # Remove non-cacheable parameters
                search_params.pop('demographics', None)
                
                # Try to get from cache
                cached_results = demographic_cache_manager.get_search_results(
                    query_vector, demographics, search_params
                )
                
                if cached_results is not None:
                    logger.debug(f"Demographic search cache hit for {func.__name__}")
                    return cached_results
            
            # Execute function
            results = func(*args, **kwargs)
            
            # Cache results if we have the right parameters
            if len(args) >= 2 and results:
                demographic_cache_manager.cache_search_results(
                    query_vector, demographics, search_params, results
                )
                logger.debug(f"Cached demographic search results for {func.__name__}")
            
            return results
        
        return wrapper
    return decorator


def preload_common_demographics():
    """Preload common demographic combinations into cache"""
    logger.info("Preloading common demographic combinations...")
    
    common_profiles = [
        DemographicProfile('caucasian', 'normal', '25-35'),
        DemographicProfile('caucasian', 'oily', '18-25'),
        DemographicProfile('caucasian', 'dry', '35-45'),
        DemographicProfile('african', 'oily', '18-25'),
        DemographicProfile('african', 'normal', '25-35'),
        DemographicProfile('east_asian', 'sensitive', '25-35'),
        DemographicProfile('east_asian', 'normal', '18-25'),
        DemographicProfile('hispanic', 'combination', '25-35'),
        DemographicProfile('south_asian', 'normal', '25-35'),
    ]
    
    # Pre-calculate weightings between common profiles
    preloaded_count = 0
    for i, profile1 in enumerate(common_profiles):
        for profile2 in common_profiles[i:]:  # Avoid duplicates
            weighting = demographic_cache_manager.get_demographic_weighting(profile1, profile2)
            preloaded_count += 1
    
    logger.info(f"Preloaded {preloaded_count} demographic weighting combinations")
    return preloaded_count