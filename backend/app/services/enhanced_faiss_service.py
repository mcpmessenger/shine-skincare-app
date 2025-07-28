"""
Enhanced Production FAISS Service with advanced indexing strategies and optimizations
"""
import os
import logging
import numpy as np
import pickle
import threading
import time
import json
import hashlib
from typing import List, Tuple, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import tempfile

logger = logging.getLogger(__name__)

# Try to import FAISS, fall back gracefully if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS library not available. Service will be disabled.")
    FAISS_AVAILABLE = False
    faiss = None


class IndexType(Enum):
    """Supported FAISS index types"""
    FLAT_IP = "IndexFlatIP"  # Exact search with inner product (cosine similarity)
    FLAT_L2 = "IndexFlatL2"  # Exact search with L2 distance
    IVF_FLAT = "IndexIVFFlat"  # Inverted file with flat quantizer
    IVF_PQ = "IndexIVFPQ"  # Inverted file with product quantization
    HNSW = "IndexHNSWFlat"  # Hierarchical Navigable Small World
    LSH = "IndexLSH"  # Locality Sensitive Hashing


@dataclass
class IndexConfig:
    """Configuration for FAISS index"""
    index_type: IndexType = IndexType.FLAT_IP
    dimension: int = 2048
    nlist: int = 100  # Number of clusters for IVF
    m: int = 8  # Number of subquantizers for PQ
    nbits: int = 8  # Number of bits per subquantizer
    M: int = 16  # Number of connections for HNSW
    efConstruction: int = 200  # Construction parameter for HNSW
    efSearch: int = 50  # Search parameter for HNSW
    nbits_per_idx: int = 8  # Bits per index for LSH


@dataclass
class SearchConfig:
    """Configuration for search operations"""
    k: int = 10
    nprobe: int = 10  # Number of clusters to search for IVF
    max_codes: int = 0  # Maximum codes to examine (0 = no limit)
    use_gpu: bool = False
    gpu_id: int = 0


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    total_vectors: int = 0
    search_count: int = 0
    add_count: int = 0
    batch_add_count: int = 0
    avg_search_time_ms: float = 0.0
    avg_add_time_ms: float = 0.0
    last_search_time_ms: float = 0.0
    last_add_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    index_size_mb: float = 0.0
    cache_hit_rate: float = 0.0
    error_count: int = 0


class EnhancedFAISSService:
    """
    Enhanced production-grade FAISS service with configurable indexing strategies,
    performance optimizations, and comprehensive monitoring
    """
    
    def __init__(self, 
                 index_config: IndexConfig = None,
                 search_config: SearchConfig = None,
                 index_path: str = "enhanced_faiss_index",
                 enable_caching: bool = True,
                 cache_size: int = 1000,
                 auto_optimize: bool = True):
        """
        Initialize the enhanced FAISS service
        
        Args:
            index_config: Configuration for the FAISS index
            search_config: Configuration for search operations
            index_path: Base path for saving/loading the index and metadata
            enable_caching: Whether to enable search result caching
            cache_size: Maximum number of cached search results
            auto_optimize: Whether to automatically optimize the index
        """
        self.index_config = index_config or IndexConfig()
        self.search_config = search_config or SearchConfig()
        self.index_path = index_path
        self.enable_caching = enable_caching
        self.cache_size = cache_size
        self.auto_optimize = auto_optimize
        
        # Core FAISS components
        self.index = None
        self.gpu_index = None
        self.image_ids = []  # Map FAISS index positions to image IDs
        self.metadata = {}   # Store additional metadata for each vector
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance monitoring
        self.metrics = PerformanceMetrics()
        self._performance_history = []
        
        # Caching system
        self._search_cache = {} if enable_caching else None
        self._cache_timestamps = {} if enable_caching else None
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Auto-optimization settings
        self._last_optimization = None
        self._optimization_threshold = 10000  # Optimize after this many additions
        self._operations_since_optimization = 0
        
        # Configuration
        self.auto_save = True
        self.save_interval = 500  # Save every N operations
        self.operation_count = 0
        
        # Backup and recovery
        self._backup_enabled = True
        self._backup_interval = 3600  # Backup every hour
        self._last_backup = None
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the enhanced FAISS service with proper error handling"""
        if not FAISS_AVAILABLE:
            logger.error("FAISS library not available")
            return
        
        with self._lock:
            try:
                # Try to load existing index
                if self._index_files_exist():
                    success = self.load_index()
                    if success:
                        logger.info(f"Loaded existing enhanced FAISS index with {self.index.ntotal} vectors")
                        self._validate_and_repair_index()
                        return
                    else:
                        logger.warning("Failed to load existing index, creating new one")
                
                # Create new index based on configuration
                self._create_new_index()
                
                # Initialize GPU index if requested
                if self.search_config.use_gpu:
                    self._initialize_gpu_index()
                
                logger.info(f"Created new enhanced FAISS index: {self.index_config.index_type.value}")
                
                # Save the new empty index
                if self.auto_save:
                    self.save_index()
                    
            except Exception as e:
                logger.error(f"Failed to initialize enhanced FAISS service: {e}")
                self.index = None
    
    def _create_new_index(self):
        """Create a new FAISS index based on configuration"""
        try:
            if self.index_config.index_type == IndexType.FLAT_IP:
                self.index = faiss.IndexFlatIP(self.index_config.dimension)
                
            elif self.index_config.index_type == IndexType.FLAT_L2:
                self.index = faiss.IndexFlatL2(self.index_config.dimension)
                
            elif self.index_config.index_type == IndexType.IVF_FLAT:
                quantizer = faiss.IndexFlatL2(self.index_config.dimension)
                self.index = faiss.IndexIVFFlat(quantizer, self.index_config.dimension, self.index_config.nlist)
                
            elif self.index_config.index_type == IndexType.IVF_PQ:
                quantizer = faiss.IndexFlatL2(self.index_config.dimension)
                self.index = faiss.IndexIVFPQ(quantizer, self.index_config.dimension, 
                                            self.index_config.nlist, self.index_config.m, self.index_config.nbits)
                
            elif self.index_config.index_type == IndexType.HNSW:
                self.index = faiss.IndexHNSWFlat(self.index_config.dimension, self.index_config.M)
                self.index.hnsw.efConstruction = self.index_config.efConstruction
                
            elif self.index_config.index_type == IndexType.LSH:
                self.index = faiss.IndexLSH(self.index_config.dimension, self.index_config.nbits_per_idx)
                
            else:
                # Default to IndexFlatIP
                logger.warning(f"Unknown index type {self.index_config.index_type}, using IndexFlatIP")
                self.index = faiss.IndexFlatIP(self.index_config.dimension)
            
            # Initialize metadata
            self.image_ids = []
            self.metadata = {}
            self.metrics = PerformanceMetrics()
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            # Fallback to simple index
            self.index = faiss.IndexFlatIP(self.index_config.dimension)
    
    def _initialize_gpu_index(self):
        """Initialize GPU index if CUDA is available"""
        try:
            if not hasattr(faiss, 'StandardGpuResources'):
                logger.warning("GPU support not available in FAISS")
                return
            
            # Check if GPU is available
            if faiss.get_num_gpus() == 0:
                logger.warning("No GPUs available for FAISS")
                return
            
            # Create GPU resources
            gpu_res = faiss.StandardGpuResources()
            
            # Move index to GPU
            self.gpu_index = faiss.index_cpu_to_gpu(gpu_res, self.search_config.gpu_id, self.index)
            
            logger.info(f"Initialized GPU index on device {self.search_config.gpu_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPU index: {e}")
            self.gpu_index = None
    
    def _index_files_exist(self) -> bool:
        """Check if index files exist"""
        index_file = f"{self.index_path}.index"
        ids_file = f"{self.index_path}_ids.pkl"
        metadata_file = f"{self.index_path}_metadata.pkl"
        config_file = f"{self.index_path}_config.json"
        
        return (os.path.exists(index_file) and 
                os.path.exists(ids_file) and 
                os.path.exists(metadata_file) and
                os.path.exists(config_file))
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        Normalize vector based on index type with robust error handling
        
        Args:
            vector: Input vector as numpy array
            
        Returns:
            Normalized vector appropriate for the index type
        """
        try:
            # Ensure vector is float32 for FAISS compatibility
            if vector.dtype != np.float32:
                vector = vector.astype(np.float32)
            
            # Normalize based on index type
            if self.index_config.index_type in [IndexType.FLAT_IP, IndexType.IVF_FLAT]:
                # L2-normalize for cosine similarity
                vector_norm = np.linalg.norm(vector)
                if vector_norm > 1e-8:
                    normalized_vector = vector / vector_norm
                else:
                    # Handle zero vector case
                    logger.warning("Encountered zero vector during normalization")
                    normalized_vector = np.random.normal(0, 0.01, vector.shape).astype(np.float32)
                    normalized_vector = normalized_vector / np.linalg.norm(normalized_vector)
            else:
                # For L2-based indices, no normalization needed
                normalized_vector = vector
                
            return normalized_vector
            
        except Exception as e:
            logger.error(f"Error normalizing vector: {e}")
            # Return a small random normalized vector as fallback
            fallback_vector = np.random.normal(0, 0.01, vector.shape).astype(np.float32)
            if self.index_config.index_type in [IndexType.FLAT_IP, IndexType.IVF_FLAT]:
                return fallback_vector / np.linalg.norm(fallback_vector)
            return fallback_vector
    
    def _validate_vector_dimension(self, vector: np.ndarray) -> bool:
        """Validate that vector has the correct dimension"""
        if vector.ndim == 1:
            return vector.shape[0] == self.index_config.dimension
        elif vector.ndim == 2:
            return vector.shape[1] == self.index_config.dimension
        else:
            return False
    
    def _generate_cache_key(self, query_vector: np.ndarray, k: int, search_params: Dict[str, Any] = None) -> str:
        """Generate cache key for search results"""
        try:
            # Create hash from vector and parameters
            vector_hash = hashlib.md5(query_vector.tobytes()).hexdigest()
            params_str = json.dumps(search_params or {}, sort_keys=True)
            cache_key = f"{vector_hash}_{k}_{params_str}"
            return hashlib.md5(cache_key.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return str(time.time())  # Fallback to timestamp
    
    def _get_cached_results(self, cache_key: str) -> Optional[List[Tuple[str, float]]]:
        """Get cached search results if available and valid"""
        if not self.enable_caching or not self._search_cache:
            return None
        
        try:
            if cache_key in self._search_cache:
                # Check if cache entry is still valid (1 hour TTL)
                timestamp = self._cache_timestamps.get(cache_key, 0)
                if time.time() - timestamp < 3600:  # 1 hour TTL
                    self._cache_hits += 1
                    return self._search_cache[cache_key]
                else:
                    # Remove expired entry
                    del self._search_cache[cache_key]
                    del self._cache_timestamps[cache_key]
            
            self._cache_misses += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached results: {e}")
            return None
    
    def _cache_results(self, cache_key: str, results: List[Tuple[str, float]]):
        """Cache search results"""
        if not self.enable_caching or not self._search_cache:
            return
        
        try:
            # Implement LRU eviction if cache is full
            if len(self._search_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = min(self._cache_timestamps.keys(), 
                               key=lambda k: self._cache_timestamps[k])
                del self._search_cache[oldest_key]
                del self._cache_timestamps[oldest_key]
            
            self._search_cache[cache_key] = results
            self._cache_timestamps[cache_key] = time.time()
            
        except Exception as e:
            logger.error(f"Error caching results: {e}")
    
    def add_vector(self, vector: np.ndarray, image_id: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a vector to the FAISS index with enhanced error handling and performance tracking
        
        Args:
            vector: Feature vector as numpy array
            image_id: ID of the image
            metadata: Optional metadata for the vector
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("Enhanced FAISS service not available")
            return False
        
        start_time = time.time()
        
        with self._lock:
            try:
                # Ensure vector is the right shape
                if vector.ndim == 1:
                    vector = vector.reshape(1, -1)
                
                # Validate dimension
                if not self._validate_vector_dimension(vector):
                    logger.error(f"Vector dimension {vector.shape} doesn't match index dimension {self.index_config.dimension}")
                    self.metrics.error_count += 1
                    return False
                
                # Check for duplicate image_id
                if image_id in self.image_ids:
                    logger.warning(f"Image ID {image_id} already exists, skipping")
                    return False
                
                # Normalize vector based on index type
                normalized_vector = self._normalize_vector(vector[0])
                normalized_vector = normalized_vector.reshape(1, -1)
                
                # Train index if necessary (for IVF indices)
                if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                    if len(self.image_ids) >= self.index_config.nlist:
                        self._train_index()
                
                # Add normalized vector to index
                self.index.add(normalized_vector)
                
                # Update GPU index if available
                if self.gpu_index is not None:
                    try:
                        self.gpu_index.add(normalized_vector)
                    except Exception as e:
                        logger.warning(f"Failed to add vector to GPU index: {e}")
                
                # Store image ID and metadata
                self.image_ids.append(image_id)
                vector_metadata = {
                    'added_at': datetime.utcnow().isoformat(),
                    'vector_norm': float(np.linalg.norm(vector[0])),
                    'index_position': len(self.image_ids) - 1,
                    'custom_metadata': metadata or {}
                }
                self.metadata[image_id] = vector_metadata
                
                # Update metrics
                add_time_ms = (time.time() - start_time) * 1000
                self.metrics.add_count += 1
                self.metrics.total_vectors = len(self.image_ids)
                self.metrics.last_add_time_ms = add_time_ms
                self.metrics.avg_add_time_ms = (
                    (self.metrics.avg_add_time_ms * (self.metrics.add_count - 1) + add_time_ms) / 
                    self.metrics.add_count
                )
                
                self.operation_count += 1
                self._operations_since_optimization += 1
                
                # Clear cache since index has changed
                if self.enable_caching:
                    self._search_cache.clear()
                    self._cache_timestamps.clear()
                
                # Auto-save if configured
                if self.auto_save and self.operation_count % self.save_interval == 0:
                    self.save_index()
                
                # Auto-optimize if configured
                if (self.auto_optimize and 
                    self._operations_since_optimization >= self._optimization_threshold):
                    self._auto_optimize_index()
                
                # Auto-backup if configured
                if self._backup_enabled:
                    self._check_and_create_backup()
                
                logger.debug(f"Added vector for image {image_id} in {add_time_ms:.2f}ms")
                return True
                
            except Exception as e:
                logger.error(f"Error adding vector to enhanced FAISS index: {e}")
                self.metrics.error_count += 1
                return False
    
    def search_similar(self, 
                      query_vector: np.ndarray, 
                      k: int = None,
                      search_params: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """
        Search for similar vectors with enhanced performance and caching
        
        Args:
            query_vector: Query vector as numpy array
            k: Number of similar vectors to return (uses config default if None)
            search_params: Optional search parameters (nprobe, etc.)
            
        Returns:
            List of tuples (image_id, similarity_score)
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("Enhanced FAISS service not available")
            return []
        
        k = k or self.search_config.k
        search_params = search_params or {}
        start_time = time.time()
        
        with self._lock:
            try:
                if self.index.ntotal == 0:
                    logger.warning("Enhanced FAISS index is empty")
                    return []
                
                # Ensure vector is the right shape
                if query_vector.ndim == 1:
                    query_vector = query_vector.reshape(1, -1)
                
                # Validate dimension
                if not self._validate_vector_dimension(query_vector):
                    logger.error(f"Query vector dimension {query_vector.shape} doesn't match index dimension {self.index_config.dimension}")
                    self.metrics.error_count += 1
                    return []
                
                # Check cache first
                cache_key = self._generate_cache_key(query_vector, k, search_params)
                cached_results = self._get_cached_results(cache_key)
                if cached_results is not None:
                    search_time_ms = (time.time() - start_time) * 1000
                    self.metrics.last_search_time_ms = search_time_ms
                    logger.debug(f"Returned cached results in {search_time_ms:.2f}ms")
                    return cached_results
                
                # Normalize query vector based on index type
                normalized_query = self._normalize_vector(query_vector[0])
                normalized_query = normalized_query.reshape(1, -1)
                
                # Configure search parameters
                self._configure_search_parameters(search_params)
                
                # Choose index for search (GPU if available and beneficial)
                search_index = self._choose_search_index(k)
                
                # Perform search
                similarities, indices = search_index.search(normalized_query, min(k, self.index.ntotal))
                
                # Convert to results format
                results = []
                for i, (sim, idx) in enumerate(zip(similarities[0], indices[0])):
                    if 0 <= idx < len(self.image_ids):
                        image_id = self.image_ids[idx]
                        # Convert based on index type
                        if self.index_config.index_type in [IndexType.FLAT_IP, IndexType.IVF_FLAT]:
                            # For IP indices, similarity is already correct (higher = more similar)
                            similarity_score = float(sim)
                        else:
                            # For L2 indices, convert distance to similarity (lower distance = higher similarity)
                            similarity_score = 1.0 / (1.0 + float(sim))
                        
                        results.append((image_id, similarity_score))
                    else:
                        logger.warning(f"Invalid index {idx} returned by FAISS search")
                
                # Cache results
                self._cache_results(cache_key, results)
                
                # Update metrics
                search_time_ms = (time.time() - start_time) * 1000
                self.metrics.search_count += 1
                self.metrics.last_search_time_ms = search_time_ms
                self.metrics.avg_search_time_ms = (
                    (self.metrics.avg_search_time_ms * (self.metrics.search_count - 1) + search_time_ms) / 
                    self.metrics.search_count
                )
                
                # Update cache hit rate
                total_searches = self._cache_hits + self._cache_misses
                self.metrics.cache_hit_rate = self._cache_hits / max(total_searches, 1)
                
                logger.debug(f"Search completed in {search_time_ms:.2f}ms, found {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Error searching enhanced FAISS index: {e}")
                self.metrics.error_count += 1
                return []
    
    def _configure_search_parameters(self, search_params: Dict[str, Any]):
        """Configure search parameters for the index"""
        try:
            # Configure nprobe for IVF indices
            if hasattr(self.index, 'nprobe'):
                nprobe = search_params.get('nprobe', self.search_config.nprobe)
                self.index.nprobe = min(nprobe, getattr(self.index, 'nlist', nprobe))
            
            # Configure efSearch for HNSW indices
            if hasattr(self.index, 'hnsw'):
                ef_search = search_params.get('efSearch', self.search_config.efSearch)
                self.index.hnsw.efSearch = ef_search
            
            # Configure max_codes if supported
            max_codes = search_params.get('max_codes', self.search_config.max_codes)
            if hasattr(self.index, 'max_codes') and max_codes > 0:
                self.index.max_codes = max_codes
                
        except Exception as e:
            logger.error(f"Error configuring search parameters: {e}")
    
    def _choose_search_index(self, k: int):
        """Choose the best index for search (CPU vs GPU)"""
        # Use GPU index if available and beneficial
        if (self.gpu_index is not None and 
            self.index.ntotal > 10000 and  # GPU beneficial for large indices
            k <= 100):  # GPU efficient for reasonable k values
            return self.gpu_index
        return self.index
    
    def _train_index(self):
        """Train the index if necessary (for IVF indices)"""
        try:
            if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                logger.info("Training FAISS index...")
                
                # Get training vectors (use existing vectors)
                if len(self.image_ids) >= self.index_config.nlist:
                    training_vectors = []
                    for i in range(min(len(self.image_ids), self.index_config.nlist * 10)):
                        try:
                            vector = self.index.reconstruct(i)
                            training_vectors.append(vector)
                        except:
                            continue
                    
                    if training_vectors:
                        training_data = np.array(training_vectors, dtype=np.float32)
                        self.index.train(training_data)
                        logger.info("Index training completed")
                    
        except Exception as e:
            logger.error(f"Error training index: {e}")
    
    def _auto_optimize_index(self):
        """Automatically optimize the index for better performance"""
        try:
            logger.info("Auto-optimizing FAISS index...")
            
            # Reset optimization counter
            self._operations_since_optimization = 0
            self._last_optimization = datetime.utcnow()
            
            # Perform optimization based on index type
            if self.index_config.index_type == IndexType.IVF_FLAT:
                # Re-train with more recent data if index has grown significantly
                if self.index.ntotal > self.index_config.nlist * 20:
                    self._retrain_ivf_index()
            
            elif self.index_config.index_type == IndexType.HNSW:
                # HNSW doesn't need retraining, but we can adjust search parameters
                # based on index size
                if self.index.ntotal > 100000:
                    self.search_config.efSearch = min(self.search_config.efSearch * 2, 200)
            
            # Clear cache to ensure fresh results
            if self.enable_caching:
                self._search_cache.clear()
                self._cache_timestamps.clear()
            
            logger.info("Index optimization completed")
            
        except Exception as e:
            logger.error(f"Error during auto-optimization: {e}")
    
    def _retrain_ivf_index(self):
        """Retrain IVF index with more recent data"""
        try:
            if not hasattr(self.index, 'is_trained'):
                return
            
            # Sample recent vectors for training
            sample_size = min(self.index.ntotal, self.index_config.nlist * 50)
            sample_indices = np.random.choice(self.index.ntotal, sample_size, replace=False)
            
            training_vectors = []
            for idx in sample_indices:
                try:
                    vector = self.index.reconstruct(int(idx))
                    training_vectors.append(vector)
                except:
                    continue
            
            if training_vectors:
                training_data = np.array(training_vectors, dtype=np.float32)
                
                # Create new index with same configuration
                if self.index_config.index_type == IndexType.IVF_FLAT:
                    quantizer = faiss.IndexFlatL2(self.index_config.dimension)
                    new_index = faiss.IndexIVFFlat(quantizer, self.index_config.dimension, self.index_config.nlist)
                    new_index.train(training_data)
                    
                    # Transfer all vectors to new index
                    all_vectors = []
                    for i in range(self.index.ntotal):
                        try:
                            vector = self.index.reconstruct(i)
                            all_vectors.append(vector)
                        except:
                            continue
                    
                    if all_vectors:
                        all_vectors_array = np.array(all_vectors, dtype=np.float32)
                        new_index.add(all_vectors_array)
                        
                        # Replace old index
                        self.index = new_index
                        
                        # Update GPU index if available
                        if self.gpu_index is not None:
                            self._initialize_gpu_index()
                        
                        logger.info("IVF index retrained successfully")
                
        except Exception as e:
            logger.error(f"Error retraining IVF index: {e}")
    
    def _check_and_create_backup(self):
        """Check if backup is needed and create one"""
        try:
            current_time = datetime.utcnow()
            
            if (self._last_backup is None or 
                (current_time - self._last_backup).total_seconds() >= self._backup_interval):
                
                self._create_backup()
                self._last_backup = current_time
                
        except Exception as e:
            logger.error(f"Error checking/creating backup: {e}")
    
    def _create_backup(self):
        """Create a backup of the current index"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.index_path}_backup_{timestamp}"
            
            # Save index with backup path
            original_path = self.index_path
            self.index_path = backup_path
            success = self.save_index()
            self.index_path = original_path
            
            if success:
                logger.info(f"Created backup at {backup_path}")
            else:
                logger.error("Failed to create backup")
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
    
    def save_index(self) -> bool:
        """
        Save the enhanced FAISS index and all metadata with comprehensive error handling
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("Enhanced FAISS service not available")
            return False
        
        with self._lock:
            try:
                # Save FAISS index
                index_file = f"{self.index_path}.index"
                faiss.write_index(self.index, index_file)
                
                # Save image IDs
                ids_file = f"{self.index_path}_ids.pkl"
                with open(ids_file, 'wb') as f:
                    pickle.dump(self.image_ids, f)
                
                # Save metadata
                metadata_file = f"{self.index_path}_metadata.pkl"
                with open(metadata_file, 'wb') as f:
                    pickle.dump(self.metadata, f)
                
                # Save configuration
                config_file = f"{self.index_path}_config.json"
                config_data = {
                    'index_config': {
                        'index_type': self.index_config.index_type.value,
                        'dimension': self.index_config.dimension,
                        'nlist': self.index_config.nlist,
                        'm': self.index_config.m,
                        'nbits': self.index_config.nbits,
                        'M': self.index_config.M,
                        'efConstruction': self.index_config.efConstruction,
                        'efSearch': self.index_config.efSearch,
                        'nbits_per_idx': self.index_config.nbits_per_idx
                    },
                    'search_config': {
                        'k': self.search_config.k,
                        'nprobe': self.search_config.nprobe,
                        'max_codes': self.search_config.max_codes,
                        'use_gpu': self.search_config.use_gpu,
                        'gpu_id': self.search_config.gpu_id
                    },
                    'service_config': {
                        'enable_caching': self.enable_caching,
                        'cache_size': self.cache_size,
                        'auto_optimize': self.auto_optimize,
                        'auto_save': self.auto_save,
                        'save_interval': self.save_interval
                    }
                }
                
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                # Save metrics
                metrics_file = f"{self.index_path}_metrics.json"
                metrics_data = {
                    'total_vectors': self.metrics.total_vectors,
                    'search_count': self.metrics.search_count,
                    'add_count': self.metrics.add_count,
                    'batch_add_count': self.metrics.batch_add_count,
                    'avg_search_time_ms': self.metrics.avg_search_time_ms,
                    'avg_add_time_ms': self.metrics.avg_add_time_ms,
                    'cache_hit_rate': self.metrics.cache_hit_rate,
                    'error_count': self.metrics.error_count,
                    'last_save_time': datetime.utcnow().isoformat(),
                    'last_optimization': self._last_optimization.isoformat() if self._last_optimization else None
                }
                
                with open(metrics_file, 'w') as f:
                    json.dump(metrics_data, f, indent=2)
                
                logger.info(f"Successfully saved enhanced FAISS index with {self.index.ntotal} vectors")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save enhanced FAISS index: {e}")
                return False
    
    def load_index(self) -> bool:
        """
        Load the enhanced FAISS index and all metadata with validation
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS library not available")
            return False
        
        with self._lock:
            try:
                # Load configuration first
                config_file = f"{self.index_path}_config.json"
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    # Update configurations
                    index_config_data = config_data.get('index_config', {})
                    self.index_config.index_type = IndexType(index_config_data.get('index_type', 'IndexFlatIP'))
                    self.index_config.dimension = index_config_data.get('dimension', 2048)
                    self.index_config.nlist = index_config_data.get('nlist', 100)
                    # ... load other config parameters
                
                # Load FAISS index
                index_file = f"{self.index_path}.index"
                if not os.path.exists(index_file):
                    logger.warning(f"Index file {index_file} does not exist")
                    return False
                
                self.index = faiss.read_index(index_file)
                
                # Load image IDs
                ids_file = f"{self.index_path}_ids.pkl"
                if os.path.exists(ids_file):
                    with open(ids_file, 'rb') as f:
                        self.image_ids = pickle.load(f)
                else:
                    logger.warning("Image IDs file not found, initializing empty list")
                    self.image_ids = []
                
                # Load metadata
                metadata_file = f"{self.index_path}_metadata.pkl"
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'rb') as f:
                        self.metadata = pickle.load(f)
                else:
                    logger.warning("Metadata file not found, initializing empty dict")
                    self.metadata = {}
                
                # Load metrics
                metrics_file = f"{self.index_path}_metrics.json"
                if os.path.exists(metrics_file):
                    with open(metrics_file, 'r') as f:
                        metrics_data = json.load(f)
                    
                    self.metrics.total_vectors = metrics_data.get('total_vectors', 0)
                    self.metrics.search_count = metrics_data.get('search_count', 0)
                    self.metrics.add_count = metrics_data.get('add_count', 0)
                    self.metrics.avg_search_time_ms = metrics_data.get('avg_search_time_ms', 0.0)
                    self.metrics.avg_add_time_ms = metrics_data.get('avg_add_time_ms', 0.0)
                    self.metrics.cache_hit_rate = metrics_data.get('cache_hit_rate', 0.0)
                    self.metrics.error_count = metrics_data.get('error_count', 0)
                
                # Validate consistency
                if not self._validate_index_consistency():
                    logger.error("Index consistency validation failed")
                    return False
                
                # Initialize GPU index if configured
                if self.search_config.use_gpu:
                    self._initialize_gpu_index()
                
                logger.info(f"Successfully loaded enhanced FAISS index with {self.index.ntotal} vectors")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load enhanced FAISS index: {e}")
                return False
    
    def _validate_and_repair_index(self):
        """Validate and repair index if necessary"""
        try:
            if not self._validate_index_consistency():
                logger.warning("Index inconsistency detected, attempting repair...")
                self._repair_index()
                
        except Exception as e:
            logger.error(f"Error validating/repairing index: {e}")
    
    def _validate_index_consistency(self) -> bool:
        """Validate consistency between FAISS index and metadata"""
        try:
            # Check if number of vectors matches
            if self.index.ntotal != len(self.image_ids):
                logger.error(f"Inconsistency: FAISS index has {self.index.ntotal} vectors but {len(self.image_ids)} image IDs")
                return False
            
            # Check for duplicate image IDs
            if len(self.image_ids) != len(set(self.image_ids)):
                logger.error("Duplicate image IDs detected")
                return False
            
            # Check metadata consistency
            for i, image_id in enumerate(self.image_ids):
                if image_id in self.metadata:
                    if self.metadata[image_id].get('index_position') != i:
                        logger.warning(f"Metadata position mismatch for {image_id}")
                        # Fix the position
                        self.metadata[image_id]['index_position'] = i
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating index consistency: {e}")
            return False
    
    def _repair_index(self):
        """Attempt to repair index inconsistencies"""
        try:
            logger.info("Attempting to repair index inconsistencies...")
            
            # Truncate image_ids to match index size
            if len(self.image_ids) > self.index.ntotal:
                self.image_ids = self.image_ids[:self.index.ntotal]
                logger.info(f"Truncated image_ids to {len(self.image_ids)}")
            
            # Remove metadata for non-existent images
            valid_ids = set(self.image_ids)
            invalid_metadata_keys = [k for k in self.metadata.keys() if k not in valid_ids]
            for key in invalid_metadata_keys:
                del self.metadata[key]
            
            # Fix index positions in metadata
            for i, image_id in enumerate(self.image_ids):
                if image_id in self.metadata:
                    self.metadata[image_id]['index_position'] = i
            
            # Update metrics
            self.metrics.total_vectors = len(self.image_ids)
            
            logger.info("Index repair completed")
            
        except Exception as e:
            logger.error(f"Error repairing index: {e}")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics and health information"""
        with self._lock:
            try:
                # Calculate memory usage
                if self.index:
                    estimated_memory_mb = (self.index_config.dimension * self.index.ntotal * 4) / (1024 * 1024)
                    self.metrics.memory_usage_mb = round(estimated_memory_mb, 2)
                
                # Calculate index file size
                try:
                    index_file = f"{self.index_path}.index"
                    if os.path.exists(index_file):
                        file_size_bytes = os.path.getsize(index_file)
                        self.metrics.index_size_mb = round(file_size_bytes / (1024 * 1024), 2)
                except:
                    pass
                
                stats = {
                    # Basic metrics
                    'total_vectors': self.metrics.total_vectors,
                    'search_count': self.metrics.search_count,
                    'add_count': self.metrics.add_count,
                    'batch_add_count': self.metrics.batch_add_count,
                    'error_count': self.metrics.error_count,
                    
                    # Performance metrics
                    'avg_search_time_ms': round(self.metrics.avg_search_time_ms, 2),
                    'avg_add_time_ms': round(self.metrics.avg_add_time_ms, 2),
                    'last_search_time_ms': round(self.metrics.last_search_time_ms, 2),
                    'last_add_time_ms': round(self.metrics.last_add_time_ms, 2),
                    
                    # Memory and storage
                    'memory_usage_mb': self.metrics.memory_usage_mb,
                    'index_size_mb': self.metrics.index_size_mb,
                    
                    # Cache metrics
                    'cache_enabled': self.enable_caching,
                    'cache_hit_rate': round(self.metrics.cache_hit_rate, 3),
                    'cache_size': len(self._search_cache) if self._search_cache else 0,
                    'cache_max_size': self.cache_size,
                    
                    # Configuration
                    'index_type': self.index_config.index_type.value,
                    'dimension': self.index_config.dimension,
                    'auto_optimize': self.auto_optimize,
                    'auto_save': self.auto_save,
                    'gpu_enabled': self.search_config.use_gpu,
                    'gpu_available': self.gpu_index is not None,
                    
                    # Health indicators
                    'is_available': self.is_available(),
                    'is_trained': getattr(self.index, 'is_trained', True) if self.index else False,
                    'last_optimization': self._last_optimization.isoformat() if self._last_optimization else None,
                    'operations_since_optimization': self._operations_since_optimization,
                    
                    # System info
                    'faiss_available': FAISS_AVAILABLE,
                    'thread_safe': True,
                    'backup_enabled': self._backup_enabled,
                    'last_backup': self._last_backup.isoformat() if self._last_backup else None
                }
                
                return stats
                
            except Exception as e:
                logger.error(f"Error getting comprehensive stats: {e}")
                return {'error': str(e)}
    
    def is_available(self) -> bool:
        """Check if the enhanced service is available and healthy"""
        return (FAISS_AVAILABLE and 
                self.index is not None and 
                self.metrics.error_count < 100)  # Threshold for too many errors
    
    def clear_cache(self):
        """Clear the search result cache"""
        if self.enable_caching and self._search_cache:
            with self._lock:
                self._search_cache.clear()
                self._cache_timestamps.clear()
                self._cache_hits = 0
                self._cache_misses = 0
                self.metrics.cache_hit_rate = 0.0
                logger.info("Search cache cleared")
    
    def optimize_index(self) -> bool:
        """Manually trigger index optimization"""
        try:
            self._auto_optimize_index()
            return True
        except Exception as e:
            logger.error(f"Error during manual optimization: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Manually create a backup"""
        try:
            self._create_backup()
            return True
        except Exception as e:
            logger.error(f"Error creating manual backup: {e}")
            return False