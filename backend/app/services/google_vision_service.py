import os
import logging
import json
from typing import Dict, Any, Optional
from google.cloud import vision
from google.cloud.vision_v1 import types
from PIL import Image
import io

logger = logging.getLogger(__name__)

class GoogleVisionService:
    """Service for Google Cloud Vision AI integration"""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the Google Vision service"""
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Vision client"""
        try:
            # Check if credentials are set via environment variable
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                # Use JSON content from environment variable
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(credentials_json)
                    temp_credentials_path = f.name
                
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_credentials_path
                self.client = vision.ImageAnnotatorClient()
                logger.info("Google Vision client initialized with JSON credentials")
                
            elif credentials_path and os.path.exists(credentials_path):
                # Use file path
                self.client = vision.ImageAnnotatorClient()
                logger.info("Google Vision client initialized with file credentials")
            else:
                logger.warning("Google Vision credentials not found. Service will be disabled.")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision client: {e}")
            self.client = None
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image using Google Vision AI
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.client:
            return {
                'error': 'Google Vision service not available',
                'status': 'disabled'
            }
        
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = types.Image(content=content)
            
            # Perform analysis
            results = {
                'face_detection': self._detect_faces(image),
                'image_properties': self._get_image_properties(image),
                'label_detection': self._detect_labels(image),
                'safe_search': self._detect_safe_search(image)
            }
            
            return {
                'status': 'success',
                'results': results,
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def analyze_image_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze an image from bytes using Google Vision AI
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.client:
            return {
                'error': 'Google Vision service not available',
                'status': 'disabled'
            }
        
        try:
            # Create image object
            image = types.Image(content=image_bytes)
            
            # Perform analysis
            results = {
                'face_detection': self._detect_faces(image),
                'image_properties': self._get_image_properties(image),
                'label_detection': self._detect_labels(image),
                'safe_search': self._detect_safe_search(image)
            }
            
            return {
                'status': 'success',
                'results': results,
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image from bytes: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def _detect_faces(self, image: types.Image) -> Dict[str, Any]:
        """Detect faces in the image"""
        try:
            response = self.client.face_detection(image=image)
            faces = response.face_annotations
            
            face_data = []
            for face in faces:
                face_info = {
                    'confidence': face.detection_confidence,
                    'joy_likelihood': face.joy_likelihood,
                    'sorrow_likelihood': face.sorrow_likelihood,
                    'anger_likelihood': face.anger_likelihood,
                    'surprise_likelihood': face.surprise_likelihood,
                    'bounding_poly': self._convert_vertices(face.bounding_poly.vertices)
                }
                face_data.append(face_info)
            
            return {
                'faces_found': len(faces),
                'face_data': face_data
            }
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return {'error': str(e)}
    
    def _get_image_properties(self, image: types.Image) -> Dict[str, Any]:
        """Get image properties including dominant colors"""
        try:
            response = self.client.image_properties(image=image)
            properties = response.image_properties_annotation
            
            colors = []
            for color in properties.dominant_colors.colors:
                color_info = {
                    'red': color.color.red,
                    'green': color.color.green,
                    'blue': color.color.blue,
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                }
                colors.append(color_info)
            
            return {
                'dominant_colors': colors,
                'color_count': len(colors)
            }
        except Exception as e:
            logger.error(f"Error getting image properties: {e}")
            return {'error': str(e)}
    
    def _detect_labels(self, image: types.Image) -> Dict[str, Any]:
        """Detect labels in the image"""
        try:
            response = self.client.label_detection(image=image)
            labels = response.label_annotations
            
            label_data = []
            for label in labels:
                label_info = {
                    'description': label.description,
                    'score': label.score,
                    'mid': label.mid
                }
                label_data.append(label_info)
            
            return {
                'labels_found': len(labels),
                'label_data': label_data
            }
        except Exception as e:
            logger.error(f"Error detecting labels: {e}")
            return {'error': str(e)}
    
    def _detect_safe_search(self, image: types.Image) -> Dict[str, Any]:
        """Detect safe search annotations"""
        try:
            response = self.client.safe_search_detection(image=image)
            safe = response.safe_search_annotation
            
            return {
                'adult': safe.adult,
                'racy': safe.racy,
                'violence': safe.violence,
                'medical': safe.medical,
                'spoof': safe.spoof
            }
        except Exception as e:
            logger.error(f"Error detecting safe search: {e}")
            return {'error': str(e)}
    
    def _convert_vertices(self, vertices) -> list:
        """Convert vertices to list format"""
        return [{'x': vertex.x, 'y': vertex.y} for vertex in vertices]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.client is not None 