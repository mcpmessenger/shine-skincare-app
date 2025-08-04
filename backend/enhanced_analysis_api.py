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
CORS(app)

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
        
        # Perform face detection using OpenCV with multiple cascade files
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Try different detection parameters
        faces = []
        
        # Method 1: Standard frontal face detection
        faces1 = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        if len(faces1) > 0:
            faces.extend(faces1)
        
        # Method 2: More sensitive frontal face detection
        faces2 = face_cascade.detectMultiScale(gray, 1.05, 6, minSize=(20, 20))
        if len(faces2) > 0:
            faces.extend(faces2)
        
        # Method 3: Very sensitive frontal face detection
        faces3 = face_cascade.detectMultiScale(gray, 1.02, 8, minSize=(15, 15))
        if len(faces3) > 0:
            faces.extend(faces3)
        
        # Method 4: Profile face detection
        faces4 = profile_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        if len(faces4) > 0:
            faces.extend(faces4)
        
        # Method 5: Very sensitive profile face detection
        faces5 = profile_cascade.detectMultiScale(gray, 1.05, 6, minSize=(20, 20))
        if len(faces5) > 0:
            faces.extend(faces5)
        
        # Remove duplicates and overlapping faces
        if len(faces) > 0:
            # Convert to list of tuples for easier processing
            faces = [tuple(face) for face in faces]
            
            # Remove overlapping faces (keep the larger one)
            filtered_faces = []
            for face in faces:
                x, y, w, h = face
                is_overlapping = False
                
                for existing_face in filtered_faces:
                    ex, ey, ew, eh = existing_face
                    # Check if faces overlap significantly
                    overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
                    overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
                    overlap_area = overlap_x * overlap_y
                    face_area = w * h
                    existing_area = ew * eh
                    
                    if overlap_area > 0.5 * min(face_area, existing_area):
                        is_overlapping = True
                        break
                
                if not is_overlapping:
                    filtered_faces.append(face)
            
            faces = filtered_faces
        
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Calculate confidence based on face size and position
            img_height, img_width = img_array.shape[:2]
            face_area = w * h
            img_area = img_width * img_height
            area_ratio = face_area / img_area
            
            # Calculate position score (center is better)
            center_x = x + w/2
            center_y = y + h/2
            distance_from_center = np.sqrt((center_x - img_width/2)**2 + (center_y - img_height/2)**2)
            max_distance = np.sqrt((img_width/2)**2 + (img_height/2)**2)
            position_score = 1 - (distance_from_center / max_distance)
            
            # Calculate overall confidence
            confidence = min(0.9, area_ratio * 10 + position_score * 0.1)
            
            # Determine quality metrics
            lighting = 'good' if np.mean(gray) > 100 else 'poor'
            sharpness = 'high' if confidence > 0.7 else 'low'
            positioning = 'optimal' if position_score > 0.8 else 'suboptimal'
            
            return jsonify({
                'status': 'success',
                'face_detected': True,
                'confidence': float(confidence),
                'face_bounds': {
                    'x': float(x),
                    'y': float(y),
                    'width': float(w),
                    'height': float(h)
                },
                'quality_metrics': {
                    'lighting': lighting,
                    'sharpness': sharpness,
                    'positioning': positioning
                },
                'guidance': {
                    'message': 'Face detected successfully',
                    'suggestions': [
                        'Position your face in the center of the frame',
                        'Ensure good lighting conditions',
                        'Keep your face steady for better analysis'
                    ]
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'face_detected': False,
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
                    'positioning': 'unknown'
                },
                'guidance': {
                    'message': 'No face detected',
                    'suggestions': [
                        'Ensure your face is clearly visible in the frame',
                        'Check lighting conditions',
                        'Position your face in the center of the camera',
                        'Try moving closer to the camera'
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"❌ Face detection failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'face_detected': False,
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
                'positioning': 'unknown'
            },
            'guidance': {
                'message': 'Face detection failed',
                'suggestions': [
                    'Please try again',
                    'Check your internet connection',
                    'Ensure image data is valid'
                ]
            },
            'error': str(e)
        }), 500

@app.route('/api/v3/skin/analyze-enhanced-embeddings', methods=['POST'])
def analyze_skin_enhanced_embeddings():
    """
    Enhanced skin analysis with embeddings and cosine similarity search
    Accepts pre-detected face information to avoid redundant detection
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
        
        # Check if face detection result is provided
        face_detection_result = data.get('face_detection_result')
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {e}'}), 400
        
        # Convert to numpy array for face detection (if needed)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_array is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Use provided face detection result or perform detection
        if face_detection_result and face_detection_result.get('face_detected'):
            # Use the provided face detection result
            logger.info("Using provided face detection result")
            face_detection_result = {
                'detected': face_detection_result.get('face_detected', False),
                'confidence': face_detection_result.get('confidence', 0.0),
                'face_bounds': face_detection_result.get('face_bounds', {'x': 0, 'y': 0, 'width': 0, 'height': 0}),
                'method': 'frontend_provided',
                'quality_metrics': {
                    'overall_quality': 'good' if face_detection_result.get('confidence', 0.0) > 0.7 else 'poor',
                    'quality_score': face_detection_result.get('confidence', 0.0)
                }
            }
        else:
            # Perform face detection on backend
            logger.info("Performing face detection on backend")
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_detection_result = {
                'detected': False,
                'confidence': 0.0,
                'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'method': 'opencv_haar',
                'quality_metrics': {
                    'overall_quality': 'unknown',
                    'quality_score': 0.0
                }
            }
            
            if len(faces) > 0:
                # Get the largest face
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # Calculate confidence based on face size and position
                img_height, img_width = img_array.shape[:2]
                face_area = w * h
                img_area = img_width * img_height
                area_ratio = face_area / img_area
                
                # Calculate position score (center is better)
                center_x = x + w/2
                center_y = y + h/2
                distance_from_center = np.sqrt((center_x - img_width/2)**2 + (center_y - img_height/2)**2)
                max_distance = np.sqrt((img_width/2)**2 + (img_height/2)**2)
                position_score = 1 - (distance_from_center / max_distance)
                
                # Calculate overall confidence
                confidence = min(0.9, area_ratio * 10 + position_score * 0.1)
                
                face_detection_result = {
                    'detected': True,
                    'confidence': float(confidence),
                    'face_bounds': {
                        'x': float(x),
                        'y': float(y),
                        'width': float(w),
                        'height': float(h)
                    },
                    'method': 'opencv_haar',
                    'quality_metrics': {
                        'overall_quality': 'good' if confidence > 0.7 else 'poor',
                        'quality_score': float(confidence)
                    }
                }
        
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
                'age_category': age_category,
                'race_category': race_category
            },
            'face_detection': face_detection_result,
            'skin_analysis': {
                'overall_health_score': serializable_results.get('analysis_summary', {}).get('overall_health_score', 0.0),
                'texture': serializable_results.get('basic_analysis', {}).get('texture', 'unknown'),
                'tone': serializable_results.get('basic_analysis', {}).get('tone', 'unknown'),
                'conditions_detected': serializable_results.get('basic_analysis', {}).get('conditions_detected', []),
                'analysis_confidence': serializable_results.get('analysis_summary', {}).get('confidence', 0.0)
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