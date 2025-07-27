"""
Mock Skin Classifier Service for Vercel deployment
This provides the same interface as EnhancedSkinTypeClassifier but without heavy dependencies
"""
import logging
import hashlib
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MockSkinClassifierService:
    """Mock implementation of Enhanced Skin Type Classifier for deployment testing"""
    
    def __init__(self):
        self.service_name = "mock_skin_classifier"
        self._available = True
        self._confidence_threshold = 0.5
        logger.info("Mock Skin Classifier Service initialized")
    
    def is_available(self):
        """Check if the service is available"""
        return self._available
    
    def classify_skin_type(self, image_data: bytes, ethnicity: Optional[str] = None) -> Dict[str, Any]:
        """
        Mock skin type classification that returns consistent results based on image hash
        """
        try:
            # Generate consistent hash from image data
            image_hash = hashlib.md5(image_data).hexdigest()
            hash_int = int(image_hash[:8], 16)
            
            # Generate mock Fitzpatrick classification
            fitzpatrick_types = ['I', 'II', 'III', 'IV', 'V', 'VI']
            fitzpatrick_type = fitzpatrick_types[hash_int % len(fitzpatrick_types)]
            
            fitzpatrick_descriptions = {
                'I': 'Very fair skin, always burns, never tans',
                'II': 'Fair skin, usually burns, tans minimally',
                'III': 'Medium skin, sometimes burns, tans gradually',
                'IV': 'Olive skin, rarely burns, tans easily',
                'V': 'Brown skin, very rarely burns, tans very easily',
                'VI': 'Dark brown/black skin, never burns, tans very easily'
            }
            
            # Generate mock Monk tone
            monk_tones = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            monk_tone = monk_tones[hash_int % len(monk_tones)]
            
            monk_descriptions = {
                '1': 'Very light skin tone',
                '2': 'Light skin tone',
                '3': 'Light-medium skin tone',
                '4': 'Medium skin tone',
                '5': 'Medium-tan skin tone',
                '6': 'Tan skin tone',
                '7': 'Medium-dark skin tone',
                '8': 'Dark skin tone',
                '9': 'Very dark skin tone',
                '10': 'Deepest skin tone'
            }
            
            # Calculate mock confidence
            base_confidence = 0.6 + (hash_int % 40) / 100.0  # 0.6 to 1.0
            
            # Adjust confidence based on ethnicity if provided
            ethnicity_considered = bool(ethnicity)
            if ethnicity_considered:
                base_confidence += 0.1  # Bonus for having ethnicity context
            
            confidence = min(1.0, base_confidence)
            
            result = {
                'fitzpatrick_type': fitzpatrick_type,
                'fitzpatrick_description': fitzpatrick_descriptions[fitzpatrick_type],
                'monk_tone': monk_tone,
                'monk_description': monk_descriptions[monk_tone],
                'confidence': confidence,
                'ethnicity_considered': ethnicity_considered,
                'ethnicity': ethnicity or '',
                'service': 'mock_skin_classifier',
                'image_hash': image_hash[:8]
            }
            
            logger.info(f"Mock skin classification completed: {fitzpatrick_type}/{monk_tone} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Mock skin classification error: {e}")
            return {
                'fitzpatrick_type': 'III',
                'fitzpatrick_description': 'Medium skin, sometimes burns, tans gradually',
                'monk_tone': '5',
                'monk_description': 'Medium-tan skin tone',
                'confidence': 0.5,
                'ethnicity_considered': False,
                'ethnicity': '',
                'service': 'mock_skin_classifier',
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the mock model"""
        return {
            'name': 'Mock Enhanced Skin Type Classifier',
            'version': '1.0.0',
            'type': 'mock',
            'status': 'available' if self._available else 'unavailable',
            'confidence_threshold': self._confidence_threshold,
            'supported_scales': ['Fitzpatrick', 'Monk'],
            'description': 'Mock skin type classifier for testing and deployment'
        }
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Set the confidence threshold"""
        self._confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Mock classifier confidence threshold set to: {self._confidence_threshold}")