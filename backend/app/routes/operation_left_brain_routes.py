"""
Operation Left Brain API Routes - Enhanced AI Analysis Endpoints

This module provides the API endpoints for the Operation Left Brain AI integration,
implementing the complete AI analysis pipeline with real AI capabilities.
"""

import logging
import os
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename

from ..services.ai_analysis_orchestrator import ai_orchestrator
from ..error_handlers import APIError, ServiceError, ValidationError
from ..logging_config import get_service_logger

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
def analyze_skin_v2():
    """
    Enhanced skin analysis endpoint with full AI pipeline
    
    This endpoint implements the complete Operation Left Brain pipeline for general skin photos:
    1. Image embedding generation using pre-trained CNN
    2. Skin condition detection using AI models
    3. SCIN dataset similarity search using FAISS
    4. Treatment recommendations based on AI analysis
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
        
        logger.info(f"Starting Operation Left Brain skin analysis for user {current_user_id}")
        
        # Perform AI analysis using the orchestrator
        analysis_result = ai_orchestrator.analyze_skin(image_data, current_user_id)
        
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
        
        logger.info(f"✅ Operation Left Brain skin analysis completed for user {current_user_id}")
        return jsonify(result_dict), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in skin analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'validation_error'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in Operation Left Brain skin analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during AI analysis',
            'status': 'error',
            'operation': 'left_brain'
        }), 500

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