#!/usr/bin/env python3
"""
Enhanced Analysis API for Shine Skincare App
Provides normalized skin analysis using healthy baselines and condition matching
"""

import os
import json
import logging
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback

# Import our integrated analysis system
from integrated_skin_analysis import IntegratedSkinAnalysis

# Import enhanced face detection
from enhanced_face_detection_fixed import enhanced_face_detector as robust_face_detector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to Python types for JSON serialization"""
    try:
        # Handle numpy arrays and scalars
        if hasattr(obj, 'dtype'):  # numpy array or scalar
            if obj.dtype.kind in 'i':  # integer types
                return int(obj)
            elif obj.dtype.kind in 'f':  # float types
                return float(obj)
            elif obj.dtype.kind in 'b':  # boolean types
                return bool(obj)
            elif obj.dtype.kind in 'U':  # unicode string types
                return str(obj)
            else:
                return obj.tolist()
        # Handle specific numpy scalar types
        elif isinstance(obj, (np.integer, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Handle nested structures
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(convert_numpy_types(item) for item in obj)
        else:
            return obj
    except Exception as e:
        # Fallback: try to convert to basic Python types
        try:
            if hasattr(obj, 'item'):
                return obj.item()
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            else:
                return str(obj)
        except:
            return str(obj)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], supports_credentials=True)

# Initialize the integrated analysis system
try:
    integrated_analyzer = IntegratedSkinAnalysis()
    logger.info("✅ Integrated skin analysis system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize integrated analysis system: {e}")
    integrated_analyzer = None

@app.route('/api/v3/skin/analyze-comprehensive', methods=['POST'])
def analyze_skin_comprehensive():
    """
    Comprehensive skin analysis with healthy baseline comparison
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data') or data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Get user demographics (optional)
        demographics = data.get('demographics', {})
        
        # Perform comprehensive analysis
        if integrated_analyzer:
            results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Convert results for JSON serialization
        serializable_results = convert_numpy_types(results)
        return jsonify(serializable_results)
        
    except Exception as e:
        logger.error(f"❌ Comprehensive analysis failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/skin/analyze-basic', methods=['POST'])
def analyze_skin_basic():
    """
    Basic skin analysis using integrated system (conditions + normalized baselines)
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data') or data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Get user demographics (optional)
        demographics = data.get('demographics', {})
        
        # Perform integrated analysis (uses both conditions and normalized baselines)
        if integrated_analyzer:
            results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Convert results for JSON serialization
        serializable_results = convert_numpy_types(results)
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'basic_integrated',
            'results': serializable_results
        })
        
    except Exception as e:
        logger.error(f"❌ Basic integrated analysis failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/skin/analyze-normalized', methods=['POST'])
def analyze_skin_normalized():
    """
    Normalized skin analysis with demographic-specific healthy baselines
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data') or data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Get user demographics (required for normalized analysis)
        demographics = data.get('demographics', {})
        if not demographics:
            return jsonify({'error': 'Demographics required for normalized analysis'}), 400
        
        # Perform normalized analysis
        if integrated_analyzer:
            results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Convert results for JSON serialization
        serializable_results = convert_numpy_types(results)
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'normalized',
            'demographics_used': demographics,
            'results': serializable_results
        })
        
    except Exception as e:
        logger.error(f"❌ Normalized analysis failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/face/detect', methods=['POST'])
def face_detect():
    """
    Face detection endpoint for camera interface
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_array is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Use enhanced face detection
        face_detection_result = robust_face_detector.detect_faces(img_array)
        
        if face_detection_result['detected']:
            return jsonify({
                'status': 'success',
                'face_detected': True,
                'confidence': face_detection_result['confidence'],
                'face_bounds': face_detection_result['face_bounds'],
                'quality_metrics': face_detection_result['quality_metrics'],
                'guidance': {
                    'message': 'Face detected successfully',
                    'method': face_detection_result['method'],
                    'suggestions': [
                        'Ensure good lighting for better analysis',
                        'Keep face centered in the frame',
                        'Avoid shadows and reflections'
                    ]
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'face_detected': False,
                'confidence': 0.0,
                'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'quality_metrics': {
                    'lighting': 'unknown',
                    'sharpness': 'unknown',
                    'positioning': 'unknown'
                },
                'guidance': {
                    'message': 'No face detected',
                    'method': face_detection_result['method'],
                    'suggestions': [
                        'Ensure a face is clearly visible in the image',
                        'Try adjusting lighting conditions',
                        'Make sure the face is not too small or too large',
                        'Avoid extreme angles or partial occlusion'
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Face detection failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/v3/skin/analyze-enhanced-embeddings', methods=['POST'])
def analyze_skin_enhanced_embeddings():
    """
    Enhanced skin analysis with embeddings and cosine similarity search
    Performs face detection and analysis in a single step
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract image data
        image_data = data.get('image_data') or data.get('image')
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Convert to numpy array for face detection
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_array is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Perform face detection
        logger.info("Performing face detection for enhanced analysis")
        face_detection_result = robust_face_detector.detect_faces(img_array)
        
        # Get user demographics (optional)
        demographics = data.get('demographics', {})
        user_parameters = data.get('user_parameters', {})
        
        # Extract age and race categories from user parameters
        age_category = user_parameters.get('age_category', demographics.get('age_category'))
        race_category = user_parameters.get('race_category', demographics.get('race_category'))
        
        # Perform comprehensive analysis using integrated system
        if integrated_analyzer:
            results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Generate embeddings for cosine similarity search
        try:
            from enhanced_embeddings import EnhancedEmbeddingSystem
            embedding_system = EnhancedEmbeddingSystem()
            
            # Generate embeddings for the user image
            user_embedding_result = embedding_system.generate_enhanced_embeddings(image_bytes)
            user_embedding = user_embedding_result.get('combined', [])
            
            # Perform cosine similarity search against condition embeddings
            similarity_results = []
            if hasattr(integrated_analyzer, 'condition_embeddings') and integrated_analyzer.condition_embeddings:
                for condition, embeddings in integrated_analyzer.condition_embeddings.items():
                    if embeddings and len(embeddings) > 0:
                        # Calculate cosine similarity with each embedding
                        similarities = []
                        for embedding in embeddings[:5]:  # Use first 5 embeddings per condition
                            if len(embedding) == len(user_embedding):
                                similarity = np.dot(user_embedding, embedding) / (np.linalg.norm(user_embedding) * np.linalg.norm(embedding))
                                similarities.append(similarity)
                        
                        if similarities:
                            avg_similarity = np.mean(similarities)
                            max_similarity = np.max(similarities)
                            similarity_results.append({
                                'condition': condition,
                                'avg_similarity': float(avg_similarity),
                                'max_similarity': float(max_similarity),
                                'confidence': float(max_similarity * 100)
                            })
                
                # Sort by max similarity
                similarity_results.sort(key=lambda x: x['max_similarity'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            similarity_results = []
        
        # Convert results for JSON serialization
        serializable_results = convert_numpy_types(results)
        
        # Build enhanced response
        enhanced_response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive',
            'demographics': {
                'age_category': age_category or 'unknown',
                'race_category': race_category or 'unknown'
            },
            'face_detection': face_detection_result,
            'skin_analysis': {
                'overall_health_score': serializable_results.get('analysis_summary', {}).get('overall_health_score', 50.0),
                'texture': serializable_results.get('basic_analysis', {}).get('conditions', {}).get('texture', {}).get('type', 'normal'),
                'tone': serializable_results.get('basic_analysis', {}).get('conditions', {}).get('pigmentation', {}).get('type', 'normal'),
                'conditions_detected': [
                    {
                        'condition': condition,
                        'severity': 'moderate',
                        'confidence': 0.7,
                        'location': 'face',
                        'description': f'Detected {condition.replace("_", " ")} condition'
                    }
                    for condition, data in serializable_results.get('basic_analysis', {}).get('conditions', {}).items()
                    if isinstance(data, dict) and data.get('detected', False)
                ],
                'analysis_confidence': serializable_results.get('analysis_summary', {}).get('confidence', 0.7)
            },
            'similarity_search': {
                'dataset_used': 'integrated_embeddings',
                'similar_cases': similarity_results[:5]  # Top 5 matches
            },
            'recommendations': {
                'immediate_care': serializable_results.get('analysis_summary', {}).get('immediate_recommendations', []),
                'long_term_care': serializable_results.get('analysis_summary', {}).get('long_term_recommendations', []),
                'professional_consultation': serializable_results.get('analysis_summary', {}).get('professional_consultation', False)
            },
            'quality_assessment': {
                'image_quality': 'good' if face_detection_result['detected'] else 'poor',
                'confidence_reliability': 'high' if face_detection_result['confidence'] > 0.7 else 'low'
            },
            'frontend_metadata': {
                'endpoint': '/api/v3/skin/analyze-enhanced-embeddings',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify(enhanced_response)
        
    except Exception as e:
        logger.error(f"❌ Enhanced embeddings analysis failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/system/status', methods=['GET'])
def get_system_status():
    """
    Get system status and capabilities
    """
    try:
        if integrated_analyzer:
            status = integrated_analyzer.get_system_status()
        else:
            status = {
                'system_status': 'error',
                'error': 'Analysis system not available'
            }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v3/system/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Enhanced Skin Analysis API',
        'version': '3.0.0'
    })

@app.route('/api/v3/system/capabilities', methods=['GET'])
def get_capabilities():
    """
    Get system capabilities and available analysis types
    """
    capabilities = {
        'analysis_types': {
            'basic': {
                'description': 'Basic skin condition analysis',
                'endpoint': '/api/v3/skin/analyze-basic',
                'requires_demographics': False
            },
            'comprehensive': {
                'description': 'Comprehensive analysis with condition matching',
                'endpoint': '/api/v3/skin/analyze-comprehensive',
                'requires_demographics': False
            },
            'normalized': {
                'description': 'Normalized analysis with demographic-specific healthy baselines',
                'endpoint': '/api/v3/skin/analyze-normalized',
                'requires_demographics': True
            }
        },
        'datasets': {
            'condition_embeddings': '6 skin conditions with 2304-dimensional embeddings',
            'demographic_baselines': '103 demographic groups with healthy skin baselines',
            'utkface_dataset': '23,705 healthy face images with demographic metadata'
        },
        'features': {
            'healthy_baseline_comparison': True,
            'condition_similarity_analysis': True,
            'demographic_normalization': True,
            'multi_model_embeddings': True,
            'quality_assessment': True
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(capabilities)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 