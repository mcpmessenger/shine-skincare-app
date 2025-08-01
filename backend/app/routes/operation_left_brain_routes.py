"""
Operation Left Brain API Routes - Enhanced AI Analysis Endpoints

This module provides the API endpoints for the Operation Left Brain AI integration,
implementing the complete AI analysis pipeline with real AI capabilities.
"""

import logging
import os
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS, cross_origin

from ..services.ai_analysis_orchestrator import ai_orchestrator
from ..error_handlers import APIError, ServiceError, ValidationError
from ..logging_config import get_service_logger
from ..services.fast_embedding_service import fast_embedding_service

logger = logging.getLogger(__name__)

# Create blueprint
operation_left_brain_bp = Blueprint('operation_left_brain', __name__)

def allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def verify_jwt_in_request_optional():
    """Verify JWT token if present, return user ID or 'guest'"""
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except:
        return "guest"

@operation_left_brain_bp.route('/api/v2/selfie/analyze', methods=['POST', 'OPTIONS'])
def analyze_selfie_v2():
    """
    Enhanced selfie analysis endpoint with full AI pipeline
    
    This endpoint implements the complete Operation Left Brain pipeline:
    1. Face detection and isolation using Google Vision API
    2. Image embedding generation using pre-trained CNN
    3. Skin condition detection using AI models
    4. SCIN dataset similarity search using FAISS
    5. Treatment recommendations based on AI analysis
    """
    try:
        # Handle CORS preflight
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        # Get user ID (authenticated or guest)
        current_user_id = verify_jwt_in_request_optional()
        
        # Check if image file is present
        if 'image' not in request.files:
            raise ValidationError('No image file provided')
        
        file = request.files['image']
        if file.filename == '':
            raise ValidationError('No file selected')
        
        # Validate file type
        if not allowed_file(file.filename):
            raise ValidationError('Invalid file type. Please upload a valid image.')
        
        # Read image data
        image_data = file.read()
        
        # Check file size (100MB limit)
        if len(image_data) > 100 * 1024 * 1024:
            raise ValidationError('File too large. Please upload an image smaller than 100MB.')
        
        logger.info(f"Starting Operation Left Brain selfie analysis for user {current_user_id}")
        
        # Perform AI analysis using the orchestrator
        analysis_result = ai_orchestrator.analyze_selfie(image_data, current_user_id)
        
        # Convert result to dictionary
        result_dict = analysis_result.to_dict()
        
        # Add additional metadata
        result_dict.update({
            'success': True,
            'message': 'AI analysis completed successfully',
            'operation': 'left_brain',
            'version': '2.0',
            'total_conditions': len(analysis_result.skin_conditions),
            'similar_cases_found': len(analysis_result.scin_similar_cases)
        })
        
        logger.info(f"✅ Operation Left Brain selfie analysis completed for user {current_user_id}")
        return jsonify(result_dict), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in selfie analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in Operation Left Brain selfie analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during AI analysis',
            'status': 'error',
            'operation': 'left_brain'
        }), 500

@operation_left_brain_bp.route('/api/v2/skin/analyze', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['https://www.shineskincollective.com', 'https://shineskincollective.com', 'http://localhost:3000'])
def analyze_skin_v2():
    """Enhanced skin analysis endpoint with CORS support"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get user ID (authenticated or guest)
        current_user_id = verify_jwt_in_request_optional()
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please upload an image file'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select an image file'
            }), 400
        
        # Validate file type
        if not allowed_file(image_file.filename):
            raise ValidationError('Invalid file type. Please upload a valid image.')
        
        # Read image data
        image_bytes = image_file.read()
        
        # Check file size (limit to 10MB to prevent 413 errors)
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': 'Please upload an image smaller than 10MB'
            }), 413
        
        # Use lightweight analysis for stability
        analysis_result = perform_lightweight_analysis(image_bytes)
        
        response = jsonify({
            'success': True,
            'message': 'Skin analysis completed',
            'data': analysis_result,
            'processing_time_ms': analysis_result.get('processing_time_ms', 0),
            'analysis_type': 'lightweight_stable'
        })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error in skin analysis: {e}")
        response = jsonify({
            'success': False,
            'error': str(e),
            'status': 'validation_error'
        }), 400
        
        # Add CORS headers even for errors
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
            response[0].headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response[0].headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Skin analysis error: {e}")
        response = jsonify({
            'success': False,
            'error': 'Analysis failed',
            'message': 'Failed to analyze image. Please try again.',
            'details': str(e)
        }), 500
        
        # Add CORS headers even for errors
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
            response[0].headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response[0].headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response

@operation_left_brain_bp.route('/api/v2/ai/status', methods=['GET'])
def get_ai_status():
    """
    Get the status of all AI services in Operation Left Brain
    """
    try:
        status = ai_orchestrator.get_orchestrator_status()
        
        return jsonify({
            'success': True,
            'operation': 'left_brain',
            'status': status,
            'message': 'AI services status retrieved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve AI services status',
            'status': 'error'
        }), 500

@operation_left_brain_bp.route('/api/v2/ai/health', methods=['GET'])
def ai_health_check():
    """
    Health check for Operation Left Brain AI services
    """
    try:
        status = ai_orchestrator.get_orchestrator_status()
        
        # Check if all services are ready
        all_ready = status.get('services_ready', False)
        
        if all_ready:
            return jsonify({
                'success': True,
                'status': 'healthy',
                'operation': 'left_brain',
                'message': 'All AI services are operational',
                'services': {
                    'embedding_service': 'operational',
                    'scin_service': 'operational',
                    'vision_service': 'operational',
                    'condition_service': 'operational'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'status': 'degraded',
                'operation': 'left_brain',
                'message': 'Some AI services are not fully operational',
                'services': status
            }), 503
            
    except Exception as e:
        logger.error(f"Error in AI health check: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'operation': 'left_brain',
            'error': 'AI services health check failed'
        }), 500

@operation_left_brain_bp.route('/api/v2/ai/diagnostic', methods=['GET'])
def ai_diagnostic():
    """Diagnostic endpoint to check ML service initialization issues"""
    diagnostic_info = {
        'timestamp': datetime.now().isoformat(),
        'operation': 'left_brain',
        'diagnostic': 'ml_service_initialization',
        'checks': {}
    }
    
    # Check if heavy ML libraries are available
    try:
        import timm
        diagnostic_info['checks']['timm'] = {
            'status': 'available',
            'version': timm.__version__ if hasattr(timm, '__version__') else 'unknown'
        }
    except ImportError as e:
        diagnostic_info['checks']['timm'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    try:
        import faiss
        diagnostic_info['checks']['faiss'] = {
            'status': 'available',
            'version': faiss.__version__ if hasattr(faiss, '__version__') else 'unknown'
        }
    except ImportError as e:
        diagnostic_info['checks']['faiss'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    try:
        import torch
        diagnostic_info['checks']['torch'] = {
            'status': 'available',
            'version': torch.__version__ if hasattr(torch, '__version__') else 'unknown',
            'cuda_available': torch.cuda.is_available() if hasattr(torch, 'cuda') else False
        }
    except ImportError as e:
        diagnostic_info['checks']['torch'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    try:
        import transformers
        diagnostic_info['checks']['transformers'] = {
            'status': 'available',
            'version': transformers.__version__ if hasattr(transformers, '__version__') else 'unknown'
        }
    except ImportError as e:
        diagnostic_info['checks']['transformers'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    # Check system resources
    try:
        import psutil
        diagnostic_info['checks']['system_resources'] = {
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_count': psutil.cpu_count()
        }
    except ImportError as e:
        diagnostic_info['checks']['system_resources'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    # Check if services are trying to initialize
    try:
        from ..services.ai_embedding_service import AIEmbeddingService
        diagnostic_info['checks']['ai_embedding_service'] = {
            'status': 'importable',
            'class': 'AIEmbeddingService'
        }
    except ImportError as e:
        diagnostic_info['checks']['ai_embedding_service'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    try:
        from ..services.scin_vector_search_service import SCINVectorSearchService
        diagnostic_info['checks']['scin_vector_search_service'] = {
            'status': 'importable',
            'class': 'SCINVectorSearchService'
        }
    except ImportError as e:
        diagnostic_info['checks']['scin_vector_search_service'] = {
            'status': 'unavailable',
            'error': str(e)
        }
    
    return jsonify({
        'success': True,
        'message': 'AI diagnostic information retrieved',
        'data': diagnostic_info
    })

@operation_left_brain_bp.route('/api/v2/ai/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_result(analysis_id: str):
    """
    Get a specific analysis result by ID
    
    Note: This is a placeholder endpoint. In a real implementation,
    you would store analysis results in a database and retrieve them here.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # For now, return a mock response
        # In a real implementation, you would query a database
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'user_id': current_user_id,
            'message': 'Analysis result retrieved successfully',
            'note': 'This is a placeholder endpoint. Implement database storage for full functionality.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analysis result: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analysis result',
            'status': 'error'
        }), 500

@operation_left_brain_bp.route('/api/v2/ai/analysis/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    """
    Get analysis history for the current user
    
    Note: This is a placeholder endpoint. In a real implementation,
    you would query a database for the user's analysis history.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # For now, return a mock response
        # In a real implementation, you would query a database
        return jsonify({
            'success': True,
            'user_id': current_user_id,
            'analyses': [],
            'total_analyses': 0,
            'message': 'Analysis history retrieved successfully',
            'note': 'This is a placeholder endpoint. Implement database storage for full functionality.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve analysis history',
            'status': 'error'
        }), 500 

@operation_left_brain_bp.route('/api/v2/image/process-lightweight', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['https://www.shineskincollective.com', 'https://shineskincollective.com', 'http://localhost:3000'])
def process_image_lightweight():
    """Lightweight image processing endpoint for stable, fast image analysis with CORS support"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please upload an image file'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select an image file'
            }), 400
        
        # Read image data
        image_bytes = image_file.read()
        
        # Check file size (limit to 10MB to prevent 413 errors)
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': 'Please upload an image smaller than 10MB'
            }), 413
        
        # Lightweight image analysis (no heavy ML)
        analysis_result = perform_lightweight_analysis(image_bytes)
        
        response = jsonify({
            'success': True,
            'message': 'Lightweight image analysis completed',
            'data': analysis_result,
            'processing_time_ms': analysis_result.get('processing_time_ms', 0),
            'analysis_type': 'lightweight_stable'
        })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Lightweight image processing error: {e}")
        response = jsonify({
            'success': False,
            'error': 'Image processing failed',
            'message': 'Failed to process image. Please try again.',
            'details': str(e)
        }), 500
        
        # Add CORS headers even for errors
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
            response[0].headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response[0].headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response

@operation_left_brain_bp.route('/api/scin/search', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['https://www.shineskincollective.com', 'https://shineskincollective.com', 'http://localhost:3000'])
def scin_search_fallback():
    """Fallback SCIN search endpoint for compatibility with CORS support"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please upload an image file'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select an image file'
            }), 400
        
        # Read image data
        image_bytes = image_file.read()
        
        # Check file size (limit to 10MB to prevent 413 errors)
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': 'Please upload an image smaller than 10MB'
            }), 413
        
        # Mock SCIN search results (fallback)
        mock_results = {
            'success': True,
            'message': 'SCIN search completed (fallback mode)',
            'data': {
                'similar_cases': [
                    {
                        'id': 'fallback_1',
                        'similarity_score': 0.85,
                        'condition': 'Acne',
                        'treatment': 'Gentle cleanser and spot treatment',
                        'confidence': 0.8
                    },
                    {
                        'id': 'fallback_2',
                        'similarity_score': 0.78,
                        'condition': 'Dry skin',
                        'treatment': 'Hydrating moisturizer',
                        'confidence': 0.75
                    },
                    {
                        'id': 'fallback_3',
                        'similarity_score': 0.72,
                        'condition': 'Sensitive skin',
                        'treatment': 'Fragrance-free products',
                        'confidence': 0.7
                    }
                ],
                'total_results': 3,
                'search_quality': 'fallback_mock'
            },
            'fallback_used': True,
            'fallback_reason': 'SCIN search service unavailable'
        }
        
        response = jsonify(mock_results)
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"SCIN search fallback error: {e}")
        response = jsonify({
            'success': False,
            'error': 'Search failed',
            'message': 'Failed to process search request. Please try again.',
            'details': str(e)
        }), 500
        
        # Add CORS headers even for errors
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
            response[0].headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response[0].headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response

@operation_left_brain_bp.route('/api/v2/embedding/search-fast', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['https://www.shineskincollective.com', 'https://shineskincollective.com', 'http://localhost:3000'])
def fast_embedding_search():
    """Fast embedding search endpoint (<5 minutes) with CORS support"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get image from request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please upload an image file'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select an image file'
            }), 400
        
        # Read image data
        image_bytes = image_file.read()
        
        # Check file size (limit to 10MB to prevent 413 errors)
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({
                'success': False,
                'error': 'File too large',
                'message': 'Please upload an image smaller than 10MB'
            }), 413
        
        # Get search parameters
        top_k = request.form.get('top_k', 5, type=int)
        conditions = request.form.getlist('conditions') if request.form.get('conditions') else None
        skin_types = request.form.getlist('skin_types') if request.form.get('skin_types') else None
        
        # Create or load database (for now, use mock database)
        # In production, this would load from a pre-computed database
        database = fast_embedding_service.create_mock_database(size=1000)
        
        # Perform fast search
        start_time = time.time()
        search_results = fast_embedding_service.fast_search(image_bytes, database, top_k)
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for result in search_results:
            item = result['item']
            formatted_results.append({
                'id': item['id'],
                'similarity_score': round(result['similarity'], 3),
                'condition': item['condition'],
                'treatment': item['treatment'],
                'confidence': round(item['confidence'], 2)
            })
        
        response = jsonify({
            'success': True,
            'message': 'Fast embedding search completed',
            'data': {
                'similar_cases': formatted_results,
                'total_results': len(formatted_results),
                'search_time_seconds': round(search_time, 2),
                'search_quality': 'fast_optimized'
            },
            'search_time_ms': round(search_time * 1000, 2),
            'search_type': 'fast_embedding'
        })
        
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response
        
    except Exception as e:
        logger.error(f"Fast embedding search error: {e}")
        response = jsonify({
            'success': False,
            'error': 'Search failed',
            'message': 'Failed to perform embedding search. Please try again.',
            'details': str(e)
        }), 500
        
        # Add CORS headers even for errors
        if isinstance(response, tuple):
            response[0].headers.add('Access-Control-Allow-Origin', '*')
            response[0].headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response[0].headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        
        return response

def perform_lightweight_analysis(image_bytes):
    """Perform lightweight image analysis without heavy ML libraries"""
    import time
    import io
    from PIL import Image
    import numpy as np
    
    start_time = time.time()
    
    try:
        # Load image with PIL (lightweight)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Basic image characteristics
        width, height = image.size
        aspect_ratio = width / height
        file_size_mb = len(image_bytes) / (1024 * 1024)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for analysis
        img_array = np.array(image)
        
        # Basic color analysis
        mean_color = np.mean(img_array, axis=(0, 1))
        std_color = np.std(img_array, axis=(0, 1))
        
        # Basic brightness analysis
        brightness = np.mean(img_array)
        
        # Basic contrast analysis
        contrast = np.std(img_array)
        
        # Basic texture analysis (simplified)
        gray_img = np.mean(img_array, axis=2)
        texture_score = np.std(gray_img)
        
        # Generate lightweight recommendations
        recommendations = generate_lightweight_recommendations(
            brightness, contrast, texture_score, aspect_ratio
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            'image_info': {
                'width': width,
                'height': height,
                'aspect_ratio': round(aspect_ratio, 2),
                'file_size_mb': round(file_size_mb, 2),
                'format': image.format
            },
            'analysis': {
                'brightness': round(brightness, 2),
                'contrast': round(contrast, 2),
                'texture_score': round(texture_score, 2),
                'mean_color_rgb': [round(c, 2) for c in mean_color],
                'color_variance': [round(c, 2) for c in std_color]
            },
            'recommendations': recommendations,
            'processing_time_ms': round(processing_time, 2),
            'analysis_quality': 'lightweight_stable'
        }
        
    except Exception as e:
        logger.error(f"Lightweight analysis error: {e}")
        return {
            'error': 'Analysis failed',
            'processing_time_ms': round((time.time() - start_time) * 1000, 2)
        }

def generate_lightweight_recommendations(brightness, contrast, texture_score, aspect_ratio):
    """Generate basic recommendations based on image characteristics"""
    recommendations = []
    
    # Brightness-based recommendations
    if brightness < 100:
        recommendations.append({
            'type': 'lighting',
            'priority': 'high',
            'message': 'Image appears dark. Consider better lighting for clearer analysis.',
            'suggestion': 'Take photo in well-lit area'
        })
    elif brightness > 200:
        recommendations.append({
            'type': 'lighting',
            'priority': 'medium',
            'message': 'Image appears overexposed. Consider reducing brightness.',
            'suggestion': 'Avoid direct light sources'
        })
    
    # Contrast-based recommendations
    if contrast < 30:
        recommendations.append({
            'type': 'quality',
            'priority': 'medium',
            'message': 'Low contrast detected. Image may be blurry.',
            'suggestion': 'Hold camera steady and focus clearly'
        })
    
    # Aspect ratio recommendations
    if aspect_ratio < 0.8 or aspect_ratio > 1.2:
        recommendations.append({
            'type': 'composition',
            'priority': 'low',
            'message': 'Consider square or portrait orientation for better analysis.',
            'suggestion': 'Use square crop for consistent results'
        })
    
    # Texture-based recommendations
    if texture_score > 50:
        recommendations.append({
            'type': 'detail',
            'priority': 'medium',
            'message': 'High detail detected. Good for analysis.',
            'suggestion': 'Image quality suitable for detailed analysis'
        })
    
    # Default recommendation if none generated
    if not recommendations:
        recommendations.append({
            'type': 'general',
            'priority': 'low',
            'message': 'Image appears suitable for analysis.',
            'suggestion': 'Proceed with confidence'
        })
    
    return recommendations 