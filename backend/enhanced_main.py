#!/usr/bin/env python3
"""
Shine Backend API - Full Capability Version
Enhanced with ML services, vector database, and advanced analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import logging

# Import enhanced modules
try:
    from app.enhanced_analysis_router import EnhancedAnalysisRouter
    from app.service_manager import service_manager
    from app.error_handlers import APIError, safe_service_call
    from app.logging_config import get_service_logger
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    logging.warning("Enhanced modules not available, using basic functionality")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])

# Initialize enhanced analysis router if available
if ENHANCED_AVAILABLE:
    try:
        enhanced_router = EnhancedAnalysisRouter()
        app.register_blueprint(enhanced_router.blueprint, url_prefix='/api/v3')
        logger.info("Enhanced analysis router initialized")
    except Exception as e:
        logger.error(f"Failed to initialize enhanced router: {e}")
        ENHANCED_AVAILABLE = False

# Configuration
USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'false').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine API - Full Capability Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'production',
        'enhanced_available': ENHANCED_AVAILABLE,
        'features': [
            'Enhanced AI Skin Analysis',
            'Vector Database Recommendations',
            'Google Vision Integration',
            'Demographic Matching',
            'Advanced Error Recovery'
        ] if ENHANCED_AVAILABLE else [
            'Basic API Endpoints',
            'Health Checks',
            'Product Recommendations'
        ]
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Full capability backend is working!',
        'environment': 'production',
        'enhanced_available': ENHANCED_AVAILABLE,
        'services': {
            'enhanced_analysis': 'available' if ENHANCED_AVAILABLE else 'unavailable',
            'vector_database': 'available' if ENHANCED_AVAILABLE else 'unavailable',
            'skin_classifier': 'available' if ENHANCED_AVAILABLE else 'unavailable',
            'google_vision': 'available' if ENHANCED_AVAILABLE else 'unavailable'
        }
    })

@app.route('/api/recommendations/trending')
def get_trending_products():
    """Get trending skincare products"""
    trending_products = [
        {
            "id": "1",
            "name": "TNS Advanced+ Serum",
            "brand": "SkinMedica",
            "price": 199.00,
            "rating": 4.8,
            "image": "/products/TNS_Advanced+_Serum_1oz_2_FullWidth.jpg",
            "description": "Clinically proven anti-aging formula",
            "category": "serum",
            "subcategory": "anti-aging",
            "ingredients": ["Growth Factors", "Peptides", "Antioxidants"],
            "currency": "USD",
            "availability_status": "available",
            "review_count": 342
        },
        {
            "id": "2",
            "name": "C E Ferulic",
            "brand": "SkinCeuticals",
            "price": 169.00,
            "rating": 4.9,
            "image": "/products/SkinCeuticals C E Ferulic.webp",
            "description": "Antioxidant serum for brighter skin",
            "category": "serum",
            "subcategory": "brightening",
            "ingredients": ["Vitamin C", "Vitamin E", "Ferulic Acid"],
            "currency": "USD",
            "availability_status": "available",
            "review_count": 567
        },
        {
            "id": "3",
            "name": "UltraCalming Cleanser",
            "brand": "Dermalogica",
            "price": 45.00,
            "rating": 4.6,
            "image": "/products/Dermalogica UltraCalming Cleanser.webp",
            "description": "Gentle cleanser for sensitive skin",
            "category": "cleanser",
            "subcategory": "gentle",
            "ingredients": ["Oat Extract", "Aloe Vera", "Chamomile"],
            "currency": "USD",
            "availability_status": "available",
            "review_count": 234
        }
    ]
    
    return jsonify({
        "data": {
            "trending_products": trending_products
        },
        "message": "Trending products retrieved successfully",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/recommendations')
def get_recommendations():
    """Get personalized recommendations using vector database"""
    if not ENHANCED_AVAILABLE:
        return jsonify({
            "error": "Enhanced recommendations not available",
            "message": "Basic recommendations only"
        }), 503
    
    try:
        # Use enhanced recommendation service
        recommendations = service_manager.get_recommendations_service().get_personalized_recommendations()
        return jsonify({
            "data": {
                "recommendations": recommendations
            },
            "message": "Personalized recommendations retrieved successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            "error": "Failed to get recommendations",
            "message": str(e)
        }), 500

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_guest():
    """Enhanced guest skin analysis with AI"""
    if not ENHANCED_AVAILABLE:
        return jsonify({
            "error": "Enhanced analysis not available",
            "message": "Basic analysis only"
        }), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Use enhanced analysis service
        result = enhanced_router.analyze_image_guest()
        return result
        
    except Exception as e:
        logger.error(f"Error in guest analysis: {e}")
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/api/v2/analyze', methods=['POST'])
def analyze_skin():
    """Enhanced authenticated skin analysis with AI"""
    if not ENHANCED_AVAILABLE:
        return jsonify({
            "error": "Enhanced analysis not available",
            "message": "Basic analysis only"
        }), 503
    
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Use enhanced analysis service
        result = enhanced_router.analyze_image()
        return result
        
    except Exception as e:
        logger.error(f"Error in authenticated analysis: {e}")
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@app.route('/api/payments/create-intent', methods=['POST'])
def create_payment_intent():
    """Create payment intent"""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        
        # Mock payment intent creation
        intent_id = f"pi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            "client_secret": f"pi_{intent_id}_secret",
            "intent_id": intent_id,
            "amount": amount,
            "currency": "usd",
            "status": "requires_payment_method"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login')
def get_auth_url():
    """Get authentication URL"""
    return jsonify({
        "auth_url": "https://accounts.google.com/oauth/authorize",
        "client_id": "your-google-client-id",
        "redirect_uri": "https://your-app.com/auth/callback"
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        "message": "Enhanced backend test endpoint",
        "timestamp": datetime.utcnow().isoformat(),
        "enhanced_available": ENHANCED_AVAILABLE,
        "features": [
            "Enhanced AI Analysis",
            "Vector Database",
            "Google Vision",
            "Demographic Matching"
        ] if ENHANCED_AVAILABLE else [
            "Basic API Endpoints"
        ]
    })

@app.route('/api/test-env')
def test_env():
    """Test environment variables"""
    return jsonify({
        "USE_MOCK_SERVICES": USE_MOCK_SERVICES,
        "LOG_LEVEL": LOG_LEVEL,
        "ENVIRONMENT": "production",
        "ENHANCED_AVAILABLE": ENHANCED_AVAILABLE
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 