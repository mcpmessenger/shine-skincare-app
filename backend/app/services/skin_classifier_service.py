import logging
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime
import cv2
import io
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import Google Vision service
try:
    from .google_vision_service import GoogleVisionService
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    logger.warning("Google Vision service not available for skin classifier")
    GOOGLE_VISION_AVAILABLE = False
    GoogleVisionService = None


class EnhancedSkinTypeClassifier:
    """
    Enhanced skin type classifier that uses multiple scales (Fitzpatrick and Monk)
    and incorporates ethnicity context to improve classification accuracy.
    """
    
    def __init__(self, google_vision_service: Optional[GoogleVisionService] = None):
        """Initialize the enhanced skin type classifier with Google Vision integration"""
        # Initialize Google Vision service for face detection
        self.google_vision_service = google_vision_service
        if not self.google_vision_service and GOOGLE_VISION_AVAILABLE:
            try:
                self.google_vision_service = GoogleVisionService()
                logger.info("Initialized Google Vision service for skin classifier")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Vision service: {e}")
                self.google_vision_service = None
        
        # In a real implementation, you would load pre-trained models here
        self.fitzpatrick_classifier = self._load_fitzpatrick_model()
        self.monk_classifier = self._load_monk_model()
        
        # Classification confidence threshold
        self.confidence_threshold = 0.7
        
        # Ethnicity-based adjustment rules
        self.ethnicity_adjustments = {
            'african': {
                'fitzpatrick_min': 'V',
                'monk_min': 7,
                'confidence_bonus': 0.1
            },
            'east_asian': {
                'fitzpatrick_range': ('II', 'IV'),
                'monk_range': (3, 5),
                'confidence_bonus': 0.05
            },
            'south_asian': {
                'fitzpatrick_range': ('III', 'V'),
                'monk_range': (4, 7),
                'confidence_bonus': 0.05
            },
            'caucasian': {
                'fitzpatrick_range': ('I', 'III'),
                'monk_range': (1, 4),
                'confidence_bonus': 0.05
            },
            'hispanic': {
                'fitzpatrick_range': ('III', 'V'),
                'monk_range': (3, 7),
                'confidence_bonus': 0.05
            },
            'middle_eastern': {
                'fitzpatrick_range': ('III', 'IV'),
                'monk_range': (4, 6),
                'confidence_bonus': 0.05
            }
        }
        
        # Fitzpatrick scale mapping
        self.fitzpatrick_scale = {
            'I': {'description': 'Always burns, never tans', 'range': (1, 1)},
            'II': {'description': 'Usually burns, tans minimally', 'range': (2, 2)},
            'III': {'description': 'Sometimes burns, tans gradually', 'range': (3, 3)},
            'IV': {'description': 'Burns minimally, always tans well', 'range': (4, 4)},
            'V': {'description': 'Very rarely burns, tans very easily', 'range': (5, 5)},
            'VI': {'description': 'Never burns, deeply pigmented', 'range': (6, 6)}
        }
        
        logger.info("Enhanced skin type classifier initialized")
    
    def _load_fitzpatrick_model(self):
        """
        Load pre-trained Fitzpatrick classification model
        
        Returns:
            Model object (placeholder for actual implementation)
        """
        # Placeholder for loading a pre-trained Fitzpatrick classification model
        # In a real implementation, this would load a trained ML model
        logger.info("Loading Fitzpatrick classification model (placeholder)")
        return None
    
    def _load_monk_model(self):
        """
        Load pre-trained Monk scale classification model
        
        Returns:
            Model object (placeholder for actual implementation)
        """
        # Placeholder for loading a pre-trained Monk scale classification model
        # In a real implementation, this would load a trained ML model
        logger.info("Loading Monk scale classification model (placeholder)")
        return None
    
    def classify_skin_type(self, image_data: Union[bytes, np.ndarray], 
                          ethnicity: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify skin type using multiple models and ethnicity context
        
        Args:
            image_data: Image data as bytes or a numpy array
            ethnicity: Optional ethnicity information for context-based adjustments
            
        Returns:
            Dictionary with skin type classifications, confidence scores, and metadata
        """
        try:
            logger.info(f"Classifying skin type with ethnicity context: {ethnicity}")
            
            # Extract skin regions from the image
            skin_regions = self._extract_skin_regions(image_data)
            
            # Perform base classification using both scales
            fitzpatrick_type = self._classify_fitzpatrick(skin_regions)
            monk_tone = self._classify_monk(skin_regions)
            
            # Store original classifications for comparison
            original_fitzpatrick = fitzpatrick_type
            original_monk = monk_tone
            
            # Apply ethnicity-based adjustments if available
            if ethnicity:
                fitzpatrick_type, monk_tone = self._apply_ethnicity_context(
                    fitzpatrick_type, monk_tone, ethnicity
                )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(skin_regions, ethnicity)
            
            # Prepare detailed result
            result = {
                'fitzpatrick_type': fitzpatrick_type,
                'fitzpatrick_description': self.fitzpatrick_scale.get(fitzpatrick_type, {}).get('description', ''),
                'monk_tone': monk_tone,
                'monk_description': f"Monk Scale Tone {monk_tone}",
                'ethnicity_considered': ethnicity is not None,
                'ethnicity': ethnicity or '',
                'confidence': confidence,
                'high_confidence': confidence >= self.confidence_threshold,
                'original_classifications': {
                    'fitzpatrick': original_fitzpatrick,
                    'monk': original_monk
                },
                'adjustments_applied': ethnicity is not None and (
                    original_fitzpatrick != fitzpatrick_type or original_monk != monk_tone
                ),
                'classification_timestamp': datetime.utcnow().isoformat(),
                'classifier_version': '1.0.0'
            }
            
            logger.info(f"Classification complete: Fitzpatrick {fitzpatrick_type}, "
                       f"Monk {monk_tone}, Confidence {confidence:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in skin type classification: {e}")
            return {
                'error': str(e),
                'status': 'error',
                'classification_timestamp': datetime.utcnow().isoformat()
            }
    
    def _extract_skin_regions(self, image_data: Union[bytes, np.ndarray]) -> Dict[str, Any]:
        """
        Extract skin regions from the image using Google Vision facial landmarks
        
        Args:
            image_data: Image data as bytes or numpy array
            
        Returns:
            Dictionary containing processed skin regions and metadata
        """
        try:
            # Convert image data to bytes if needed
            if isinstance(image_data, np.ndarray):
                # Convert numpy array to bytes
                pil_image = Image.fromarray((image_data * 255).astype(np.uint8))
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='JPEG')
                image_bytes = img_byte_arr.getvalue()
            elif isinstance(image_data, bytes):
                image_bytes = image_data
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            # Use Google Vision API for face detection if available
            if self.google_vision_service and self.google_vision_service.is_available():
                logger.debug("Using Google Vision API for skin region extraction")
                
                # Get face detection results
                faces = self.google_vision_service.detect_faces(image_bytes)
                
                # Get image properties for color analysis
                image_properties = self.google_vision_service.extract_image_properties(image_bytes)
                
                if faces and len(faces) > 0:
                    # Use the first detected face
                    face = faces[0]
                    
                    # Extract skin-relevant information from face landmarks
                    landmarks = face.get('landmarks', {})
                    
                    # Get key facial landmarks for skin analysis
                    skin_analysis_points = self._extract_skin_analysis_points(landmarks)
                    
                    # Combine face detection with image properties
                    skin_regions_data = {
                        'face_detected': True,
                        'face_confidence': face.get('detection_confidence', 0.0),
                        'landmarks': landmarks,
                        'skin_analysis_points': skin_analysis_points,
                        'image_properties': image_properties,
                        'bounding_poly': face.get('bounding_poly', []),
                        'face_angles': {
                            'roll_angle': face.get('roll_angle', 0.0),
                            'pan_angle': face.get('pan_angle', 0.0),
                            'tilt_angle': face.get('tilt_angle', 0.0)
                        },
                        'face_quality': {
                            'blurred_likelihood': face.get('blurred_likelihood', 'UNKNOWN'),
                            'under_exposed_likelihood': face.get('under_exposed_likelihood', 'UNKNOWN')
                        }
                    }
                    
                    logger.debug(f"Extracted skin regions using Google Vision: "
                               f"confidence={face.get('detection_confidence', 0.0):.3f}")
                    
                    return skin_regions_data
                else:
                    logger.warning("No faces detected by Google Vision API")
                    # Fall back to image properties only
                    return {
                        'face_detected': False,
                        'face_confidence': 0.0,
                        'image_properties': image_properties,
                        'fallback_reason': 'no_faces_detected'
                    }
            else:
                logger.debug("Google Vision API not available, using fallback method")
                # Fallback to basic image analysis
                return self._extract_skin_regions_fallback(image_bytes)
                
        except Exception as e:
            logger.error(f"Error extracting skin regions: {e}")
            # Return fallback data
            return {
                'face_detected': False,
                'face_confidence': 0.0,
                'error': str(e),
                'fallback_reason': 'extraction_error'
            }
    
    def _extract_skin_analysis_points(self, landmarks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key points from facial landmarks for skin tone analysis
        
        Args:
            landmarks: Facial landmarks from Google Vision
            
        Returns:
            Dictionary with skin analysis points
        """
        try:
            # Key landmarks for skin tone analysis
            skin_landmarks = [
                'LEFT_CHEEK_CENTER', 'RIGHT_CHEEK_CENTER',
                'NOSE_TIP', 'CHIN_GNATHION',
                'FOREHEAD_GLABELLA'
            ]
            
            analysis_points = {}
            for landmark_name in skin_landmarks:
                if landmark_name in landmarks:
                    landmark = landmarks[landmark_name]
                    analysis_points[landmark_name] = {
                        'x': landmark.get('x', 0),
                        'y': landmark.get('y', 0),
                        'z': landmark.get('z', 0)
                    }
            
            # Calculate skin region center points
            if analysis_points:
                center_x = np.mean([point['x'] for point in analysis_points.values()])
                center_y = np.mean([point['y'] for point in analysis_points.values()])
                
                analysis_points['skin_center'] = {
                    'x': center_x,
                    'y': center_y,
                    'point_count': len(analysis_points)
                }
            
            return analysis_points
            
        except Exception as e:
            logger.error(f"Error extracting skin analysis points: {e}")
            return {}
    
    def _extract_skin_regions_fallback(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Fallback method for skin region extraction without Google Vision
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary with fallback skin region data
        """
        try:
            # Convert bytes to PIL Image for basic analysis
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to numpy array
            image_array = np.array(pil_image)
            
            # Basic color analysis
            if len(image_array.shape) == 3:
                # RGB image
                mean_color = np.mean(image_array, axis=(0, 1))
                color_std = np.std(image_array, axis=(0, 1))
            else:
                # Grayscale image
                mean_color = np.mean(image_array)
                color_std = np.std(image_array)
            
            return {
                'face_detected': False,
                'face_confidence': 0.0,
                'fallback_analysis': {
                    'mean_color': mean_color.tolist() if hasattr(mean_color, 'tolist') else mean_color,
                    'color_std': color_std.tolist() if hasattr(color_std, 'tolist') else color_std,
                    'image_shape': image_array.shape
                },
                'fallback_reason': 'google_vision_unavailable'
            }
            
        except Exception as e:
            logger.error(f"Error in fallback skin region extraction: {e}")
            return {
                'face_detected': False,
                'face_confidence': 0.0,
                'error': str(e),
                'fallback_reason': 'fallback_error'
            }
    
    def _classify_fitzpatrick(self, skin_regions: Dict[str, Any]) -> str:
        """
        Classify according to the Fitzpatrick scale using Google Vision data
        
        Args:
            skin_regions: Processed skin regions data from Google Vision
            
        Returns:
            Fitzpatrick type (I-VI)
        """
        try:
            logger.debug("Classifying Fitzpatrick type using enhanced analysis")
            
            # Use Google Vision data if available
            if skin_regions.get('face_detected', False):
                return self._classify_fitzpatrick_with_vision(skin_regions)
            else:
                return self._classify_fitzpatrick_fallback(skin_regions)
                
        except Exception as e:
            logger.error(f"Error in Fitzpatrick classification: {e}")
            return "III"  # Default to middle type
    
    def _classify_fitzpatrick_with_vision(self, skin_regions: Dict[str, Any]) -> str:
        """
        Classify Fitzpatrick type using Google Vision facial analysis
        
        Args:
            skin_regions: Google Vision analysis data
            
        Returns:
            Fitzpatrick type (I-VI)
        """
        try:
            # Extract color information from image properties
            image_properties = skin_regions.get('image_properties', {})
            dominant_colors = image_properties.get('dominant_colors', [])
            
            if not dominant_colors:
                logger.warning("No dominant colors found, using fallback classification")
                return self._classify_fitzpatrick_fallback(skin_regions)
            
            # Calculate weighted average brightness from dominant colors
            total_brightness = 0
            total_weight = 0
            
            for color in dominant_colors:
                # Calculate luminance using standard formula
                r, g, b = color['red'] / 255.0, color['green'] / 255.0, color['blue'] / 255.0
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                weight = color['pixel_fraction']
                
                total_brightness += luminance * weight
                total_weight += weight
            
            if total_weight > 0:
                avg_brightness = total_brightness / total_weight
            else:
                avg_brightness = 0.5  # Default
            
            # Enhanced classification using brightness and face quality
            face_quality = skin_regions.get('face_quality', {})
            under_exposed = face_quality.get('under_exposed_likelihood', 'UNKNOWN')
            
            # Adjust brightness based on exposure
            if under_exposed in ['LIKELY', 'VERY_LIKELY']:
                avg_brightness *= 1.2  # Compensate for under-exposure
            elif under_exposed in ['UNLIKELY', 'VERY_UNLIKELY']:
                avg_brightness *= 0.9  # Adjust for good exposure
            
            # Classify based on adjusted brightness
            if avg_brightness < 0.15:
                return "VI"
            elif avg_brightness < 0.3:
                return "V"
            elif avg_brightness < 0.45:
                return "IV"
            elif avg_brightness < 0.6:
                return "III"
            elif avg_brightness < 0.75:
                return "II"
            else:
                return "I"
                
        except Exception as e:
            logger.error(f"Error in Google Vision Fitzpatrick classification: {e}")
            return self._classify_fitzpatrick_fallback(skin_regions)
    
    def _classify_fitzpatrick_fallback(self, skin_regions: Dict[str, Any]) -> str:
        """
        Fallback Fitzpatrick classification without Google Vision
        
        Args:
            skin_regions: Fallback analysis data
            
        Returns:
            Fitzpatrick type (I-VI)
        """
        try:
            fallback_analysis = skin_regions.get('fallback_analysis', {})
            mean_color = fallback_analysis.get('mean_color', [128, 128, 128])
            
            # Convert to luminance if RGB
            if isinstance(mean_color, list) and len(mean_color) == 3:
                r, g, b = [c / 255.0 for c in mean_color]
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
            else:
                luminance = mean_color / 255.0 if isinstance(mean_color, (int, float)) else 0.5
            
            # Simple classification based on luminance
            if luminance < 0.2:
                return "VI"
            elif luminance < 0.35:
                return "V"
            elif luminance < 0.5:
                return "IV"
            elif luminance < 0.65:
                return "III"
            elif luminance < 0.8:
                return "II"
            else:
                return "I"
                
        except Exception as e:
            logger.error(f"Error in fallback Fitzpatrick classification: {e}")
            return "III"
    
    def _classify_monk(self, skin_regions: Dict[str, Any]) -> int:
        """
        Classify according to the Monk scale using Google Vision data
        
        Args:
            skin_regions: Processed skin regions data from Google Vision
            
        Returns:
            Monk tone (1-10)
        """
        try:
            logger.debug("Classifying Monk tone using enhanced analysis")
            
            # Use Google Vision data if available
            if skin_regions.get('face_detected', False):
                return self._classify_monk_with_vision(skin_regions)
            else:
                return self._classify_monk_fallback(skin_regions)
                
        except Exception as e:
            logger.error(f"Error in Monk classification: {e}")
            return 5  # Default to middle tone
    
    def _classify_monk_with_vision(self, skin_regions: Dict[str, Any]) -> int:
        """
        Classify Monk tone using Google Vision facial analysis
        
        Args:
            skin_regions: Google Vision analysis data
            
        Returns:
            Monk tone (1-10)
        """
        try:
            # Extract color information from image properties
            image_properties = skin_regions.get('image_properties', {})
            dominant_colors = image_properties.get('dominant_colors', [])
            
            if not dominant_colors:
                logger.warning("No dominant colors found for Monk classification, using fallback")
                return self._classify_monk_fallback(skin_regions)
            
            # Calculate weighted average brightness and color characteristics
            total_brightness = 0
            total_weight = 0
            color_variance = 0
            
            for color in dominant_colors:
                # Calculate luminance
                r, g, b = color['red'] / 255.0, color['green'] / 255.0, color['blue'] / 255.0
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                weight = color['pixel_fraction']
                
                total_brightness += luminance * weight
                total_weight += weight
                
                # Calculate color variance for better tone classification
                color_variance += weight * ((r - 0.5)**2 + (g - 0.5)**2 + (b - 0.5)**2)
            
            if total_weight > 0:
                avg_brightness = total_brightness / total_weight
                avg_variance = color_variance / total_weight
            else:
                avg_brightness = 0.5
                avg_variance = 0.1
            
            # Enhanced Monk scale classification with more granular mapping
            # Monk scale 1-10 (1 = lightest, 10 = darkest)
            
            # Adjust for color variance (higher variance might indicate mixed lighting)
            brightness_adjustment = min(0.1, avg_variance * 0.5)
            adjusted_brightness = avg_brightness + brightness_adjustment
            
            # Map to Monk scale with finer gradations
            if adjusted_brightness >= 0.9:
                return 1
            elif adjusted_brightness >= 0.8:
                return 2
            elif adjusted_brightness >= 0.7:
                return 3
            elif adjusted_brightness >= 0.6:
                return 4
            elif adjusted_brightness >= 0.5:
                return 5
            elif adjusted_brightness >= 0.4:
                return 6
            elif adjusted_brightness >= 0.3:
                return 7
            elif adjusted_brightness >= 0.2:
                return 8
            elif adjusted_brightness >= 0.1:
                return 9
            else:
                return 10
                
        except Exception as e:
            logger.error(f"Error in Google Vision Monk classification: {e}")
            return self._classify_monk_fallback(skin_regions)
    
    def _classify_monk_fallback(self, skin_regions: Dict[str, Any]) -> int:
        """
        Fallback Monk classification without Google Vision
        
        Args:
            skin_regions: Fallback analysis data
            
        Returns:
            Monk tone (1-10)
        """
        try:
            fallback_analysis = skin_regions.get('fallback_analysis', {})
            mean_color = fallback_analysis.get('mean_color', [128, 128, 128])
            
            # Convert to luminance if RGB
            if isinstance(mean_color, list) and len(mean_color) == 3:
                r, g, b = [c / 255.0 for c in mean_color]
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
            else:
                luminance = mean_color / 255.0 if isinstance(mean_color, (int, float)) else 0.5
            
            # Map luminance to Monk scale
            if luminance >= 0.9:
                return 1
            elif luminance >= 0.8:
                return 2
            elif luminance >= 0.7:
                return 3
            elif luminance >= 0.6:
                return 4
            elif luminance >= 0.5:
                return 5
            elif luminance >= 0.4:
                return 6
            elif luminance >= 0.3:
                return 7
            elif luminance >= 0.2:
                return 8
            elif luminance >= 0.1:
                return 9
            else:
                return 10
                
        except Exception as e:
            logger.error(f"Error in fallback Monk classification: {e}")
            return 5
    
    def _apply_ethnicity_context(self, fitzpatrick_type: str, monk_tone: int, 
                                ethnicity: str) -> Tuple[str, int]:
        """
        Apply ethnicity-based adjustments to the classification results
        
        Args:
            fitzpatrick_type: Original Fitzpatrick classification
            monk_tone: Original Monk tone classification
            ethnicity: User's ethnicity
            
        Returns:
            Tuple of (adjusted_fitzpatrick_type, adjusted_monk_tone)
        """
        try:
            ethnicity_lower = ethnicity.lower()
            
            if ethnicity_lower not in self.ethnicity_adjustments:
                logger.debug(f"No adjustments available for ethnicity: {ethnicity}")
                return fitzpatrick_type, monk_tone
            
            adjustments = self.ethnicity_adjustments[ethnicity_lower]
            adjusted_fitzpatrick = fitzpatrick_type
            adjusted_monk = monk_tone
            
            # Apply Fitzpatrick adjustments
            if 'fitzpatrick_min' in adjustments:
                min_type = adjustments['fitzpatrick_min']
                if self._compare_fitzpatrick_types(fitzpatrick_type, min_type) < 0:
                    adjusted_fitzpatrick = min_type
                    logger.debug(f"Adjusted Fitzpatrick from {fitzpatrick_type} to {min_type} "
                               f"based on ethnicity minimum")
            
            if 'fitzpatrick_range' in adjustments:
                min_type, max_type = adjustments['fitzpatrick_range']
                if self._compare_fitzpatrick_types(fitzpatrick_type, min_type) < 0:
                    adjusted_fitzpatrick = min_type
                    logger.debug(f"Adjusted Fitzpatrick from {fitzpatrick_type} to {min_type} "
                               f"(range minimum)")
                elif self._compare_fitzpatrick_types(fitzpatrick_type, max_type) > 0:
                    adjusted_fitzpatrick = max_type
                    logger.debug(f"Adjusted Fitzpatrick from {fitzpatrick_type} to {max_type} "
                               f"(range maximum)")
            
            # Apply Monk scale adjustments
            if 'monk_min' in adjustments:
                min_tone = adjustments['monk_min']
                if monk_tone < min_tone:
                    adjusted_monk = min_tone
                    logger.debug(f"Adjusted Monk tone from {monk_tone} to {min_tone} "
                               f"based on ethnicity minimum")
            
            if 'monk_range' in adjustments:
                min_tone, max_tone = adjustments['monk_range']
                if monk_tone < min_tone:
                    adjusted_monk = min_tone
                    logger.debug(f"Adjusted Monk tone from {monk_tone} to {min_tone} "
                               f"(range minimum)")
                elif monk_tone > max_tone:
                    adjusted_monk = max_tone
                    logger.debug(f"Adjusted Monk tone from {monk_tone} to {max_tone} "
                               f"(range maximum)")
            
            return adjusted_fitzpatrick, adjusted_monk
            
        except Exception as e:
            logger.error(f"Error applying ethnicity context: {e}")
            return fitzpatrick_type, monk_tone
    
    def _compare_fitzpatrick_types(self, type1: str, type2: str) -> int:
        """
        Compare two Fitzpatrick types
        
        Args:
            type1: First Fitzpatrick type
            type2: Second Fitzpatrick type
            
        Returns:
            -1 if type1 < type2, 0 if equal, 1 if type1 > type2
        """
        type_order = ['I', 'II', 'III', 'IV', 'V', 'VI']
        
        try:
            index1 = type_order.index(type1)
            index2 = type_order.index(type2)
            
            if index1 < index2:
                return -1
            elif index1 > index2:
                return 1
            else:
                return 0
        except ValueError:
            logger.warning(f"Invalid Fitzpatrick type comparison: {type1} vs {type2}")
            return 0
    
    def _calculate_confidence(self, skin_regions: Dict[str, Any], ethnicity: Optional[str]) -> float:
        """
        Calculate a confidence score for the classification using Google Vision confidence integration
        
        Args:
            skin_regions: Processed skin regions data from Google Vision
            ethnicity: Optional ethnicity information
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Base confidence from Google Vision face detection
            face_confidence = skin_regions.get('face_confidence', 0.0)
            
            if skin_regions.get('face_detected', False):
                # Use Google Vision confidence as base
                base_confidence = min(0.9, face_confidence + 0.1)  # Cap at 0.9, add small bonus
                
                # Image quality factors from Google Vision
                face_quality = skin_regions.get('face_quality', {})
                quality_factor = 0.0
                
                # Adjust based on image quality indicators
                blurred = face_quality.get('blurred_likelihood', 'UNKNOWN')
                under_exposed = face_quality.get('under_exposed_likelihood', 'UNKNOWN')
                
                if blurred in ['UNLIKELY', 'VERY_UNLIKELY']:
                    quality_factor += 0.05  # Good image quality
                elif blurred in ['LIKELY', 'VERY_LIKELY']:
                    quality_factor -= 0.1  # Poor image quality
                
                if under_exposed in ['UNLIKELY', 'VERY_UNLIKELY']:
                    quality_factor += 0.05  # Good exposure
                elif under_exposed in ['LIKELY', 'VERY_LIKELY']:
                    quality_factor -= 0.1  # Poor exposure
                
                # Color analysis quality from image properties
                image_properties = skin_regions.get('image_properties', {})
                dominant_colors = image_properties.get('dominant_colors', [])
                
                if len(dominant_colors) >= 3:
                    quality_factor += 0.05  # Good color diversity
                elif len(dominant_colors) == 0:
                    quality_factor -= 0.15  # No color information
                
                # Landmark quality
                landmarks = skin_regions.get('landmarks', {})
                skin_analysis_points = skin_regions.get('skin_analysis_points', {})
                
                if len(skin_analysis_points) >= 3:
                    quality_factor += 0.05  # Good landmark detection
                elif len(skin_analysis_points) == 0:
                    quality_factor -= 0.1  # No landmarks
                
            else:
                # Fallback confidence calculation
                base_confidence = 0.4  # Lower base confidence without face detection
                quality_factor = 0.0
                
                # Try to assess fallback analysis quality
                fallback_analysis = skin_regions.get('fallback_analysis', {})
                if fallback_analysis:
                    # Basic quality assessment from fallback
                    color_std = fallback_analysis.get('color_std', [])
                    if isinstance(color_std, list) and len(color_std) > 0:
                        avg_std = np.mean(color_std)
                        if avg_std > 20:  # Good color variation
                            quality_factor += 0.1
                        elif avg_std < 5:  # Very low variation
                            quality_factor -= 0.1
            
            # Ethnicity context bonus
            ethnicity_bonus = 0.0
            if ethnicity and ethnicity.lower() in self.ethnicity_adjustments:
                ethnicity_bonus = self.ethnicity_adjustments[ethnicity.lower()].get('confidence_bonus', 0.0)
            
            # Calculate final confidence
            confidence = base_confidence + quality_factor + ethnicity_bonus
            
            # Ensure confidence is within valid range
            confidence = max(0.1, min(1.0, confidence))  # Minimum 0.1, maximum 1.0
            
            logger.debug(f"Calculated confidence: {confidence:.3f} "
                        f"(base: {base_confidence:.3f}, quality: {quality_factor:.3f}, "
                        f"ethnicity: {ethnicity_bonus:.3f}, face_detected: {skin_regions.get('face_detected', False)})")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default moderate confidence
    
    def get_supported_ethnicities(self) -> list:
        """
        Get list of supported ethnicities for context-based adjustments
        
        Returns:
            List of supported ethnicity strings
        """
        return list(self.ethnicity_adjustments.keys())
    
    def get_fitzpatrick_info(self, fitzpatrick_type: str) -> Dict[str, Any]:
        """
        Get detailed information about a Fitzpatrick type
        
        Args:
            fitzpatrick_type: Fitzpatrick type (I-VI)
            
        Returns:
            Dictionary with type information
        """
        return self.fitzpatrick_scale.get(fitzpatrick_type, {})
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold for high-confidence classifications
        
        Args:
            threshold: Confidence threshold (0-1)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.info(f"Updated confidence threshold to {threshold}")
        else:
            logger.warning(f"Invalid confidence threshold {threshold}, must be between 0 and 1")
    
    def is_available(self) -> bool:
        """
        Check if the classifier is available and ready to use
        
        Returns:
            True if classifier is available
        """
        # In a real implementation, this would check if models are loaded
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded models
        
        Returns:
            Dictionary with model information
        """
        return {
            'fitzpatrick_model_loaded': self.fitzpatrick_classifier is not None,
            'monk_model_loaded': self.monk_classifier is not None,
            'supported_ethnicities': self.get_supported_ethnicities(),
            'confidence_threshold': self.confidence_threshold,
            'classifier_version': '1.0.0'
        }