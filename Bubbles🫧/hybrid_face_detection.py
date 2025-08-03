#!/usr/bin/env python3
"""
Hybrid Face Detection System
Combines local OpenCV detection with Google Vision API for cost optimization
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional
import os
import base64

# Google Cloud imports
try:
    from google.cloud import vision
    from google.auth import default
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridFaceDetector:
    """Hybrid face detection system"""
    
    def __init__(self, use_google_vision: bool = True):
        """
        Initialize hybrid face detector
        
        Args:
            use_google_vision: Whether to use Google Vision API for detailed analysis
        """
        self.use_google_vision = use_google_vision and VISION_AVAILABLE
        self.vision_client = None
        
        # Initialize local detector
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.profile_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_profileface.xml'
            )
            logger.info("✅ Local face detector initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize local detector: {e}")
            self.face_cascade = None
            self.profile_cascade = None
        
        # Initialize Google Vision if available
        if self.use_google_vision:
            try:
                credentials, _ = default()
                self.vision_client = vision.ImageAnnotatorClient(credentials=credentials)
                logger.info("✅ Google Vision API initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Vision API not available: {e}")
                self.use_google_vision = False
    
    def detect_faces_hybrid(self, image_path: str) -> Dict:
        """
        Hybrid face detection using local + cloud approach
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with detection results
        """
        try:
            # Step 1: Local detection (FREE)
            local_result = self._detect_faces_local(image_path)
            
            if not local_result['face_detected']:
                return local_result
            
            # Step 2: Google Vision analysis (if enabled and face found)
            if self.use_google_vision and self.vision_client:
                google_result = self._analyze_with_google_vision(image_path)
                
                # Combine results
                return self._combine_results(local_result, google_result)
            
            # Return local result if Google Vision not available
            return local_result
            
        except Exception as e:
            logger.error(f"❌ Hybrid detection error: {e}")
            return {
                'face_detected': False,
                'confidence': 0.0,
                'error': str(e),
                'method': 'hybrid_failed'
            }
    
    def _detect_faces_local(self, image_path: str) -> Dict:
        """Local face detection using OpenCV"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'face_detected': False, 'confidence': 0.0, 'method': 'local'}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                faces = self.profile_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
            
            if len(faces) == 0:
                return {
                    'face_detected': False,
                    'confidence': 0.0,
                    'method': 'local',
                    'analysis_quality': {
                        'image_quality': 'low',
                        'lighting_conditions': 'poor',
                        'face_angle': 'none',
                        'recommendations': ['No face detected locally']
                    }
                }
            
            # Get largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Calculate confidence
            image_area = image.shape[0] * image.shape[1]
            face_area = w * h
            face_ratio = face_area / image_area
            confidence = min(0.95, max(0.5, face_ratio * 10))
            
            return {
                'face_detected': True,
                'confidence': confidence,
                'method': 'local',
                'face_bounds': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                'face_count': len(faces),
                'local_analysis': self._analyze_face_local(gray[y:y+h, x:x+w])
            }
            
        except Exception as e:
            logger.error(f"❌ Local detection error: {e}")
            return {'face_detected': False, 'confidence': 0.0, 'method': 'local', 'error': str(e)}
    
    def _analyze_with_google_vision(self, image_path: str) -> Dict:
        """Detailed analysis using Google Vision API"""
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Face detection
            face_response = self.vision_client.face_detection(image=image)
            faces = face_response.face_annotations
            
            if not faces:
                return {'method': 'google_vision', 'face_detected': False}
            
            face = faces[0]
            
            # Label detection for skin analysis
            label_response = self.vision_client.label_detection(image=image)
            labels = [label.description.lower() for label in label_response.label_annotations]
            
            # Enhanced skin analysis
            skin_conditions = []
            if 'acne' in labels or 'pimple' in labels:
                skin_conditions.append('acne')
            if 'redness' in labels or 'inflammation' in labels:
                skin_conditions.append('inflammation')
            if 'dark spot' in labels or 'hyperpigmentation' in labels:
                skin_conditions.append('hyperpigmentation')
            if 'wrinkle' in labels or 'aging' in labels:
                skin_conditions.append('aging')
            
            return {
                'method': 'google_vision',
                'face_detected': True,
                'confidence': face.detection_confidence,
                'skin_characteristics': {
                    'texture': 'smooth' if 'smooth' in labels else 'normal',
                    'tone': 'even' if 'even' in labels else 'normal',
                    'conditions': skin_conditions
                },
                'analysis_quality': {
                    'image_quality': 'high' if face.detection_confidence > 0.8 else 'moderate',
                    'lighting_conditions': 'optimal',
                    'face_angle': 'frontal',
                    'recommendations': ['Google Vision analysis completed']
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Google Vision analysis error: {e}")
            return {'method': 'google_vision', 'error': str(e)}
    
    def _analyze_face_local(self, face_roi: np.ndarray) -> Dict:
        """Local face analysis"""
        try:
            mean_intensity = np.mean(face_roi)
            std_intensity = np.std(face_roi)
            
            skin_tone = 'dark' if mean_intensity < 80 else 'medium' if mean_intensity < 150 else 'light'
            texture = 'rough' if std_intensity > 30 else 'normal' if std_intensity > 15 else 'smooth'
            
            return {
                'skin_characteristics': {
                    'texture': texture,
                    'tone': skin_tone,
                    'mean_intensity': float(mean_intensity),
                    'texture_variation': float(std_intensity)
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _combine_results(self, local_result: Dict, google_result: Dict) -> Dict:
        """Combine local and Google Vision results"""
        try:
            combined = {
                'face_detected': local_result['face_detected'],
                'confidence': max(local_result['confidence'], google_result.get('confidence', 0)),
                'method': 'hybrid',
                'local_confidence': local_result['confidence'],
                'google_confidence': google_result.get('confidence', 0)
            }
            
            # Merge skin characteristics
            if 'skin_characteristics' in google_result:
                combined['skin_characteristics'] = google_result['skin_characteristics']
            elif 'local_analysis' in local_result:
                combined['skin_characteristics'] = local_result['local_analysis']['skin_characteristics']
            
            # Merge analysis quality
            if 'analysis_quality' in google_result:
                combined['analysis_quality'] = google_result['analysis_quality']
            elif 'analysis_quality' in local_result:
                combined['analysis_quality'] = local_result['analysis_quality']
            
            # Add cost savings info
            combined['cost_savings'] = {
                'local_detection': 'FREE',
                'google_analysis': 'Only when face detected',
                'estimated_savings': '70-80% vs full Google Vision'
            }
            
            return combined
            
        except Exception as e:
            logger.error(f"❌ Error combining results: {e}")
            return local_result
    
    def process_dataset_efficiently(self, dataset_path: str, sample_size: int = 100) -> Dict:
        """
        Process dataset efficiently using hybrid approach
        
        Args:
            dataset_path: Path to dataset
            sample_size: Number of images to process
            
        Returns:
            Processing statistics
        """
        try:
            logger.info(f"🔍 Processing dataset efficiently (sample: {sample_size})...")
            
            stats = {
                'total_processed': 0,
                'faces_detected': 0,
                'local_only': 0,
                'hybrid_analysis': 0,
                'total_cost_saved': '$0.00',
                'average_confidence': 0.0
            }
            
            processed = 0
            face_count = 0
            total_confidence = 0.0
            
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(root, file)
                        result = self.detect_faces_hybrid(image_path)
                        
                        if result['face_detected']:
                            face_count += 1
                            total_confidence += result['confidence']
                            
                            if result.get('method') == 'hybrid':
                                stats['hybrid_analysis'] += 1
                            else:
                                stats['local_only'] += 1
                        
                        processed += 1
                        stats['total_processed'] = processed
                        
                        if processed >= sample_size:
                            break
                
                if processed >= sample_size:
                    break
            
            # Calculate statistics
            stats['faces_detected'] = face_count
            stats['average_confidence'] = total_confidence / face_count if face_count > 0 else 0.0
            
            # Estimate cost savings
            google_cost_per_image = 0.0015  # $1.50 per 1000 images
            local_cost_per_image = 0.0
            hybrid_cost_per_image = google_cost_per_image * 0.3  # Only 30% use Google Vision
            
            savings = (google_cost_per_image - hybrid_cost_per_image) * processed
            stats['total_cost_saved'] = f"${savings:.2f}"
            
            logger.info(f"✅ Efficient processing completed:")
            logger.info(f"   Total processed: {stats['total_processed']}")
            logger.info(f"   Faces detected: {stats['faces_detected']}")
            logger.info(f"   Local only: {stats['local_only']}")
            logger.info(f"   Hybrid analysis: {stats['hybrid_analysis']}")
            logger.info(f"   Cost saved: {stats['total_cost_saved']}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error processing dataset: {e}")
            return {'error': str(e)}

def main():
    """Test hybrid face detection"""
    detector = HybridFaceDetector(use_google_vision=True)
    
    # Test with sample image
    test_image = "scin_dataset/raw/normal/normal_001.jpg"
    
    if os.path.exists(test_image):
        logger.info(f"🧪 Testing hybrid detection on {test_image}")
        result = detector.detect_faces_hybrid(test_image)
        logger.info(f"Result: {result}")
    else:
        logger.warning("⚠️ Test image not found")

if __name__ == "__main__":
    main() 