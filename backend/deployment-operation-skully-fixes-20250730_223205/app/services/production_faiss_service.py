"""
Production FAISS Service with persistence, thread safety, and advanced features
"""
import os
import logging
import numpy as np
import pickle
import threading
import time
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import FAISS, fall back gracefully if not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("FAISS library not available. Service will be disabled.")
    FAISS_AVAILABLE = False
    faiss = None


class ProductionFAISSService:
    """Production-grade FAISS service with IndexFlatIP for cosine similarity"""
    
    def __init__(self, dimension: int = 2048, index_path: str = "faiss_index"):
        """
        Initialize the production FAISS service
        
        Args:
            dimension: Dimension of the feature vectors
            index_path: Base path for saving/loading the FAISS index and metadata
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.image_ids = []  # Map FAISS index positions to image IDs
        self.metadata = {}   # Store additional metadata for each vector
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance monitoring
        self._stats = {
            'total_vectors': 0,
            'search_count': 0,
            'add_count': 0,
            'last_save_time': None,
            'last_load_time': None,
            'corruption_detected': False,
            'rebuild_count': 0
        }
        
        # Configuration
        self.auto_save = True
        self.save_interval = 100  # Save every N operations
        self.operation_count = 0
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the FAISS index with proper error handling and recovery"""
        if not FAISS_AVAILABLE:
            logger.error("FAISS library not available")
            return
        
        with self._lock:
            try:
                # Try to load existing index
                if self._index_files_exist():
                    success = self.load_index()
                    if success:
                        logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
                        return
                    else:
                        logger.warning("Failed to load existing index, creating new one")
                
                # Create new index using IndexFlatIP for cosine similarity
                self.index = faiss.IndexFlatIP(self.dimension)
                self.image_ids = []
                self.metadata = {}
                self._stats['total_vectors'] = 0
                
                logger.info(f"Created new FAISS IndexFlatIP with dimension {self.dimension}")
                
                # Save the new empty index
                if self.auto_save:
                    self.save_index()
                    
            except Exception as e:
                logger.error(f"Failed to initialize FAISS index: {e}")
                self.index = None
    
    def _index_files_exist(self) -> bool:
        """Check if index files exist"""
        index_file = f"{self.index_path}.index"
        ids_file = f"{self.index_path}_ids.pkl"
        metadata_file = f"{self.index_path}_metadata.pkl"
        stats_file = f"{self.index_path}_stats.json"
        
        return (os.path.exists(index_file) and 
                os.path.exists(ids_file) and 
                os.path.exists(metadata_file))
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        L2-normalize vector for cosine similarity with robust error handling
        
        Args:
            vector: Input vector as numpy array
            
        Returns:
            L2-normalized vector
        """
        try:
            # Ensure vector is float32 for FAISS compatibility
            if vector.dtype != np.float32:
                vector = vector.astype(np.float32)
            
            # Calculate L2 norm
            vector_norm = np.linalg.norm(vector)
            
            # Handle zero vector case
            if vector_norm > 1e-8:  # Use small epsilon to avoid numerical issues
                normalized_vector = vector / vector_norm
            else:
                # Handle zero vector case - return small random vector
                logger.warning("Encountered zero vector during normalization, using random fallback")
                normalized_vector = np.random.normal(0, 0.01, vector.shape).astype(np.float32)
                normalized_vector = normalized_vector / np.linalg.norm(normalized_vector)
                
            return normalized_vector
            
        except Exception as e:
            logger.error(f"Error normalizing vector: {e}")
            # Return a small random normalized vector as fallback
            fallback_vector = np.random.normal(0, 0.01, vector.shape).astype(np.float32)
            return fallback_vector / np.linalg.norm(fallback_vector)
    
    def _validate_vector_dimension(self, vector: np.ndarray) -> bool:
        """
        Validate that vector has the correct dimension
        
        Args:
            vector: Input vector
            
        Returns:
            True if dimension is correct, False otherwise
        """
        if vector.ndim == 1:
            return vector.shape[0] == self.dimension
        elif vector.ndim == 2:
            return vector.shape[1] == self.dimension
        else:
            return False
    
    def add_vector(self, vector: np.ndarray, image_id: str) -> bool:
        """
        Add a vector to the FAISS index with thread safety and persistence
        
        Args:
            vector: Feature vector as numpy array
            image_id: ID of the image
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("FAISS service not available")
            return False
        
        with self._lock:
            try:
                # Ensure vector is the right shape
                if vector.ndim == 1:
                    vector = vector.reshape(1, -1)
                
                # Validate dimension
                if not self._validate_vector_dimension(vector):
                    logger.error(f"Vector dimension {vector.shape} doesn't match index dimension {self.dimension}")
                    return False
                
                # Check for duplicate image_id
                if image_id in self.image_ids:
                    logger.warning(f"Image ID {image_id} already exists, skipping")
                    return False
                
                # Normalize vector for cosine similarity
                normalized_vector = self._normalize_vector(vector[0])
                normalized_vector = normalized_vector.reshape(1, -1)
                
                # Add normalized vector to index
                self.index.add(normalized_vector)
                
                # Store image ID and metadata
                self.image_ids.append(image_id)
                self.metadata[image_id] = {
                    'added_at': datetime.utcnow().isoformat(),
                    'vector_norm': float(np.linalg.norm(vector[0])),
                    'index_position': len(self.image_ids) - 1
                }
                
                # Update stats
                self._stats['add_count'] += 1
                self._stats['total_vectors'] = len(self.image_ids)
                self.operation_count += 1
                
                # Auto-save if configured
                if self.auto_save and self.operation_count % self.save_interval == 0:
                    self.save_index()
                
                logger.debug(f"Added normalized vector for image {image_id} to FAISS index")
                return True
                
            except Exception as e:
                logger.error(f"Error adding vector to FAISS index: {e}")
                return False
    
    def search_similar(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar vectors using cosine similarity with robust error handling
        
        Args:
            query_vector: Query vector as numpy array
            k: Number of similar vectors to return
            
        Returns:
            List of tuples (image_id, similarity_score) where higher score = more similar
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("FAISS service not available")
            return []
        
        with self._lock:
            try:
                if self.index.ntotal == 0:
                    logger.warning("FAISS index is empty")
                    return []
                
                # Ensure vector is the right shape
                if query_vector.ndim == 1:
                    query_vector = query_vector.reshape(1, -1)
                
                # Validate dimension
                if not self._validate_vector_dimension(query_vector):
                    logger.error(f"Query vector dimension {query_vector.shape} doesn't match index dimension {self.dimension}")
                    return []
                
                # Normalize query vector for cosine similarity
                normalized_query = self._normalize_vector(query_vector[0])
                normalized_query = normalized_query.reshape(1, -1)
                
                # Search returns cosine similarities (higher = more similar)
                similarities, indices = self.index.search(normalized_query, min(k, self.index.ntotal))
                
                # Convert to results format
                results = []
                for i, (sim, idx) in enumerate(zip(similarities[0], indices[0])):
                    if 0 <= idx < len(self.image_ids):
                        image_id = self.image_ids[idx]
                        # Return similarity score (higher = more similar)
                        similarity_score = float(sim)
                        results.append((image_id, similarity_score))
                    else:
                        logger.warning(f"Invalid index {idx} returned by FAISS search")
                
                # Update stats
                self._stats['search_count'] += 1
                
                return results
                
            except Exception as e:
                logger.error(f"Error searching FAISS index: {e}")
                return []
    
    def save_index(self) -> bool:
        """
        Save the FAISS index and metadata to disk with error handling
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("FAISS service not available")
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
                
                # Save stats
                stats_file = f"{self.index_path}_stats.json"
                self._stats['last_save_time'] = datetime.utcnow().isoformat()
                with open(stats_file, 'w') as f:
                    json.dump(self._stats, f, indent=2)
                
                logger.info(f"Successfully saved FAISS index with {self.index.ntotal} vectors")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save FAISS index: {e}")
                return False
    
    def load_index(self) -> bool:
        """
        Load the FAISS index and metadata from disk with corruption detection
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS library not available")
            return False
        
        with self._lock:
            try:
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
                
                # Load stats
                stats_file = f"{self.index_path}_stats.json"
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        loaded_stats = json.load(f)
                        self._stats.update(loaded_stats)
                
                # Validate consistency
                if not self._validate_index_consistency():
                    logger.error("Index consistency validation failed")
                    self._stats['corruption_detected'] = True
                    return False
                
                self._stats['last_load_time'] = datetime.utcnow().isoformat()
                self._stats['total_vectors'] = len(self.image_ids)
                
                logger.info(f"Successfully loaded FAISS index with {self.index.ntotal} vectors")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._stats['corruption_detected'] = True
                return False
    
    def _validate_index_consistency(self) -> bool:
        """
        Validate consistency between FAISS index and metadata
        
        Returns:
            True if consistent, False otherwise
        """
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
    
    def rebuild_index(self) -> bool:
        """
        Rebuild the index from scratch (useful for corruption recovery)
        
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE:
            logger.error("FAISS library not available")
            return False
        
        with self._lock:
            try:
                logger.info("Starting index rebuild...")
                
                # Create new index
                new_index = faiss.IndexFlatIP(self.dimension)
                
                # If we have vectors to rebuild from
                if self.index and self.index.ntotal > 0:
                    # Reconstruct all vectors and re-add them
                    for i in range(self.index.ntotal):
                        try:
                            vector = self.index.reconstruct(i)
                            new_index.add(vector.reshape(1, -1))
                        except Exception as e:
                            logger.error(f"Failed to reconstruct vector {i}: {e}")
                            # Skip corrupted vectors
                            continue
                
                # Replace the old index
                self.index = new_index
                
                # Update stats
                self._stats['rebuild_count'] += 1
                self._stats['corruption_detected'] = False
                self._stats['total_vectors'] = self.index.ntotal
                
                # Save the rebuilt index
                self.save_index()
                
                logger.info(f"Index rebuild completed with {self.index.ntotal} vectors")
                return True
                
            except Exception as e:
                logger.error(f"Failed to rebuild index: {e}")
                return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the FAISS index
        
        Returns:
            Dictionary containing index statistics and health information
        """
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'dimension': self.dimension,
                'index_path': self.index_path,
                'vectors_in_index': self.index.ntotal if self.index else 0,
                'image_ids_count': len(self.image_ids),
                'metadata_count': len(self.metadata),
                'auto_save_enabled': self.auto_save,
                'save_interval': self.save_interval,
                'operation_count': self.operation_count,
                'is_available': self.is_available(),
                'index_type': 'IndexFlatIP' if self.index else None,
                'thread_safe': True,
                'faiss_available': FAISS_AVAILABLE
            })
            
            # Add memory usage estimate
            if self.index:
                # Rough estimate: dimension * ntotal * 4 bytes (float32)
                estimated_memory_mb = (self.dimension * self.index.ntotal * 4) / (1024 * 1024)
                stats['estimated_memory_mb'] = round(estimated_memory_mb, 2)
            
            return stats
    
    def is_available(self) -> bool:
        """Check if the service is available and healthy"""
        return (FAISS_AVAILABLE and 
                self.index is not None and 
                not self._stats.get('corruption_detected', False))
    
    def add_vectors_batch(self, vectors: np.ndarray, image_ids: List[str]) -> List[bool]:
        """
        Add multiple vectors in batch for efficiency
        
        Args:
            vectors: Array of vectors (n_vectors, dimension)
            image_ids: List of image IDs corresponding to vectors
            
        Returns:
            List of boolean results for each vector
        """
        if not FAISS_AVAILABLE or self.index is None:
            logger.error("FAISS service not available")
            return [False] * len(image_ids)
        
        if len(vectors) != len(image_ids):
            logger.error("Number of vectors and image IDs must match")
            return [False] * len(image_ids)
        
        results = []
        with self._lock:
            try:
                # Process vectors in batch
                normalized_vectors = []
                valid_ids = []
                
                for i, (vector, image_id) in enumerate(zip(vectors, image_ids)):
                    try:
                        # Skip duplicates
                        if image_id in self.image_ids:
                            logger.warning(f"Image ID {image_id} already exists, skipping")
                            results.append(False)
                            continue
                        
                        # Validate and normalize
                        if not self._validate_vector_dimension(vector):
                            logger.error(f"Vector {i} has invalid dimension")
                            results.append(False)
                            continue
                        
                        normalized_vector = self._normalize_vector(vector)
                        normalized_vectors.append(normalized_vector)
                        valid_ids.append(image_id)
                        results.append(True)
                        
                    except Exception as e:
                        logger.error(f"Error processing vector {i}: {e}")
                        results.append(False)
                
                # Add valid vectors to index
                if normalized_vectors:
                    batch_vectors = np.array(normalized_vectors, dtype=np.float32)
                    self.index.add(batch_vectors)
                    
                    # Update metadata
                    for image_id in valid_ids:
                        self.image_ids.append(image_id)
                        self.metadata[image_id] = {
                            'added_at': datetime.utcnow().isoformat(),
                            'index_position': len(self.image_ids) - 1
                        }
                    
                    # Update stats
                    self._stats['add_count'] += len(valid_ids)
                    self._stats['total_vectors'] = len(self.image_ids)
                    self.operation_count += len(valid_ids)
                    
                    # Auto-save if needed
                    if self.auto_save and self.operation_count % self.save_interval == 0:
                        self.save_index()
                    
                    logger.info(f"Added {len(valid_ids)} vectors to FAISS index in batch")
                
                return results
                
            except Exception as e:
                logger.error(f"Error in batch vector addition: {e}")
                return [False] * len(image_ids)
    
    def clear_index(self):
        """Clear the entire index and reset all data"""
        with self._lock:
            try:
                if FAISS_AVAILABLE:
                    self.index = faiss.IndexFlatIP(self.dimension)
                self.image_ids = []
                self.metadata = {}
                self.operation_count = 0
                
                # Reset stats
                self._stats.update({
                    'total_vectors': 0,
                    'search_count': 0,
                    'add_count': 0,
                    'corruption_detected': False
                })
                
                # Save empty index
                if self.auto_save:
                    self.save_index()
                
                logger.info("FAISS index cleared successfully")
                
            except Exception as e:
                logger.error(f"Error clearing FAISS index: {e}")
    
    def get_vector_by_id(self, image_id: str) -> Optional[np.ndarray]:
        """
        Retrieve a vector by image ID
        
        Args:
            image_id: ID of the image
            
        Returns:
            Vector as numpy array or None if not found
        """
        if not FAISS_AVAILABLE or self.index is None:
            return None
        
        with self._lock:
            try:
                if image_id not in self.image_ids:
                    return None
                
                idx = self.image_ids.index(image_id)
                vector = self.index.reconstruct(idx)
                return vector
                
            except Exception as e:
                logger.error(f"Error retrieving vector for {image_id}: {e}")
                return None
    
    def remove_vector(self, image_id: str) -> bool:
        """
        Remove a vector from the index (requires rebuild)
        
        Args:
            image_id: ID of the image to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not FAISS_AVAILABLE or self.index is None:
            return False
        
        with self._lock:
            try:
                if image_id not in self.image_ids:
                    logger.warning(f"Image ID {image_id} not found in index")
                    return False
                
                # Remove from tracking lists
                idx = self.image_ids.index(image_id)
                self.image_ids.pop(idx)
                
                if image_id in self.metadata:
                    del self.metadata[image_id]
                
                # Update positions in metadata
                for i, img_id in enumerate(self.image_ids):
                    if img_id in self.metadata:
                        self.metadata[img_id]['index_position'] = i
                
                # Rebuild index (FAISS doesn't support efficient single vector removal)
                success = self.rebuild_index()
                
                if success:
                    logger.info(f"Removed vector for image {image_id}")
                
                return success
                
            except Exception as e:
                logger.error(f"Error removing vector {image_id}: {e}")
                return False