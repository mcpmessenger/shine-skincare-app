#!/usr/bin/env python3
"""
Advanced Face Detection for Version 4
Uses MediaPipe as primary method, with OpenCV as fallback
"""

import cv2
import numpy as np
import base64
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFaceDetector:
    """
    Advanced Face Detector using MediaPipe and OpenCV
    """
    
    def __init__(self, method: str = "opencv", confidence_threshold: float = 0.5):
        """
        Initialize the face detector
        
        Args:
            method: Detection method ("mediapipe", "opencv", "auto")
            confidence_threshold: Minimum confidence for detection
        """
        self.method = method
        self.confidence_threshold = confidence_threshold
        self.mediapipe_available = False
        self.opencv_cascade = None
        
        # Try to initialize MediaPipe
        try:
            import mediapipe as mp
            self.mp = mp
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils
            self.mediapipe_available = True
            logger.info("✅ MediaPipe face detection initialized")
        except ImportError:
            logger.warning("⚠️ MediaPipe not available, will use OpenCV")
        
        # Initialize OpenCV cascade
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.opencv_cascade = cv2.CascadeClassifier(cascade_path)
            if self.opencv_cascade.empty():
                logger.warning("⚠️ OpenCV cascade not loaded properly")
            else:
                logger.info("✅ OpenCV cascade loaded")
        except Exception as e:
            logger.error(f"❌ Error loading OpenCV cascade: {e}")
    
    def detect_faces(self, image: np.ndarray) -> Dict:
        """
        Detect faces in the image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Try OpenCV first (since it worked previously)
            if self.method == "opencv" or self.method == "auto":
                opencv_result = self._detect_faces_opencv(image)
                if opencv_result['success'] and opencv_result['faces_detected'] > 0:
                    logger.info("✅ OpenCV detected faces successfully")
                    return opencv_result
            
            # Try MediaPipe if OpenCV failed or no faces detected
            if self.method == "mediapipe" or (self.method == "auto" and self.mediapipe_available):
                mediapipe_result = self._detect_faces_mediapipe(image)
                if mediapipe_result['success'] and mediapipe_result['faces_detected'] > 0:
                    logger.info("✅ MediaPipe detected faces successfully")
                    return mediapipe_result
                elif opencv_result['success'] and opencv_result['faces_detected'] > 0:
                    # Fall back to OpenCV result if MediaPipe failed
                    logger.info("⚠️ MediaPipe failed, using OpenCV result")
                    return opencv_result
            
            # If both failed, return OpenCV result (even if no faces)
            return opencv_result
                
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return {
                'success': False,
                'error': str(e),
                'faces_detected': 0,
                'faces': []
            }
    
    def _detect_faces_mediapipe(self, image: np.ndarray) -> Dict:
        """Detect faces using MediaPipe"""
        try:
            with self.mp_face_detection.FaceDetection(
                model_selection=1,  # 0 for short-range, 1 for full-range
                min_detection_confidence=self.confidence_threshold
            ) as face_detection:
                
                # Convert BGR to RGB
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_image)
                
                faces = []
                if results.detections:
                    for detection in results.detections:
                        # Get bounding box
                        bbox = detection.location_data.relative_bounding_box
                        h, w, _ = image.shape
                        
                        x = int(bbox.xmin * w)
                        y = int(bbox.ymin * h)
                        width = int(bbox.width * w)
                        height = int(bbox.height * h)
                        
                        # Get confidence
                        confidence = detection.score[0]
                        
                        # Get keypoints (eyes, nose, mouth)
                        landmarks = {}
                        if detection.location_data.relative_keypoints:
                            for i, keypoint in enumerate(detection.location_data.relative_keypoints):
                                landmarks[f'point_{i}'] = {
                                    'x': int(keypoint.x * w),
                                    'y': int(keypoint.y * h)
                                }
                        
                        faces.append({
                            'box': [x, y, width, height],
                            'confidence': float(confidence),
                            'landmarks': landmarks
                        })
                
                return {
                    'success': True,
                    'faces_detected': len(faces),
                    'faces': faces,
                    'method': 'mediapipe'
                }
                
        except Exception as e:
            logger.error(f"Error in MediaPipe detection: {e}")
            return {
                'success': False,
                'error': str(e),
                'faces_detected': 0,
                'faces': [],
                'method': 'mediapipe'
            }
    
    def _detect_faces_opencv(self, image: np.ndarray) -> Dict:
        """Detect faces using OpenCV cascade"""
        try:
            if self.opencv_cascade is None:
                return {
                    'success': False,
                    'error': 'OpenCV cascade not available',
                    'faces_detected': 0,
                    'faces': []
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with more sensitive parameters
            faces = self.opencv_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # More sensitive (was 1.1)
                minNeighbors=3,    # More sensitive (was 5)
                minSize=(20, 20),  # Smaller minimum size (was 30, 30)
                maxSize=(0, 0)     # No maximum size limit
            )
            
            detected_faces = []
            for (x, y, w, h) in faces:
                # Calculate confidence based on face size and position
                face_area = w * h
                image_area = image.shape[0] * image.shape[1]
                area_ratio = face_area / image_area
                
                # Higher confidence for larger, well-positioned faces
                confidence = min(0.9, 0.5 + (area_ratio * 10))
                
                detected_faces.append({
                    'box': [int(x), int(y), int(w), int(h)],  # Convert to regular Python ints
                    'confidence': float(confidence),  # Ensure it's a regular Python float
                    'landmarks': {}
                })
            
            logger.info(f"OpenCV detected {len(detected_faces)} faces")
            return {
                'success': True,
                'faces_detected': len(detected_faces),
                'faces': detected_faces,
                'method': 'opencv'
            }
            
        except Exception as e:
            logger.error(f"Error in OpenCV detection: {e}")
            return {
                'success': False,
                'error': str(e),
                'faces_detected': 0,
                'faces': [],
                'method': 'opencv'
            }
    
    def align_face(self, image: np.ndarray, landmarks: Dict) -> np.ndarray:
        """
        Align face based on landmarks
        
        Args:
            image: Input image
            landmarks: Face landmarks
            
        Returns:
            Aligned face image
        """
        try:
            # Simple alignment based on eye landmarks if available
            if 'point_0' in landmarks and 'point_1' in landmarks:
                # Assuming point_0 and point_1 are eyes
                left_eye = landmarks['point_0']
                right_eye = landmarks['point_1']
                
                # Calculate angle
                eye_angle = np.arctan2(
                    right_eye['y'] - left_eye['y'],
                    right_eye['x'] - left_eye['x']
                )
                
                # Rotate image
                center = (image.shape[1] // 2, image.shape[0] // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, np.degrees(eye_angle), 1.0)
                aligned = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
                
                return aligned
            
            return image
            
        except Exception as e:
            logger.error(f"Error in face alignment: {e}")
            return image
    
    def crop_face(self, image: np.ndarray, face_box: List[int], padding: float = 0.2) -> np.ndarray:
        """
        Crop face from image with padding
        
        Args:
            image: Input image
            face_box: [x, y, width, height]
            padding: Padding ratio
            
        Returns:
            Cropped face image
        """
        try:
            x, y, w, h = face_box
            
            # Add padding
            pad_x = int(w * padding)
            pad_y = int(h * padding)
            
            # Calculate crop coordinates
            crop_x1 = max(0, x - pad_x)
            crop_y1 = max(0, y - pad_y)
            crop_x2 = min(image.shape[1], x + w + pad_x)
            crop_y2 = min(image.shape[0], y + h + pad_y)
            
            # Crop face
            cropped = image[crop_y1:crop_y2, crop_x1:crop_x2]
            
            return cropped
            
        except Exception as e:
            logger.error(f"Error in face cropping: {e}")
            return image

# Global instance for easy access
advanced_face_detector = AdvancedFaceDetector()

def detect_faces_advanced(image_data: str, confidence_threshold: float = 0.3) -> Dict:
    """
    Advanced face detection function for API compatibility
    
    Args:
        image_data: Base64 encoded image string
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        Detection results dictionary
    """
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                'success': False,
                'error': 'Failed to decode image',
                'faces_detected': 0,
                'faces': []
            }
        
        # Update detector confidence threshold
        advanced_face_detector.confidence_threshold = confidence_threshold
        
        # Perform detection
        results = advanced_face_detector.detect_faces(img)
        
        logger.info(f"Face detection completed: {results.get('faces_detected', 0)} faces found")
        return results
        
    except Exception as e:
        logger.error(f"Error in advanced face detection: {e}")
        return {
            'success': False,
            'error': str(e),
            'faces_detected': 0,
            'faces': []
        } 