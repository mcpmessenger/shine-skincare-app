import os
import logging
from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS
from datetime import datetime
import base64
import json

# NO ML imports - maximum stability
ML_AVAILABLE = False

app = Flask(__name__)

# Configure CORS with proper handling to prevent duplication
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.shineskincollective.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
        "supports_credentials": True
    }
})

# Enhanced CORS handling to prevent duplication
@app.after_request
def after_request(response):
    """Add CORS headers to all responses, ensuring no duplication"""
    # Only add CORS headers if they don't already exist
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers.add('Access-Control-Allow-Origin', 'https://www.shineskincollective.com')
    if 'Access-Control-Allow-Headers' not in response.headers:
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Origin, Accept')
    if 'Access-Control-Allow-Methods' not in response.headers:
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    if 'Access-Control-Allow-Credentials' not in response.headers:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    if 'Access-Control-Max-Age' not in response.headers:
        response.headers.add('Access-Control-Max-Age', '86400')
    return response

# Explicit OPTIONS handler for preflight requests
@app.route('/api/v2/analyze/guest', methods=['OPTIONS'])
def handle_analyze_options():
    """Handle OPTIONS preflight for skin analysis endpoint"""
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'https://www.shineskincollective.com')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Origin, Accept')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

@app.route('/api/recommendations/trending', methods=['OPTIONS'])
def handle_trending_options():
    """Handle OPTIONS preflight for trending recommendations endpoint"""
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', 'https://www.shineskincollective.com')
    response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Origin, Accept')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

# Configure file upload limits
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['MAX_CONTENT_PATH'] = None

# Custom error handler for 413 errors
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'Maximum file size is 50MB'
    }), 413

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': 'cors-duplication-fix-v1',
        'ml_available': ML_AVAILABLE
    })

# Enhanced skin analysis endpoint (mock)
@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_enhanced():
    """Enhanced skin analysis endpoint with CORS duplication fix"""
    try:
        # Get image data
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Mock analysis results
        analysis_result = {
            'success': True,
            'version': 'cors-duplication-fix-v1',
            'timestamp': datetime.now().isoformat(),
            'results': {
                'skin_type': 'Combination',
                'concerns': ['General maintenance', 'Hydration'],
                'confidence': 0.85
            },
            'message': 'CORS duplication fix - Mock analysis completed successfully'
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'CORS duplication fix - Analysis failed'
        }), 500

# Trending recommendations endpoint (mock)
@app.route('/api/recommendations/trending', methods=['GET'])
def get_trending_recommendations():
    """Get trending recommendations with CORS duplication fix"""
    try:
        # Mock trending products
        trending_products = [
            {
                'id': 'trending_001',
                'name': 'Gentle Cleanser',
                'brand': 'CeraVe',
                'price': 14.99,
                'image_url': '/products/cerave-cleanser.jpg',
                'description': 'Non-comedogenic cleanser with ceramides',
                'trending_score': 0.95
            },
            {
                'id': 'trending_002',
                'name': 'Daily Moisturizer',
                'brand': 'The Ordinary',
                'price': 7.99,
                'image_url': '/products/ordinary-ha.jpg',
                'description': 'Hydrating serum for all skin types',
                'trending_score': 0.92
            }
        ]
        
        return jsonify({
            'success': True,
            'version': 'cors-duplication-fix-v1',
            'products': trending_products,
            'message': 'CORS duplication fix - Trending products retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'CORS duplication fix - Failed to get trending products'
        }), 500

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with CORS duplication fix"""
    return jsonify({
        'success': True,
        'message': 'CORS duplication fix - Backend is working!',
        'version': 'cors-duplication-fix-v1',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
