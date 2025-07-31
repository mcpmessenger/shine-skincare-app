import os
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
from PIL import Image
import io

from .scin_skin_condition_service import SCINSkinConditionService
from .google_vision_service import GoogleVisionService

logger = logging.getLogger(__name__)

class EnhancedVectorizationService:
    """Enhanced vectorization service that combines Google Vision and skin condition detection"""
    
    def __init__(self):
        """Initialize the enhanced vectorization service"""
        self.google_vision_service = GoogleVisionService()
        self.skin_condition_service = SCINSkinConditionService()
        self.vector_dimension = 2048
        
    def vectorize_skin_image(self, image_data: bytes,
                           ethnicity: Optional[str] = None,
                           age: Optional[int] = None) -> Dict[str, Any]:
        """
        Vectorize skin image using both Google Vision and skin condition detection
        
        Args:
            image_data: Image data as bytes
            ethnicity: Optional ethnicity for context
            age: Optional age for context
            
        Returns:
            Dictionary with vectorization results
        """
        try:
            logger.info("Vectorizing skin image with enhanced analysis")
            
            # Step 1: Google Vision analysis for facial features
            vision_result = self.google_vision_service.analyze_image_from_bytes(image_data)
            
            # Step 2: Skin condition detection
            condition_result = self.skin_condition_service.detect_skin_conditions(
                image_data, ethnicity, age
            )
            
            # Step 3: Combine results into enhanced vector
            enhanced_vector = self._create_enhanced_vector(vision_result, condition_result)
            
            # Step 4: Prepare response
            response = {
                'status': 'success',
                'vector': enhanced_vector.tolist(),
                'vector_dimension': self.vector_dimension,
                'vision_analysis': vision_result,
                'skin_conditions': condition_result,
                'ethnicity_context': ethnicity,
                'age_context': age,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error vectorizing skin image: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_enhanced_vector(self, vision_result: Dict[str, Any], 
                               condition_result: Dict[str, Any]) -> np.ndarray:
        """Create enhanced vector combining vision and condition data"""
        try:
            # Start with condition vector as base
            condition_vector = np.array(condition_result.get('condition_vector', []))
            if len(condition_vector) == 0:
                condition_vector = np.zeros(self.vector_dimension, dtype=np.float32)
            
            # Extract vision features
            vision_features = self._extract_vision_features(vision_result)
            
            # Combine features (simple concatenation for now)
            # In production, you might use a more sophisticated fusion method
            combined_vector = np.zeros(self.vector_dimension, dtype=np.float32)
            
            # Use first half for condition features
            condition_half = min(len(condition_vector) // 2, self.vector_dimension // 2)
            combined_vector[:condition_half] = condition_vector[:condition_half]
            
            # Use second half for vision features
            vision_half = self.vector_dimension - condition_half
            if len(vision_features) > 0:
                vision_features_padded = np.pad(
                    vision_features, 
                    (0, max(0, vision_half - len(vision_features))), 
                    'constant'
                )
                combined_vector[condition_half:] = vision_features_padded[:vision_half]
            
            # Normalize the combined vector
            norm = np.linalg.norm(combined_vector)
            if norm > 0:
                combined_vector = combined_vector / norm
            
            return combined_vector
            
        except Exception as e:
            logger.error(f"Error creating enhanced vector: {e}")
            return np.zeros(self.vector_dimension, dtype=np.float32)
    
    def _extract_vision_features(self, vision_result: Dict[str, Any]) -> np.ndarray:
        """Extract features from Google Vision analysis"""
        try:
            features = []
            
            if vision_result.get('status') == 'success':
                results = vision_result.get('results', {})
                
                # Extract face detection features
                face_data = results.get('face_detection', {})
                if face_data:
                    # Add face confidence
                    features.append(face_data.get('confidence', 0.0))
                    
                    # Add face bounds area
                    bounds = face_data.get('bounds', {})
                    if bounds:
                        width = bounds.get('width', 0)
                        height = bounds.get('height', 0)
                        features.append(width * height)  # Area
                        features.append(width / max(height, 1))  # Aspect ratio
                
                # Extract image properties
                image_props = results.get('image_properties', {})
                if image_props:
                    # Add dominant colors
                    colors = image_props.get('dominant_colors', [])
                    for color in colors[:3]:  # Top 3 colors
                        features.extend([
                            color.get('red', 0) / 255.0,
                            color.get('green', 0) / 255.0,
                            color.get('blue', 0) / 255.0,
                            color.get('score', 0.0)
                        ])
                
                # Extract label features
                labels = results.get('label_detection', {})
                if labels:
                    # Add label confidence scores
                    label_scores = labels.get('label_scores', [])
                    features.extend(label_scores[:10])  # Top 10 labels
            
            # Pad to ensure we have some features
            if len(features) == 0:
                features = [0.0] * 10
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error extracting vision features: {e}")
            return np.zeros(10, dtype=np.float32)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the enhanced vectorization service"""
        return {
            'service_type': 'enhanced_vectorization',
            'vector_dimension': self.vector_dimension,
            'google_vision_available': self.google_vision_service.is_available(),
            'skin_condition_available': self.skin_condition_service.is_available(),
            'skin_condition_model': self.skin_condition_service.get_model_info()
        }
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return (self.google_vision_service.is_available() and 
                self.skin_condition_service.is_available()) 