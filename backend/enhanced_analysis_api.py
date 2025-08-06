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
# Import enhanced image processing
from enhanced_image_processing import enhanced_face_detect_endpoint

# Import enhanced systems
from enhanced_severity_scoring import enhanced_severity_scorer
from enhanced_recommendation_engine import enhanced_recommendation_engine
from real_skin_analysis import RealSkinAnalysis

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
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002'], supports_credentials=True)

# Initialize the integrated analysis system
try:
    integrated_analyzer = IntegratedSkinAnalysis()
    logger.info("✅ Integrated skin analysis system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize integrated analysis system: {e}")
    integrated_analyzer = None

# Initialize the real skin analysis system
try:
    real_analyzer = RealSkinAnalysis()
    logger.info("✅ Real skin analysis system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize real analysis system: {e}")
    real_analyzer = None

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
    Enhanced face detection endpoint with robust image processing
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
        
        # Use enhanced face detection with robust image processing
        result = enhanced_face_detect_endpoint(image_data)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'face_detected': result['face_detected'],
                'confidence': result['confidence'],
                'face_bounds': result['face_bounds'],
                'quality_metrics': result.get('quality_metrics', {}),
                'guidance': result.get('guidance', {}),
                'processing_metadata': result.get('processing_metadata', {})
            })
        else:
            return jsonify({
                'status': 'error',
                'error': result['error'],
                'details': result.get('details', ''),
                'metadata': result.get('metadata', {})
            }), 400
            
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
        face_detection_result = robust_face_detector(image_data)
        
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
                'image_quality': 'good' if face_detection_result.get('success', False) and face_detection_result.get('faces_detected', 0) > 0 else 'poor',
                'confidence_reliability': 'high' if face_detection_result.get('confidence', 0) > 0.7 else 'low'
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

@app.route('/api/v3/skin/analyze-enhanced-comprehensive', methods=['POST'])
def analyze_skin_enhanced_comprehensive():
    """
    Enhanced comprehensive skin analysis with severity scoring and personalized recommendations
    Integrates with existing 103 demographic baselines and condition embeddings
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
        logger.info("Performing face detection for enhanced comprehensive analysis")
        face_detection_result = robust_face_detector(image_data)
        
        # Transform face detection result to match frontend expectations
        if face_detection_result.get('success') and face_detection_result.get('faces_detected', 0) > 0:
            # Get the first detected face
            first_face = face_detection_result.get('faces', [{}])[0]
            bbox = first_face.get('bbox', [0, 0, 0, 0])
            image_dimensions = face_detection_result.get('image_dimensions', [640, 480])
            image_width = image_dimensions[0]
            image_height = image_dimensions[1]
            
            # Convert pixel coordinates to percentages
            x_percent = (bbox[0] / image_width) * 100
            y_percent = (bbox[1] / image_height) * 100
            width_percent = (bbox[2] / image_width) * 100
            height_percent = (bbox[3] / image_height) * 100
            
            # Debug logging
            logger.info(f"🔍 Comprehensive Analysis Face Detection Debug:")
            logger.info(f"  Original bbox (pixels): {bbox}")
            logger.info(f"  Image dimensions: {image_dimensions}")
            logger.info(f"  Converted to percentages: x={x_percent:.2f}%, y={y_percent:.2f}%, w={width_percent:.2f}%, h={height_percent:.2f}%")
            
            transformed_face_detection = {
                'detected': True,
                'confidence': face_detection_result.get('confidence', 0.0),
                'face_bounds': {
                    'x': x_percent,
                    'y': y_percent, 
                    'width': width_percent,
                    'height': height_percent
                },
                'image_dimensions': image_dimensions
            }
        else:
            transformed_face_detection = {
                'detected': False,
                'confidence': 0.0,
                'face_bounds': {
                    'x': 0,
                    'y': 0,
                    'width': 0,
                    'height': 0
                },
                'image_dimensions': face_detection_result.get('image_dimensions', [640, 480])
            }
        
        # Get user demographics and preferences
        demographics = data.get('demographics', {})
        user_parameters = data.get('user_parameters', {})
        user_preferences = data.get('user_preferences', {})
        
        # Extract age and race categories from user parameters
        age_category = user_parameters.get('age_category', demographics.get('age_category'))
        race_category = user_parameters.get('race_category', demographics.get('race_category'))
        
        # Perform comprehensive analysis using integrated system
        if integrated_analyzer:
            basic_results = integrated_analyzer.analyze_skin_comprehensive(image_bytes, demographics)
        else:
            return jsonify({'error': 'Analysis system not available'}), 500
        
        # Step 1: Enhanced Severity Scoring
        enhanced_severity_results = {}
        try:
            # Extract condition data for severity scoring
            skin_analysis = basic_results.get('skin_analysis', {})
            
            for condition, condition_data in skin_analysis.items():
                if isinstance(condition_data, dict) and 'confidence' in condition_data:
                    # Prepare condition data for severity scoring
                    severity_input = {
                        'intensity': condition_data.get('intensity', 0),
                        'distribution': condition_data.get('distribution', 0),
                        'size': condition_data.get('size', 0),
                        'persistence': condition_data.get('persistence', 0),
                        'impact': condition_data.get('impact', 0),
                        'confidence': condition_data.get('confidence', 0.8)
                    }
                    
                    # Calculate enhanced severity score
                    severity_result = enhanced_severity_scorer.calculate_enhanced_severity_score(
                        severity_input, demographics, condition)
                    
                    enhanced_severity_results[condition] = severity_result
                    
        except Exception as e:
            logger.error(f"❌ Enhanced severity scoring failed: {e}")
            enhanced_severity_results = {}
        
        # Step 2: Generate Personalized Recommendations
        personalized_recommendations = {}
        try:
            # Prepare analysis results for recommendation engine
            analysis_for_recommendations = {
                'skin_analysis': basic_results.get('skin_analysis', {}),
                'enhanced_severity': enhanced_severity_results,
                'demographics': demographics,
                'face_detection': face_detection_result
            }
            
            # Generate personalized recommendations
            recommendation_result = enhanced_recommendation_engine.generate_personalized_recommendations(
                analysis_for_recommendations, user_preferences, demographics)
            
            personalized_recommendations = recommendation_result
            
        except Exception as e:
            logger.error(f"❌ Personalized recommendations failed: {e}")
            personalized_recommendations = {'error': str(e)}
        
        # Step 3: Generate embeddings for cosine similarity search
        similarity_results = []
        try:
            from enhanced_embeddings import EnhancedEmbeddingSystem
            embedding_system = EnhancedEmbeddingSystem()
            
            # Generate embeddings for the user image
            user_embedding_result = embedding_system.generate_enhanced_embeddings(image_bytes)
            user_embedding = user_embedding_result.get('combined', [])
            
            # Perform cosine similarity search against condition embeddings
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
        serializable_results = convert_numpy_types(basic_results)
        
        # Build enhanced comprehensive response
        enhanced_comprehensive_response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'enhanced_comprehensive',
            'demographics': {
                'age_category': age_category or 'unknown',
                'race_category': race_category or 'unknown'
            },
            'face_detection': transformed_face_detection,
            'skin_analysis': {
                'overall_health_score': serializable_results.get('analysis_summary', {}).get('overall_health_score', 50.0),
                'texture': serializable_results.get('basic_analysis', {}).get('conditions', {}).get('texture', {}).get('type', 'normal'),
                'tone': serializable_results.get('basic_analysis', {}).get('conditions', {}).get('pigmentation', {}).get('type', 'normal'),
                'conditions_detected': len(enhanced_severity_results)
            },
            'enhanced_severity_scoring': {
                'conditions_analyzed': len(enhanced_severity_results),
                'severity_results': enhanced_severity_results,
                'scoring_methodology': {
                    'scale': '0-10 with demographic normalization',
                    'demographic_baselines_used': len(enhanced_severity_scorer.demographic_baselines),
                    'condition_embeddings_used': len(enhanced_severity_scorer.condition_embeddings)
                }
            },
            'personalized_recommendations': {
                'recommendation_confidence': personalized_recommendations.get('recommendation_confidence', 0.0),
                'individual_products': personalized_recommendations.get('individual_products', []),
                'complete_routine': personalized_recommendations.get('complete_routine', {}),
                'ingredient_analysis': personalized_recommendations.get('ingredient_analysis', {}),
                'efficacy_data': personalized_recommendations.get('efficacy_data', {}),
                'demographic_factors': personalized_recommendations.get('demographic_factors', {})
            },
            'similarity_analysis': {
                'conditions_matched': len(similarity_results),
                'top_matches': similarity_results[:3] if similarity_results else [],
                'embedding_dimensions': len(user_embedding) if user_embedding else 0
            },
            'system_capabilities': {
                'demographic_baselines': len(enhanced_severity_scorer.demographic_baselines),
                'condition_embeddings': len(enhanced_severity_scorer.condition_embeddings),
                'enhanced_conditions': len(enhanced_severity_scorer.enhanced_conditions),
                'product_categories': len(enhanced_recommendation_engine.product_database),
                'ingredients_analyzed': len(enhanced_recommendation_engine.ingredient_analysis)
            }
        }
        
        return jsonify(enhanced_comprehensive_response)
        
    except Exception as e:
        logger.error(f"❌ Enhanced comprehensive analysis failed: {e}")
        return jsonify({
            'error': f'Enhanced comprehensive analysis failed: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v3/skin/analyze-real', methods=['POST'])
def analyze_skin_real():
    """
    Real skin analysis using actual facial skin diseases dataset
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
        
        # Extract user demographics (optional)
        user_demographics = data.get('user_demographics', {})
        
        # Decode base64 image data
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        # Check if real analyzer is available
        if not real_analyzer:
            return jsonify({'error': 'Real analysis system not available'}), 500
        
        # Perform real skin analysis
        logger.info("🔄 Starting real skin analysis...")
        analysis_result = real_analyzer.analyze_skin_real(image_bytes, user_demographics)
        logger.info(f"🔍 Real analysis result: {analysis_result}")
        
        if analysis_result.get('status') == 'error':
            logger.error(f"❌ Real analysis returned error: {analysis_result}")
            return jsonify(analysis_result), 500
        
        # Add face detection if available
        face_detection_result = None
        try:
            face_detection_result = robust_face_detector(image_data)
        except Exception as e:
            logger.warning(f"⚠️ Face detection failed: {e}")
        
        # Transform face detection result if available
        transformed_face_detection = None
        if face_detection_result and face_detection_result.get('success'):
            # Get the first detected face
            first_face = face_detection_result.get('faces', [{}])[0]
            bbox = first_face.get('bbox', [0, 0, 0, 0])
            image_dimensions = face_detection_result.get('image_dimensions', [640, 480])
            image_width = image_dimensions[0]
            image_height = image_dimensions[1]
            
            # Convert pixel coordinates to percentages
            x_percent = (bbox[0] / image_width) * 100
            y_percent = (bbox[1] / image_height) * 100
            width_percent = (bbox[2] / image_width) * 100
            height_percent = (bbox[3] / image_height) * 100
            
            transformed_face_detection = {
                'detected': True,
                'confidence': face_detection_result.get('confidence', 0.0),
                'face_bounds': {
                    'x': x_percent,
                    'y': y_percent,
                    'width': width_percent,
                    'height': height_percent
                },
                'image_dimensions': image_dimensions
            }
        else:
            transformed_face_detection = {
                'detected': False,
                'confidence': 0.0,
                'face_bounds': {
                    'x': 0,
                    'y': 0,
                    'width': 0,
                    'height': 0
                },
                'image_dimensions': [640, 480]
            }
        
        # Create unified comprehensive response
        real_analysis_response = {
            'status': 'success',
            'analysis_type': 'unified_skin_analysis',
            'timestamp': datetime.now().isoformat(),
            'face_detection': transformed_face_detection,
            'confidence_score': analysis_result.get('confidence_score', 0.0),
            'analysis_summary': analysis_result.get('analysis_summary', ''),
            'primary_concerns': analysis_result.get('primary_concerns', []),
            'detected_conditions': analysis_result.get('detected_conditions', []),
            'severity_level': analysis_result.get('severity_level', 'healthy'),
            'top_recommendations': analysis_result.get('top_recommendations', []),
            'immediate_actions': analysis_result.get('immediate_actions', []),
            'lifestyle_changes': analysis_result.get('lifestyle_changes', []),
            'medical_advice': analysis_result.get('medical_advice', []),
            'prevention_tips': analysis_result.get('prevention_tips', []),
            'best_match': analysis_result.get('best_match'),
            'condition_matches': analysis_result.get('condition_matches', []),
            'system_capabilities': {
                'real_dataset_conditions': len(real_analyzer.condition_embeddings) if real_analyzer else 0,
                'computer_vision_algorithms': True,
                'condition_matching': True,
                'severity_scoring': True,
                'personalized_recommendations': True
            }
        }
        
        # Convert any numpy types to JSON-serializable types
        real_analysis_response = convert_numpy_types(real_analysis_response)
        
        return jsonify(real_analysis_response)
        
    except Exception as e:
        logger.error(f"❌ Real skin analysis failed: {e}")
        return jsonify({
            'error': f'Real skin analysis failed: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

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

@app.route('/api/v3/system/enhanced-capabilities', methods=['GET'])
def get_enhanced_capabilities():
    """Get enhanced system capabilities and status"""
    try:
        # Get status from enhanced systems
        severity_status = enhanced_severity_scorer.get_system_status()
        recommendation_status = enhanced_recommendation_engine.get_system_status()
        
        # Get basic system status
        try:
            if integrated_analyzer:
                basic_status = integrated_analyzer.get_system_status()
            else:
                basic_status = {
                    'system_status': 'error',
                    'error': 'Analysis system not available'
                }
        except Exception as e:
            basic_status = {
                'system_status': 'error',
                'error': str(e)
            }
        
        enhanced_capabilities = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'enhanced_systems': {
                'severity_scoring': severity_status,
                'recommendation_engine': recommendation_status
            },
            'basic_system': basic_status,
            'integration_status': {
                'demographic_baselines_integrated': len(enhanced_severity_scorer.demographic_baselines) > 0,
                'condition_embeddings_integrated': len(enhanced_severity_scorer.condition_embeddings) > 0,
                'enhanced_conditions_available': len(enhanced_severity_scorer.enhanced_conditions),
                'product_recommendations_available': len(enhanced_recommendation_engine.product_database) > 0
            },
            'capabilities_summary': {
                'total_demographic_baselines': len(enhanced_severity_scorer.demographic_baselines),
                'total_condition_embeddings': len(enhanced_severity_scorer.condition_embeddings),
                'enhanced_conditions_supported': list(enhanced_severity_scorer.enhanced_conditions.keys()),
                'product_categories_available': list(enhanced_recommendation_engine.product_database.keys()),
                'ingredients_analyzed': len(enhanced_recommendation_engine.ingredient_analysis)
            }
        }
        
        return jsonify(enhanced_capabilities)
        
    except Exception as e:
        logger.error(f"❌ Failed to get enhanced capabilities: {e}")
        return jsonify({
            'error': f'Failed to get enhanced capabilities: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 