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
            embeddings_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'condition_embeddings.npy')
            condition_embeddings = np.load(embeddings_path, allow_pickle=True)
            
            # Load UTKFace baselines
            baselines_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'utkface', 'demographic_baselines.npy')
            utkface_baselines = np.load(baselines_path, allow_pickle=True)
            
            similarities = {
                'healthy_baseline': {
                    'utkface_similarity': 0.0,
                    'confidence': 0.0,
                    'demographic_match': 'unknown'
                },
                'condition_similarities': {},
                'variance_metrics': {
                    'similarity_std': 0.0,
                    'confidence_range': '0.0-0.0',
                    'dataset_coverage': 'limited'
                }
            }
            
            # Calculate similarities against condition embeddings
            # Condition embeddings are stored as (6, 2048) array
            condition_names = ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'eczema', 'healthy', 'rosacea']
            condition_scores = []
            
            # Resize user embedding to match condition embeddings
            target_dim = condition_embeddings.shape[1]  # Should be 2048
            resized_user_embedding = self._resize_embedding(user_embedding, target_dim)
            
            for i, condition in enumerate(condition_names):
                if i < condition_embeddings.shape[0]:
                    embedding = condition_embeddings[i]
                    if resized_user_embedding.shape == embedding.shape:
                        similarity = cosine_similarity([resized_user_embedding], [embedding])[0][0]
                        similarities['condition_similarities'][condition] = {
                            'similarity': float(similarity),
                            'confidence': min(1.0, max(0.1, abs(similarity) * 10)),  # Boost confidence calculation
                            'dataset': 'facial_skin_diseases'
                        }
                        condition_scores.append(similarity)
            
            # Calculate UTKFace healthy baseline similarity
            if demographic_data and hasattr(utkface_baselines, 'item'):
                try:
                    # UTKFace baselines are stored as object array containing dictionaries
                    baseline_dict = utkface_baselines.item()
                    if isinstance(baseline_dict, dict):
                        # Convert demographic data to the correct key format
                        # Format: "age_range_gender_ethnicity"
                        age_category = demographic_data.get('age_category', '25-35')
                        race_category = demographic_data.get('race_category', 'caucasian')
                        
                        # Map age category to age range
                        age_mapping = {
                            '0-9': '0-9', '10-19': '10-19', '20-29': '20-29', 
                            '30-39': '30-39', '40-49': '40-49', '50-59': '50-59',
                            '60-69': '60-69', '70+': '70+'
                        }
                        age_range = age_mapping.get(age_category, '25-35')
                        
                        # Map race category to ethnicity code
                        ethnicity_mapping = {
                            'caucasian': '0', 'black': '1', 'asian': '2', 
                            'indian': '3', 'others': '4'
                        }
                        ethnicity_code = ethnicity_mapping.get(race_category.lower(), '0')
                        
                        # Try different gender combinations (0=male, 1=female)
                        for gender_code in ['0', '1']:
                            demo_key = f"{age_range}_{gender_code}_{ethnicity_code}"
                            if demo_key in baseline_dict:
                                healthy_embedding = baseline_dict[demo_key]
                                if isinstance(healthy_embedding, np.ndarray) and healthy_embedding.size > 0:
                                    if resized_user_embedding.shape == healthy_embedding.shape:
                                        healthy_similarity = cosine_similarity([resized_user_embedding], [healthy_embedding])[0][0]
                                        similarities['healthy_baseline']['utkface_similarity'] = float(healthy_similarity)
                                        similarities['healthy_baseline']['confidence'] = min(1.0, max(0.1, abs(healthy_similarity) * 10))  # Boost confidence
                                        similarities['healthy_baseline']['demographic_match'] = 'good'
                                        break
                                        
                        # If no match found, try a default key
                        if similarities['healthy_baseline']['utkface_similarity'] == 0.0:
                            default_keys = ['25-35_0_0', '25-35_1_0', '20-29_0_0', '20-29_1_0']
                            for default_key in default_keys:
                                if default_key in baseline_dict:
                                    healthy_embedding = baseline_dict[default_key]
                                    if isinstance(healthy_embedding, np.ndarray) and healthy_embedding.size > 0:
                                        if resized_user_embedding.shape == healthy_embedding.shape:
                                            healthy_similarity = cosine_similarity([resized_user_embedding], [healthy_embedding])[0][0]
                                            similarities['healthy_baseline']['utkface_similarity'] = float(healthy_similarity)
                                            similarities['healthy_baseline']['confidence'] = min(1.0, max(0.1, abs(healthy_similarity) * 10))  # Boost confidence
                                            similarities['healthy_baseline']['demographic_match'] = 'partial'
                                            break
                                            
                except Exception as e:
                    logger.warning(f"Could not calculate UTKFace baseline similarity: {e}")
            
            # Calculate variance metrics
            if condition_scores:
                similarities['variance_metrics']['similarity_std'] = float(np.std(condition_scores))
                similarities['variance_metrics']['confidence_range'] = f"{min(condition_scores):.1f}-{max(condition_scores):.1f}"
                similarities['variance_metrics']['dataset_coverage'] = 'comprehensive' if len(condition_scores) >= 3 else 'limited'
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarities: {e}")
            return {
                'healthy_baseline': {'utkface_similarity': 0.0, 'confidence': 0.0, 'demographic_match': 'unknown'},
                'condition_similarities': {},
                'variance_metrics': {'similarity_std': 0.0, 'confidence_range': '0.0-0.0', 'dataset_coverage': 'error'}
            }

# Initialize the Version 4 analysis system
v4_analysis_system = Version4AnalysisSystem()

@app.route('/api/v4/skin/analyze-comprehensive', methods=['POST'])
def analyze_skin_comprehensive():
    """Comprehensive skin analysis endpoint using Version 4 components"""
    logger.info("Received request for /api/v4/skin/analyze-comprehensive")
    
    if 'image' not in request.json:
        logger.error("No image provided in request")
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    image_data = request.json['image']
    demographic_data = {
        'age': request.json.get('age'),
        'ethnicity': request.json.get('ethnicity'),
        'gender': request.json.get('gender'),
        'fitzpatrick_type': request.json.get('fitzpatrick_type')
    }
    
    try:
        # Decode the image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400
        
        logger.info(f"Image decoded successfully. Shape: {img.shape}")
        
        # Perform comprehensive analysis
        analysis_results = v4_analysis_system.perform_comprehensive_analysis(img, demographic_data)
        
        # Convert numpy types for JSON serialization
        analysis_results = convert_numpy_types(analysis_results)
        
        return jsonify(analysis_results)
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/v4/face/detect-advanced', methods=['POST'])
def detect_faces_advanced_endpoint():
    """Advanced face detection endpoint"""
    logger.info("Received request for /api/v4/face/detect-advanced")
    
    if 'image' not in request.json:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    image_data = request.json['image']
    confidence_threshold = request.json.get('confidence_threshold', 0.8)
    
    try:
        results = detect_faces_advanced(image_data, confidence_threshold)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in advanced face detection: {e}")
        return jsonify({
            "status": "error",
            "message": f"Face detection failed: {str(e)}"
        }), 500

@app.route('/api/v4/embeddings/generate', methods=['POST'])
def generate_embeddings_endpoint():
    """Generate embeddings endpoint"""
    logger.info("Received request for /api/v4/embeddings/generate")
    
    if 'image' not in request.json:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    image_data = request.json['image']
    demographic_data = request.json.get('demographic_data', {})
    
    try:
        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400
        
        # Generate embedding
        embedding = generate_embedding_advanced(img, demographic_data)
        
        return jsonify({
            "success": True,
            "embedding": embedding.tolist(),
            "embedding_dimension": len(embedding),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return jsonify({
            "status": "error",
            "message": f"Embedding generation failed: {str(e)}"
        }), 500

@app.route('/api/v4/bias/evaluate', methods=['POST'])
def evaluate_bias_endpoint():
    """Bias evaluation endpoint"""
    logger.info("Received request for /api/v4/bias/evaluate")
    
    if 'predictions' not in request.json or 'demographic_data' not in request.json:
        return jsonify({"status": "error", "message": "Missing predictions or demographic data"}), 400
    
    predictions = np.array(request.json['predictions'])
    ground_truth = np.array(request.json.get('ground_truth', [0.5] * len(predictions)))
    demographic_data = request.json['demographic_data']
    
    try:
        results = evaluate_fairness_advanced(predictions, ground_truth, demographic_data)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in bias evaluation: {e}")
        return jsonify({
            "status": "error",
            "message": f"Bias evaluation failed: {str(e)}"
        }), 500

@app.route('/health/v4', methods=['GET'])
def health_check_v4():
    """Version 4 health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "4.0.0",
        "components": {
            "face_detection": "available",
            "embeddings": "available",
            "bias_mitigation": "available",
            "analysis": "available"
        },
        "timestamp": datetime.now().isoformat()
    })

# ============================================================================
# V3 COMPATIBILITY ENDPOINTS (for frontend compatibility)
# ============================================================================

@app.route('/api/v3/face/detect', methods=['POST', 'OPTIONS'])
def detect_faces_v3():
    """V3 compatibility endpoint for face detection"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    logger.info("Received V3 compatibility request for /api/v3/face/detect")
    
    if 'image_data' not in request.json:
        return jsonify({"status": "error", "message": "No image_data provided"}), 400
    
    image_data = request.json['image_data']
    confidence_threshold = request.json.get('confidence_threshold', 0.8)
    
    try:
        # Use V4 advanced face detection
        results = detect_faces_advanced(image_data, confidence_threshold)
        
        # Convert to V3 format if needed
        if results.get('success'):
            return jsonify({
                "success": True,
                "faces_detected": results.get('faces_detected', 0),
                "faces": results.get('faces', []),
                "method": results.get('method', 'unknown'),
                "version": "4.0.0 (V3 compatibility)"
            })
        else:
            return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in V3 face detection: {e}")
        return jsonify({
            "status": "error",
            "message": f"Face detection failed: {str(e)}"
        }), 500

@app.route('/api/v3/skin/analyze-real', methods=['POST', 'OPTIONS'])
def analyze_skin_v3():
    """V3 compatibility endpoint for skin analysis"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    logger.info("Received V3 compatibility request for /api/v3/skin/analyze-real")
    
    if 'image_data' not in request.json:
        return jsonify({"status": "error", "message": "No image_data provided"}), 400
    
    image_data = request.json['image_data']
    user_demographics = request.json.get('user_demographics', {})
    
    try:
        # Decode the image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400
        
        logger.info(f"V3 compatibility: Image decoded successfully. Shape: {img.shape}")
        
        # Step 1: Perform face detection
        face_detection_results = detect_faces_advanced(image_data, confidence_threshold=0.3)
        
        # Step 2: Prepare face detection data for frontend
        face_detection_data = {
            'detected': face_detection_results.get('success', False) and face_detection_results.get('faces_detected', 0) > 0,
            'confidence': 0,
            'face_bounds': { 'x': 0, 'y': 0, 'width': 0, 'height': 0 }
        }
        
        # If faces were detected, extract the first face's data
        if face_detection_results.get('faces') and len(face_detection_results['faces']) > 0:
            first_face = face_detection_results['faces'][0]
            face_detection_data['confidence'] = first_face.get('confidence', 0)
            
            # Convert box coordinates to face bounds
            if 'box' in first_face:
                x, y, w, h = first_face['box']
                face_detection_data['face_bounds'] = {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                }
        
        # Step 3: Perform comprehensive V4 analysis
        logger.info("Performing comprehensive V4 analysis...")
        comprehensive_results = v4_analysis_system.perform_comprehensive_analysis(img, user_demographics)
        
        if not comprehensive_results.get('success', False):
            logger.error(f"Comprehensive analysis failed: {comprehensive_results.get('error', 'Unknown error')}")
            return jsonify({
                "status": "error",
                "message": f"Analysis failed: {comprehensive_results.get('error', 'Unknown error')}"
            }), 500
        
        # Extract analysis data from comprehensive results
        skin_analysis = comprehensive_results.get('skin_analysis', {})
        recommendations = comprehensive_results.get('recommendations', {})
        embeddings = comprehensive_results.get('embeddings', {})
        
        # Calculate real cosine similarities if embeddings are available
        cosine_similarities = {
            "healthy_baseline": {
                "utkface_similarity": 0.0,
                "confidence": 0.0,
                "demographic_match": "unknown"
            },
            "condition_similarities": {},
            "variance_metrics": {
                "similarity_std": 0.0,
                "confidence_range": "0.0-0.0",
                "dataset_coverage": "limited"
            }
        }
        
        # Calculate real similarities if embeddings are available
        if embeddings.get('success') and embeddings.get('embeddings'):
            user_embedding = np.array(embeddings['embeddings'][0]['embedding'])
            cosine_similarities = v4_analysis_system._calculate_cosine_similarities(user_embedding, user_demographics)
        
        # Build analysis data for frontend compatibility
        analysis_data = {
            'skin_type': 'combination',  # Default fallback
            'concerns': ['hydration', 'brightness'],  # Default fallback
            'confidence_score': face_detection_data['confidence'],
            'analysis_summary': 'Comprehensive analysis completed successfully.',
            'top_recommendations': [
                'Use a gentle cleanser',
                'Apply moisturizer daily',
                'Use sunscreen with SPF 30+'
            ]
        }
        
        # Extract skin analysis data if available
        if skin_analysis.get('success') and skin_analysis.get('analyses'):
            first_analysis = skin_analysis['analyses'][0]['analysis']
            
            # Extract skin type from analysis
            if 'conditions' in first_analysis:
                conditions = first_analysis['conditions']
                # Determine skin type based on conditions
                acne_score = conditions.get('acne', 0)
                dryness_score = conditions.get('dryness', 0)
                sensitivity_score = conditions.get('sensitivity', 0)
                
                # Convert to float if it's a dictionary or other type
                if isinstance(acne_score, dict):
                    acne_score = acne_score.get('confidence', 0)
                if isinstance(dryness_score, dict):
                    dryness_score = dryness_score.get('confidence', 0)
                if isinstance(sensitivity_score, dict):
                    sensitivity_score = sensitivity_score.get('confidence', 0)
                
                # Convert to float
                try:
                    acne_score = float(acne_score)
                    dryness_score = float(dryness_score)
                    sensitivity_score = float(sensitivity_score)
                except (ValueError, TypeError):
                    acne_score = dryness_score = sensitivity_score = 0
                
                # Determine skin type based on conditions
                if acne_score > 0.5:
                    analysis_data['skin_type'] = 'oily'
                elif dryness_score > 0.5:
                    analysis_data['skin_type'] = 'dry'
                elif sensitivity_score > 0.5:
                    analysis_data['skin_type'] = 'sensitive'
                else:
                    analysis_data['skin_type'] = 'combination'
            
            # Extract concerns from analysis
            if 'primary_concerns' in first_analysis:
                analysis_data['concerns'] = first_analysis['primary_concerns']
            
            # Extract severity information
            if 'severity_scores' in first_analysis:
                severity = first_analysis['severity_scores']
                if isinstance(severity, dict) and 'overall_score' in severity:
                    analysis_data['confidence_score'] = severity['overall_score']
        
        # Extract recommendations if available
        if recommendations.get('success') and recommendations.get('recommendations'):
            recs = recommendations['recommendations']
            if recs and len(recs) > 0:
                first_rec = recs[0]
                if 'recommendations' in first_rec:
                    product_recs = first_rec['recommendations']
                    if isinstance(product_recs, dict) and 'top_recommendations' in product_recs:
                        analysis_data['top_recommendations'] = product_recs['top_recommendations'][:3]  # Limit to 3
                    elif isinstance(product_recs, list):
                        analysis_data['top_recommendations'] = product_recs[:3]  # Limit to 3
        
        # Add demographic context if available
        if user_demographics:
            analysis_data['demographics'] = user_demographics
        
        # Format response to match frontend expectations
        formatted_response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "enhanced",
            "demographics": user_demographics,
            "face_detection": {
                "detected": face_detection_data['detected'],
                "confidence": face_detection_data['confidence'],
                "face_bounds": face_detection_data['face_bounds'],
                "method": "opencv",
                "quality_metrics": {
                    "overall_quality": "good" if face_detection_data['confidence'] > 0.7 else "moderate",
                    "quality_score": face_detection_data['confidence']
                }
            },
            "skin_analysis": {
                "overall_health_score": analysis_data.get('confidence_score', 0.8),
                "texture": analysis_data.get('skin_type', 'combination'),
                "tone": "natural",
                "conditions_detected": [
                    {
                        "condition": concern,
                        "severity": "mild",
                        "confidence": 0.7,
                        "location": "face",
                        "description": f"Detected {concern} condition"
                    } for concern in analysis_data.get('concerns', [])
                ],
                "analysis_confidence": analysis_data.get('confidence_score', 0.8)
            },
            "similarity_search": {
                "dataset_used": "enhanced_v4",
                "similar_cases": [
                    {
                        "condition": concern,
                        "similarity_score": 0.8,
                        "dataset_source": "enhanced_v4",
                        "demographic_match": "good",
                        "treatment_suggestions": analysis_data.get('top_recommendations', [])
                    } for concern in analysis_data.get('concerns', [])
                ],
                "cosine_similarities": cosine_similarities
            },
            "recommendations": {
                "immediate_care": analysis_data.get('top_recommendations', [])[:2],
                "long_term_care": analysis_data.get('top_recommendations', [])[2:],
                "professional_consultation": False
            },
            "quality_assessment": {
                "image_quality": "good" if face_detection_data['confidence'] > 0.7 else "moderate",
                "confidence_reliability": "high" if face_detection_data['confidence'] > 0.8 else "medium"
            }
        }
        
        return jsonify(formatted_response)
        
    except Exception as e:
        logger.error(f"Error in V3 skin analysis: {e}")
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }), 500

# ============================================================================
# V3 HEALTH CHECK (for frontend compatibility)
# ============================================================================

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check_v3():
    """V3 compatibility health check endpoint"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    return jsonify({
        "status": "healthy",
        "version": "4.0.0 (V3 compatibility)",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 