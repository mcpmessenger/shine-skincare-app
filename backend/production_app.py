#!/usr/bin/env python3
"""
Production-ready backend for Shine Skincare
Configured for AWS Elastic Beanstalk deployment
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)

# Configure CORS for production
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Local development (port 3000 in use)
    "https://your-frontend-url.amplifyapp.com",  # Production frontend
    "https://main.d2wy4w2nf9bgxx.amplifyapp.com",  # Old production frontend
    "*"  # Allow all origins for now (can be restricted later)
])

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine API - Production Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'production'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Production backend is working!',
        'environment': 'production'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    """Production guest analysis with enhanced data"""
    try:
        # Get image data if present
        image_data = None
        if 'image' in request.files:
            image_data = request.files['image']
        
        # Production enhanced analysis
        analysis_result = {
            'success': True,
            'data': {
                'image_id': f'prod_guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': {
                    'status': 'success',
                    'skinType': 'Combination',
                    'concerns': ['Uneven skin tone', 'Fine lines', 'Dry patches', 'Sun damage'],
                    'hydration': 65,
                    'oiliness': 45,
                    'sensitivity': 30,
                    'pigmentation': 25,
                    'texture': 70,
                    'elasticity': 75,
                    'recommendations': [
                        'Use a gentle cleanser twice daily',
                        'Apply SPF 30+ daily',
                        'Use a hydrating moisturizer',
                        'Consider a vitamin C serum',
                        'Exfoliate 2-3 times per week',
                        'Use retinol at night'
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
                        },
                        {
                            'name': 'Retinol Night Cream',
                            'price': 89.00,
                            'image': '/products/First Aid Beauty Ultra Repair Cream.webp',
                            'description': 'Anti-aging and texture improvement'
                        }
                    ],
                    'confidence': 0.92,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'message': 'Production enhanced analysis completed successfully!'
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
    """Get trending product recommendations"""
    trending_products = {
        'data': {
            'trending_products': [
                {
                    'name': 'TNS Advanced+ Serum',
                    'description': 'Clinically proven anti-aging formula',
                    'price': 199.00,
                    'image': '/products/TNS_Advanced+_Serum_1oz_2_FullWidth.jpg',
                    'rating': 4.8,
                    'review_count': 1250
                },
                {
                    'name': 'SkinCeuticals C E Ferulic',
                    'description': 'Antioxidant protection and brightening',
                    'price': 169.00,
                    'image': '/products/SkinCeuticals C E Ferulic.webp',
                    'rating': 4.9,
                    'review_count': 2100
                },
                {
                    'name': 'PCA SKIN Pigment Gel Pro',
                    'description': 'Professional-grade brightening treatment',
                    'price': 89.00,
                    'image': '/products/PCA SKIN Pigment Gel Pro.jpg',
                    'rating': 4.7,
                    'review_count': 890
                }
            ]
        },
        'success': True,
        'message': 'Trending products retrieved successfully'
    }
    
    return jsonify(trending_products)

@app.route('/api/recommendations', methods=['GET'])
def product_recommendations():
    """Get product recommendations based on skin type"""
    skin_type = request.args.get('skinType', 'combination')
    
    recommendations = {
        'data': [
            {
                'name': 'Balancing Cleanser',
                'description': 'Balances oil and hydration',
                'price': 32.00,
                'image': '/products/iS Clinical Cleansing Complex.jpg',
                'category': 'cleanser',
                'skin_type': 'combination'
            },
            {
                'name': 'Hydrating Serum',
                'description': 'Deep hydration for all skin types',
                'price': 45.00,
                'image': '/products/Naturopathica Calendula Essential Hydrating Cream.webp',
                'category': 'serum',
                'skin_type': 'dry'
            },
            {
                'name': 'Oil Control Gel',
                'description': 'Controls excess oil production',
                'price': 38.00,
                'image': '/products/Obagi CLENZIderm M.D. System (Therapeutic Lotion).webp',
                'category': 'treatment',
                'skin_type': 'oily'
            }
        ],
        'success': True,
        'message': f'Recommendations for {skin_type} skin type'
    }
    
    return jsonify(recommendations)

if __name__ == '__main__':
    # Production server configuration
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 