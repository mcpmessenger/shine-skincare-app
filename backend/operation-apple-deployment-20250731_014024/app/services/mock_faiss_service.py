"""
Mock FAISS Service for Vercel deployment
This provides the same interface as FAISSService but without FAISS dependency
"""
import logging
import hashlib
import math
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class MockFAISSService:
    """Mock implementation of FAISS Service for deployment testing"""
    
    def __init__(self, dimension: int = 2048, index_path: str = 'mock_index'):
        self.dimension = dimension
        self.index_path = index_path
        self._vectors = {}  # Store vectors in memory: {id: vector}
        self._next_id = 0
        self._available = True
        logger.info(f"Mock FAISS Service initialized (dimension: {dimension})")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector to unit length"""
        try:
            # Calculate norm
            norm = math.sqrt(sum(x * x for x in vector))
            if norm == 0:
                return [0.0] * len(vector)
            return [x / norm for x in vector]
        except Exception as e:
            logger.error(f"Vector normalization error: {e}")
            return [0.0] * self.dimension
    
    def add_vector(self, vector: List[float], metadata_id: str = None) -> bool:
        """Add a vector to the mock index"""
        try:
            # Convert to list if needed
            if hasattr(vector, 'tolist'):
                vector = vector.tolist()
            
            # Normalize the vector
            normalized_vector = self.normalize_vector(vector)
            
            # Use provided ID or generate one
            vector_id = metadata_id or str(self._next_id)
            self._next_id += 1
            
            # Store the vector
            self._vectors[vector_id] = normalized_vector
            
            logger.info(f"Vector added to mock index: {vector_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add vector: {e}")
            return False
    
    def search_similar(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar vectors using cosine similarity"""
        try:
            if not self._vectors:
                logger.warning("No vectors in mock index")
                return []
            
            # Convert to list if needed
            if hasattr(query_vector, 'tolist'):
                query_vector = query_vector.tolist()
            
            # Normalize query vector
            query_normalized = self.normalize_vector(query_vector)
            
            # Calculate similarities
            similarities = []
            for vector_id, stored_vector in self._vectors.items():
                # Cosine similarity (dot product of normalized vectors)
                similarity = sum(a * b for a, b in zip(query_normalized, stored_vector))
                # Convert similarity to distance (FAISS uses distance, lower is better)
                distance = 1.0 - similarity
                similarities.append((vector_id, distance))
            
            # Sort by distance (ascending - lower distance = higher similarity)
            similarities.sort(key=lambda x: x[1])
            
            # Return top k results
            results = similarities[:k]
            logger.info(f"Mock similarity search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Mock similarity search error: {e}")
            return []
    
    def get_index_info(self) -> dict:
        """Get information about the mock index"""
        return {
            'type': 'mock_faiss',
            'dimension': self.dimension,
            'total_vectors': len(self._vectors),
            'index_path': self.index_path,
            'available': self._available
        }
    
    def save_index(self) -> bool:
        """Mock save operation"""
        logger.info("Mock index save operation (no-op)")
        return True
    
    def load_index(self) -> bool:
        """Mock load operation"""
        logger.info("Mock index load operation (no-op)")
        return True