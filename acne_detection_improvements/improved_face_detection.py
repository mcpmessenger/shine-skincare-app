#!/usr/bin/env python3
"""
Improved Face Detection for Shine Skincare App
Addresses the issues identified in the problem screenshot
"""

import cv2
import numpy as np
import logging
import base64
from typing import Dict, List, Optional, Tuple, Union
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedFaceDetector:
    """Improved face detection with better confidence scoring and validation"""
    
    def __init__(self):
        """Initialize the face detector with multiple cascade classifiers"""
        self.face_cascades = []
        
        # Load multiple cascade classifiers for better detection
        cascade_files = [
            'haarcascade_frontalface_default.xml',
            'haarcascade_frontalface_alt.xml',
            'haarcascade_frontalface_alt2.xml'
        ]
        
        for cascade_file in cascade_files:
            try:
                cascade_path = cv2.data.haarcascades + cascade_file
                cascade = cv2.CascadeClassifier(cascade_path)
                if not cascade.empty():
                    self.face_cascades.append((cascade_file, cascade))
                    logger.info(f"✅ Loaded cascade: {cascade_file}")
                else:
                    logger.warning(f"⚠️  Failed to load cascade: {cascade_file}")
            except Exception as e:
                logger.warning(f"⚠️  Error loading cascade {cascade_file}: {e}")
        
        if not self.face_cascades:
            logger.error("❌ No face cascade classifiers loaded!")
    
    def calculate_face_quality_score(self, face_roi: np.ndarray, bbox: Tuple[int, int, int, int], 
                                   image_shape: Tuple[int, int]) -> float:
        """
        Calculate a comprehensive quality score for detected face
        
        Args:
            face_roi: The face region of interest
            bbox: Bounding box (x, y, w, h)
            image_shape: Original image shape (height, width)
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            x, y, w, h = bbox
            img_height, img_width = image_shape
            
            # Factor 1: Face size relative to image (larger faces = better quality)
            face_area = w * h
            image_area = img_width * img_height
            size_ratio = face_area / image_area
            size_score = min(1.0, size_ratio * 10)  # Normalize to 0-1
            
            # Factor 2: Face position (centered faces = better quality)
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            img_center_x = img_width // 2
            img_center_y = img_height // 2
            
            # Calculate distance from center as percentage of image diagonal
            center_distance = np.sqrt((face_center_x - img_center_x)**2 + (face_center_y - img_center_y)**2)
            img_diagonal = np.sqrt(img_width**2 + img_height**2)
            center_score = max(0.0, 1.0 - (center_distance / img_diagonal) * 2)
            
            # Factor 3: Face aspect ratio (closer to 1:1 = better quality)
            aspect_ratio = w / h if h > 0 else 0
            ideal_ratio = 1.0
            ratio_diff = abs(aspect_ratio - ideal_ratio)
            aspect_score = max(0.0, 1.0 - ratio_diff)
            
            # Factor 4: Image sharpness (Laplacian variance)
            if face_roi.size > 0:
                gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) > 2 else face_roi
                laplacian_var = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
                # Normalize sharpness score (typical range 0-1000+)
                sharpness_score = min(1.0, laplacian_var / 500.0)
            else:
                sharpness_score = 0.0
            
            # Factor 5: Minimum size threshold
            min_face_size = 50  # Minimum face width/height in pixels
            size_threshold_score = 1.0 if (w >= min_face_size and h >= min_face_size) else 0.0
            
            # Weighted combination of all factors
            weights = {
                'size': 0.3,
                'center': 0.2,
                'aspect': 0.2,
                'sharpness': 0.2,
                'threshold': 0.1
            }
            
            quality_score = (
                weights['size'] * size_score +
                weights['center'] * center_score +
                weights['aspect'] * aspect_score +
                weights['sharpness'] * sharpness_score +
                weights['threshold'] * size_threshold_score
            )
            
            logger.debug(f"Quality factors - Size: {size_score:.3f}, Center: {center_score:.3f}, "
                        f"Aspect: {aspect_score:.3f}, Sharpness: {sharpness_score:.3f}, "
                        f"Threshold: {size_threshold_score:.3f}, Final: {quality_score:.3f}")
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating face quality score: {e}")
            return 0.0
    
    def detect_faces_multi_cascade(self, image: np.ndarray, confidence_threshold: float = 0.5) -> Dict:
        """
        Detect faces using multiple cascade classifiers and return the best results
        
        Args:
            image: Input image as numpy array
            confidence_threshold: Minimum confidence threshold for face detection
            
        Returns:
            Dictionary with detection results
        """
        if image is None or image.size == 0:
            return {
                'success': False,
                'error': 'Invalid input image',
                'faces_detected': 0,
                'confidence': 0.0
            }
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
        
        all_detections = []
        
        # Try each cascade classifier
        for cascade_name, cascade in self.face_cascades:
            try:
                # Use more aggressive parameters for better detection
                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,      # Smaller scale factor for more thorough search
                    minNeighbors=3,        # Lower threshold for initial detection
                    minSize=(30, 30),      # Smaller minimum size
                    maxSize=(int(gray.shape[1]*0.8), int(gray.shape[0]*0.8)),  # Reasonable maximum size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                logger.debug(f"Cascade {cascade_name} found {len(faces)} potential faces")
                
                # Process each detected face
                for (x, y, w, h) in faces:
                    # Extract face ROI for quality assessment
                    face_roi = image[y:y+h, x:x+w] if len(image.shape) > 2 else gray[y:y+h, x:x+w]
                    
                    # Calculate comprehensive quality score
                    quality_score = self.calculate_face_quality_score(
                        face_roi, (x, y, w, h), gray.shape
                    )
                    
                    all_detections.append({
                        'bbox': [int(x), int(y), int(w), int(h)],
                        'confidence': float(quality_score),
                        'center': [int(x + w/2), int(y + h/2)],
                        'area': int(w * h),
                        'cascade': cascade_name
                    })
                    
                    logger.debug(f"Face from {cascade_name}: bbox=({x},{y},{w},{h}), quality={quality_score:.3f}")
                    
            except Exception as e:
                logger.warning(f"Error with cascade {cascade_name}: {e}")
                continue
        
        if not all_detections:
            return {
                'success': True,
                'faces_detected': 0,
                'confidence': 0.0,
                'message': 'No faces detected by any cascade classifier'
            }
        
        # Remove duplicate detections (faces detected by multiple cascades)
        filtered_detections = self.remove_duplicate_faces(all_detections)
        
        # Filter by confidence threshold
        valid_detections = [
            face for face in filtered_detections 
            if face['confidence'] >= confidence_threshold
        ]
        
        if not valid_detections:
            max_confidence = max(det['confidence'] for det in filtered_detections)
            return {
                'success': True,
                'faces_detected': 0,
                'confidence': float(max_confidence),
                'message': f'Faces detected but below confidence threshold {confidence_threshold:.3f} (max: {max_confidence:.3f})',
                'all_detections': len(filtered_detections)
            }
        
        # Sort by confidence (highest first)
        valid_detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'success': True,
            'faces_detected': len(valid_detections),
            'confidence': float(valid_detections[0]['confidence']),
            'faces': valid_detections,
            'image_dimensions': [image.shape[1], image.shape[0]],
            'total_detections': len(all_detections),
            'filtered_detections': len(filtered_detections)
        }
    
    def remove_duplicate_faces(self, detections: List[Dict], overlap_threshold: float = 0.5) -> List[Dict]:
        """
        Remove duplicate face detections based on bounding box overlap
        
        Args:
            detections: List of face detection dictionaries
            overlap_threshold: Minimum overlap ratio to consider faces as duplicates
            
        Returns:
            List of unique face detections
        """
        if len(detections) <= 1:
            return detections
        
        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        unique_detections = []
        
        for detection in detections:
            bbox1 = detection['bbox']
            is_duplicate = False
            
            for unique_detection in unique_detections:
                bbox2 = unique_detection['bbox']
                
                # Calculate intersection over union (IoU)
                iou = self.calculate_iou(bbox1, bbox2)
                
                if iou > overlap_threshold:
                    is_duplicate = True
                    logger.debug(f"Removing duplicate face (IoU: {iou:.3f})")
                    break
            
            if not is_duplicate:
                unique_detections.append(detection)
        
        return unique_detections
    
    def calculate_iou(self, bbox1: List[int], bbox2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) of two bounding boxes
        
        Args:
            bbox1: First bounding box [x, y, w, h]
            bbox2: Second bounding box [x, y, w, h]
            
        Returns:
            IoU value between 0.0 and 1.0
        """
        try:
            x1, y1, w1, h1 = bbox1
            x2, y2, w2, h2 = bbox2
            
            # Calculate intersection
            x_left = max(x1, x2)
            y_top = max(y1, y2)
            x_right = min(x1 + w1, x2 + w2)
            y_bottom = min(y1 + h1, y2 + h2)
            
            if x_right < x_left or y_bottom < y_top:
                return 0.0
            
            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            
            # Calculate union
            area1 = w1 * h1
            area2 = w2 * h2
            union_area = area1 + area2 - intersection_area
            
            if union_area == 0:
                return 0.0
            
            return intersection_area / union_area
            
        except Exception as e:
            logger.error(f"Error calculating IoU: {e}")
            return 0.0

# Global detector instance
improved_detector = ImprovedFaceDetector()

def improved_face_detector(image_data: str, confidence_threshold: float = 0.5) -> Dict:
    """
    Improved face detection function with better confidence scoring
    
    Args:
        image_data: Base64 encoded image data
        confidence_threshold: Minimum confidence threshold for face detection
        
    Returns:
        Dictionary with detection results
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {
                'success': False,
                'error': 'Failed to decode image',
                'faces_detected': 0,
                'confidence': 0.0
            }

        logger.info(f"🔍 Improved face detection on image: {image.shape[1]}x{image.shape[0]}")
        logger.info(f"🔍 Confidence threshold: {confidence_threshold}")

        # Use improved multi-cascade detection
        result = improved_detector.detect_faces_multi_cascade(image, confidence_threshold)
        
        if result['success'] and result['faces_detected'] > 0:
            logger.info(f"✅ Detected {result['faces_detected']} face(s) with max confidence {result['confidence']:.3f}")
            for i, face in enumerate(result.get('faces', [])):
                bbox = face['bbox']
                conf = face['confidence']
                cascade = face.get('cascade', 'unknown')
                logger.info(f"  Face {i+1}: bbox=({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}), "
                           f"confidence={conf:.3f}, cascade={cascade}")
        else:
            logger.warning(f"⚠️  No faces detected above threshold {confidence_threshold}")
            if 'message' in result:
                logger.info(f"ℹ️  {result['message']}")

        return result

    except Exception as e:
        logger.error(f"❌ Improved face detection error: {e}")
        return {
            'success': False,
            'error': str(e),
            'faces_detected': 0,
            'confidence': 0.0
        }

if __name__ == "__main__":
    # Test the improved face detector
    print("🧪 Testing Improved Face Detector")
    
    # This would be used in the actual application
    # For testing, you would need to provide base64 image data
    pass

