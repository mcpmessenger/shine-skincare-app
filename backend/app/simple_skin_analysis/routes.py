import os
import logging
import uuid
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request_optional
from werkzeug.utils import secure_filename
from datetime import datetime

from . import simple_skin_bp
from app.services.google_vision_service import GoogleVisionService

logger = logging.getLogger(__name__)

# Initialize only the Google Vision service
google_vision_service = GoogleVisionService()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@simple_skin_bp.route('/analyze/skin', methods=['POST'])
def analyze_skin():
    """
    Simplified skin analysis endpoint using only Google Vision API
    Returns data in frontend-expected format
    """
    try:
        # Accept both authenticated and guest / anonymous requests
        verify_jwt_in_request_optional()
        current_user_id = get_jwt_identity() or "guest"
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Analyze with Google Vision AI
        logger.info("Analyzing skin with Google Vision AI")
        vision_result = google_vision_service.analyze_image_from_bytes(image_data)
        
        if vision_result.get('status') != 'success':
            return jsonify({
                'error': 'Failed to analyze image',
                'details': vision_result.get('error', 'Unknown error')
            }), 500
        
        # Process Vision results into frontend-expected format
        skin_analysis = _process_skin_analysis(vision_result, current_user_id)
        
        return jsonify(skin_analysis), 200
        
    except Exception as e:
        logger.error(f"Error in skin analysis: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@simple_skin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for simplified skin analysis service"""
    try:
        services_status = {
            'google_vision': google_vision_service.is_available(),
        }
        
        return jsonify({
            'status': 'healthy',
            'services': services_status,
            'message': 'Simplified skin analysis service ready'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({'error': 'Health check failed'}), 500

def _process_skin_analysis(vision_result, user_id):
    """
    Process Google Vision results into frontend-expected format
    """
    try:
        results = vision_result.get('results', {})
        face_data = results.get('face_detection', {})
        image_props = results.get('image_properties', {})
        labels = results.get('label_detection', {})
        
        # Determine skin type based on analysis
        skin_type = _determine_skin_type(face_data, image_props, labels)
        
        # Determine skin concerns
        concerns = _determine_skin_concerns(face_data, labels)
        
        # Calculate metrics
        metrics = _calculate_skin_metrics(face_data, image_props)
        
        # Generate recommendations
        recommendations = _generate_recommendations(skin_type, concerns, metrics)
        
        # Get product recommendations
        products = _get_product_recommendations(skin_type, concerns)
        
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
            'analysis_id': str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"Error processing skin analysis: {str(e)}")
        return {
            'error': str(e),
            'status': 'error'
        }

def _determine_skin_type(face_data, image_props, labels):
    """Determine skin type based on Vision analysis"""
    # Default to combination skin
    skin_type = 'Combination'
    
    # Check if face was detected
    if face_data.get('faces_found', 0) > 0:
        # Analyze face data for skin characteristics
        face_info = face_data.get('face_data', [{}])[0]
        
        # Simple logic based on face detection confidence and image properties
        if face_info.get('confidence', 0) > 0.8:
            # High confidence face detection - could indicate clearer skin
            skin_type = 'Normal'
        elif face_info.get('confidence', 0) > 0.6:
            skin_type = 'Combination'
        else:
            skin_type = 'Sensitive'
    
    return skin_type

def _determine_skin_concerns(face_data, labels):
    """Determine skin concerns based on analysis"""
    concerns = []
    
    # Check labels for skin-related terms
    label_descriptions = [label.get('description', '').lower() for label in labels.get('labels', [])]
    
    # Map labels to concerns
    concern_mapping = {
        'acne': 'Acne',
        'pimple': 'Acne',
        'blemish': 'Acne',
        'dark spot': 'Hyperpigmentation',
        'pigment': 'Hyperpigmentation',
        'freckle': 'Hyperpigmentation',
        'wrinkle': 'Fine Lines',
        'line': 'Fine Lines',
        'dry': 'Dryness',
        'oily': 'Oiliness',
        'red': 'Redness',
        'sensitive': 'Sensitivity'
    }
    
    for label in label_descriptions:
        for key, concern in concern_mapping.items():
            if key in label and concern not in concerns:
                concerns.append(concern)
    
    # Default concerns if none detected
    if not concerns:
        concerns = ['Even Skin Tone', 'Hydration']
    
    return concerns[:3]  # Limit to top 3 concerns

def _calculate_skin_metrics(face_data, image_props):
    """Calculate skin metrics based on analysis"""
    # Default metrics
    metrics = {
        'hydration': 75,
        'oiliness': 45,
        'sensitivity': 30
    }
    
    # Adjust based on face detection confidence
    if face_data.get('faces_found', 0) > 0:
        face_info = face_data.get('face_data', [{}])[0]
        confidence = face_info.get('confidence', 0.5)
        
        # Higher confidence might indicate better skin condition
        if confidence > 0.8:
            metrics['hydration'] = 85
            metrics['oiliness'] = 35
            metrics['sensitivity'] = 25
        elif confidence > 0.6:
            metrics['hydration'] = 75
            metrics['oiliness'] = 45
            metrics['sensitivity'] = 30
        else:
            metrics['hydration'] = 65
            metrics['oiliness'] = 55
            metrics['sensitivity'] = 40
    
    return metrics

def _generate_recommendations(skin_type, concerns, metrics):
    """Generate personalized recommendations"""
    recommendations = []
    
    # Base recommendations by skin type
    type_recommendations = {
        'Normal': [
            'Use a gentle cleanser twice daily',
            'Apply SPF 30+ sunscreen every morning',
            'Maintain a consistent skincare routine'
        ],
        'Combination': [
            'Use a gentle cleanser twice daily',
            'Apply SPF 30+ sunscreen every morning',
            'Consider a vitamin C serum for brightening',
            'Use a lightweight moisturizer for combination skin'
        ],
        'Sensitive': [
            'Use fragrance-free, gentle products',
            'Patch test new products before use',
            'Avoid harsh exfoliants',
            'Use a calming moisturizer'
        ]
    }
    
    recommendations.extend(type_recommendations.get(skin_type, type_recommendations['Combination']))
    
    # Add concern-specific recommendations
    if 'Acne' in concerns:
        recommendations.append('Consider a salicylic acid cleanser')
    if 'Hyperpigmentation' in concerns:
        recommendations.append('Use products with niacinamide or vitamin C')
    if 'Fine Lines' in concerns:
        recommendations.append('Consider a retinol product (start slowly)')
    
    return recommendations[:4]  # Limit to 4 recommendations

def _get_product_recommendations(skin_type, concerns):
    """Get product recommendations based on analysis"""
    # Mock product data - in real app, this would come from a database
    products = [
        {
            'name': 'Gentle Foaming Cleanser',
            'category': 'Cleanser',
            'rating': 4.5,
            'price': 24.99,
            'image': '/products/cleanser.jpg'
        },
        {
            'name': 'Vitamin C Brightening Serum',
            'category': 'Serum',
            'rating': 4.8,
            'price': 45.99,
            'image': '/products/serum.jpg'
        },
        {
            'name': 'Lightweight Hydrating Moisturizer',
            'category': 'Moisturizer',
            'rating': 4.3,
            'price': 32.99,
            'image': '/products/moisturizer.jpg'
        }
    ]
    
    return products 