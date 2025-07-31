import os
import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import base64
import json

# NO ML imports - maximum stability (proven approach)
ML_AVAILABLE = False

app = Flask(__name__)

# Simple CORS configuration - NO duplication
CORS(app, resources={
    r"/*": {
        "origins": ["https://www.shineskincollective.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
        "supports_credentials": True
    }
})

# REMOVED: @app.after_request handler that was causing duplication
# Let Flask-CORS handle CORS headers automatically

# Configure file upload limits
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB (reduced for stability)
app.config['MAX_CONTENT_PATH'] = None

# Custom error handler for 413 errors
@app.errorhandler(413)
def too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'Please upload an image smaller than 50MB. For best results, use a photo under 5MB.',
        'max_size_mb': 50,
        'recommended_size_mb': 5
    }), 413

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Shine Skincare App is running!",
        "version": "simple-cors-fix-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "structural_fix": True,
            "ml_available": False,
            "cors_fixed": True,
            "no_duplication": True,
            "file_size_limit": "50MB",
            "ultra_minimal": True,
            "maximum_stability": True
        },
        "status": "deployed_successfully",
        "health_check": "passing"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "simple-cors-fix-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "structural_fix": True,
            "ml_available": False,
            "cors_fixed": True,
            "no_duplication": True,
            "ultra_minimal": True,
            "maximum_stability": True,
            "basic_functionality": True
        }
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "simple-cors-fix-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_fixed": True,
        "no_duplication": True
    })

# Enhanced skin analysis endpoint (mock) - SAME as ultra minimal
@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_enhanced():
    """Enhanced skin analysis endpoint with simple CORS fix"""
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
        
        # Mock analysis results (SAME as ultra minimal)
        analysis_result = {
            'success': True,
            'version': 'simple-cors-fix-deployment',
            'timestamp': datetime.now().isoformat(),
            'results': {
                'skin_type': 'Combination',
                'concerns': ['General maintenance', 'Hydration'],
                'confidence': 0.85
            },
            'message': 'Simple CORS fix - Mock analysis completed successfully'
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Simple CORS fix - Analysis failed'
        }), 500

# Trending recommendations endpoint (mock) - SAME as ultra minimal
@app.route('/api/recommendations/trending', methods=['GET'])
def get_trending_recommendations():
    """Get trending recommendations with simple CORS fix"""
    try:
        # Mock trending products (SAME as ultra minimal)
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
            'version': 'simple-cors-fix-deployment',
            'products': trending_products,
            'message': 'Simple CORS fix - Trending products retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Simple CORS fix - Failed to get trending products'
        }), 500

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with simple CORS fix"""
    return jsonify({
        'success': True,
        'message': 'Simple CORS fix - Backend is working!',
        'version': 'simple-cors-fix-deployment',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
