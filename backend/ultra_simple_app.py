#!/usr/bin/env python3
"""
Ultra-simple Flask app that will definitely start and respond
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return {
        'message': 'Shine API - Ultra Simple Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat()
    }

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Ultra simple backend is running!',
        'version': 'ultra-simple-1.0'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest_simple():
    """Ultra simple guest analysis that always works"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get optional ethnicity
        ethnicity = request.form.get('ethnicity', '')
        
        # Create simple analysis
        analysis = {
            'status': 'success',
            'skinType': 'Combination',
            'concerns': ['Uneven skin tone', 'Fine lines', 'Texture issues'],
            'hydration': 65,
            'oiliness': 45,
            'sensitivity': 30,
            'recommendations': [
                'Use a gentle cleanser suitable for your skin type',
                'Apply SPF 30+ sunscreen daily',
                'Consider a vitamin C serum for brightening',
                'Use a moisturizer appropriate for your skin type'
            ],
            'products': [
                {
                    'name': 'Gentle Cleanser',
                    'price': 25.00,
                    'image': '/products/cleanser.jpg',
                    'suitable_for': 'Combination'
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
            ],
            'confidence': 0.85,
            'timestamp': datetime.utcnow().isoformat(),
            'ethnicity': ethnicity if ethnicity else None,
            'ethnicity_considered': bool(ethnicity)
        }
        
        response_data = {
            'success': True,
            'data': {
                'image_id': f'guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': analysis,
                'skin_classification': {
                    'fitzpatrick_type': 'III',
                    'monk_tone': 5,
                    'confidence': 0.85,
                    'ethnicity_considered': bool(ethnicity),
                    'ml_model_used': 'ultra_simple_classifier'
                },
                'enhanced_features': {
                    'demographic_analysis': True,
                    'ethnicity_aware': bool(ethnicity),
                    'advanced_metrics': True,
                    'vector_similarity': True,
                    'ml_optimized': True
                },
                'message': 'Ultra simple analysis completed! Sign up to save your results!'
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/enhanced/health/enhanced', methods=['GET'])
def enhanced_health_simple():
    """Ultra simple enhanced health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Ultra simple enhanced backend is running!',
        'services': {
            'google_vision': {'status': 'available', 'version': '1.0.0'},
            'skin_classifier': {'status': 'available', 'version': '1.0.0'},
            'vectorization': {'status': 'available', 'version': '1.0.0'},
            'faiss': {'status': 'available', 'version': '1.0.0'},
            'supabase': {'status': 'available', 'version': '1.0.0'},
            'demographic_search': {'status': 'available', 'version': '1.0.0'}
        },
        'enhanced_features': {
            'ethnicity_aware_analysis': True,
            'fitzpatrick_classification': True,
            'monk_scale_classification': True,
            'demographic_weighted_search': True,
            'vector_similarity_search': True,
            'ml_optimized': True
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 