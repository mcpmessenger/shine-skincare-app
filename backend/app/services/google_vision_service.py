import os
import logging
import json
import time
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime
import io

logger = logging.getLogger(__name__)

# Try to import Google Vision, fall back gracefully if not available
try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud Vision library not available. Service will be disabled.")
    GOOGLE_VISION_AVAILABLE = False
    vision = None
    types = None

class GoogleVisionService:
    """Service for Google Cloud Vision AI integration with enhanced features"""
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize the Google Vision service
        
        Args:
            credentials_path: Optional path to service account credentials file
        """
        self.credentials_path = credentials_path
        self.client = None
        self.max_retries = 3
        self.base_delay = 1.0
        self._initialize_client()
    
    def _authenticate_client(self) -> Optional[Any]:
        """
        Authenticate and create Google Vision client with proper credential management
        
        Returns:
            vision.ImageAnnotatorClient or None if authentication fails
        """
        if not GOOGLE_VISION_AVAILABLE:
            logger.warning("Google Vision library not available")
            return None
            
        try:
            # Priority order for credential sources
            credentials_path = (
                self.credentials_path or 
                os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            )
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            
            if credentials_json:
                # Use JSON content from environment variable
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(credentials_json)
                    temp_credentials_path = f.name
                
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_credentials_path
                client = vision.ImageAnnotatorClient()
                logger.info("Google Vision client authenticated with JSON credentials")
                return client
                
            elif credentials_path and os.path.exists(credentials_path):
                # Use file path
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                client = vision.ImageAnnotatorClient()
                logger.info(f"Google Vision client authenticated with file credentials: {credentials_path}")
                return client
            else:
                logger.warning("Google Vision credentials not found. Service will be disabled.")
                return None
                
        except Exception as e:
            logger.error(f"Failed to authenticate Google Vision client: {e}")
            return None
    
    def _initialize_client(self):
        """Initialize the Google Vision client"""
        self.client = self._authenticate_client()
    
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
            if types is not None:
                image = types.Image(content=content)
            else:
                raise RuntimeError("Google Vision is not available")
            
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
    
    def analyze_image_from_bytes(self, image_data: bytes) -> Dict[str, Any]:
        """
        Comprehensive image analysis from bytes using Google Vision AI with retry logic
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        if not self.client:
            return {
                'error': 'Google Vision service not available',
                'status': 'disabled'
            }
        
        return self._execute_with_retry(self._analyze_image_internal, image_data)
    
    def detect_faces(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Detect faces with facial landmark extraction
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            List of face detection results with landmarks and confidence scores
        """
        if not self.client:
            logger.warning("Google Vision client not available for face detection")
            return []
        
        try:
            if types is not None:
                image = types.Image(content=image_data)
            else:
                raise RuntimeError("Google Vision is not available")
            result = self._execute_with_retry(self._detect_faces_with_landmarks, image)
            return result.get('faces', [])
        except Exception as e:
            logger.error(f"Error in detect_faces: {e}")
            return []
    
    def extract_image_properties(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract comprehensive image properties including color and brightness analysis
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Dictionary containing color information, brightness, and texture data
        """
        if not self.client:
            logger.warning("Google Vision client not available for image properties")
            return {}
        
        try:
            if types is not None:
                image = types.Image(content=image_data)
            else:
                raise RuntimeError("Google Vision is not available")
            return self._execute_with_retry(self._extract_comprehensive_properties, image)
        except Exception as e:
            logger.error(f"Error in extract_image_properties: {e}")
            return {}
    
    def detect_labels(self, image_data: bytes) -> List[Dict[str, str]]:
        """
        Detect labels for skin-related feature recognition
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            List of detected labels with descriptions and confidence scores
        """
        if not self.client:
            logger.warning("Google Vision client not available for label detection")
            return []
        
        try:
            if types is not None:
                image = types.Image(content=image_data)
            else:
                raise RuntimeError("Google Vision is not available")
            result = self._execute_with_retry(self._detect_skin_related_labels, image)
            return result.get('labels', [])
        except Exception as e:
            logger.error(f"Error in detect_labels: {e}")
            return []
    
    def _detect_faces(self, image) -> Dict[str, Any]:
        """Detect faces in the image"""
        if types is None:
            raise RuntimeError("Google Vision is not available")
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
    
    def _get_image_properties(self, image) -> Dict[str, Any]:
        """Get image properties including dominant colors"""
        if types is None:
            raise RuntimeError("Google Vision is not available")
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
    
    def _detect_labels(self, image) -> Dict[str, Any]:
        """Detect labels in the image"""
        if types is None:
            raise RuntimeError("Google Vision is not available")
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
    
    def _detect_safe_search(self, image) -> Dict[str, Any]:
        """Detect safe search annotations"""
        if types is None:
            raise RuntimeError("Google Vision is not available")
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
    
    def _execute_with_retry(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute a function with exponential backoff retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or error dictionary
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed. Last error: {e}")
        
        return {
            'error': str(last_exception),
            'status': 'error',
            'attempts': self.max_retries
        }
    
    def _analyze_image_internal(self, image_data: bytes) -> Dict[str, Any]:
        """
        Internal method for comprehensive image analysis
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        try:
            if types is not None:
                image = types.Image(content=image_data)
            else:
                raise RuntimeError("Google Vision is not available")
            
            # Perform comprehensive analysis
            results = {
                'face_detection': self._detect_faces_with_landmarks(image),
                'image_properties': self._extract_comprehensive_properties(image),
                'label_detection': self._detect_skin_related_labels(image),
                'safe_search': self._detect_safe_search(image)
            }
            
            return {
                'status': 'success',
                'results': results,
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'google_vision'
            }
            
        except Exception as e:
            logger.error(f"Error in internal image analysis: {e}")
            raise e
    
    def _detect_faces_with_landmarks(self, image) -> Dict[str, Any]:
        """
        Enhanced face detection with facial landmarks and bounding boxes
        
        Args:
            image: Google Vision Image object
            
        Returns:
            Dictionary containing detailed face detection results
        """
        if types is None:
            raise RuntimeError("Google Vision is not available")
        try:
            response = self.client.face_detection(image=image)
            faces = response.face_annotations
            
            face_data = []
            for face in faces:
                # Extract facial landmarks
                landmarks = {}
                for landmark in face.landmarks:
                    landmark_type = landmark.type_.name
                    landmarks[landmark_type] = {
                        'x': landmark.position.x,
                        'y': landmark.position.y,
                        'z': landmark.position.z
                    }
                
                face_info = {
                    'detection_confidence': face.detection_confidence,
                    'landmarking_confidence': face.landmarking_confidence,
                    'joy_likelihood': face.joy_likelihood.name,
                    'sorrow_likelihood': face.sorrow_likelihood.name,
                    'anger_likelihood': face.anger_likelihood.name,
                    'surprise_likelihood': face.surprise_likelihood.name,
                    'under_exposed_likelihood': face.under_exposed_likelihood.name,
                    'blurred_likelihood': face.blurred_likelihood.name,
                    'headwear_likelihood': face.headwear_likelihood.name,
                    'bounding_poly': self._convert_vertices(face.bounding_poly.vertices),
                    'fd_bounding_poly': self._convert_vertices(face.fd_bounding_poly.vertices),
                    'landmarks': landmarks,
                    'roll_angle': face.roll_angle,
                    'pan_angle': face.pan_angle,
                    'tilt_angle': face.tilt_angle
                }
                face_data.append(face_info)
            
            return {
                'faces_found': len(faces),
                'faces': face_data
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced face detection: {e}")
            raise e
    
    def _extract_comprehensive_properties(self, image) -> Dict[str, Any]:
        """
        Extract comprehensive image properties including color, brightness, and texture data
        
        Args:
            image: Google Vision Image object
            
        Returns:
            Dictionary containing detailed image properties
        """
        if types is None:
            raise RuntimeError("Google Vision is not available")
        try:
            response = self.client.image_properties(image=image)
            properties = response.image_properties_annotation
            
            # Extract dominant colors with detailed information
            colors = []
            total_score = 0
            total_pixel_fraction = 0
            
            for color in properties.dominant_colors.colors:
                color_info = {
                    'red': color.color.red,
                    'green': color.color.green,
                    'blue': color.color.blue,
                    'alpha': getattr(color.color, 'alpha', 1.0),
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                }
                colors.append(color_info)
                total_score += color.score
                total_pixel_fraction += color.pixel_fraction
            
            # Calculate brightness and contrast estimates
            brightness = self._calculate_brightness(colors)
            contrast = self._calculate_contrast(colors)
            
            return {
                'dominant_colors': colors,
                'color_count': len(colors),
                'total_score': total_score,
                'total_pixel_fraction': total_pixel_fraction,
                'brightness': brightness,
                'contrast': contrast,
                'color_diversity': len(colors) / max(1, total_pixel_fraction)
            }
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive properties: {e}")
            raise e
    
    def _detect_skin_related_labels(self, image) -> Dict[str, Any]:
        """
        Detect labels with focus on skin-related features
        
        Args:
            image: Google Vision Image object
            
        Returns:
            Dictionary containing skin-related labels and features
        """
        if types is None:
            raise RuntimeError("Google Vision is not available")
        try:
            response = self.client.label_detection(image=image)
            labels = response.label_annotations
            
            # Filter and categorize labels
            skin_related_keywords = {
                'skin', 'face', 'person', 'human', 'portrait', 'beauty', 
                'complexion', 'facial', 'cheek', 'forehead', 'chin', 'nose',
                'smile', 'expression', 'makeup', 'cosmetics', 'skincare'
            }
            
            all_labels = []
            skin_labels = []
            
            for label in labels:
                label_info = {
                    'description': label.description,
                    'score': label.score,
                    'mid': label.mid,
                    'topicality': getattr(label, 'topicality', 0.0)
                }
                all_labels.append(label_info)
                
                # Check if label is skin-related
                if any(keyword in label.description.lower() for keyword in skin_related_keywords):
                    skin_labels.append(label_info)
            
            return {
                'labels_found': len(all_labels),
                'skin_labels_found': len(skin_labels),
                'labels': all_labels,
                'skin_labels': skin_labels
            }
            
        except Exception as e:
            logger.error(f"Error detecting skin-related labels: {e}")
            raise e
    
    def _calculate_brightness(self, colors: List[Dict[str, Any]]) -> float:
        """
        Calculate estimated brightness from dominant colors
        
        Args:
            colors: List of color information dictionaries
            
        Returns:
            Brightness value between 0 and 1
        """
        if not colors:
            return 0.5
        
        weighted_brightness = 0
        total_weight = 0
        
        for color in colors:
            # Calculate luminance using standard formula
            r, g, b = color['red'] / 255.0, color['green'] / 255.0, color['blue'] / 255.0
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            weight = color['pixel_fraction']
            
            weighted_brightness += luminance * weight
            total_weight += weight
        
        return weighted_brightness / max(total_weight, 0.001)
    
    def _calculate_contrast(self, colors: List[Dict[str, Any]]) -> float:
        """
        Calculate estimated contrast from color distribution
        
        Args:
            colors: List of color information dictionaries
            
        Returns:
            Contrast value between 0 and 1
        """
        if len(colors) < 2:
            return 0.0
        
        # Calculate luminance values
        luminances = []
        for color in colors:
            r, g, b = color['red'] / 255.0, color['green'] / 255.0, color['blue'] / 255.0
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            luminances.append(luminance)
        
        # Calculate contrast as the difference between max and min luminance
        max_luminance = max(luminances)
        min_luminance = min(luminances)
        
        return max_luminance - min_luminance 