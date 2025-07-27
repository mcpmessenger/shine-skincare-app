"""
Mock Vectorization Service for Vercel deployment
This provides the same interface as ImageVectorizationService but without heavy dependencies
"""
import logging
import hashlib
from typing import Optional, List

logger = logging.getLogger(__name__)

class MockVectorizationService:
    """Mock implementation of Image Vectorization Service for deployment testing"""
    
    def __init__(self):
        self.model_name = "mock_vectorization_model"
        self.dimension = 2048
        self._available = True
        logger.info("Mock Vectorization Service initialized")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def vectorize_image_from_bytes(self, image_data: bytes) -> Optional[List[float]]:
        """
        Mock image vectorization that returns consistent vectors based on image hash
        """
        try:
            # Generate consistent hash from image data
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Generate a consistent vector based on the hash
            vector = []
            for i in range(self.dimension):
                # Use different parts of the hash to generate vector components
                hash_segment = image_hash[(i % len(image_hash))]
                # Convert hex character to float between -1 and 1
                value = (int(hash_segment, 16) - 7.5) / 7.5
                vector.append(value)
            
            logger.info(f"Mock vectorization completed for image hash: {image_hash[:8]}")
            return vector
            
        except Exception as e:
            logger.error(f"Mock vectorization error: {e}")
            return None
    
    def get_model_info(self) -> dict:
        """Get information about the mock model"""
        return {
            'name': self.model_name,
            'dimension': self.dimension,
            'type': 'mock',
            'status': 'available' if self._available else 'unavailable',
            'description': 'Mock vectorization service for testing and deployment'
        }