import os
import logging
import base64
import io
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify
from PIL import Image
import numpy as np
from datetime import datetime

from app.auth.supabase_auth import optional_auth
from app.services.supabase_service import SupabaseService
from app.services.enhanced_image_analysis import EnhancedImageAnalysisService
from app.services.faiss_service import FAISSService

logger = logging.getLogger(__name__)

medical_bp = Blueprint('medical', __name__, url_prefix='/api/v2/medical')

# Initialize services
supabase_service = SupabaseService()
enhanced_analysis_service = EnhancedImageAnalysisService()
faiss_service = FAISSService()

@medical_bp.route('/analyze', methods=['POST'])
@optional_auth
def analyze_skin_condition():
    """
    Medical tool endpoint for skin condition analysis
    This endpoint analyzes skin images (not faces) for medical conditions
    """
    try:
        # Get user from request context (set by auth decorator)
        user = getattr(request, 'user', None)
        user_id = user['id'] if user else None
        
        # Get image data from request
        if 'image' not in request.files and 'image_data' not in request.json:
            return jsonify({'error': 'No image provided'}), 400
        
        # Handle image data
        image_data = None
        if 'image' in request.files:
            # File upload
            file = request.files['image']
            image_data = file.read()
        elif 'image_data' in request.json:
            # Base64 encoded image
            base64_data = request.json['image_data']
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
            image_data = base64.b64decode(base64_data)
        
        if not image_data:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Validate image
        try:
            image = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            logger.error(f"Invalid image format: {e}")
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Upload image to Supabase Storage
        image_url = supabase_service.upload_image(image_data, 'medical_analysis.jpg')
        if not image_url:
            return jsonify({'error': 'Failed to upload image'}), 500
        
        # Create image record in database
        image_record = supabase_service.create_image_record(user_id, image_url)
        if not image_record:
            return jsonify({'error': 'Failed to create image record'}), 500
        
        # Perform enhanced medical analysis
        analysis_result = enhanced_analysis_service.analyze_medical_condition(image)
        
        # Search for similar conditions in SCIN dataset
        similar_conditions = faiss_service.search_similar_conditions(
            analysis_result['features'], 
            top_k=5
        )
        
        # Create medical analysis record
        medical_analysis = {
            'user_id': user_id,
            'image_id': image_record['id'],
            'condition_identified': analysis_result['primary_condition'],
            'confidence_score': analysis_result['confidence'],
            'detailed_description': analysis_result['description'],
            'recommended_treatments': analysis_result['treatments'],
            'similar_conditions': similar_conditions,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store medical analysis in Supabase
        medical_record = supabase_service.create_medical_analysis_record(medical_analysis)
        
        # Prepare response
        response_data = {
            'analysis_id': medical_record['id'],
            'condition': {
                'name': analysis_result['primary_condition'],
                'confidence': analysis_result['confidence'],
                'description': analysis_result['description']
            },
            'treatments': analysis_result['treatments'],
            'similar_conditions': similar_conditions,
            'image_url': image_url,
            'analysis_timestamp': medical_record['created_at']
        }
        
        logger.info(f"Medical analysis completed for user {user_id}: {analysis_result['primary_condition']}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Medical analysis failed: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@medical_bp.route('/history', methods=['GET'])
@optional_auth
def get_medical_history():
    """
    Get medical analysis history for the current user
    """
    try:
        user = getattr(request, 'user', None)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = user['id']
        
        # Get medical analysis history from Supabase
        history = supabase_service.get_medical_analysis_history(user_id)
        
        return jsonify({
            'history': history,
            'total_analyses': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get medical history: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@medical_bp.route('/analysis/<analysis_id>', methods=['GET'])
@optional_auth
def get_medical_analysis(analysis_id: str):
    """
    Get specific medical analysis by ID
    """
    try:
        user = getattr(request, 'user', None)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = user['id']
        
        # Get medical analysis from Supabase
        analysis = supabase_service.get_medical_analysis_by_id(analysis_id, user_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis), 200
        
    except Exception as e:
        logger.error(f"Failed to get medical analysis: {e}")
        return jsonify({'error': 'Failed to retrieve analysis'}), 500

@medical_bp.route('/conditions', methods=['GET'])
def get_available_conditions():
    """
    Get list of available skin conditions for reference
    """
    try:
        # This would typically come from a medical database
        # For now, returning a curated list
        conditions = [
            {
                'id': 'acne',
                'name': 'Acne',
                'description': 'Common skin condition characterized by pimples, blackheads, and whiteheads',
                'severity_levels': ['mild', 'moderate', 'severe']
            },
            {
                'id': 'eczema',
                'name': 'Eczema',
                'description': 'Inflammatory skin condition causing red, itchy patches',
                'severity_levels': ['mild', 'moderate', 'severe']
            },
            {
                'id': 'psoriasis',
                'name': 'Psoriasis',
                'description': 'Autoimmune condition causing rapid skin cell growth',
                'severity_levels': ['mild', 'moderate', 'severe']
            },
            {
                'id': 'rosacea',
                'name': 'Rosacea',
                'description': 'Chronic skin condition causing facial redness and visible blood vessels',
                'severity_levels': ['mild', 'moderate', 'severe']
            },
            {
                'id': 'melasma',
                'name': 'Melasma',
                'description': 'Skin condition causing brown patches on the face',
                'severity_levels': ['mild', 'moderate', 'severe']
            }
        ]
        
        return jsonify({
            'conditions': conditions,
            'total': len(conditions)
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get conditions: {e}")
        return jsonify({'error': 'Failed to retrieve conditions'}), 500 