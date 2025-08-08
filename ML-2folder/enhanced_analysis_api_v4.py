#!/usr/bin/env python3
"""
Enhanced Analysis API for Version 4
Integrates advanced face detection, robust embeddings, and bias mitigation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback
from typing import Optional, Dict, List
from sklearn.metrics.pairwise import cosine_similarity

# Import Version 4 components
from advanced_face_detection import advanced_face_detector, detect_faces_advanced
from robust_embeddings import robust_embedding_system, generate_embedding_advanced
from bias_mitigation import bias_mitigation_system, evaluate_fairness_advanced, apply_bias_correction_advanced

# Import existing components for compatibility
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
from enhanced_recommendation_engine import EnhancedRecommendationEngine
from enhanced_severity_scoring import EnhancedSeverityScoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to Python types for JSON serialization"""
    try:
        if hasattr(obj, 'dtype'):
            if obj.dtype.kind == 'i':
                return int(obj)
            elif obj.dtype.kind == 'f':
                return float(obj)
            elif obj.dtype.kind == 'b':
                return bool(obj)
            elif obj.dtype.kind == 'U':
                return str(obj)
            else:
                return obj.tolist()
        elif isinstance(obj, (np.integer, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(element) for element in obj]
        elif isinstance(obj, tuple):
            return tuple(convert_numpy_types(element) for element in obj)
        else:
            return obj
    except Exception as e:
        logger.error(f"Error converting numpy type: {e}")
        return str(obj)

app = Flask(__name__)
# Configure CORS explicitly for development
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "supports_credentials": True
    }
})

# Initialize components
analysis_algorithms = EnhancedSkinAnalyzer()
recommendation_engine = EnhancedRecommendationEngine()
severity_scorer = EnhancedSeverityScoring()

class Version4AnalysisSystem:
    """
    Version 4 Analysis System
    Integrates advanced face detection, robust embeddings, and bias mitigation
    """
    
    def __init__(self):
        """Initialize the Version 4 analysis system"""
        self.face_detector = advanced_face_detector
        self.embedding_system = robust_embedding_system
        self.bias_mitigation = bias_mitigation_system
        
        logger.info("✅ Version 4 Analysis System initialized")
    
    def perform_comprehensive_analysis(self, image: np.ndarray, 
                                     demographic_data: Optional[Dict] = None) -> Dict:
        """
        Perform comprehensive skin analysis using Version 4 components
        
        Args:
            image: Input image as numpy array
            demographic_data: Optional demographic information
            
        Returns:
            Comprehensive analysis results
        """
        try:
            results = {
                'success': True,
                'version': '4.0.0',
                'timestamp': datetime.now().isoformat(),
                'face_detection': {},
                'embeddings': {},
                'skin_analysis': {},
                'bias_evaluation': {},
                'recommendations': {},
                'metadata': {}
            }
            
            # Step 1: Advanced Face Detection
            logger.info("Step 1: Performing advanced face detection")
            face_results = self._perform_face_detection(image)
            results['face_detection'] = face_results
            
            if not face_results['success'] or face_results['faces_detected'] == 0:
                return self._create_error_response("No faces detected in image")
            
            # Step 2: Face Alignment and Cropping
            logger.info("Step 2: Aligning and cropping faces")
            aligned_faces = self._align_and_crop_faces(image, face_results['faces'])
            
            # Step 3: Generate Robust Embeddings
            logger.info("Step 3: Generating robust embeddings")
            embeddings = self._generate_embeddings(aligned_faces, demographic_data)
            results['embeddings'] = embeddings
            
            # Step 4: Skin Analysis
            logger.info("Step 4: Performing skin analysis")
            skin_analysis = self._perform_skin_analysis(aligned_faces, demographic_data)
            results['skin_analysis'] = skin_analysis
            
            # Step 5: Bias Evaluation
            logger.info("Step 5: Evaluating bias")
            bias_evaluation = self._evaluate_bias(skin_analysis, demographic_data)
            results['bias_evaluation'] = bias_evaluation
            
            # Step 6: Generate Recommendations
            logger.info("Step 6: Generating recommendations")
            recommendations = self._generate_recommendations(skin_analysis, demographic_data)
            results['recommendations'] = recommendations
            
            # Step 7: Add Metadata
            results['metadata'] = {
                'image_shape': image.shape,
                'demographic_data': demographic_data,
                'processing_time': datetime.now().isoformat()
            }
            
            logger.info("✅ Comprehensive analysis completed successfully")
            # Convert numpy types before returning
            results = convert_numpy_types(results)
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return self._create_error_response(str(e))
    
    def _perform_face_detection(self, image: np.ndarray) -> Dict:
        """Perform advanced face detection"""
        try:
            # Convert image to base64 for API compatibility
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Perform detection
            detection_results = detect_faces_advanced(image_base64)
            
            return detection_results
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return {'success': False, 'error': str(e)}
    
    def _align_and_crop_faces(self, image: np.ndarray, faces: List[Dict]) -> List[np.ndarray]:
        """Align and crop detected faces"""
        try:
            aligned_faces = []
            
            for face in faces:
                face_box = face['box']
                landmarks = face.get('landmarks', {})
                
                # Align face if landmarks are available
                if landmarks:
                    aligned_image = self.face_detector.align_face(image, landmarks)
                else:
                    aligned_image = image
                
                # Crop face with padding
                cropped_face = self.face_detector.crop_face(aligned_image, face_box, padding=0.2)
                aligned_faces.append(cropped_face)
            
            return aligned_faces
            
        except Exception as e:
            logger.error(f"Error in face alignment and cropping: {e}")
            return [image]  # Return original image as fallback
    
    def _generate_embeddings(self, faces: List[np.ndarray], 
                            demographic_data: Optional[Dict] = None) -> Dict:
        """Generate robust embeddings for faces"""
        try:
            embeddings = []
            
            for i, face in enumerate(faces):
                embedding = generate_embedding_advanced(face, demographic_data)
                embeddings.append({
                    'face_index': i,
                    'embedding': embedding.tolist(),
                    'embedding_dim': len(embedding)
                })
            
            return {
                'success': True,
                'embeddings': embeddings,
                'total_faces': len(faces),
                'embedding_dimension': len(embeddings[0]['embedding']) if embeddings else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return {'success': False, 'error': str(e)}
    
    def _perform_skin_analysis(self, faces: List[np.ndarray], 
                              demographic_data: Optional[Dict] = None) -> Dict:
        """Perform skin analysis on aligned faces"""
        try:
            analysis_results = []
            
            for i, face in enumerate(faces):
                # Use existing analysis algorithms with demographic data
                analysis = analysis_algorithms.analyze_skin_conditions(face)
                
                # Add demographic context
                if demographic_data:
                    analysis['demographic_context'] = demographic_data
                
                # Add severity scoring
                severity = severity_scorer.calculate_enhanced_severity_score(analysis)
                analysis['severity_scores'] = severity
                
                analysis_results.append({
                    'face_index': i,
                    'analysis': analysis
                })
            
            return {
                'success': True,
                'analyses': analysis_results,
                'total_faces': len(faces)
            }
            
        except Exception as e:
            logger.error(f"Error in skin analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def _evaluate_bias(self, skin_analysis: Dict, 
                       demographic_data: Optional[Dict] = None) -> Dict:
        """Evaluate bias in analysis results"""
        try:
            if not demographic_data:
                return {'success': True, 'bias_evaluation': 'No demographic data provided'}
            
            # Extract predictions and create ground truth (placeholder)
            predictions = []
            ground_truth = []  # This would be actual ground truth in practice
            demo_data_list = []
            
            for analysis in skin_analysis.get('analyses', []):
                # Extract condition predictions
                conditions = analysis['analysis'].get('conditions', {})
                for condition, confidence in conditions.items():
                    predictions.append(confidence)
                    ground_truth.append(0.5)  # Placeholder ground truth
                    demo_data_list.append(demographic_data)
            
            if predictions:
                # Evaluate fairness
                fairness_results = evaluate_fairness_advanced(
                    np.array(predictions),
                    np.array(ground_truth),
                    demo_data_list
                )
                
                return {
                    'success': True,
                    'fairness_evaluation': fairness_results
                }
            else:
                return {
                    'success': True,
                    'bias_evaluation': 'No predictions available for bias evaluation'
                }
                
        except Exception as e:
            logger.error(f"Error in bias evaluation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_recommendations(self, skin_analysis: Dict, 
                                 demographic_data: Optional[Dict] = None) -> Dict:
        """Generate product recommendations"""
        try:
            recommendations = []
            
            for analysis in skin_analysis.get('analyses', []):
                # Generate recommendations based on analysis
                recs = recommendation_engine.generate_personalized_recommendations(
                    analysis['analysis'],
                    None,
                    demographic_data
                )
                
                recommendations.append({
                    'face_index': analysis['face_index'],
                    'recommendations': recs
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'total_faces': len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            'version': '4.0.0',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': error_message,
            'face_detection': {'success': False, 'error': error_message},
            'embeddings': {'success': False, 'error': error_message},
            'skin_analysis': {'success': False, 'error': error_message},
            'bias_evaluation': {'success': False, 'error': error_message},
            'recommendations': {'success': False, 'error': error_message}
        }
    
    def _resize_embedding(self, embedding: np.ndarray, target_dim: int = 2048) -> np.ndarray:
        """Resize embedding to target dimension for compatibility using interpolation"""
        try:
            if len(embedding) == target_dim:
                return embedding
            elif len(embedding) < target_dim:
                # Use interpolation to expand the embedding
                from scipy.interpolate import interp1d
                
                # Create interpolation function
                x_old = np.linspace(0, 1, len(embedding))
                x_new = np.linspace(0, 1, target_dim)
                
                # Interpolate each dimension
                resized = np.zeros(target_dim)
                f = interp1d(x_old, embedding, kind='linear', bounds_error=False, fill_value='extrapolate')
                resized = f(x_new)
                
                # Normalize to maintain similar magnitude
                resized = resized * (len(embedding) / target_dim)
                
                return resized
            else:
                # Truncate or use interpolation to shrink
                from scipy.interpolate import interp1d
                
                x_old = np.linspace(0, 1, len(embedding))
                x_new = np.linspace(0, 1, target_dim)
                
                f = interp1d(x_old, embedding, kind='linear', bounds_error=False, fill_value='extrapolate')
                resized = f(x_new)
                
                return resized
        except Exception as e:
            logger.error(f"Error resizing embedding: {e}")
            # Fallback to simple padding if interpolation fails
            if len(embedding) < target_dim:
                resized = np.zeros(target_dim)
                resized[:len(embedding)] = embedding
                return resized
            else:
                return embedding[:target_dim]

    def _calculate_cosine_similarities(self, user_embedding: np.ndarray, 
                                     demographic_data: Optional[Dict] = None) -> Dict:
        """Calculate cosine similarities against dataset embeddings"""
        try:
            # Load condition embeddings
            embeddings
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)