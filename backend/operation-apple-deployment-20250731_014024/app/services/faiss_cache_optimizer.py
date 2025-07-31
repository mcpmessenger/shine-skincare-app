"""
FAISS Vector Database Caching and Optimization Layer

This module provides advanced caching, performance monitoring, and optimization
capabilities for FAISS vector databases.
"""
import os
import logging
import numpy as np
import pickle
import threading
import time
import json
import hashlib
import gzip
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import OrderedDict, defaultdict
from enum import Enum
import tempfile

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on access patterns


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds
    
    def touch(self):
        """Update access information"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    memory_usage_mb: float = 0.0


class FAISSCacheOptimizer:
    """
    Advanced caching and optimization layer for FAISS vector databases
    """
    
    def __init__(self,
                 max_cache_size_mb: int = 1024,
                 cache_strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 default_ttl_seconds: int = 3600,
                 enable_compression: bool = True,
                 enable_persistence: bool = True,
                 cache_dir: str = "faiss_cache"):
        """
        Initialize the FAISS cache optimizer
        
        Args:
            max_cache_size_mb: Maximum cache size in MB
            cache_strategy: Cache eviction strategy
            default_ttl_seconds: Default TTL for cache entries
            enable_compression: Whether to compress cached data
            enable_persistence: Whether to persist cache to disk
            cache_dir: Directory for cache persistence
        """
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.cache_strategy = cache_strategy
        self.default_ttl_seconds = default_ttl_seconds
        self.enable_compression = enable_compression
        self.enable_persistence = enable_persistence
        self.cache_dir = cache_dir
        
        # Cache storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._access_frequency: Dict[str, int] = defaultdict(int)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = CacheStats()
        
        # Performance monitoring
        self._access_times: List[float] = []
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
        
        # Optimization settings
        self._auto_optimize = True
        self._optimization_threshold = 1000  # Operations before optimization
        self._operations_count = 0
        
        # Initialize cache directory
        if self.enable_persistence:
            self._initialize_cache_dir()
            self._load_persistent_cache()
    
    def _initialize_cache_dir(self):
        """Initialize cache directory"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Initialized cache directory: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize cache directory: {e}")
            self.enable_persistence = False    

    def _load_persistent_cache(self):
        """Load cache from persistent storage"""
        try:
            cache_file = os.path.join(self.cache_dir, "cache_data.pkl.gz")
            stats_file = os.path.join(self.cache_dir, "cache_stats.json")
            
            if os.path.exists(cache_file):
                with gzip.open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    
                # Restore cache entries that haven't expired
                current_time = time.time()
                for key, entry in cache_data.items():
                    if not entry.is_expired():
                        self._cache[key] = entry
                
                logger.info(f"Loaded {len(self._cache)} cache entries from persistent storage")
            
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                    # Restore relevant stats
                    self.stats.hits = stats_data.get('hits', 0)
                    self.stats.misses = stats_data.get('misses', 0)
                    self.stats.evictions = stats_data.get('evictions', 0)
                    
        except Exception as e:
            logger.error(f"Failed to load persistent cache: {e}")
    
    def _save_persistent_cache(self):
        """Save cache to persistent storage"""
        if not self.enable_persistence:
            return
            
        try:
            cache_file = os.path.join(self.cache_dir, "cache_data.pkl.gz")
            stats_file = os.path.join(self.cache_dir, "cache_stats.json")
            
            # Save cache data
            with gzip.open(cache_file, 'wb') as f:
                pickle.dump(dict(self._cache), f)
            
            # Save statistics
            stats_data = asdict(self.stats)
            stats_data['last_saved'] = datetime.utcnow().isoformat()
            
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
                
            logger.debug("Saved cache to persistent storage")
            
        except Exception as e:
            logger.error(f"Failed to save persistent cache: {e}")
    
    def _calculate_entry_size(self, data: Any) -> int:
        """Calculate the size of a cache entry in bytes"""
        try:
            if self.enable_compression:
                # Estimate compressed size
                serialized = pickle.dumps(data)
                compressed = gzip.compress(serialized)
                return len(compressed)
            else:
                return len(pickle.dumps(data))
        except Exception as e:
            logger.error(f"Error calculating entry size: {e}")
            return 1024  # Default estimate
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data for storage"""
        try:
            serialized = pickle.dumps(data)
            if self.enable_compression:
                return gzip.compress(serialized)
            return serialized
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            return pickle.dumps(data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data from storage"""
        try:
            if self.enable_compression:
                decompressed = gzip.decompress(compressed_data)
                return pickle.loads(decompressed)
            return pickle.loads(compressed_data)
        except Exception as e:
            logger.error(f"Error decompressing data: {e}")
            return None
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        try:
            # Create a hash from all arguments
            key_data = str(args) + str(sorted(kwargs.items()))
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return str(time.time())  # Fallback to timestamp    

    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache"""
        start_time = time.time()
        
        with self._lock:
            try:
                if key in self._cache:
                    entry = self._cache[key]
                    
                    # Check if expired
                    if entry.is_expired():
                        del self._cache[key]
                        self.stats.misses += 1
                        return None
                    
                    # Update access information
                    entry.touch()
                    self._access_frequency[key] += 1
                    
                    # Move to end for LRU
                    if self.cache_strategy == CacheStrategy.LRU:
                        self._cache.move_to_end(key)
                    
                    # Update statistics
                    self.stats.hits += 1
                    access_time = (time.time() - start_time) * 1000
                    self._access_times.append(access_time)
                    
                    # Decompress data
                    data = self._decompress_data(entry.data)
                    
                    logger.debug(f"Cache hit for key: {key[:8]}...")
                    return data
                else:
                    self.stats.misses += 1
                    logger.debug(f"Cache miss for key: {key[:8]}...")
                    return None
                    
            except Exception as e:
                logger.error(f"Error getting cache entry: {e}")
                self.stats.misses += 1
                return None
            finally:
                self._update_stats()
    
    def put(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Put an item in the cache"""
        with self._lock:
            try:
                # Calculate entry size
                compressed_data = self._compress_data(data)
                entry_size = len(compressed_data)
                
                # Check if we need to make space
                if self._need_eviction(entry_size):
                    self._evict_entries(entry_size)
                
                # Create cache entry
                current_time = time.time()
                entry = CacheEntry(
                    key=key,
                    data=compressed_data,
                    created_at=current_time,
                    last_accessed=current_time,
                    access_count=1,
                    size_bytes=entry_size,
                    ttl_seconds=ttl_seconds or self.default_ttl_seconds
                )
                
                # Add to cache
                self._cache[key] = entry
                self._access_frequency[key] = 1
                
                # Update statistics
                self.stats.size_bytes += entry_size
                self.stats.entry_count += 1
                
                logger.debug(f"Cached entry for key: {key[:8]}... (size: {entry_size} bytes)")
                return True
                
            except Exception as e:
                logger.error(f"Error putting cache entry: {e}")
                return False
            finally:
                self._operations_count += 1
                self._check_maintenance()
    
    def _need_eviction(self, new_entry_size: int) -> bool:
        """Check if eviction is needed for new entry"""
        return (self.stats.size_bytes + new_entry_size) > self.max_cache_size_bytes
    
    def _evict_entries(self, space_needed: int):
        """Evict entries based on cache strategy"""
        try:
            space_freed = 0
            entries_to_remove = []
            
            if self.cache_strategy == CacheStrategy.LRU:
                # Remove least recently used entries
                for key, entry in self._cache.items():
                    entries_to_remove.append(key)
                    space_freed += entry.size_bytes
                    if space_freed >= space_needed:
                        break
                        
            elif self.cache_strategy == CacheStrategy.LFU:
                # Remove least frequently used entries
                sorted_entries = sorted(
                    self._cache.items(),
                    key=lambda x: self._access_frequency[x[0]]
                )
                for key, entry in sorted_entries:
                    entries_to_remove.append(key)
                    space_freed += entry.size_bytes
                    if space_freed >= space_needed:
                        break
                        
            elif self.cache_strategy == CacheStrategy.TTL:
                # Remove expired entries first, then oldest
                current_time = time.time()
                expired_entries = [
                    (key, entry) for key, entry in self._cache.items()
                    if entry.is_expired()
                ]
                
                for key, entry in expired_entries:
                    entries_to_remove.append(key)
                    space_freed += entry.size_bytes
                    if space_freed >= space_needed:
                        break
                
                # If not enough space, remove oldest entries
                if space_freed < space_needed:
                    remaining_entries = [
                        (key, entry) for key, entry in self._cache.items()
                        if key not in entries_to_remove
                    ]
                    remaining_entries.sort(key=lambda x: x[1].created_at)
                    
                    for key, entry in remaining_entries:
                        entries_to_remove.append(key)
                        space_freed += entry.size_bytes
                        if space_freed >= space_needed:
                            break
                            
            elif self.cache_strategy == CacheStrategy.ADAPTIVE:
                # Adaptive strategy based on access patterns
                self._adaptive_eviction(space_needed, entries_to_remove)
            
            # Remove selected entries
            for key in entries_to_remove:
                if key in self._cache:
                    entry = self._cache[key]
                    self.stats.size_bytes -= entry.size_bytes
                    self.stats.entry_count -= 1
                    self.stats.evictions += 1
                    del self._cache[key]
                    if key in self._access_frequency:
                        del self._access_frequency[key]
            
            logger.debug(f"Evicted {len(entries_to_remove)} entries, freed {space_freed} bytes")
            
        except Exception as e:
            logger.error(f"Error during eviction: {e}")
    
    def _adaptive_eviction(self, space_needed: int, entries_to_remove: List[str]):
        """Adaptive eviction strategy"""
        try:
            current_time = time.time()
            
            # Score entries based on multiple factors
            scored_entries = []
            for key, entry in self._cache.items():
                # Factors: recency, frequency, size, TTL remaining
                recency_score = current_time - entry.last_accessed
                frequency_score = 1.0 / max(entry.access_count, 1)
                size_score = entry.size_bytes / self.max_cache_size_bytes
                
                if entry.ttl_seconds:
                    ttl_remaining = entry.ttl_seconds - (current_time - entry.created_at)
                    ttl_score = 1.0 / max(ttl_remaining, 1)
                else:
                    ttl_score = 0
                
                # Combined score (higher = more likely to evict)
                combined_score = (
                    0.4 * recency_score +
                    0.3 * frequency_score +
                    0.2 * size_score +
                    0.1 * ttl_score
                )
                
                scored_entries.append((key, entry, combined_score))
            
            # Sort by score (highest first)
            scored_entries.sort(key=lambda x: x[2], reverse=True)
            
            # Select entries to remove
            space_freed = 0
            for key, entry, score in scored_entries:
                entries_to_remove.append(key)
                space_freed += entry.size_bytes
                if space_freed >= space_needed:
                    break
                    
        except Exception as e:
            logger.error(f"Error in adaptive eviction: {e}")
            # Fallback to LRU
            for key in list(self._cache.keys()):
                entries_to_remove.append(key)
                if len(entries_to_remove) * 1024 >= space_needed:  # Rough estimate
                    break    
    de
f _update_stats(self):
        """Update cache statistics"""
        try:
            total_requests = self.stats.hits + self.stats.misses
            if total_requests > 0:
                self.stats.hit_rate = self.stats.hits / total_requests
            
            if self._access_times:
                self.stats.avg_access_time_ms = sum(self._access_times) / len(self._access_times)
                # Keep only recent access times
                if len(self._access_times) > 1000:
                    self._access_times = self._access_times[-500:]
            
            self.stats.memory_usage_mb = self.stats.size_bytes / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    def _check_maintenance(self):
        """Check if maintenance tasks need to be performed"""
        try:
            current_time = time.time()
            
            # Periodic cleanup
            if current_time - self._last_cleanup > self._cleanup_interval:
                self._cleanup_expired_entries()
                self._last_cleanup = current_time
            
            # Auto-optimization
            if (self._auto_optimize and 
                self._operations_count % self._optimization_threshold == 0):
                self._optimize_cache()
            
            # Periodic persistence
            if (self.enable_persistence and 
                self._operations_count % 100 == 0):  # Save every 100 operations
                self._save_persistent_cache()
                
        except Exception as e:
            logger.error(f"Error during maintenance: {e}")
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from cache"""
        try:
            expired_keys = []
            current_time = time.time()
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self._cache[key]
                self.stats.size_bytes -= entry.size_bytes
                self.stats.entry_count -= 1
                del self._cache[key]
                if key in self._access_frequency:
                    del self._access_frequency[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _optimize_cache(self):
        """Optimize cache performance"""
        try:
            logger.info("Optimizing cache performance...")
            
            # Analyze access patterns
            if len(self._access_frequency) > 0:
                avg_frequency = sum(self._access_frequency.values()) / len(self._access_frequency)
                
                # Identify hot and cold entries
                hot_entries = {k: v for k, v in self._access_frequency.items() if v > avg_frequency * 2}
                cold_entries = {k: v for k, v in self._access_frequency.items() if v < avg_frequency * 0.5}
                
                logger.debug(f"Cache analysis: {len(hot_entries)} hot, {len(cold_entries)} cold entries")
                
                # Adjust TTL for hot entries (extend) and cold entries (reduce)
                for key in hot_entries:
                    if key in self._cache:
                        entry = self._cache[key]
                        if entry.ttl_seconds:
                            entry.ttl_seconds = min(entry.ttl_seconds * 1.5, self.default_ttl_seconds * 2)
                
                for key in cold_entries:
                    if key in self._cache:
                        entry = self._cache[key]
                        if entry.ttl_seconds:
                            entry.ttl_seconds = max(entry.ttl_seconds * 0.7, self.default_ttl_seconds * 0.5)
            
            # Compact cache if fragmented
            if self.stats.entry_count > 0:
                avg_entry_size = self.stats.size_bytes / self.stats.entry_count
                if avg_entry_size < 1024:  # Many small entries
                    self._compact_cache()
            
            logger.info("Cache optimization completed")
            
        except Exception as e:
            logger.error(f"Error during cache optimization: {e}")
    
    def _compact_cache(self):
        """Compact cache by removing small, infrequently accessed entries"""
        try:
            entries_to_remove = []
            
            for key, entry in self._cache.items():
                frequency = self._access_frequency.get(key, 0)
                if entry.size_bytes < 512 and frequency < 2:  # Small and rarely accessed
                    entries_to_remove.append(key)
            
            # Remove up to 10% of entries
            max_removals = max(1, len(self._cache) // 10)
            entries_to_remove = entries_to_remove[:max_removals]
            
            for key in entries_to_remove:
                entry = self._cache[key]
                self.stats.size_bytes -= entry.size_bytes
                self.stats.entry_count -= 1
                del self._cache[key]
                if key in self._access_frequency:
                    del self._access_frequency[key]
            
            if entries_to_remove:
                logger.debug(f"Compacted cache: removed {len(entries_to_remove)} small entries")
                
        except Exception as e:
            logger.error(f"Error during cache compaction: {e}")
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            try:
                self._cache.clear()
                self._access_frequency.clear()
                self.stats = CacheStats()
                logger.info("Cache cleared")
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self._lock:
            try:
                self._update_stats()
                
                stats = asdict(self.stats)
                stats.update({
                    'cache_strategy': self.cache_strategy.value,
                    'max_size_mb': self.max_cache_size_bytes / (1024 * 1024),
                    'compression_enabled': self.enable_compression,
                    'persistence_enabled': self.enable_persistence,
                    'operations_count': self._operations_count,
                    'last_cleanup': datetime.fromtimestamp(self._last_cleanup).isoformat(),
                    
                    # Access pattern analysis
                    'hot_entries': len([k for k, v in self._access_frequency.items() 
                                      if v > sum(self._access_frequency.values()) / len(self._access_frequency) * 2])
                    if self._access_frequency else 0,
                    
                    'cold_entries': len([k for k, v in self._access_frequency.items() 
                                       if v < sum(self._access_frequency.values()) / len(self._access_frequency) * 0.5])
                    if self._access_frequency else 0,
                    
                    # Size distribution
                    'avg_entry_size_bytes': self.stats.size_bytes / max(self.stats.entry_count, 1),
                    'cache_utilization': (self.stats.size_bytes / self.max_cache_size_bytes) * 100,
                })
                
                return stats
                
            except Exception as e:
                logger.error(f"Error getting cache stats: {e}")
                return {'error': str(e)}
    
    def optimize_now(self):
        """Manually trigger cache optimization"""
        try:
            self._optimize_cache()
        except Exception as e:
            logger.error(f"Error during manual optimization: {e}")
    
    def backup_cache(self, backup_path: str) -> bool:
        """Create a backup of the cache"""
        try:
            with self._lock:
                backup_data = {
                    'cache_entries': dict(self._cache),
                    'access_frequency': dict(self._access_frequency),
                    'stats': asdict(self.stats),
                    'config': {
                        'cache_strategy': self.cache_strategy.value,
                        'max_cache_size_bytes': self.max_cache_size_bytes,
                        'default_ttl_seconds': self.default_ttl_seconds,
                        'enable_compression': self.enable_compression
                    },
                    'backup_timestamp': datetime.utcnow().isoformat()
                }
                
                with gzip.open(backup_path, 'wb') as f:
                    pickle.dump(backup_data, f)
                
                logger.info(f"Cache backup created: {backup_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating cache backup: {e}")
            return False
    
    def restore_cache(self, backup_path: str) -> bool:
        """Restore cache from backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            with self._lock:
                with gzip.open(backup_path, 'rb') as f:
                    backup_data = pickle.load(f)
                
                # Restore cache entries
                self._cache.clear()
                self._access_frequency.clear()
                
                for key, entry in backup_data['cache_entries'].items():
                    if not entry.is_expired():
                        self._cache[key] = entry
                
                # Restore access frequency
                self._access_frequency.update(backup_data['access_frequency'])
                
                # Restore stats
                stats_data = backup_data['stats']
                self.stats.hits = stats_data.get('hits', 0)
                self.stats.misses = stats_data.get('misses', 0)
                self.stats.evictions = stats_data.get('evictions', 0)
                
                logger.info(f"Cache restored from backup: {len(self._cache)} entries")
                return True
                
        except Exception as e:
            logger.error(f"Error restoring cache from backup: {e}")
            return False