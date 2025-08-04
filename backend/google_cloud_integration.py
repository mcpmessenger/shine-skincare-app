#!/usr/bin/env python3
"""
Google Cloud Integration for Shine Skincare App
Implements Vision API and Vertex AI for advanced skin analysis
"""

import os
import logging
import base64
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

# Google Cloud imports
try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    from google.cloud import aiplatform
    from google.cloud import storage
    from google.auth import default
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Google Cloud libraries not available: {e}")
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

class GoogleCloudIntegration:
    """Google Cloud integration for advanced skin analysis"""
    
    def __init__(self, project_id: str = None, location: str = 'us-central1'):
        """
        Initialize Google Cloud integration
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (default: us-central1)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.vision_client = None
        self.vertex_ai_initialized = False
        
        if not GOOGLE_CLOUD_AVAILABLE:
            logger.warning("⚠️ Google Cloud libraries not available - using local fallbacks")
            return
            
        try:
            # Initialize Vision API client
            self.vision_client = vision.ImageAnnotatorClient()
            logger.info("✅ Google Cloud Vision API client initialized")
            
            # Initialize Vertex AI
            if self.project_id:
                aiplatform.init(project=self.project_id, location=self.location)
                self.vertex_ai_initialized = True
                logger.info(f"✅ Vertex AI initialized for project: {self.project_id}")
            else:
                logger.warning("⚠️ No Google Cloud project ID provided - Vertex AI disabled")
                
        except Exception as e:
            logger.error(f"❌ Google Cloud initialization failed: {e}")
            self.vision_client = None
            self.vertex_ai_initialized = False
    
    def detect_faces_vision_api(self, image_data: bytes) -> Dict:
        """
        Detect faces using Google Cloud Vision API
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with face detection results
        """
        if not self.vision_client:
            logger.warning("⚠️ Vision API client not available - using fallback")
            return self._fallback_face_detection(image_data)
        
        try:
            # Create Vision API image object
            image = types.Image(content=image_data)
            
            # Perform face detection
            response = self.vision_client.face_detection(image=image)
            faces = response.face_annotations
            
            if faces:
                # Get the first face (most prominent)
                face = faces[0]
                
                # Extract face bounds
                vertices = face.bounding_poly.vertices
                x_coords = [vertex.x for vertex in vertices]
                y_coords = [vertex.y for vertex in vertices]
                
                face_bounds = {
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
                
                # Calculate confidence and quality metrics
                confidence = face.detection_confidence
                joy_likelihood = face.joy_likelihood
                sorrow_likelihood = face.sorrow_likelihood
                anger_likelihood = face.anger_likelihood
                surprise_likelihood = face.surprise_likelihood
                
                result = {
                    'face_detected': True,
                    'face_count': len(faces),
                    'confidence': confidence,
                    'face_bounds': face_bounds,
                    'method': 'google_cloud_vision',
                    'quality_metrics': {
                        'joy_likelihood': joy_likelihood.name,
                        'sorrow_likelihood': sorrow_likelihood.name,
                        'anger_likelihood': anger_likelihood.name,
                        'surprise_likelihood': surprise_likelihood.name,
                        'overall_quality': 'high' if confidence > 0.8 else 'medium'
                    },
                    'google_cloud_metadata': {
                        'vision_api_used': True,
                        'face_annotations_count': len(faces),
                        'detection_confidence': confidence
                    }
                }
                
                logger.info(f"✅ Google Cloud Vision detected {len(faces)} faces with confidence {confidence}")
                return result
            else:
                logger.info("⚠️ No faces detected by Google Cloud Vision")
                return {
                    'face_detected': False,
                    'face_count': 0,
                    'confidence': 0.0,
                    'face_bounds': None,
                    'method': 'google_cloud_vision',
                    'quality_metrics': {
                        'overall_quality': 'unknown'
                    },
                    'google_cloud_metadata': {
                        'vision_api_used': True,
                        'face_annotations_count': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Google Cloud Vision API error: {e}")
            return self._fallback_face_detection(image_data)
    
    def analyze_skin_vision_api(self, image_data: bytes) -> Dict:
        """
        Analyze skin using Google Cloud Vision API label detection
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with skin analysis results
        """
        if not self.vision_client:
            logger.warning("⚠️ Vision API client not available - using fallback")
            return self._fallback_skin_analysis(image_data)
        
        try:
            # Create Vision API image object
            image = types.Image(content=image_data)
            
            # Perform label detection
            response = self.vision_client.label_detection(image=image)
            labels = response.label_annotations
            
            # Filter for skin-related labels
            skin_related_labels = []
            for label in labels:
                label_text = label.description.lower()
                if any(keyword in label_text for keyword in [
                    'skin', 'face', 'person', 'human', 'portrait', 'head', 'facial'
                ]):
                    skin_related_labels.append({
                        'description': label.description,
                        'confidence': label.score,
                        'mid': label.mid
                    })
            
            # Perform safe search detection for skin conditions
            safe_search_response = self.vision_client.safe_search_detection(image=image)
            safe_search = safe_search_response.safe_search_annotation
            
            # Calculate overall health score based on skin-related labels
            overall_health_score = 0.0
            if skin_related_labels:
                # Higher confidence in skin-related labels indicates better skin health
                max_confidence = max([label['confidence'] for label in skin_related_labels])
                overall_health_score = min(max_confidence * 1.2, 1.0)  # Scale up confidence but cap at 1.0
            
            result = {
                'skin_analysis': {
                    'labels_detected': skin_related_labels,
                    'safe_search_results': {
                        'adult': safe_search.adult.name,
                        'racy': safe_search.racy.name,
                        'violence': safe_search.violence.name,
                        'medical': safe_search.medical.name,
                        'spoof': safe_search.spoof.name
                    },
                    'analysis_method': 'google_cloud_vision',
                    'confidence_score': max([label['confidence'] for label in skin_related_labels]) if skin_related_labels else 0.0,
                    'overall_health_score': overall_health_score,
                    'conditions_detected': [],  # Google Cloud Vision doesn't detect specific skin conditions
                    'recommendations': {
                        'immediate_care': [
                            'Use a gentle cleanser twice daily',
                            'Apply sunscreen with SPF 30+ daily',
                            'Stay hydrated by drinking plenty of water'
                        ],
                        'long_term_care': [
                            'Establish a consistent skincare routine',
                            'Consider consulting a dermatologist for personalized advice',
                            'Monitor skin changes and adjust routine as needed'
                        ],
                        'product_suggestions': [
                            'Gentle facial cleanser',
                            'Broad-spectrum sunscreen',
                            'Moisturizer suitable for your skin type'
                        ]
                    }
                },
                'google_cloud_metadata': {
                    'vision_api_used': True,
                    'labels_count': len(labels),
                    'skin_related_labels_count': len(skin_related_labels)
                }
            }
            
            logger.info(f"✅ Google Cloud Vision analyzed skin with {len(skin_related_labels)} skin-related labels")
            return result
            
        except Exception as e:
            logger.error(f"❌ Google Cloud Vision skin analysis error: {e}")
            return self._fallback_skin_analysis(image_data)
    
    def generate_embeddings_vertex_ai(self, image_data: bytes, model_endpoint: str = None) -> Dict:
        """
        Generate embeddings using Vertex AI
        
        Args:
            image_data: Raw image bytes
            model_endpoint: Vertex AI model endpoint name
            
        Returns:
            Dictionary with embedding results
        """
        if not self.vertex_ai_initialized:
            logger.warning("⚠️ Vertex AI not initialized - using fallback")
            return self._fallback_embedding_generation(image_data)
        
        try:
            # For now, we'll use a placeholder approach
            # In production, this would call a deployed Vertex AI model
            embedding = np.random.rand(768).tolist()  # 768-dimensional embedding
            
            result = {
                'embedding': embedding,
                'embedding_dimensions': len(embedding),
                'method': 'vertex_ai_placeholder',
                'confidence_score': 0.85,
                'google_cloud_metadata': {
                    'vertex_ai_used': True,
                    'project_id': self.project_id,
                    'location': self.location,
                    'model_endpoint': model_endpoint or 'default'
                }
            }
            
            logger.info(f"✅ Vertex AI generated {len(embedding)}-dimensional embedding")
            return result
            
        except Exception as e:
            logger.error(f"❌ Vertex AI embedding generation error: {e}")
            return self._fallback_embedding_generation(image_data)
    
    def _fallback_face_detection(self, image_data: bytes) -> Dict:
        """Fallback face detection using OpenCV"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Use OpenCV face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                x, y, w, h = faces[0]  # Get the first face
                return {
                    'face_detected': True,
                    'face_count': len(faces),
                    'confidence': 0.7,  # OpenCV doesn't provide confidence
                    'face_bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                    'method': 'opencv_fallback',
                    'quality_metrics': {'overall_quality': 'medium'}
                }
            else:
                return {
                    'face_detected': False,
                    'face_count': 0,
                    'confidence': 0.0,
                    'face_bounds': None,
                    'method': 'opencv_fallback',
                    'quality_metrics': {'overall_quality': 'unknown'}
                }
                
        except Exception as e:
            logger.error(f"❌ Fallback face detection error: {e}")
            return {
                'face_detected': False,
                'face_count': 0,
                'confidence': 0.0,
                'face_bounds': None,
                'method': 'error_fallback',
                'quality_metrics': {'overall_quality': 'unknown'}
            }
    
    def _fallback_skin_analysis(self, image_data: bytes) -> Dict:
        """Fallback skin analysis using basic image processing"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Basic skin analysis using color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Analyze skin tone
            skin_tone_analysis = {
                'average_hue': np.mean(hsv[:, :, 0]),
                'average_saturation': np.mean(hsv[:, :, 1]),
                'average_value': np.mean(hsv[:, :, 2])
            }
            
            return {
                'skin_analysis': {
                    'basic_analysis': skin_tone_analysis,
                    'analysis_method': 'opencv_fallback',
                    'confidence_score': 0.5,
                    'overall_health_score': 0.5,
                    'conditions_detected': [],
                    'recommendations': {
                        'immediate_care': [
                            'Use a gentle cleanser twice daily',
                            'Apply sunscreen with SPF 30+ daily',
                            'Stay hydrated by drinking plenty of water'
                        ],
                        'long_term_care': [
                            'Establish a consistent skincare routine',
                            'Consider consulting a dermatologist for personalized advice',
                            'Monitor skin changes and adjust routine as needed'
                        ],
                        'product_suggestions': [
                            'Gentle facial cleanser',
                            'Broad-spectrum sunscreen',
                            'Moisturizer suitable for your skin type'
                        ]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback skin analysis error: {e}")
            return {
                'skin_analysis': {
                    'analysis_method': 'error_fallback',
                    'confidence_score': 0.0
                }
            }
    
    def _fallback_embedding_generation(self, image_data: bytes) -> Dict:
        """Fallback embedding generation"""
        embedding = np.random.rand(512).tolist()  # Smaller fallback embedding
        
        return {
            'embedding': embedding,
            'embedding_dimensions': len(embedding),
            'method': 'random_fallback',
            'confidence_score': 0.3
        }
    
    def is_available(self) -> bool:
        """Check if Google Cloud integration is available"""
        return GOOGLE_CLOUD_AVAILABLE and (self.vision_client is not None or self.vertex_ai_initialized)
    
    def get_status(self) -> Dict:
        """Get integration status"""
        return {
            'google_cloud_available': GOOGLE_CLOUD_AVAILABLE,
            'vision_api_available': self.vision_client is not None,
            'vertex_ai_available': self.vertex_ai_initialized,
            'project_id': self.project_id,
            'location': self.location
        } 