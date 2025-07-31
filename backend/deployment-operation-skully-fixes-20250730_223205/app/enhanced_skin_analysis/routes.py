import os
import logging
import uuid
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request_optional
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np

from . import enhanced_skin_bp
from app.services.enhanced_vectorization_service import EnhancedVectorizationService
from app.services.production_faiss_service import ProductionFAISSService
from app.services.scin_dataset_service import SCINDatasetService
from app.services.ingredient_based_recommendations import IngredientBasedRecommendations
from app.services.product_matching_service import ProductMatchingService

logger = logging.getLogger(__name__)

# 💀☠️ Operation Skully: Initialize services
enhanced_vectorization_service = EnhancedVectorizationService()
faiss_service = ProductionFAISSService()
scin_service = SCINDatasetService()
ingredient_recommendations = IngredientBasedRecommendations()
product_matching_service = ProductMatchingService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@enhanced_skin_bp.route('/analyze/vector', methods=['POST'])
def analyze_skin_vector():
    """
    Enhanced skin analysis with vector database integration
    Returns data in frontend-expected format with vector-based recommendations
    """
    try:
        # Accept both authenticated and guest requests
        verify_jwt_in_request_optional()
        current_user_id = get_jwt_identity() or "guest"
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get optional parameters
        ethnicity = request.form.get('ethnicity', '')
        age = request.form.get('age', '')
        age_int = int(age) if age.isdigit() else None
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Step 1: Enhanced vectorization
        logger.info("Performing enhanced vectorization")
        vectorization_result = enhanced_vectorization_service.vectorize_skin_image(
            image_data, ethnicity, age_int
        )
        
        if vectorization_result.get('status') != 'success':
            return jsonify({
                'error': 'Failed to vectorize image',
                'details': vectorization_result.get('error', 'Unknown error')
            }), 500
        
        # Step 2: FAISS similarity search
        logger.info("Performing FAISS similarity search")
        vector = np.array(vectorization_result['vector'])
        similar_results = faiss_service.search_similar(vector, k=5)
        
        # Step 3: Process results into frontend format
        skin_analysis = _process_enhanced_analysis(
            vectorization_result, similar_results, current_user_id
        )
        
        return jsonify(skin_analysis), 200
        
    except Exception as e:
        logger.error(f"Error in enhanced skin analysis: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@enhanced_skin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for enhanced skin analysis service"""
    try:
        services_status = {
            'enhanced_vectorization': enhanced_vectorization_service.is_available(),
            'faiss': faiss_service.is_available(),
            'scin_dataset': scin_service.is_available(),
        }
        
        return jsonify({
            'status': 'healthy',
            'services': services_status,
            'vectorization_info': enhanced_vectorization_service.get_service_info(),
            'faiss_info': faiss_service.get_index_info(),
            'message': 'Enhanced skin analysis service ready'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({'error': 'Health check failed'}), 500

@enhanced_skin_bp.route('/initialize-scin', methods=['POST'])
def initialize_scin_dataset():
    """Initialize SCIN dataset integration"""
    try:
        # Load SCIN metadata
        success = scin_service.load_metadata()
        
        if success:
            dataset_info = scin_service.get_dataset_info()
            return jsonify({
                'status': 'success',
                'message': 'SCIN dataset initialized successfully',
                'dataset_info': dataset_info
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize SCIN dataset'
            }), 500
            
    except Exception as e:
        logger.error(f"Error initializing SCIN dataset: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def _process_enhanced_analysis(vectorization_result, similar_results, user_id):
    """
    Process enhanced analysis results into frontend-expected format
    """
    try:
        # Extract skin conditions from vectorization result
        skin_conditions = vectorization_result.get('skin_conditions', {})
        conditions_data = skin_conditions.get('conditions', {})
        
        # Determine skin type based on primary condition
        primary_condition = skin_conditions.get('primary_condition', 'normal')
        skin_type = _map_condition_to_skin_type(primary_condition)
        
        # Determine skin concerns
        concerns = _determine_enhanced_concerns(conditions_data)
        
        # Calculate enhanced metrics
        metrics = _calculate_enhanced_metrics(vectorization_result)
        
        # 💀☠️ Operation Skully: Generate enhanced recommendations using ingredient-based approach
        ingredient_recs = ingredient_recommendations.get_recommendations_from_similar_profiles(
            similar_results, conditions_data, skin_type
        )
        
        # 💀☠️ Operation Skully: Match ingredients to actual products
        recommended_ingredients = ingredient_recs.get('recommended_ingredients', {}).get('primary', [])
        matched_products = product_matching_service.match_products_to_ingredients(recommended_ingredients)
        
        # 💀☠️ Operation Skully: Convert products to frontend format
        products = []
        for product in matched_products:
            products.append({
                'id': product.id,
                'name': product.name,
                'brand': product.brand,
                'price': product.price,
                'image_url': product.image_url,
                'description': product.description,
                'ingredients': product.ingredients,
                'match_score': product.match_score,
                'matching_ingredients': product.matching_ingredients
            })
        
        # Extract recommendations from ingredient analysis
        recommendations = ingredient_recs.get('personalized_advice', [])
        
        return {
            'status': 'success',
            'skinType': skin_type,
            'concerns': concerns,
            'hydration': metrics['hydration'],
            'oiliness': metrics['oiliness'],
            'sensitivity': metrics['sensitivity'],
            'recommendations': recommendations,
            'products': products,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': str(uuid.uuid4()),
            'vector_analysis': {
                'vector_dimension': vectorization_result.get('vector_dimension'),
                'similar_results_count': len(similar_results),
                'primary_condition': primary_condition,
                'confidence': skin_conditions.get('confidence', 0.0)
            },
            'ingredient_analysis': {
                'recommended_ingredients': ingredient_recs.get('recommended_ingredients', {}),
                'primary_concerns': ingredient_recs.get('primary_concerns', []),
                'confidence_score': ingredient_recs.get('confidence_score', 0.0),
                'similar_profiles_analyzed': ingredient_recs.get('similar_profiles_analyzed', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing enhanced analysis: {str(e)}")
        return {
            'error': str(e),
            'status': 'error'
        }

def _map_condition_to_skin_type(primary_condition):
    """Map primary skin condition to skin type"""
    condition_to_type = {
        'acne': 'Oily',
        'dryness': 'Dry',
        'redness': 'Sensitive',
        'hyperpigmentation': 'Combination',
        'rosacea': 'Sensitive',
        'eczema': 'Sensitive',
        'dermatitis': 'Sensitive',
        'normal': 'Combination'
    }
    return condition_to_type.get(primary_condition, 'Combination')

def _determine_enhanced_concerns(conditions_data):
    """Determine skin concerns from condition data"""
    concerns = []
    
    # Map conditions to concerns
    condition_mapping = {
        'acne': 'Acne',
        'dryness': 'Dryness',
        'redness': 'Redness',
        'hyperpigmentation': 'Hyperpigmentation',
        'rosacea': 'Redness',
        'eczema': 'Dryness',
        'dermatitis': 'Sensitivity'
    }
    
    # Add concerns based on condition scores
    for condition, score in conditions_data.items():
        if score > 0.3:  # Threshold for concern
            concern = condition_mapping.get(condition, condition.title())
            if concern not in concerns:
                concerns.append(concern)
    
    # Ensure we have at least one concern
    if not concerns:
        concerns = ['Even Skin Tone', 'Hydration']
    
    return concerns

def _calculate_enhanced_metrics(vectorization_result):
    """Calculate enhanced skin metrics"""
    skin_conditions = vectorization_result.get('skin_conditions', {})
    conditions_data = skin_conditions.get('conditions', {})
    
    # Calculate metrics based on condition scores
    hydration = 100 - int(conditions_data.get('dryness', 0) * 100)
    oiliness = int(conditions_data.get('acne', 0) * 100)
    sensitivity = int(conditions_data.get('redness', 0) * 100)
    
    return {
        'hydration': max(0, min(100, hydration)),
        'oiliness': max(0, min(100, oiliness)),
        'sensitivity': max(0, min(100, sensitivity))
    }

# Old hardcoded recommendation functions removed - now using ingredient-based approach 