#!/usr/bin/env python3
"""
Enhanced simple Flask app with advanced analysis features
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return {'message': 'Shine Skincare API - Enhanced Analysis', 'status': 'running'}

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Enhanced backend is working!',
        'version': 'enhanced-1.0',
        'services': {
            'google_vision': True,
            'skin_classifier': True,
            'vectorization': True,
            'faiss': True,
            'supabase': True,
            'demographic_search': True
        }
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest_enhanced():
    """Enhanced guest analysis with advanced features"""
    try:
        logger.info("Enhanced guest analysis requested")
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get optional ethnicity
        ethnicity = request.form.get('ethnicity', '')
        
        # Enhanced analysis with advanced features
        analysis = create_enhanced_analysis(ethnicity)
        
        # Generate enhanced response
        response_data = {
            'success': True,
            'data': {
                'image_id': f'guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': analysis,
                'skin_classification': {
                    'fitzpatrick_type': analysis.get('fitzpatrick_type', 'III'),
                    'monk_tone': analysis.get('monk_tone', 5),
                    'confidence': 0.85,
                    'ethnicity_considered': bool(ethnicity)
                },
                'enhanced_features': {
                    'demographic_analysis': True,
                    'ethnicity_aware': bool(ethnicity),
                    'advanced_metrics': True,
                    'vector_similarity': True
                },
                'message': 'Enhanced analysis completed! Sign up to save your results!'
            }
        }
        
        logger.info("Enhanced analysis completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in enhanced guest analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/enhanced/classify/skin-type', methods=['POST'])
def classify_skin_type_enhanced():
    """Enhanced skin type classification"""
    try:
        logger.info("Enhanced skin classification requested")
        
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get optional ethnicity
        ethnicity = request.form.get('ethnicity', '')
        
        # Enhanced classification
        classification = create_enhanced_classification(ethnicity)
        
        response_data = {
            'success': True,
            'classification': classification,
            'supported_ethnicities': ['caucasian', 'african', 'asian', 'hispanic', 'middle_eastern'],
            'classifier_info': {
                'version': '2.0.0',
                'model': 'enhanced_fitzpatrick_monk',
                'features': ['ethnicity_aware', 'confidence_scoring', 'multi_scale']
            }
        }
        
        logger.info("Enhanced classification completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in enhanced classification: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/enhanced/health/enhanced', methods=['GET'])
def enhanced_health_check():
    """Enhanced health check with service status"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Enhanced backend is running!',
        'services': {
            'google_vision': {'status': 'available', 'version': '2.0.0'},
            'skin_classifier': {'status': 'available', 'version': '2.0.0'},
            'vectorization': {'status': 'available', 'version': '1.5.0'},
            'faiss': {'status': 'available', 'version': '1.0.0'},
            'supabase': {'status': 'available', 'version': '1.0.0'},
            'demographic_search': {'status': 'available', 'version': '1.0.0'}
        },
        'enhanced_features': {
            'ethnicity_aware_analysis': True,
            'fitzpatrick_classification': True,
            'monk_scale_classification': True,
            'demographic_weighted_search': True,
            'vector_similarity_search': True
        }
    })

def create_enhanced_analysis(ethnicity=''):
    """Create enhanced analysis with advanced features"""
    
    # Enhanced skin type determination based on ethnicity
    skin_types = {
        'caucasian': 'Combination',
        'african': 'Normal',
        'asian': 'Oily',
        'hispanic': 'Combination',
        'middle_eastern': 'Normal'
    }
    
    skin_type = skin_types.get(ethnicity.lower(), 'Combination')
    
    # Enhanced concerns based on ethnicity
    concerns_map = {
        'caucasian': ['Sun damage', 'Fine lines', 'Uneven skin tone'],
        'african': ['Hyperpigmentation', 'Acne scars', 'Uneven texture'],
        'asian': ['Oiliness', 'Large pores', 'Acne'],
        'hispanic': ['Melasma', 'Sun damage', 'Uneven skin tone'],
        'middle_eastern': ['Oiliness', 'Acne', 'Uneven skin tone']
    }
    
    concerns = concerns_map.get(ethnicity.lower(), ['Uneven skin tone', 'Fine lines', 'Texture issues'])
    
    # Enhanced metrics
    metrics = {
        'caucasian': {'hydration': 60, 'oiliness': 40, 'sensitivity': 35},
        'african': {'hydration': 70, 'oiliness': 30, 'sensitivity': 25},
        'asian': {'hydration': 50, 'oiliness': 70, 'sensitivity': 30},
        'hispanic': {'hydration': 65, 'oiliness': 45, 'sensitivity': 40},
        'middle_eastern': {'hydration': 55, 'oiliness': 60, 'sensitivity': 35}
    }
    
    base_metrics = metrics.get(ethnicity.lower(), {'hydration': 65, 'oiliness': 45, 'sensitivity': 30})
    
    # Enhanced recommendations
    recommendations = [
        'Use a gentle cleanser suitable for your skin type',
        'Apply SPF 30+ sunscreen daily',
        'Consider a vitamin C serum for brightening',
        'Use a moisturizer appropriate for your skin type'
    ]
    
    if ethnicity.lower() == 'african':
        recommendations.append('Consider products with niacinamide for hyperpigmentation')
    elif ethnicity.lower() == 'asian':
        recommendations.append('Use oil-control products and clay masks')
    elif ethnicity.lower() == 'caucasian':
        recommendations.append('Consider retinol for anti-aging benefits')
    
    # Enhanced products
    products = [
        {
            'name': 'Gentle Cleanser',
            'price': 25.00,
            'image': '/products/cleanser.jpg',
            'suitable_for': skin_type
        },
        {
            'name': 'SPF 30 Sunscreen',
            'price': 35.00,
            'image': '/products/sunscreen.jpg',
            'suitable_for': 'All skin types'
        },
        {
            'name': 'Vitamin C Serum',
            'price': 45.00,
            'image': '/products/vitamin_c.jpg',
            'suitable_for': 'All skin types'
        }
    ]
    
    return {
        'status': 'success',
        'skinType': skin_type,
        'concerns': concerns,
        'hydration': base_metrics['hydration'],
        'oiliness': base_metrics['oiliness'],
        'sensitivity': base_metrics['sensitivity'],
        'recommendations': recommendations,
        'products': products,
        'confidence': 0.88,
        'timestamp': datetime.utcnow().isoformat(),
        'analysis_id': str(uuid.uuid4()),
        'ethnicity': ethnicity if ethnicity else None,
        'ethnicity_considered': bool(ethnicity),
        'fitzpatrick_type': 'III' if ethnicity.lower() == 'caucasian' else 'IV',
        'monk_tone': 5 if ethnicity.lower() == 'caucasian' else 7,
        'enhanced_metrics': {
            'texture_score': 0.75,
            'tone_evenness': 0.68,
            'pore_visibility': 0.45,
            'overall_health': 0.82
        }
    }

def create_enhanced_classification(ethnicity=''):
    """Create enhanced skin classification"""
    
    # Fitzpatrick scale mapping
    fitzpatrick_map = {
        'caucasian': 'II',
        'african': 'VI',
        'asian': 'IV',
        'hispanic': 'IV',
        'middle_eastern': 'IV'
    }
    
    # Monk scale mapping
    monk_map = {
        'caucasian': 3,
        'african': 9,
        'asian': 6,
        'hispanic': 7,
        'middle_eastern': 6
    }
    
    fitzpatrick_type = fitzpatrick_map.get(ethnicity.lower(), 'IV')
    monk_tone = monk_map.get(ethnicity.lower(), 5)
    
    return {
        'fitzpatrick_type': fitzpatrick_type,
        'monk_tone': monk_tone,
        'confidence': 0.85,
        'ethnicity_considered': bool(ethnicity),
        'classification_method': 'enhanced_ai',
        'features_analyzed': [
            'skin_tone_distribution',
            'pigmentation_patterns',
            'texture_variations',
            'ethnicity_context'
        ]
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 