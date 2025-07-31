"""
Mock Google Vision Service for Vercel deployment
This provides the same interface as GoogleVisionService but without external dependencies
"""
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class MockGoogleVisionService:
    """Mock implementation of Google Vision Service for deployment testing"""
    
    def __init__(self):
        self.service_name = "mock_google_vision"
        self._available = True
        logger.info("Mock Google Vision Service initialized")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def analyze_image_from_bytes(self, image_data):
        """
        Mock image analysis that returns consistent results based on image hash
        """
        try:
            # Generate consistent hash from image data
            image_hash = hashlib.md5(image_data).hexdigest()
            hash_int = int(image_hash[:8], 16)
            
            # Generate mock face detection data
            face_confidence = (hash_int % 100) / 100.0
            faces_found = 1 if face_confidence > 0.3 else 0
            
            # Generate mock image properties
            brightness = ((hash_int >> 8) % 100) / 100.0
            contrast = ((hash_int >> 16) % 100) / 100.0
            
            # Generate mock labels
            mock_labels = [
                {"description": "Person", "score": 0.9},
                {"description": "Face", "score": 0.85},
                {"description": "Skin", "score": 0.8},
                {"description": "Human", "score": 0.75}
            ]
            
            # Add some variation based on hash
            if hash_int % 4 == 0:
                mock_labels.append({"description": "Smile", "score": 0.7})
            elif hash_int % 4 == 1:
                mock_labels.append({"description": "Beauty", "score": 0.65})
            elif hash_int % 4 == 2:
                mock_labels.append({"description": "Portrait", "score": 0.6})
            
            result = {
                'status': 'success',
                'results': {
                    'face_detection': {
                        'faces_found': faces_found,
                        'face_data': [{
                            'confidence': face_confidence,
                            'bounding_box': {
                                'x': 0.2, 'y': 0.2, 'width': 0.6, 'height': 0.6
                            }
                        }] if faces_found > 0 else []
                    },
                    'image_properties': {
                        'brightness': brightness,
                        'contrast': contrast,
                        'color_count': 5
                    },
                    'label_detection': {
                        'labels_found': len(mock_labels),
                        'labels': mock_labels
                    }
                },
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'mock_google_vision'
            }
            
            logger.info(f"Mock analysis completed for image hash: {image_hash[:8]}")
            return result
            
        except Exception as e:
            logger.error(f"Mock analysis error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'service': 'mock_google_vision'
            }
    
    def get_service_info(self):
        """Get service information"""
        return {
            'name': 'Mock Google Vision Service',
            'version': '1.0.0',
            'status': 'available' if self._available else 'unavailable',
            'type': 'mock',
            'description': 'Mock implementation for testing and deployment'
        }