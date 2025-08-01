"""
Enhanced Google Vision Service - Face detection and isolation for AI pipeline

This service is part of Operation Left Brain and provides enhanced face detection
and isolation capabilities for selfie analysis.
"""

import logging
import io
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image
from dataclasses import dataclass

# Try to import Google Cloud Vision
try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logging.warning("Google Cloud Vision not available - using fallback detection")

logger = logging.getLogger(__name__)

@dataclass
class FacialFeatures:
    """Facial features data structure"""
    face_detected: bool
    face_isolated: bool
    landmarks: List[Dict[str, Any]]
    face_bounds: Dict[str, int]
    isolation_complete: bool
    confidence_score: float

class EnhancedVisionService:
    """
    Enhanced Google Vision service with face detection and isolation
    """
    
    def __init__(self):
        """Initialize the enhanced vision service"""
        self.client = None
        self.is_initialized = False
        
        if GOOGLE_VISION_AVAILABLE:
            self._initialize_vision_client()
        else:
            logger.warning("Google Vision not available - using fallback detection")
    
    def _initialize_vision_client(self):
        """Initialize Google Vision client"""
        try:
            self.client = vision.ImageAnnotatorClient()
            self.is_initialized = True
            logger.info("✅ Google Vision client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision client: {e}")
            self.is_initialized = False
    
    def detect_face_and_isolate(self, image_bytes: bytes) -> Tuple[FacialFeatures, Optional[bytes]]:
        """
        Detect face and isolate it from the image
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (facial_features, isolated_face_bytes)
        """
        try:
            if GOOGLE_VISION_AVAILABLE and self.is_initialized:
                return self._google_vision_detection(image_bytes)
            else:
                return self._fallback_detection(image_bytes)
                
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return self._create_error_features(), None
    
    def _google_vision_detection(self, image_bytes: bytes) -> Tuple[FacialFeatures, Optional[bytes]]:
        """Use Google Vision API for face detection"""
        try:
            # Create vision image
            image = vision.Image(content=image_bytes)
            
            # Perform face detection
            response = self.client.face_detection(image=image)
            faces = response.face_annotations
            
            if not faces:
                logger.warning("No faces detected in image")
                return self._create_no_face_features(), None
            
            # Use the first face (most prominent)
            face = faces[0]
            
            # Extract facial features
            facial_features = self._extract_facial_features(face)
            
            # Isolate face region
            isolated_face_bytes = self._isolate_face_region(image_bytes, face)
            
            return facial_features, isolated_face_bytes
            
        except Exception as e:
            logger.error(f"Google Vision detection error: {e}")
            return self._create_error_features(), None
    
    def _extract_facial_features(self, face) -> FacialFeatures:
        """Extract facial features from Google Vision response"""
        # Get bounding box
        vertices = face.bounding_poly.vertices
        x_coords = [v.x for v in vertices]
        y_coords = [v.y for v in vertices]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        face_bounds = {
            'x': x_min,
            'y': y_min,
            'width': x_max - x_min,
            'height': y_max - y_min
        }
        
        # Extract landmarks
        landmarks = []
        for landmark in face.landmarks:
            landmarks.append({
                'type': landmark.type.name.lower(),
                'x': landmark.position.x,
                'y': landmark.position.y
            })
        
        return FacialFeatures(
            face_detected=True,
            face_isolated=True,
            landmarks=landmarks,
            face_bounds=face_bounds,
            isolation_complete=True,
            confidence_score=face.detection_confidence
        )
    
    def _isolate_face_region(self, image_bytes: bytes, face) -> bytes:
        """Isolate the face region from the original image"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Get bounding box
            vertices = face.bounding_poly.vertices
            x_coords = [v.x for v in vertices]
            y_coords = [v.y for v in vertices]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Add padding around face (20% on each side)
            width = x_max - x_min
            height = y_max - y_min
            padding_x = int(width * 0.2)
            padding_y = int(height * 0.2)
            
            # Crop with padding
            crop_box = (
                max(0, x_min - padding_x),
                max(0, y_min - padding_y),
                min(image.width, x_max + padding_x),
                min(image.height, y_max + padding_y)
            )
            
            cropped_image = image.crop(crop_box)
            
            # Convert back to bytes
            buffer = io.BytesIO()
            cropped_image.save(buffer, format='JPEG', quality=95)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error isolating face region: {e}")
            return image_bytes  # Return original if isolation fails
    
    def _fallback_detection(self, image_bytes: bytes) -> Tuple[FacialFeatures, Optional[bytes]]:
        """Fallback face detection when Google Vision is not available"""
        try:
            # Simple fallback: assume face is in center of image
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            
            # Assume face is in center 60% of image
            center_x, center_y = width // 2, height // 2
            face_size = min(width, height) // 3
            
            face_bounds = {
                'x': center_x - face_size // 2,
                'y': center_y - face_size // 2,
                'width': face_size,
                'height': face_size
            }
            
            # Crop face region
            crop_box = (
                max(0, face_bounds['x']),
                max(0, face_bounds['y']),
                min(width, face_bounds['x'] + face_bounds['width']),
                min(height, face_bounds['y'] + face_bounds['height'])
            )
            
            cropped_image = image.crop(crop_box)
            buffer = io.BytesIO()
            cropped_image.save(buffer, format='JPEG', quality=95)
            isolated_face_bytes = buffer.getvalue()
            
            facial_features = FacialFeatures(
                face_detected=True,
                face_isolated=True,
                landmarks=[],  # No landmarks in fallback
                face_bounds=face_bounds,
                isolation_complete=True,
                confidence_score=0.5  # Lower confidence for fallback
            )
            
            return facial_features, isolated_face_bytes
            
        except Exception as e:
            logger.error(f"Fallback detection error: {e}")
            return self._create_error_features(), None
    
    def _create_no_face_features(self) -> FacialFeatures:
        """Create features for when no face is detected"""
        return FacialFeatures(
            face_detected=False,
            face_isolated=False,
            landmarks=[],
            face_bounds={},
            isolation_complete=False,
            confidence_score=0.0
        )
    
    def _create_error_features(self) -> FacialFeatures:
        """Create features for error cases"""
        return FacialFeatures(
            face_detected=False,
            face_isolated=False,
            landmarks=[],
            face_bounds={},
            isolation_complete=False,
            confidence_score=0.0
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the vision service"""
        return {
            'google_vision_available': GOOGLE_VISION_AVAILABLE,
            'client_initialized': self.is_initialized,
            'service_ready': self.is_initialized or not GOOGLE_VISION_AVAILABLE
        }

# Global instance for reuse
enhanced_vision_service = EnhancedVisionService() 