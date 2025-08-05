#!/usr/bin/env python3
"""
Enhanced Face Detection Module with Multiple Fallback Methods
Uses OpenCV, MediaPipe, and alternative approaches for robust face detection
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
import traceback
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFaceDetection:
    """
    Enhanced face detection using multiple methods with fallbacks
    """
    
    def __init__(self):
        """Initialize face detection with multiple methods"""
        self.methods = []
        self.mediapipe_available = False
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize all available face detection methods"""
        try:
            # Initialize OpenCV cascades
            self._init_opencv_cascades()
            
            # Try to initialize MediaPipe
            self._init_mediapipe()
            
            logger.info(f"Available face detection methods: {self.methods}")
            
        except Exception as e:
            logger.error(f"❌ Face detection initialization failed: {e}")
            self.methods = []
    
    def _init_opencv_cascades(self):
        """Initialize OpenCV Haar cascades"""
        try:
            # Load multiple cascade files for better detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            self.alt_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
            self.alt2_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
            
            # Check if cascades loaded successfully
            cascades = [
                ('opencv_frontalface_default', self.face_cascade),
                ('opencv_profileface', self.profile_cascade),
                ('opencv_frontalface_alt', self.alt_cascade),
                ('opencv_frontalface_alt2', self.alt2_cascade)
            ]
            
            for name, cascade in cascades:
                if not cascade.empty():
                    self.methods.append(name)
                    logger.info(f"✅ {name} cascade loaded successfully")
                else:
                    logger.warning(f"⚠️ {name} cascade failed to load")
                    
        except Exception as e:
            logger.error(f"❌ OpenCV cascade initialization failed: {e}")
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face detection"""
        try:
            import mediapipe as mp
            self.mp = mp
            self.mp_face_detection = mp.solutions.face_detection
            self.mediapipe_available = True
            self.methods.append('mediapipe')
            logger.info("✅ MediaPipe face detection initialized")
        except ImportError:
            logger.warning("⚠️ MediaPipe not available, skipping MediaPipe face detection")
            self.mediapipe_available = False
        except Exception as e:
            logger.error(f"❌ MediaPipe initialization failed: {e}")
            self.mediapipe_available = False
    
    def detect_faces_opencv_enhanced(self, img_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Enhanced OpenCV face detection with multiple cascades and parameters
        """
        faces = []
        
        if not any('opencv' in method for method in self.methods):
            logger.warning("No OpenCV cascades available")
            return faces
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # Enhance image for better detection
            gray = self._enhance_image(gray)
            
            # Define multiple parameter sets for different detection scenarios
            param_sets = [
                # Very sensitive detection
                {'scaleFactor': 1.01, 'minNeighbors': 1, 'minSize': (10, 10)},
                # More sensitive detection
                {'scaleFactor': 1.02, 'minNeighbors': 2, 'minSize': (15, 15)},
                # Standard detection
                {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (20, 20)},
                # Large face detection
                {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (30, 30)},
            ]
            
            # Try each cascade with different parameters
            for cascade_name in self.methods:
                if not cascade_name.startswith('opencv'):
                    continue
                    
                if cascade_name == 'opencv_frontalface_default':
                    cascade = self.face_cascade
                elif cascade_name == 'opencv_profileface':
                    cascade = self.profile_cascade
                elif cascade_name == 'opencv_frontalface_alt':
                    cascade = self.alt_cascade
                elif cascade_name == 'opencv_frontalface_alt2':
                    cascade = self.alt2_cascade
                else:
                    continue
                
                for params in param_sets:
                    try:
                        detected_faces = cascade.detectMultiScale(
                            gray,
                            scaleFactor=params['scaleFactor'],
                            minNeighbors=params['minNeighbors'],
                            minSize=params['minSize']
                        )
                        
                        logger.info(f"🔍 {cascade_name} with params {params}: detected {len(detected_faces)} faces")
                        
                        if len(detected_faces) > 0:
                            faces.extend(detected_faces.tolist())
                            logger.info(f"✅ OpenCV detected faces with {cascade_name}")
                            break
                            
                    except Exception as e:
                        logger.error(f"❌ {cascade_name} detection failed: {e}")
                
                if faces:  # If we found faces, no need to try other cascades
                    break
            
            # Remove duplicate faces
            if faces:
                faces = self._remove_duplicate_faces(faces)
                logger.info(f"✅ Final OpenCV detection: {len(faces)} unique faces")
            
        except Exception as e:
            logger.error(f"❌ Enhanced OpenCV face detection failed: {e}")
        
        return faces
    
    def detect_faces_mediapipe(self, img_array: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Face detection using MediaPipe
        """
        faces = []
        
        if not self.mediapipe_available:
            return faces
        
        try:
            with self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5
            ) as face_detection:
                
                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                results = face_detection.process(rgb_image)
                
                if results.detections:
                    height, width = img_array.shape[:2]
                    
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        
                        # Convert relative coordinates to absolute
                        x = int(bbox.xmin * width)
                        y = int(bbox.ymin * height)
                        w = int(bbox.width * width)
                        h = int(bbox.height * height)
                        
                        faces.append((x, y, w, h))
                    
                    logger.info(f"✅ MediaPipe detected {len(faces)} faces")
                else:
                    logger.warning("⚠️ MediaPipe detected no faces")
                    
        except Exception as e:
            logger.error(f"❌ MediaPipe face detection failed: {e}")
        
        return faces
    
    def _enhance_image(self, gray: np.ndarray) -> np.ndarray:
        """
        Enhance image for better face detection
        """
        try:
            # Apply histogram equalization for better contrast
            enhanced = cv2.equalizeHist(gray)
            
            # Apply Gaussian blur to reduce noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Image enhancement failed: {e}")
            return gray
    
    def _remove_duplicate_faces(self, faces: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """
        Remove duplicate and overlapping face detections
        """
        if len(faces) <= 1:
            return faces
        
        # Sort faces by area (largest first)
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        
        unique_faces = []
        for face in faces:
            is_duplicate = False
            
            for unique_face in unique_faces:
                # Calculate overlap
                x1, y1, w1, h1 = face
                x2, y2, w2, h2 = unique_face
                
                # Calculate intersection
                x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = x_overlap * y_overlap
                
                # Calculate areas
                area1 = w1 * h1
                area2 = w2 * h2
                smaller_area = min(area1, area2)
                
                # If overlap is more than 50% of smaller face, consider it duplicate
                if overlap_area > 0.5 * smaller_area:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_faces.append(face)
        
        return unique_faces
    
    def detect_faces(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        Main face detection method using multiple approaches
        """
        if img_array is None:
            logger.warning("No image provided for face detection")
            return self._get_fallback_response('no_image')
        
        if not self.methods:
            logger.error("No face detection methods available")
            return self._get_fallback_response('no_methods')
        
        logger.info("🔍 Starting enhanced face detection...")
        
        # Try OpenCV first
        opencv_faces = self.detect_faces_opencv_enhanced(img_array)
        
        # If OpenCV fails, try MediaPipe
        if not opencv_faces and self.mediapipe_available:
            logger.info("OpenCV failed, trying MediaPipe...")
            mediapipe_faces = self.detect_faces_mediapipe(img_array)
            
            if mediapipe_faces:
                opencv_faces = mediapipe_faces
                detection_method = 'mediapipe'
            else:
                detection_method = 'opencv_failed'
        else:
            detection_method = 'opencv' if opencv_faces else 'opencv_failed'
        
        # Calculate confidence and quality metrics
        if opencv_faces:
            confidence = self._calculate_confidence(opencv_faces[0], img_array)
            quality_metrics = self._calculate_quality_metrics(img_array, opencv_faces[0])
            
            return {
                'detected': True,
                'confidence': confidence,
                'face_bounds': {
                    'x': int(opencv_faces[0][0]),
                    'y': int(opencv_faces[0][1]),
                    'width': int(opencv_faces[0][2]),
                    'height': int(opencv_faces[0][3])
                },
                'method': detection_method,
                'quality_metrics': quality_metrics,
                'num_faces': len(opencv_faces)
            }
        else:
            logger.warning("❌ No faces detected with any method")
            return self._get_fallback_response(detection_method)
    
    def _calculate_confidence(self, face: Tuple[int, int, int, int], img_array: np.ndarray) -> float:
        """
        Calculate confidence score for detected face
        """
        try:
            x, y, w, h = face
            img_height, img_width = img_array.shape[:2]
            
            # Calculate face area ratio
            face_area = w * h
            img_area = img_width * img_height
            area_ratio = face_area / img_area
            
            # Position score (center is better)
            center_x = x + w/2
            center_y = y + h/2
            distance_from_center = np.sqrt((center_x - img_width/2)**2 + (center_y - img_height/2)**2)
            max_distance = np.sqrt((img_width/2)**2 + (img_height/2)**2)
            position_score = 1 - (distance_from_center / max_distance)
            
            # Overall confidence
            confidence = min(0.95, area_ratio * 10 + position_score * 0.2)
            
            return confidence
            
        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.5
    
    def _calculate_quality_metrics(self, img_array: np.ndarray, face_bounds: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        Calculate image quality metrics
        """
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            # Basic quality metrics
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Determine quality levels
            lighting = 'good' if mean_brightness > 100 else 'poor'
            sharpness = 'high' if laplacian_var > 100 else 'low'
            contrast = 'good' if std_brightness > 30 else 'poor'
            
            return {
                'lighting': lighting,
                'sharpness': sharpness,
                'contrast': contrast,
                'overall_quality': 'good' if all(q == 'good' for q in [lighting, contrast]) else 'poor'
            }
            
        except Exception as e:
            logger.error(f"❌ Quality metrics calculation failed: {e}")
            return {
                'lighting': 'unknown',
                'sharpness': 'unknown',
                'contrast': 'unknown',
                'overall_quality': 'unknown'
            }
    
    def _get_fallback_response(self, method: str) -> Dict[str, Any]:
        """
        Get fallback response when face detection fails
        """
        return {
            'detected': False,
            'confidence': 0.0,
            'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
            'method': method,
            'quality_metrics': {
                'lighting': 'unknown',
                'sharpness': 'unknown',
                'contrast': 'unknown',
                'overall_quality': 'unknown'
            },
            'num_faces': 0
        }

# Global instance
enhanced_face_detector = EnhancedFaceDetection() 