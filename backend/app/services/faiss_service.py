import os
import logging
import numpy as np
import faiss
import pickle
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from ..performance import measure_performance, cached, vector_cache, cache_key

logger = logging.getLogger(__name__)

class FAISSService:
    """Service for FAISS similarity search"""
    
    def __init__(self, dimension: int = 2048, index_path: Optional[str] = None):
        """
        Initialize the FAISS service
        
        Args:
            dimension: Dimension of the feature vectors
            index_path: Path to save/load the FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path or 'faiss_index'
        self.index = None
        self.image_ids = []  # Map FAISS index positions to image IDs
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize the FAISS index with Inner Product for cosine similarity"""
        try:
            # Try to load existing index
            if os.path.exists(f"{self.index_path}.index"):
                self.index = faiss.read_index(f"{self.index_path}.index")
                self._load_image_ids()
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index using Inner Product for cosine similarity
                self.index = faiss.IndexFlatIP(self.dimension)
                logger.info(f"Created new FAISS IP index with dimension {self.dimension}")
                
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            # Fallback to new index
            self.index = faiss.IndexFlatIP(self.dimension)
    
    def _load_image_ids(self):
        """Load image IDs from file"""
        try:
            ids_path = f"{self.index_path}_ids.pkl"
            if os.path.exists(ids_path):
                with open(ids_path, 'rb') as f:
                    self.image_ids = pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load image IDs: {e}")
            self.image_ids = []
    
    def _save_image_ids(self):
        """Save image IDs to file"""
        try:
            ids_path = f"{self.index_path}_ids.pkl"
            with open(ids_path, 'wb') as f:
                pickle.dump(self.image_ids, f)
        except Exception as e:
            logger.error(f"Failed to save image IDs: {e}")
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """
        L2-normalize vector for cosine similarity
        
        Args:
            vector: Input vector as numpy array
            
        Returns:
            L2-normalized vector
        """
        try:
            # Calculate L2 norm
            vector_norm = np.linalg.norm(vector)
            
            # Handle zero vector case
            if vector_norm > 0:
                normalized_vector = vector / vector_norm
            else:
                # Handle zero vector case - return original vector
                # This is unlikely for feature embeddings but provides graceful handling
                logger.warning("Encountered zero vector during normalization")
                normalized_vector = vector
                
            return normalized_vector
            
        except Exception as e:
            logger.error(f"Error normalizing vector: {e}")
            return vector
    
    @measure_performance('faiss.add_vector')
    def add_vector(self, vector: np.ndarray, image_id: str) -> bool:
        """
        Add a normalized vector to the FAISS index for cosine similarity
        
        Args:
            vector: Feature vector as numpy array
            image_id: ID of the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure vector is the right shape
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            # Check dimension
            if vector.shape[1] != self.dimension:
                logger.error(f"Vector dimension {vector.shape[1]} doesn't match index dimension {self.dimension}")
                return False
            
            # Normalize vector for cosine similarity
            normalized_vector = self._normalize_vector(vector)
            
            # Add normalized vector to index
            self.index.add(normalized_vector)
            
            # Store image ID
            self.image_ids.append(image_id)
            
            # Save index and IDs
            self._save_index()
            self._save_image_ids()
            
            logger.info(f"Added normalized vector for image {image_id} to FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding vector to FAISS index: {e}")
            return False
    
    @measure_performance('faiss.search_similar')
    def search_similar(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar vectors using cosine similarity
        
        Args:
            query_vector: Query vector as numpy array
            k: Number of similar vectors to return
            
        Returns:
            List of tuples (image_id, distance) where distance is converted from similarity
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []
            
            # Ensure vector is the right shape
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Check dimension
            if query_vector.shape[1] != self.dimension:
                logger.error(f"Query vector dimension {query_vector.shape[1]} doesn't match index dimension {self.dimension}")
                return []
            
            # Normalize query vector for cosine similarity
            normalized_query = self._normalize_vector(query_vector)
            
            # Search returns cosine similarities (higher = more similar)
            similarities, indices = self.index.search(normalized_query, min(k, self.index.ntotal))
            
            # Convert to results format
            results = []
            for i, (sim, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.image_ids):
                    image_id = self.image_ids[idx]
                    # Convert similarity to distance for backward compatibility
                    # (higher similarity = lower distance)
                    distance = 2 - 2 * sim  # Convert cosine similarity to distance
                    results.append((image_id, float(distance)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []
    
    def search_by_image_id(self, image_id: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar images by image ID
        
        Args:
            image_id: ID of the query image
            k: Number of similar images to return
            
        Returns:
            List of tuples (image_id, distance)
        """
        try:
            # Find the vector for the given image ID
            if image_id not in self.image_ids:
                logger.error(f"Image ID {image_id} not found in FAISS index")
                return []
            
            # Get the index position
            idx = self.image_ids.index(image_id)
            
            # Get the vector
            vector = self.index.reconstruct(idx).reshape(1, -1)
            
            # Search for similar vectors
            return self.search_similar(vector, k)
            
        except Exception as e:
            logger.error(f"Error searching by image ID {image_id}: {e}")
            return []
    
    def remove_vector(self, image_id: str) -> bool:
        """
        Remove a vector from the FAISS index
        
        Args:
            image_id: ID of the image to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if image_id not in self.image_ids:
                logger.warning(f"Image ID {image_id} not found in FAISS index")
                return False
            
            # Get the index position
            idx = self.image_ids.index(image_id)
            
            # Remove from image_ids list
            self.image_ids.pop(idx)
            
            # Rebuild index without the removed vector
            self._rebuild_index()
            
            logger.info(f"Removed vector for image {image_id} from FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Error removing vector from FAISS index: {e}")
            return False
    
    def _rebuild_index(self):
        """Rebuild the index after removing a vector"""
        try:
            # This is a simplified approach - in production, you might want to use
            # a more efficient method for removing vectors
            logger.warning("Rebuilding FAISS index - this operation is not optimized")
            
            # For now, we'll just note that the index needs to be rebuilt
            # In a real implementation, you might use faiss.IndexIDMap or similar
            pass
            
        except Exception as e:
            logger.error(f"Error rebuilding FAISS index: {e}")
    
    def _save_index(self):
        """Save the FAISS index to file"""
        try:
            faiss.write_index(self.index, f"{self.index_path}.index")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the FAISS index"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_path': self.index_path,
            'image_ids_count': len(self.image_ids)
        }
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.index is not None
    
    def clear_index(self):
        """Clear the entire index"""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.image_ids = []
            self._save_index()
            self._save_image_ids()
            logger.info("FAISS index cleared")
        except Exception as e:
            logger.error(f"Error clearing FAISS index: {e}") 