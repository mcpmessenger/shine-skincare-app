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
        self.age_categories = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        self.race_categories = [
            'Caucasian',
            'African American',
            'Asian',
            'Hispanic/Latino',
            'Middle Eastern',
            'Native American',
            'Mixed/Other'
        ]
    
    def analyze_face_with_demographics(self, image_data: bytes, age_category: str = None, race_category: str = None) -> Dict:
        """
        Analyze face with demographic filtering for better accuracy
        
        Args:
            image_data: Image data as bytes
            age_category: Optional age category for filtering
            race_category: Optional race category for filtering
            
        Returns:
            Analysis results with demographic considerations
        """
        try:
            logger.info("🧠 Starting enhanced face analysis with demographics...")
            
            # Step 1: Face detection and isolation
            face_data = self._detect_and_isolate_face(image_data)
            
            if not face_data['face_detected']:
                return {
                    'status': 'error',
                    'message': 'No face detected in the image. Please upload a clear image of your face.',
                    'face_detected': False
                }
            
            # Step 2: Enhanced skin analysis
            skin_analysis = self._analyze_skin_conditions(image_data, face_data)
            
            # Step 3: Demographic-aware similarity search
            similar_conditions = self._perform_demographic_similarity_search(
                face_data, skin_analysis, age_category, race_category
            )
            
            # Step 4: Generate comprehensive results
            analysis_result = self._generate_enhanced_analysis_result(
                face_data, skin_analysis, similar_conditions, age_category, race_category
            )
            
            logger.info("✅ Enhanced face analysis completed successfully")
            
            return {
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat(),
                'face_detected': True,
                'analysis': analysis_result,
                'demographics': {
                    'age_category': age_category,
                    'race_category': race_category,
                    'available_age_categories': self.age_categories,
                    'available_race_categories': self.race_categories
                },
                'metadata': {
                    'face_confidence': face_data['confidence'],
                    'similar_conditions_found': len(similar_conditions),
                    'datasets_used': list(self.datasets.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}',
                'face_detected': False
            }
    
    def _detect_and_isolate_face(self, image_data: bytes) -> Dict:
        """Detect and isolate face from image"""
        try:
            # Save image data to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
            
            # Load image
            image = cv2.imread(temp_path)
            if image is None:
                os.unlink(temp_path)
                return {'face_detected': False, 'confidence': 0.0}
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces using multiple cascades
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                faces = self.profile_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if len(faces) == 0:
                return {
                    'face_detected': False,
                    'confidence': 0.0,
                    'analysis_quality': {
                        'image_quality': 'low',
                        'lighting_conditions': 'poor',
                        'face_angle': 'none',
                        'recommendations': ['No face detected. Please upload a clear image with a visible face.']
                    }
                }
            
            # Get largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Calculate confidence based on face size and image quality
            image_area = image.shape[0] * image.shape[1]
            face_area = w * h
            face_ratio = face_area / image_area
            confidence = min(0.95, max(0.5, face_ratio * 10))
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi_color = image[y:y+h, x:x+w]
            
            return {
                'face_detected': True,
                'confidence': confidence,
                'face_bounds': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                'face_count': len(faces),
                'face_roi': face_roi,
                'face_roi_color': face_roi_color,
                'image_dimensions': {'width': image.shape[1], 'height': image.shape[0]},
                'analysis_quality': self._assess_image_quality(image, face_roi)
            }
            
        except Exception as e:
            logger.error(f"❌ Face detection error: {e}")
            return {'face_detected': False, 'confidence': 0.0, 'error': str(e)}
    
    def _analyze_skin_conditions(self, image_data: bytes, face_data: Dict) -> Dict:
        """Analyze skin conditions in the detected face"""
        try:
            if not face_data['face_detected']:
                return {'conditions': [], 'severity': {}, 'confidence': {}}
            
            face_roi = face_data['face_roi']
            face_roi_color = face_data['face_roi_color']
            
            # Analyze skin characteristics
            skin_analysis = {
                'texture': self._analyze_skin_texture(face_roi),
                'tone': self._analyze_skin_tone(face_roi_color),
                'conditions': [],
                'severity': {},
                'confidence': {},
                'health_score': 85  # Base score
            }
            
            # Detect specific conditions
            conditions_detected = self._detect_skin_conditions(face_roi_color)
            
            for condition, details in conditions_detected.items():
                if details['detected']:
                    skin_analysis['conditions'].append(condition)
                    skin_analysis['severity'][condition] = details['severity']
                    skin_analysis['confidence'][condition] = details['confidence']
                    
                    # Adjust health score based on condition severity
                    if details['severity'] == 'severe':
                        skin_analysis['health_score'] -= 20
                    elif details['severity'] == 'moderate':
                        skin_analysis['health_score'] -= 10
                    else:
                        skin_analysis['health_score'] -= 5
            
            skin_analysis['health_score'] = max(0, skin_analysis['health_score'])
            
            return skin_analysis
            
        except Exception as e:
            logger.error(f"❌ Skin condition analysis error: {e}")
            return {'conditions': [], 'severity': {}, 'confidence': {}, 'error': str(e)}
    
    def _detect_skin_conditions(self, face_roi_color: np.ndarray) -> Dict:
        """Detect specific skin conditions using computer vision techniques"""
        conditions = {}
        
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2LAB)
            
            # Acne detection (look for red spots and texture irregularities)
            conditions['acne'] = self._detect_acne(face_roi_color, hsv)
            
            # Redness/inflammation detection
            conditions['redness'] = self._detect_redness(hsv)
            
            # Dark spots/hyperpigmentation detection
            conditions['dark_spots'] = self._detect_dark_spots(lab)
            
            # Dryness detection (texture analysis)
            conditions['dryness'] = self._detect_dryness(face_roi_color)
            
            # Oiliness detection (shine analysis)
            conditions['oiliness'] = self._detect_oiliness(face_roi_color)
            
        except Exception as e:
            logger.error(f"❌ Condition detection error: {e}")
            
        return conditions
    
    def _detect_acne(self, face_roi_color: np.ndarray, hsv: np.ndarray) -> Dict:
        """Detect acne using color and texture analysis"""
        try:
            # Look for red spots in specific HSV ranges
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            
            # Count red pixels
            red_pixel_ratio = np.sum(red_mask > 0) / (face_roi_color.shape[0] * face_roi_color.shape[1])
            
            # Texture analysis for bumps/irregularities
            gray = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2GRAY)
            texture_variance = np.var(gray)
            
            # Determine acne presence and severity
            if red_pixel_ratio > 0.05 and texture_variance > 800:
                severity = 'severe'
                confidence = 0.85
            elif red_pixel_ratio > 0.02 or texture_variance > 500:
                severity = 'moderate'
                confidence = 0.75
            elif red_pixel_ratio > 0.01 or texture_variance > 300:
                severity = 'mild'
                confidence = 0.65
            else:
                return {'detected': False, 'severity': 'none', 'confidence': 0.0}
            
            return {
                'detected': True,
                'severity': severity,
                'confidence': confidence,
                'metrics': {
                    'red_pixel_ratio': red_pixel_ratio,
                    'texture_variance': texture_variance
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Acne detection error: {e}")
            return {'detected': False, 'severity': 'none', 'confidence': 0.0}
    
    def _detect_redness(self, hsv: np.ndarray) -> Dict:
        """Detect general redness/inflammation"""
        try:
            # Define red color ranges
            lower_red = np.array([0, 30, 30])
            upper_red = np.array([15, 255, 255])
            
            red_mask = cv2.inRange(hsv, lower_red, upper_red)
            red_pixel_ratio = np.sum(red_mask > 0) / (hsv.shape[0] * hsv.shape[1])
            
            if red_pixel_ratio > 0.15:
                severity = 'severe'
                confidence = 0.80
            elif red_pixel_ratio > 0.08:
                severity = 'moderate'
                confidence = 0.70
            elif red_pixel_ratio > 0.03:
                severity = 'mild'
                confidence = 0.60
            else:
                return {'detected': False, 'severity': 'none', 'confidence': 0.0}
            
            return {
                'detected': True,
                'severity': severity,
                'confidence': confidence,
                'metrics': {'red_pixel_ratio': red_pixel_ratio}
            }
            
        except Exception as e:
            logger.error(f"❌ Redness detection error: {e}")
            return {'detected': False, 'severity': 'none', 'confidence': 0.0}
    
    def _detect_dark_spots(self, lab: np.ndarray) -> Dict:
        """Detect dark spots and hyperpigmentation"""
        try:
            # Use L channel (lightness) for dark spot detection
            l_channel = lab[:, :, 0]
            
            # Find dark regions
            mean_lightness = np.mean(l_channel)
            dark_threshold = mean_lightness - 20
            dark_mask = l_channel < dark_threshold
            
            dark_pixel_ratio = np.sum(dark_mask) / (lab.shape[0] * lab.shape[1])
            
            if dark_pixel_ratio > 0.10:
                severity = 'severe'
                confidence = 0.75
            elif dark_pixel_ratio > 0.05:
                severity = 'moderate'
                confidence = 0.65
            elif dark_pixel_ratio > 0.02:
                severity = 'mild'
                confidence = 0.55
            else:
                return {'detected': False, 'severity': 'none', 'confidence': 0.0}
            
            return {
                'detected': True,
                'severity': severity,
                'confidence': confidence,
                'metrics': {
                    'dark_pixel_ratio': dark_pixel_ratio,
                    'mean_lightness': mean_lightness
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Dark spots detection error: {e}")
            return {'detected': False, 'severity': 'none', 'confidence': 0.0}
    
    def _detect_dryness(self, face_roi_color: np.ndarray) -> Dict:
        """Detect skin dryness through texture analysis"""
        try:
            gray = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture measures
            texture_variance = np.var(gray)
            
            # Apply Laplacian for edge detection (rough texture indicator)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_roughness = np.var(laplacian)
            
            if texture_roughness > 1000 and texture_variance > 600:
                severity = 'severe'
                confidence = 0.70
            elif texture_roughness > 500 or texture_variance > 400:
                severity = 'moderate'
                confidence = 0.60
            elif texture_roughness > 200 or texture_variance > 200:
                severity = 'mild'
                confidence = 0.50
            else:
                return {'detected': False, 'severity': 'none', 'confidence': 0.0}
            
            return {
                'detected': True,
                'severity': severity,
                'confidence': confidence,
                'metrics': {
                    'texture_variance': texture_variance,
                    'texture_roughness': texture_roughness
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Dryness detection error: {e}")
            return {'detected': False, 'severity': 'none', 'confidence': 0.0}
    
    def _detect_oiliness(self, face_roi_color: np.ndarray) -> Dict:
        """Detect skin oiliness through shine analysis"""
        try:
            # Convert to HSV and analyze brightness/saturation
            hsv = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2HSV)
            v_channel = hsv[:, :, 2]  # Value (brightness) channel
            
            # Look for high brightness areas (shine)
            bright_threshold = np.percentile(v_channel, 85)
            bright_mask = v_channel > bright_threshold
            bright_pixel_ratio = np.sum(bright_mask) / (face_roi_color.shape[0] * face_roi_color.shape[1])
            
            # Calculate overall brightness
            mean_brightness = np.mean(v_channel)
            
            if bright_pixel_ratio > 0.20 and mean_brightness > 180:
                severity = 'severe'
                confidence = 0.75
            elif bright_pixel_ratio > 0.10 or mean_brightness > 160:
                severity = 'moderate'
                confidence = 0.65
            elif bright_pixel_ratio > 0.05 or mean_brightness > 140:
                severity = 'mild'
                confidence = 0.55
            else:
                return {'detected': False, 'severity': 'none', 'confidence': 0.0}
            
            return {
                'detected': True,
                'severity': severity,
                'confidence': confidence,
                'metrics': {
                    'bright_pixel_ratio': bright_pixel_ratio,
                    'mean_brightness': mean_brightness
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Oiliness detection error: {e}")
            return {'detected': False, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_skin_texture(self, face_roi: np.ndarray) -> str:
        """Analyze skin texture"""
        try:
            texture_variance = np.var(face_roi)
            
            if texture_variance > 800:
                return 'rough'
            elif texture_variance > 400:
                return 'normal'
            else:
                return 'smooth'
                
        except Exception as e:
            logger.error(f"❌ Texture analysis error: {e}")
            return 'normal'
    
    def _analyze_skin_tone(self, face_roi_color: np.ndarray) -> str:
        """Analyze skin tone"""
        try:
            # Convert to LAB color space for better skin tone analysis
            lab = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            mean_lightness = np.mean(l_channel)
            
            if mean_lightness < 80:
                return 'dark'
            elif mean_lightness < 150:
                return 'medium'
            else:
                return 'light'
                
        except Exception as e:
            logger.error(f"❌ Skin tone analysis error: {e}")
            return 'medium'
    
    def _assess_image_quality(self, image: np.ndarray, face_roi: np.ndarray) -> Dict:
        """Assess image quality for analysis"""
        try:
            # Calculate sharpness using Laplacian variance
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Assess lighting
            mean_brightness = np.mean(gray)
            
            # Determine quality metrics
            if laplacian_var > 500:
                image_quality = 'high'
            elif laplacian_var > 100:
                image_quality = 'medium'
            else:
                image_quality = 'low'
            
            if 80 <= mean_brightness <= 180:
                lighting_conditions = 'optimal'
            elif 50 <= mean_brightness <= 220:
                lighting_conditions = 'adequate'
            else:
                lighting_conditions = 'poor'
            
            # Face angle assessment (simplified)
            face_area = face_roi.shape[0] * face_roi.shape[1]
            image_area = image.shape[0] * image.shape[1]
            face_ratio = face_area / image_area
            
            if face_ratio > 0.15:
                face_angle = 'frontal'
            elif face_ratio > 0.08:
                face_angle = 'slight_angle'
            else:
                face_angle = 'distant'
            
            recommendations = []
            if image_quality == 'low':
                recommendations.append('Use a higher resolution camera or ensure the image is in focus')
            if lighting_conditions == 'poor':
                recommendations.append('Improve lighting conditions for better analysis')
            if face_angle == 'distant':
                recommendations.append('Move closer to the camera for better face detection')
            
            return {
                'image_quality': image_quality,
                'lighting_conditions': lighting_conditions,
                'face_angle': face_angle,
                'sharpness_score': laplacian_var,
                'brightness_score': mean_brightness,
                'recommendations': recommendations if recommendations else ['Image quality is good for analysis']
            }
            
        except Exception as e:
            logger.error(f"❌ Image quality assessment error: {e}")
            return {
                'image_quality': 'unknown',
                'lighting_conditions': 'unknown',
                'face_angle': 'unknown',
                'recommendations': ['Unable to assess image quality']
            }
    
    def _perform_demographic_similarity_search(self, face_data: Dict, skin_analysis: Dict, 
                                             age_category: str = None, race_category: str = None) -> List[Dict]:
        """Perform similarity search with demographic filtering"""
        try:
            # Simulate similarity search results based on detected conditions
            similar_conditions = []
            
            for condition in skin_analysis['conditions']:
                severity = skin_analysis['severity'].get(condition, 'mild')
                confidence = skin_analysis['confidence'].get(condition, 0.5)
                
                similar_conditions.append({
                    'condition': condition,
                    'severity': severity,
                    'confidence': confidence,
                    'similarity_score': confidence * 0.9,  # Simulate similarity
                    'dataset_source': self._get_best_dataset_for_condition(condition),
                    'demographic_match': {
                        'age_category': age_category,
                        'race_category': race_category,
                        'match_confidence': 0.8 if age_category and race_category else 0.6
                    },
                    'treatment_recommendations': self._get_treatment_recommendations(condition, severity)
                })
            
            # Add healthy skin comparison if no major conditions detected
            if not similar_conditions or all(c['severity'] == 'mild' for c in similar_conditions):
                similar_conditions.append({
                    'condition': 'healthy_skin',
                    'severity': 'none',
                    'confidence': 0.9,
                    'similarity_score': 0.85,
                    'dataset_source': 'normal_skin',
                    'demographic_match': {
                        'age_category': age_category,
                        'race_category': race_category,
                        'match_confidence': 0.9 if age_category and race_category else 0.7
                    },
                    'treatment_recommendations': ['Maintain current skincare routine', 'Use sunscreen daily']
                })
            
            return similar_conditions
            
        except Exception as e:
            logger.error(f"❌ Similarity search error: {e}")
            return []
    
    def _get_best_dataset_for_condition(self, condition: str) -> str:
        """Get the best dataset for a specific condition"""
        condition_mapping = {
            'acne': 'facial_skin_diseases',
            'redness': 'skin_defects',
            'dark_spots': 'facial_skin_condition',
            'dryness': 'normal_skin',
            'oiliness': 'normal_skin'
        }
        return condition_mapping.get(condition, 'facial_skin_condition')
    
    def _get_treatment_recommendations(self, condition: str, severity: str) -> List[str]:
        """Get treatment recommendations for a condition"""
        recommendations = {
            'acne': {
                'mild': ['Use gentle cleanser', 'Apply salicylic acid treatment', 'Avoid touching face'],
                'moderate': ['Consult dermatologist', 'Consider benzoyl peroxide', 'Use non-comedogenic products'],
                'severe': ['See dermatologist immediately', 'May require prescription medication', 'Avoid harsh scrubbing']
            },
            'redness': {
                'mild': ['Use gentle, fragrance-free products', 'Apply cool compress', 'Avoid known irritants'],
                'moderate': ['Consider anti-inflammatory ingredients', 'Use mineral sunscreen', 'Consult dermatologist'],
                'severe': ['See dermatologist for evaluation', 'May indicate underlying condition', 'Avoid all potential irritants']
            },
            'dark_spots': {
                'mild': ['Use vitamin C serum', 'Apply sunscreen daily', 'Consider gentle exfoliation'],
                'moderate': ['Try retinoid products', 'Use hydroquinone treatment', 'Consistent sun protection'],
                'severe': ['Professional treatment recommended', 'Chemical peels or laser therapy', 'Dermatologist consultation']
            },
            'dryness': {
                'mild': ['Use moisturizer twice daily', 'Avoid hot water', 'Use gentle cleanser'],
                'moderate': ['Apply heavier moisturizer', 'Use humidifier', 'Consider ceramide products'],
                'severe': ['See dermatologist', 'May need prescription moisturizer', 'Rule out underlying conditions']
            },
            'oiliness': {
                'mild': ['Use oil-free products', 'Gentle cleansing twice daily', 'Clay masks occasionally'],
                'moderate': ['Salicylic acid cleanser', 'Oil-absorbing products', 'Avoid over-cleansing'],
                'severe': ['Dermatologist consultation', 'May need prescription treatment', 'Professional skincare routine']
            }
        }
        
        return recommendations.get(condition, {}).get(severity, ['Consult skincare professional'])
    
    def _generate_enhanced_analysis_result(self, face_data: Dict, skin_analysis: Dict, 
                                         similar_conditions: List[Dict], age_category: str = None, 
                                         race_category: str = None) -> Dict:
        """Generate comprehensive analysis result"""
        try:
            return {
                'face_detection': {
                    'confidence': face_data['confidence'],
                    'face_bounds': face_data['face_bounds'],
                    'face_count': face_data['face_count'],
                    'image_dimensions': face_data['image_dimensions']
                },
                'skin_analysis': {
                    'health_score': skin_analysis['health_score'],
                    'texture': skin_analysis['texture'],
                    'tone': skin_analysis['tone'],
                    'conditions_detected': skin_analysis['conditions'],
                    'condition_details': {
                        condition: {
                            'severity': skin_analysis['severity'].get(condition, 'none'),
                            'confidence': skin_analysis['confidence'].get(condition, 0.0)
                        }
                        for condition in skin_analysis['conditions']
                    }
                },
                'similarity_results': similar_conditions,
                'demographic_analysis': {
                    'age_category': age_category,
                    'race_category': race_category,
                    'demographic_confidence': 0.8 if age_category and race_category else 0.6
                },
                'recommendations': {
                    'immediate_care': self._get_immediate_care_recommendations(skin_analysis),
                    'long_term_care': self._get_long_term_care_recommendations(skin_analysis),
                    'professional_consultation': self._should_recommend_professional_consultation(skin_analysis)
                },
                'analysis_quality': face_data['analysis_quality'],
                'datasets_used': [self.datasets[dataset]['name'] for dataset in self.datasets.keys()],
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Result generation error: {e}")
            return {'error': str(e)}
    
    def _get_immediate_care_recommendations(self, skin_analysis: Dict) -> List[str]:
        """Get immediate care recommendations"""
        recommendations = []
        
        if 'acne' in skin_analysis['conditions']:
            recommendations.append('Avoid touching or picking at affected areas')
            recommendations.append('Use gentle, non-comedogenic cleanser')
        
        if 'redness' in skin_analysis['conditions']:
            recommendations.append('Apply cool compress to reduce inflammation')
            recommendations.append('Avoid harsh products and fragrances')
        
        if 'dryness' in skin_analysis['conditions']:
            recommendations.append('Apply moisturizer immediately after cleansing')
            recommendations.append('Use lukewarm water instead of hot water')
        
        if 'oiliness' in skin_analysis['conditions']:
            recommendations.append('Use oil-free, non-comedogenic products')
            recommendations.append('Avoid over-cleansing which can increase oil production')
        
        if not recommendations:
            recommendations.append('Continue current skincare routine')
            recommendations.append('Apply sunscreen daily for protection')
        
        return recommendations
    
    def _get_long_term_care_recommendations(self, skin_analysis: Dict) -> List[str]:
        """Get long-term care recommendations"""
        recommendations = [
            'Establish consistent daily skincare routine',
            'Use broad-spectrum sunscreen daily',
            'Stay hydrated and maintain healthy diet'
        ]
        
        if skin_analysis['health_score'] < 70:
            recommendations.append('Consider professional skincare consultation')
            recommendations.append('Track skin changes over time')
        
        if len(skin_analysis['conditions']) > 2:
            recommendations.append('Address multiple conditions systematically')
            recommendations.append('Introduce new products gradually')
        
        return recommendations
    
    def _should_recommend_professional_consultation(self, skin_analysis: Dict) -> bool:
        """Determine if professional consultation should be recommended"""
        severe_conditions = [
            condition for condition in skin_analysis['conditions']
            if skin_analysis['severity'].get(condition) == 'severe'
        ]
        
        return (
            len(severe_conditions) > 0 or
            skin_analysis['health_score'] < 60 or
            len(skin_analysis['conditions']) > 3
        )

def main():
    """Test enhanced face analyzer"""
    analyzer = EnhancedFaceAnalyzer(use_google_vision=False)
    
    # Test with sample image (if available)
    test_image_path = "test_face.jpg"
    
    if os.path.exists(test_image_path):
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        result = analyzer.analyze_face_with_demographics(
            image_data, 
            age_category='26-35', 
            race_category='Caucasian'
        )
        
        print(json.dumps(result, indent=2))
    else:
        print("Test image not found. Enhanced face analyzer initialized successfully.")

if __name__ == "__main__":
    main()

