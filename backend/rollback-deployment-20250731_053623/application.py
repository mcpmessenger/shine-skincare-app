import os
import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import base64
import json

# NO AI imports - proven working approach
ML_AVAILABLE = False

app = Flask(__name__)

# Simple CORS configuration - NO duplication (proven approach)
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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
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
        "version": "rollback-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "structural_fix": True,
            "ml_available": ML_AVAILABLE,
            "cors_fixed": True,
            "no_duplication": True,
            "rollback_approach": True,
            "file_size_limit": "50MB",
            "ai_services": False,
            "proven_stable": True
        },
        "status": "deployed_successfully",
        "health_check": "passing"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "rollback-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "structural_fix": True,
            "ml_available": ML_AVAILABLE,
            "cors_fixed": True,
            "no_duplication": True,
            "rollback_approach": True,
            "ai_services": False,
            "basic_functionality": True,
            "proven_stable": True
        }
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "rollback-deployment",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_fixed": True,
        "no_duplication": True,
        "ml_available": ML_AVAILABLE,
        "proven_stable": True
    })

# Mock skin analysis endpoint (proven working)
@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_mock():
    """Mock skin analysis endpoint (proven working)"""
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
        
        # Mock analysis (proven working)
        analysis_result = {
            'skin_type': 'Combination',
            'concerns': ['Acne', 'Hyperpigmentation'],
            'confidence': 0.85,
            'ai_features_extracted': False,
            'rollback_approach': True,
            'proven_stable': True
        }
        
        # Build response
        response = {
            'success': True,
            'version': 'rollback-deployment',
            'timestamp': datetime.now().isoformat(),
            'results': analysis_result,
            'message': 'Mock analysis completed successfully (proven stable)',
            'ml_available': ML_AVAILABLE,
            'rollback_approach': True,
            'proven_stable': True
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Mock analysis failed',
            'ml_available': ML_AVAILABLE,
            'rollback_approach': True
        }), 500

# Mock search endpoint
@app.route('/api/mock/search', methods=['POST'])
def search_mock():
    """Mock search for similar profiles"""
    try:
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
        
        # Mock similar profiles
        similar_profiles = []
        for i in range(5):
            similarity_score = 0.8 + (0.1 * i)  # Mock scores
            profile = {
                'id': f'mock_profile_{i}',
                'similarity_score': similarity_score,
                'skin_type': 'Combination',
                'concerns': ['Acne', 'Hyperpigmentation'],
                'age_group': '25-35',
                'ethnicity': 'Caucasian'
            }
            similar_profiles.append(profile)
        
        return jsonify({
            'success': True,
            'version': 'rollback-deployment',
            'similar_profiles': similar_profiles,
            'features_extracted': False,
            'message': 'Mock search completed successfully',
            'rollback_approach': True,
            'proven_stable': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Mock search failed',
            'rollback_approach': True
        }), 500

# Trending recommendations endpoint
@app.route('/api/recommendations/trending', methods=['GET'])
def get_trending_recommendations():
    """Get trending recommendations"""
    try:
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
            'version': 'rollback-deployment',
            'products': trending_products,
            'message': 'Trending products retrieved successfully',
            'rollback_approach': True,
            'proven_stable': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get trending products',
            'rollback_approach': True
        }), 500

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with rollback approach"""
    return jsonify({
        'success': True,
        'message': 'Rollback deployment - Backend is working! (Proven stable)',
        'version': 'rollback-deployment',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'rollback_approach': True,
        'proven_stable': True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
