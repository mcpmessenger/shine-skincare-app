#!/usr/bin/env python3
"""
Minimal working backend for Shine Skincare
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine API - Working Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Backend is working!'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    """Enhanced guest analysis with mock data"""
    try:
        # Get image data if present
        image_data = None
        if 'image' in request.files:
            image_data = request.files['image']
        
        # Mock enhanced analysis
        analysis_result = {
            'success': True,
            'data': {
                'image_id': f'guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': {
                    'status': 'success',
                    'skinType': 'Combination',
                    'concerns': ['Uneven skin tone', 'Fine lines', 'Dry patches'],
                    'hydration': 65,
                    'oiliness': 45,
                    'sensitivity': 30,
                    'pigmentation': 25,
                    'texture': 70,
                    'recommendations': [
                        'Use a gentle cleanser twice daily',
                        'Apply SPF 30+ daily',
                        'Use a hydrating moisturizer',
                        'Consider a vitamin C serum',
                        'Exfoliate 2-3 times per week'
                    ],
                    'products': [
                        {
                            'name': 'Gentle Hydrating Cleanser',
                            'price': 28.00,
                            'image': '/products/Dermalogica UltraCalming Cleanser.webp',
                            'description': 'Soothes and cleanses sensitive skin'
                        },
                        {
                            'name': 'Daily Moisturizer with SPF',
                            'price': 42.00,
                            'image': '/products/EltaMD UV Clear Broad-Spectrum SPF 46.webp',
                            'description': 'Lightweight daily protection'
                        },
                        {
                            'name': 'Vitamin C Serum',
                            'price': 169.00,
                            'image': '/products/SkinCeuticals C E Ferulic.webp',
                            'description': 'Brightening and antioxidant protection'
                        }
                    ],
                    'confidence': 0.85,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'message': 'Enhanced analysis completed successfully!'
            }
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/recommendations/trending', methods=['GET'])
def trending_recommendations():
    """Mock trending recommendations"""
    return jsonify({
        'success': True,
        'data': {
            'trending_products': [
                {
                    'name': 'Advanced+ Serum',
                    'price': 199.00,
                    'image': '/products/TNS_Advanced+_Serum_1oz_2_FullWidth.jpg',
                    'description': 'Clinically proven anti-aging formula'
                },
                {
                    'name': 'C E Ferulic',
                    'price': 169.00,
                    'image': '/products/SkinCeuticals C E Ferulic.webp',
                    'description': 'Antioxidant protection and brightening'
                },
                {
                    'name': 'Ultra Repair Cream',
                    'price': 38.00,
                    'image': '/products/First Aid Beauty Ultra Repair Cream.webp',
                    'description': 'Intensive hydration for dry skin'
                }
            ]
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 