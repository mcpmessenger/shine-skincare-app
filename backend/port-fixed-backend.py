#!/usr/bin/env python3
"""
Shine Backend API - Port Fixed Version
Fixed to run on port 8000 to match Nginx configuration
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'true').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

app = Flask(__name__)
CORS(app)

# Mock data for development
TRENDING_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "SkinCeuticals C E Ferulic",
        "brand": "SkinCeuticals",
        "price": 169.00,
        "rating": 4.8,
        "reviews": 1247,
        "image": "https://example.com/skinceuticals.jpg",
        "category": "serum",
        "trending_score": 95
    },
    {
        "id": "prod_002", 
        "name": "La Mer The Moisturizing Cream",
        "brand": "La Mer",
        "price": 350.00,
        "rating": 4.6,
        "reviews": 892,
        "image": "https://example.com/lamer.jpg",
        "category": "moisturizer",
        "trending_score": 92
    },
    {
        "id": "prod_003",
        "name": "Drunk Elephant T.L.C. Framboos Glycolic Night Serum",
        "brand": "Drunk Elephant", 
        "price": 90.00,
        "rating": 4.7,
        "reviews": 1563,
        "image": "https://example.com/drunk-elephant.jpg",
        "category": "serum",
        "trending_score": 89
    }
]

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Shine Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "port-fixed",
        "environment": "production"
    })

@app.route('/api/health')
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "port-fixed",
        "environment": "production"
    })

@app.route('/api/recommendations/trending')
def get_trending_products():
    """Get trending products"""
    try:
        # Simulate some processing time
        import time
        time.sleep(0.1)
        
        return jsonify({
            "data": {
                "products": TRENDING_PRODUCTS,
                "total": len(TRENDING_PRODUCTS),
                "timestamp": datetime.utcnow().isoformat()
            },
            "success": True,
            "message": "Trending products retrieved successfully"
        })
        
    except Exception as e:
        logger.error(f"Error getting trending products: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get trending products: {str(e)}"
        }), 500

@app.route('/api/trending')
def get_trending():
    """Alternative trending endpoint"""
    return get_trending_products()

@app.route('/api/recommendations')
def get_recommendations():
    """Get personalized recommendations"""
    try:
        # Mock recommendations based on request
        data = request.get_json() or {}
        skin_type = data.get('skin_type', 'normal')
        concerns = data.get('concerns', [])
        
        # Mock recommendation logic
        recommendations = [
            {
                "id": "rec_001",
                "product_id": "prod_001",
                "reason": f"Great for {skin_type} skin",
                "confidence": 0.85,
                "category": "serum"
            },
            {
                "id": "rec_002", 
                "product_id": "prod_002",
                "reason": "Addresses your concerns",
                "confidence": 0.78,
                "category": "moisturizer"
            }
        ]
        
        return jsonify({
            "data": {
                "recommendations": recommendations,
                "skin_type": skin_type,
                "concerns": concerns,
                "timestamp": datetime.utcnow().isoformat()
            },
            "success": True,
            "message": "Recommendations generated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get recommendations: {str(e)}"
        }), 500

@app.route('/api/analysis/skin', methods=['POST'])
def analyze_skin_guest():
    """Guest skin analysis endpoint"""
    try:
        data = request.get_json() or {}
        image_data = data.get('image', '')
        
        # Mock analysis
        skin_type = "combination"
        if image_data:
            # Simulate some processing
            import time
            time.sleep(0.2)
            
            # Mock analysis based on image data length
            if len(image_data) > 1000:
                skin_type = "oily"
            elif len(image_data) < 500:
                skin_type = "dry"
        
        analysis_result = {
            "analysis_id": f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "completed",
            "results": {
                "skin_type": skin_type,
                "concerns": ["Test concern"],
                "recommendations": ["Test recommendation"],
                "confidence": 0.8,
                "image_quality": "medium"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "data": analysis_result,
            "success": True,
            "message": "Skin analysis completed successfully"
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

@app.route('/api/v2/analyze', methods=['POST'])
def analyze_skin():
    """Authenticated skin analysis endpoint"""
    # Check for authentication token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "success": False,
            "message": "Authentication required"
        }), 401
    
    # For now, use the same logic as guest endpoint
    return analyze_skin_guest()

@app.route('/api/payments/create-intent', methods=['POST'])
def create_payment_intent():
    """Create payment intent for Stripe"""
    try:
        data = request.get_json()
        amount = data.get('amount', 0)
        currency = data.get('currency', 'usd')
        
        # Simulate payment intent creation
        payment_intent = {
            "id": f"pi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "client_secret": f"pi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_secret_test"
        }
        
        return jsonify({
            "data": payment_intent,
            "success": True,
            "message": "Payment intent created successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Payment intent creation failed: {str(e)}"
        }), 500

@app.route('/api/auth/login')
def get_auth_url():
    """Get Google OAuth URL"""
    return jsonify({
        "data": {
            "url": "https://accounts.google.com/oauth/authorize?client_id=your_client_id&redirect_uri=your_redirect_uri&scope=email profile&response_type=code"
        },
        "success": True,
        "message": "OAuth URL generated"
    })

@app.route('/api/auth/signup')
def signup():
    """User signup endpoint"""
    return jsonify({
        "success": True,
        "message": "Signup endpoint available"
    })

@app.route('/api/test')
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        "message": "Test endpoint working",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "port": "8000"
    })

@app.route('/api/test-env')
def test_env():
    """Test environment variables"""
    return jsonify({
        "USE_MOCK_SERVICES": USE_MOCK_SERVICES,
        "LOG_LEVEL": LOG_LEVEL,
        "PORT": os.environ.get('PORT', '8000'),
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    # FIXED: Use port 8000 to match Nginx configuration
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 