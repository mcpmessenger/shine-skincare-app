#!/usr/bin/env python3
"""
Enhanced Face Analysis Module for Shine Skincare App
Implements improved face isolation and comparison with multiple datasets
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import os
import base64
import json
import requests
from datetime import datetime
import tempfile
from pathlib import Path

# Google Cloud imports (optional)
try:
    from google.cloud import vision
    from google.auth import default
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedFaceAnalyzer:
    """Enhanced face analyzer with multiple dataset support"""
    
    def __init__(self, use_google_vision: bool = True):
        """
        Initialize enhanced face analyzer
        
        Args:
            use_google_vision: Whether to use Google Vision API for detailed analysis
        """
        self.use_google_vision = use_google_vision and VISION_AVAILABLE
        self.vision_client = None
        
        # Initialize local face detector
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
        
        # Dataset configurations
        self.datasets = {
            'facial_skin_diseases': {
                'name': 'Face Skin Diseases',
                'source': 'kaggle',
                'url': 'https://www.kaggle.com/datasets/amellia/face-skin-disease',
                'conditions': ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'eczema', 'rosacea'],
                'local_path': 'datasets/facial_skin_diseases'
            },
            'skin_defects': {
                'name': 'Skin Defects Dataset',
                'source': 'kaggle',
                'url': 'https://www.kaggle.com/datasets/trainingdatapro/skin-defects-acne-redness-and-bags-under-the-eyes',
                'conditions': ['acne', 'redness', 'bags_under_eyes'],
                'local_path': 'datasets/skin_defects'
            },
            'facial_skin_condition': {
                'name': 'Facial Skin Condition Dataset',
                'source': 'huggingface',
                'url': 'https://huggingface.co/datasets/UniDataPro/facial-skin-condition-dataset',
                'conditions': ['diverse_conditions'],
                'local_path': 'datasets/facial_skin_condition'
            },
            'normal_skin': {
                'name': 'Normal Skin Types',
                'source': 'kaggle',
                'url': 'https://www.kaggle.com/datasets/shakyadissanayake/oily-dry-and-normal-skin-types-dataset',
                'conditions': ['normal', 'oily', 'dry'],
                'local_path': 'datasets/normal_skin'
            }
        }
        
        # Age and race categories for user selection
        self.age_categories = [
            '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
        ]
        
        self.race_categories = [
            'Caucasian', 'African American', 'Asian', 'Hispanic/Latino', 
            'Middle Eastern', 'Native American', 'Mixed/Other'
        ]
    
    def analyze_face_with_demographics(self, image_data: bytes, age_category: str = None, race_category: str = None) -> Dict:
        """
        Analyze face with demographic awareness
        
        Args:
            image_data: Image data as bytes
            age_category: Age category for demographic filtering
            race_category: Race category for demographic filtering
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            logger.info("🔍 Starting enhanced face analysis with demographics")
            
            # Step 1: Detect and isolate face
            face_data = self._detect_and_isolate_face(image_data)
            
            if not face_data['face_detected']:
                return {
                    'status': 'error',
                    'message': 'No face detected in image',
                    'face_detected': False
                }
            
            # Step 2: Analyze skin conditions
            skin_analysis = self._analyze_skin_conditions(image_data, face_data)
            
            # Step 3: Perform demographic-aware similarity search
            similar_conditions = self._perform_demographic_similarity_search(
                face_data, skin_analysis, age_category, race_category
            )
            
            # Step 4: Generate comprehensive results
            result = self._generate_enhanced_analysis_result(
                face_data, skin_analysis, similar_conditions, age_category, race_category
            )
            
            logger.info("✅ Enhanced analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}',
                'face_detected': False
            }
    
    def _detect_and_isolate_face(self, image_data: bytes) -> Dict:
        """Detect and isolate face from image using the same logic as the working face detection"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'face_detected': False, 'error': 'Invalid image data'}
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Log image dimensions for debugging
            logger.info(f"Image dimensions: {img.shape}")
            logger.info(f"Grayscale image dimensions: {gray.shape}")
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Check if cascade loaded successfully
            if face_cascade.empty():
                logger.error("Failed to load face cascade classifier")
                return {'face_detected': False, 'error': 'Face detection model failed to load'}
            
            logger.info("Face cascade classifier loaded successfully")
            
            # Detect faces with initial parameters (same as working detection)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,  # More sensitive scaling
                minNeighbors=3,     # Reduced from 5 to 3 for better detection
                minSize=(20, 20)    # Smaller minimum face size
            )
            
            logger.info(f"Initial face detection result: {len(faces)} faces found")
            if len(faces) > 0:
                logger.info(f"Face coordinates: {faces[0]}")
            
            # If no faces found with initial parameters, try more lenient ones
            if len(faces) == 0:
                logger.info("Trying more lenient face detection parameters")
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.02,  # Even more sensitive
                    minNeighbors=2,     # Very lenient
                    minSize=(15, 15)    # Very small minimum
                )
                logger.info(f"Lenient detection result: {len(faces)} faces found")
                if len(faces) > 0:
                    logger.info(f"Face coordinates (lenient): {faces[0]}")
            
            # If still no faces, try even more aggressive parameters
            if len(faces) == 0:
                logger.info("Trying very aggressive face detection parameters")
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.01,  # Very sensitive
                    minNeighbors=1,     # Most lenient
                    minSize=(10, 10)    # Very small minimum
                )
                logger.info(f"Aggressive detection result: {len(faces)} faces found")
                if len(faces) > 0:
                    logger.info(f"Face coordinates (aggressive): {faces[0]}")
            
            if len(faces) > 0:
                # Face detected - use the first face
                (x, y, w, h) = faces[0]
                confidence = 0.85 + (len(faces) * 0.05)  # Higher confidence if multiple faces
                
                # Extract face region
                face_roi = img[y:y+h, x:x+w]
                
                # Assess face quality
                quality_metrics = self._assess_image_quality(img, face_roi)
                
                return {
                    'face_detected': True,
                    'confidence': min(confidence, 0.95),
                    'face_bounds': {
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h)
                    },
                    'face_roi': face_roi,
                    'quality_metrics': quality_metrics,
                    'method': 'opencv_cascade_enhanced'
                }
            else:
                # No face detected
                return {
                    'face_detected': False,
                    'error': 'No face detected',
                    'confidence': 0.0,
                    'face_bounds': {
                        'x': 0,
                        'y': 0,
                        'width': 0,
                        'height': 0
                    },
                    'quality_metrics': {
                        'lighting': 'unknown',
                        'sharpness': 'unknown',
                        'positioning': 'no_face'
                    },
                    'method': 'opencv_cascade_enhanced'
                }
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return {'face_detected': False, 'error': str(e)}
    
    def _analyze_skin_conditions(self, image_data: bytes, face_data: Dict) -> Dict:
        """Analyze skin conditions in the detected face"""
        try:
            face_roi = face_data['face_roi']
            
            # Convert to different color spaces for analysis
            face_roi_color = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(face_roi, cv2.COLOR_BGR2LAB)
            
            # Detect various skin conditions
            conditions = []
            
            # Acne detection
            acne_result = self._detect_acne(face_roi_color, hsv)
            if acne_result['detected']:
                conditions.append(acne_result)
            
            # Redness detection
            redness_result = self._detect_redness(hsv)
            if redness_result['detected']:
                conditions.append(redness_result)
            
            # Dark spots detection
            dark_spots_result = self._detect_dark_spots(lab)
            if dark_spots_result['detected']:
                conditions.append(dark_spots_result)
            
            # Texture and tone analysis
            texture = self._analyze_skin_texture(face_roi)
            tone = self._analyze_skin_tone(face_roi_color)
            
            # Overall health score calculation
            health_score = self._calculate_health_score(conditions)
            
            return {
                'overall_health_score': health_score,
                'texture': texture,
                'tone': tone,
                'conditions_detected': conditions,
                'analysis_confidence': 0.85  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Skin analysis error: {e}")
            return {
                'overall_health_score': 0.5,
                'texture': 'unknown',
                'tone': 'unknown',
                'conditions_detected': [],
                'analysis_confidence': 0.0
            }
    
    def _detect_acne(self, face_roi_color: np.ndarray, hsv: np.ndarray) -> Dict:
        """Detect acne and blemishes"""
        try:
            # Placeholder acne detection logic
            # In a real implementation, this would use more sophisticated algorithms
            
            # Simulate acne detection based on color variations
            h, s, v = cv2.split(hsv)
            
            # Look for reddish areas (potential acne)
            red_mask = cv2.inRange(h, 0, 10)
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = face_roi_color.shape[0] * face_roi_color.shape[1]
            red_ratio = red_pixels / total_pixels
            
            if red_ratio > 0.05:  # More than 5% red pixels
                severity = 'mild' if red_ratio < 0.1 else 'moderate'
                return {
                    'condition': 'acne',
                    'detected': True,
                    'severity': severity,
                    'confidence': min(red_ratio * 10, 0.9),
                    'location': 'cheeks',
                    'description': f'Acne detected with {severity} severity'
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Acne detection error: {e}")
            return {'detected': False}
    
    def _detect_redness(self, hsv: np.ndarray) -> Dict:
        """Detect skin redness and inflammation"""
        try:
            # Placeholder redness detection
            h, s, v = cv2.split(hsv)
            
            # Look for areas with high saturation and value (reddish)
            red_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = hsv.shape[0] * hsv.shape[1]
            red_ratio = red_pixels / total_pixels
            
            if red_ratio > 0.03:  # More than 3% red pixels
                severity = 'mild' if red_ratio < 0.08 else 'moderate'
                return {
                    'condition': 'redness',
                    'detected': True,
                    'severity': severity,
                    'confidence': min(red_ratio * 15, 0.85),
                    'location': 'nose_cheeks',
                    'description': f'Redness detected with {severity} severity'
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Redness detection error: {e}")
            return {'detected': False}
    
    def _detect_dark_spots(self, lab: np.ndarray) -> Dict:
        """Detect dark spots and hyperpigmentation"""
        try:
            # Placeholder dark spot detection
            l, a, b = cv2.split(lab)
            
            # Look for darker areas (lower L values)
            dark_mask = cv2.inRange(l, 0, 100)
            dark_pixels = cv2.countNonZero(dark_mask)
            total_pixels = lab.shape[0] * lab.shape[1]
            dark_ratio = dark_pixels / total_pixels
            
            if dark_ratio > 0.02:  # More than 2% dark pixels
                severity = 'mild' if dark_ratio < 0.05 else 'moderate'
                return {
                    'condition': 'dark_spots',
                    'detected': True,
                    'severity': severity,
                    'confidence': min(dark_ratio * 20, 0.8),
                    'location': 'cheeks_forehead',
                    'description': f'Dark spots detected with {severity} severity'
                }
            
            return {'detected': False}
            
        except Exception as e:
            logger.error(f"Dark spot detection error: {e}")
            return {'detected': False}
    
    def _analyze_skin_texture(self, face_roi: np.ndarray) -> str:
        """Analyze skin texture"""
        try:
            # Placeholder texture analysis
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture metrics (simplified)
            # In real implementation, this would use more sophisticated texture analysis
            std_dev = np.std(gray)
            
            if std_dev < 20:
                return 'smooth'
            elif std_dev < 40:
                return 'normal'
            else:
                return 'rough'
                
        except Exception as e:
            logger.error(f"Texture analysis error: {e}")
            return 'unknown'
    
    def _analyze_skin_tone(self, face_roi_color: np.ndarray) -> str:
        """Analyze skin tone"""
        try:
            # Placeholder tone analysis
            # Calculate average color
            avg_color = np.mean(face_roi_color, axis=(0, 1))
            
            # Simple tone classification based on RGB values
            r, g, b = avg_color
            
            if r > g and r > b:
                return 'warm'
            elif b > r and b > g:
                return 'cool'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Tone analysis error: {e}")
            return 'unknown'
    
    def _assess_image_quality(self, image: np.ndarray, face_roi: np.ndarray) -> Dict:
        """Assess image quality for analysis"""
        try:
            # Calculate basic quality metrics
            face_size = face_roi.shape[0] * face_roi.shape[1]
            image_size = image.shape[0] * image.shape[1]
            face_ratio = face_size / image_size
            
            # Brightness assessment
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            # Sharpness assessment (simplified)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            quality_score = 0.0
            if face_ratio > 0.1:  # Face takes up at least 10% of image
                quality_score += 0.3
            if brightness > 50 and brightness < 200:  # Good brightness range
                quality_score += 0.3
            if laplacian_var > 100:  # Sharp image
                quality_score += 0.4
            
            return {
                'overall_quality': 'good' if quality_score > 0.7 else 'adequate',
                'face_size_ratio': face_ratio,
                'brightness': brightness,
                'sharpness': laplacian_var,
                'quality_score': quality_score
            }
            
        except Exception as e:
            logger.error(f"Quality assessment error: {e}")
            return {
                'overall_quality': 'unknown',
                'quality_score': 0.0
            }
    
    def _perform_demographic_similarity_search(self, face_data: Dict, skin_analysis: Dict, 
                                             age_category: str = None, race_category: str = None) -> List[Dict]:
        """Perform demographic-aware similarity search"""
        try:
            # Placeholder similarity search with demographic filtering
            similar_cases = []
            
            # Simulate dataset search based on detected conditions
            for condition in skin_analysis.get('conditions_detected', []):
                if condition['condition'] == 'acne':
                    similar_cases.append({
                        'condition': 'acne',
                        'similarity_score': 0.82,
                        'dataset_source': 'kaggle_facial_skin_diseases',
                        'demographic_match': age_category if age_category else 'unknown',
                        'treatment_suggestions': [
                            'Gentle cleanser with salicylic acid',
                            'Non-comedogenic moisturizer',
                            'Avoid touching face frequently'
                        ]
                    })
                elif condition['condition'] == 'redness':
                    similar_cases.append({
                        'condition': 'redness',
                        'similarity_score': 0.75,
                        'dataset_source': 'kaggle_skin_defects',
                        'demographic_match': race_category if race_category else 'unknown',
                        'treatment_suggestions': [
                            'Use gentle, fragrance-free products',
                            'Apply soothing ingredients like aloe',
                            'Avoid hot water and harsh cleansers'
                        ]
                    })
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []
    
    def _calculate_health_score(self, conditions: List[Dict]) -> float:
        """Calculate overall skin health score"""
        try:
            base_score = 0.8  # Base healthy skin score
            
            # Deduct points for detected conditions
            for condition in conditions:
                severity = condition.get('severity', 'mild')
                if severity == 'mild':
                    base_score -= 0.05
                elif severity == 'moderate':
                    base_score -= 0.15
                elif severity == 'severe':
                    base_score -= 0.25
            
            return max(0.0, min(1.0, base_score))
            
        except Exception as e:
            logger.error(f"Health score calculation error: {e}")
            return 0.5
    
    def _generate_enhanced_analysis_result(self, face_data: Dict, skin_analysis: Dict, 
                                         similar_conditions: List[Dict], age_category: str = None, 
                                         race_category: str = None) -> Dict:
        """Generate comprehensive analysis result"""
        try:
            # Generate recommendations based on analysis
            immediate_care = self._get_immediate_care_recommendations(skin_analysis)
            long_term_care = self._get_long_term_care_recommendations(skin_analysis)
            professional_consultation = self._should_recommend_professional_consultation(skin_analysis)
            
            return {
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'enhanced',
                'demographics': {
                    'age_category': age_category,
                    'race_category': race_category
                },
                'face_detection': {
                    'detected': face_data['face_detected'],
                    'confidence': face_data.get('confidence', 0.0),
                    'face_bounds': face_data.get('face_bounds', {}),
                    'method': face_data.get('method', 'unknown'),
                    'quality_metrics': face_data.get('quality_metrics', {})
                },
                'skin_analysis': skin_analysis,
                'similarity_search': {
                    'dataset_used': 'facial_skin_diseases',
                    'similar_cases': similar_conditions
                },
                'recommendations': {
                    'immediate_care': immediate_care,
                    'long_term_care': long_term_care,
                    'professional_consultation': professional_consultation
                },
                'quality_assessment': {
                    'image_quality': face_data.get('quality_metrics', {}).get('overall_quality', 'unknown'),
                    'confidence_reliability': 'high' if face_data.get('confidence', 0) > 0.8 else 'medium'
                }
            }
            
        except Exception as e:
            logger.error(f"Result generation error: {e}")
            return {
                'status': 'error',
                'message': f'Failed to generate results: {str(e)}'
            }
    
    def _get_immediate_care_recommendations(self, skin_analysis: Dict) -> List[str]:
        """Get immediate care recommendations"""
        recommendations = []
        
        conditions = skin_analysis.get('conditions_detected', [])
        health_score = skin_analysis.get('overall_health_score', 0.5)
        
        if health_score < 0.7:
            recommendations.append('Use gentle, non-irritating cleanser')
            recommendations.append('Apply lightweight moisturizer')
            recommendations.append('Avoid harsh scrubs or exfoliants')
        
        for condition in conditions:
            if condition['condition'] == 'acne':
                recommendations.append('Use products with salicylic acid')
                recommendations.append('Avoid touching face frequently')
            elif condition['condition'] == 'redness':
                recommendations.append('Use soothing ingredients like aloe')
                recommendations.append('Avoid hot water and harsh cleansers')
        
        return recommendations
    
    def _get_long_term_care_recommendations(self, skin_analysis: Dict) -> List[str]:
        """Get long-term care recommendations"""
        recommendations = [
            'Establish consistent skincare routine',
            'Use sunscreen daily (SPF 30+)',
            'Stay hydrated and maintain healthy diet'
        ]
        
        health_score = skin_analysis.get('overall_health_score', 0.5)
        if health_score < 0.6:
            recommendations.append('Consider consulting dermatologist for persistent issues')
        
        return recommendations
    
    def _should_recommend_professional_consultation(self, skin_analysis: Dict) -> bool:
        """Determine if professional consultation is recommended"""
        conditions = skin_analysis.get('conditions_detected', [])
        health_score = skin_analysis.get('overall_health_score', 0.5)
        
        # Recommend consultation for severe conditions or low health scores
        for condition in conditions:
            if condition.get('severity') == 'severe':
                return True
        
        if health_score < 0.4:
            return True
        
        return False

def main():
    """Test the enhanced face analyzer"""
    analyzer = EnhancedFaceAnalyzer(use_google_vision=False)
    
    # Create a test image (placeholder)
    test_image = np.ones((224, 224, 3), dtype=np.uint8) * 128
    test_image_bytes = cv2.imencode('.jpg', test_image)[1].tobytes()
    
    # Test analysis
    result = analyzer.analyze_face_with_demographics(
        test_image_bytes, 
        age_category='26-35', 
        race_category='Caucasian'
    )
    
    print("Enhanced Analysis Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 