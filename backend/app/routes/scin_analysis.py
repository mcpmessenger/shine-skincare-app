"""
SCIN Analysis Routes
API endpoints for SCIN dataset-based skin analysis using FAISS similarity search
"""

import os
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services.scin_faiss_integration import SCINFAISSIntegration
from app.error_handlers import (
    APIError, ServiceError, ValidationError, ResourceNotFoundError,
    safe_service_call, create_error_context
)
from app.logging_config import get_service_logger, log_service_operation, log_api_request

logger = logging.getLogger(__name__)

# Create the blueprint
scin_analysis_bp = Blueprint('scin_analysis', __name__)

# Initialize the SCIN FAISS integration service
scin_integration = SCINFAISSIntegration()

@scin_analysis_bp.route('/api/scin/analyze', methods=['POST'])
def analyze_skin_with_scin():
    """
    Analyze skin image using SCIN dataset and FAISS similarity search
    
    This endpoint provides comprehensive skin analysis by:
    1. Vectorizing the uploaded image
    2. Finding similar images in the SCIN dataset using FAISS
    3. Generating skin analysis and recommendations based on similar cases
    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    try:
        # Validate request
        if 'image' not in request.files:
            raise ValidationError('No image file provided', field='image')
        
        file = request.files['image']
        if file.filename == '':
            raise ValidationError('No image file selected', field='image')
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            raise ValidationError(
                f'Invalid file type. Allowed: {", ".join(allowed_extensions)}',
                field='image'
            )
        
        # Read image data
        image_data = file.read()
        if len(image_data) == 0:
            raise ValidationError('Empty image file', field='image')
        
        # Get optional parameters
        k = request.form.get('k', 5, type=int)
        conditions = request.form.get('conditions', '').split(',') if request.form.get('conditions') else None
        skin_types = request.form.get('skin_types', '').split(',') if request.form.get('skin_types') else None
        
        # Clean up parameters
        if conditions:
            conditions = [c.strip() for c in conditions if c.strip()]
        if skin_types:
            skin_types = [s.strip() for s in skin_types if s.strip()]
        
        logger.info(f"Starting SCIN analysis {analysis_id} with k={k}")
        
        # Perform SCIN analysis
        analysis_result = scin_integration.analyze_skin_image(
            image_data=image_data,
            k=k,
            conditions=conditions,
            skin_types=skin_types
        )
        
        if not analysis_result['success']:
            raise ServiceError(f"SCIN analysis failed: {analysis_result.get('error', 'Unknown error')}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Format response
        response_data = {
            'success': True,
            'analysis_id': analysis_id,
            'status': 'completed',
            'processing_time': processing_time,
            'data': {
                'skin_analysis': _format_skin_analysis_response(analysis_result['skin_analysis']),
                'similar_images': analysis_result['similar_images'],
                'recommendations': analysis_result['recommendations'],
                'metadata': {
                    'k': k,
                    'conditions_filtered': conditions,
                    'skin_types_filtered': skin_types,
                    'similar_images_found': len(analysis_result['similar_images']),
                    'timestamp': analysis_result['timestamp']
                }
            }
        }
        
        logger.info(f"SCIN analysis {analysis_id} completed in {processing_time:.2f}s")
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'analysis_id': analysis_id,
            'error': str(e),
            'error_type': 'validation_error'
        }), 400
        
    except ServiceError as e:
        return jsonify({
            'success': False,
            'analysis_id': analysis_id,
            'error': str(e),
            'error_type': 'service_error'
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in SCIN analysis {analysis_id}: {str(e)}")
        return jsonify({
            'success': False,
            'analysis_id': analysis_id,
            'error': 'Internal server error',
            'error_type': 'internal_error'
        }), 500

@scin_analysis_bp.route('/api/scin/build-index', methods=['POST'])
def build_scin_index():
    """
    Build FAISS similarity index from SCIN dataset
    
    This endpoint processes images from the SCIN dataset and builds a FAISS index
    for efficient similarity search.
    """
    try:
        # Get parameters from request
        data = request.get_json() or {}
        conditions = data.get('conditions', [])
        skin_types = data.get('skin_types', [])
        skin_tones = data.get('skin_tones', [])
        max_images = data.get('max_images', 1000)
        batch_size = data.get('batch_size', 50)
        
        logger.info(f"Building SCIN index with max_images={max_images}, batch_size={batch_size}")
        
        # Build the index
        build_result = scin_integration.build_similarity_index(
            conditions=conditions,
            skin_types=skin_types,
            skin_tones=skin_tones,
            max_images=max_images,
            batch_size=batch_size
        )
        
        if not build_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to build index',
                'details': build_result
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Index built successfully',
            'details': build_result['details']
        }), 200
        
    except Exception as e:
        logger.error(f"Error building SCIN index: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@scin_analysis_bp.route('/api/scin/status', methods=['GET'])
def get_scin_status():
    """Get SCIN integration status"""
    try:
        status = scin_integration.get_integration_status()
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting SCIN status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@scin_analysis_bp.route('/api/scin/dataset/info', methods=['GET'])
def get_scin_dataset_info():
    """Get SCIN dataset information"""
    try:
        if not scin_integration.scin_service.is_available():
            return jsonify({
                'success': False,
                'error': 'SCIN service not available'
            }), 503
        
        dataset_info = scin_integration.scin_service.get_dataset_info()
        
        return jsonify({
            'success': True,
            'data': dataset_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting SCIN dataset info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@scin_analysis_bp.route('/api/scin/dataset/sample', methods=['GET'])
def get_scin_samples():
    """Get sample images from SCIN dataset"""
    try:
        if not scin_integration.scin_service.is_available():
            return jsonify({
                'success': False,
                'error': 'SCIN service not available'
            }), 503
        
        # Get parameters
        n = request.args.get('n', 5, type=int)
        conditions = request.args.get('conditions', '').split(',') if request.args.get('conditions') else None
        
        # Clean up conditions
        if conditions:
            conditions = [c.strip() for c in conditions if c.strip()]
        
        samples = scin_integration.scin_service.get_sample_images(n=n, conditions=conditions)
        
        return jsonify({
            'success': True,
            'data': {
                'samples': samples,
                'count': len(samples),
                'requested_count': n
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting SCIN samples: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@scin_analysis_bp.route('/api/scin/search', methods=['POST'])
def search_scin_similar():
    """
    Search for similar images in SCIN dataset
    
    This endpoint allows searching for similar images without uploading a new image
    """
    try:
        # Validate request
        if 'query_image' not in request.files:
            raise ValidationError('No query image provided', field='query_image')
        
        file = request.files['query_image']
        if file.filename == '':
            raise ValidationError('No query image selected', field='query_image')
        
        # Read image data
        image_data = file.read()
        if len(image_data) == 0:
            raise ValidationError('Empty query image file', field='query_image')
        
        # Get parameters
        k = request.form.get('k', 5, type=int)
        conditions = request.form.get('conditions', '').split(',') if request.form.get('conditions') else None
        skin_types = request.form.get('skin_types', '').split(',') if request.form.get('skin_types') else None
        
        # Clean up parameters
        if conditions:
            conditions = [c.strip() for c in conditions if c.strip()]
        if skin_types:
            skin_types = [s.strip() for s in skin_types if s.strip()]
        
        # Perform search
        search_result = scin_integration.analyze_skin_image(
            image_data=image_data,
            k=k,
            conditions=conditions,
            skin_types=skin_types
        )
        
        if not search_result['success']:
            return jsonify({
                'success': False,
                'error': search_result.get('error', 'Search failed')
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'similar_images': search_result['similar_images'],
                'query_image_id': search_result['analysis_id'],
                'k': k,
                'conditions_filtered': conditions,
                'skin_types_filtered': skin_types
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in SCIN search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def _format_skin_analysis_response(skin_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Format skin analysis response for frontend consumption"""
    
    # Map Fitzpatrick type to user-friendly skin type
    fitzpatrick_type = skin_analysis.get('fitzpatrick_type', 'III')
    skin_type_mapping = {
        'I': 'Very Fair',
        'II': 'Fair',
        'III': 'Light', 
        'IV': 'Medium',
        'V': 'Dark',
        'VI': 'Very Dark'
    }
    
    skin_type = skin_type_mapping.get(fitzpatrick_type, 'Medium')
    concerns = skin_analysis.get('concerns', ['Even Skin Tone', 'Hydration'])
    confidence = skin_analysis.get('confidence', 0.8)
    
    # Calculate metrics based on confidence
    hydration = max(60, min(90, int(confidence * 100) - 10))
    oiliness = max(20, min(70, int((1 - confidence) * 80) + 20))
    sensitivity = max(15, min(60, int((1 - confidence) * 50) + 15))
    
    # Mock product recommendations
    products = [
        {
            'name': 'Gentle Daily Cleanser',
            'category': 'Cleanser',
            'rating': 4.5,
            'price': 24.99,
            'image': '/products/cleanser.jpg',
            'suitable_for': skin_type
        },
        {
            'name': 'Brightening Vitamin C Serum',
            'category': 'Serum',
            'rating': 4.8,
            'price': 45.99,
            'image': '/products/serum.jpg',
            'suitable_for': skin_type
        },
        {
            'name': 'Hydrating Daily Moisturizer',
            'category': 'Moisturizer',
            'rating': 4.3,
            'price': 32.99,
            'image': '/products/moisturizer.jpg',
            'suitable_for': skin_type
        }
    ]
    
    return {
        'status': 'success',
        'skinType': skin_type,
        'fitzpatrick_type': fitzpatrick_type,
        'concerns': concerns[:3],  # Limit to top 3 concerns
        'hydration': hydration,
        'oiliness': oiliness,
        'sensitivity': sensitivity,
        'products': products,
        'confidence': confidence,
        'similarity_score': skin_analysis.get('similarity_score', 0.0),
        'skin_tone': skin_analysis.get('skin_tone')
    } 