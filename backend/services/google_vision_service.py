"""
Google Vision API Service for Operation Right Brain 🧠
Handles face detection and isolation from uploaded images.

Author: Manus AI
Date: August 2, 2025
"""

import logging
import base64
from typing import Optional, Tuple
import io
from PIL import Image
import numpy as np

from google.cloud import vision
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

class GoogleVisionService:
    """
    Service for interacting with Google Vision API.
    Implements BR2: Integration with Google Vision API for face detection and isolation.
    """
    
    def __init__(self):
        """Initialize the Google Vision service."""
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Vision API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision API client: {str(e)}")
            raise
    
    def detect_and_isolate_face(self, image_data: bytes) -> Optional[bytes]:
        """
        Detect and isolate face from image using Google Vision API.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Isolated face image as bytes, or None if no face detected
        """
        try:
            # Create image object for Google Vision API
            image = vision.Image(content=image_data)
            
            # Perform face detection
            response = self.client.face_detection(image=image)
            faces = response.face_annotations
            
            if not faces:
                logger.warning("No faces detected in image")
                return None
            
            # Get the largest face (most prominent)
            largest_face = max(faces, key=lambda face: 
                (face.bounding_poly.vertices[2].x - face.bounding_poly.vertices[0].x) *
                (face.bounding_poly.vertices[2].y - face.bounding_poly.vertices[0].y)
            )
            
            # Extract face region
            face_image = self._extract_face_region(image_data, largest_face)
            
            if face_image:
                logger.info("Face successfully detected and isolated")
                return face_image
            else:
                logger.warning("Failed to extract face region")
                return None
                
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google Vision API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return None
    
    def _extract_face_region(self, image_data: bytes, face_annotation) -> Optional[bytes]:
        """
        Extract the face region from the original image.
        
        Args:
            image_data: Original image bytes
            face_annotation: Google Vision face annotation
            
        Returns:
            Cropped face image as bytes
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Get face bounding box
            vertices = face_annotation.bounding_poly.vertices
            left = vertices[0].x
            top = vertices[0].y
            right = vertices[2].x
            bottom = vertices[2].y
            
            # Add padding around face (20% on each side)
            width = right - left
            height = bottom - top
            padding_x = int(width * 0.2)
            padding_y = int(height * 0.2)
            
            # Ensure coordinates are within image bounds
            left = max(0, left - padding_x)
            top = max(0, top - padding_y)
            right = min(image.width, right + padding_x)
            bottom = min(image.height, bottom + padding_y)
            
            # Crop the face region
            face_crop = image.crop((left, top, right, bottom))
            
            # Convert back to bytes
            output = io.BytesIO()
            face_crop.save(output, format='JPEG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error extracting face region: {str(e)}")
            return None
    
    def check_health(self) -> dict:
        """
        Check the health status of Google Vision API.
        
        Returns:
            Health status dictionary
        """
        try:
            # Create a simple test image
            test_image = Image.new('RGB', (100, 100), color='white')
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='JPEG')
            test_data = test_bytes.getvalue()
            
            # Test API call
            image = vision.Image(content=test_data)
            response = self.client.face_detection(image=image)
            
            return {
                "status": "healthy",
                "service": "Google Vision API",
                "message": "API is responding correctly"
            }
            
        except Exception as e:
            logger.error(f"Google Vision API health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "Google Vision API",
                "error": str(e)
            }
    
    def get_face_attributes(self, image_data: bytes) -> dict:
        """
        Get detailed face attributes from Google Vision API.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary containing face attributes
        """
        try:
            image = vision.Image(content=image_data)
            response = self.client.face_detection(image=image)
            faces = response.face_annotations
            
            if not faces:
                return {"error": "No faces detected"}
            
            face = faces[0]  # Get first face
            
            attributes = {
                "confidence": face.detection_confidence,
                "joy_likelihood": face.joy_likelihood,
                "sorrow_likelihood": face.sorrow_likelihood,
                "anger_likelihood": face.anger_likelihood,
                "surprise_likelihood": face.surprise_likelihood,
                "head_angle": {
                    "roll": face.roll_angle,
                    "pan": face.pan_angle,
                    "tilt": face.tilt_angle
                },
                "bounding_box": {
                    "left": face.bounding_poly.vertices[0].x,
                    "top": face.bounding_poly.vertices[0].y,
                    "right": face.bounding_poly.vertices[2].x,
                    "bottom": face.bounding_poly.vertices[2].y
                }
            }
            
            return attributes
            
        except Exception as e:
            logger.error(f"Error getting face attributes: {str(e)}")
            return {"error": str(e)} 