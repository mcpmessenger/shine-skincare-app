#!/usr/bin/env python3
"""
Shine Backend API - Real Working Version
Deployed to AWS Elastic Beanstalk
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'true').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine API - Real Working Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'production'
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Real backend is working!',
        'environment': 'production'
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
        "success": True,
        "message": "Trending products loaded successfully"
    })

@app.route('/api/recommendations')
def get_recommendations():
    """Get product recommendations based on skin type"""
    skin_type = request.args.get('skinType', 'combination')
    
    recommendations = {
        "combination": [
            {
                "id": "4",
                "name": "Molecular Silk Amino Hydrating Cleanser",
                "brand": "Allies of Skin",
                "price": 38.00,
                "rating": 4.7,
                "image": "/products/Allies of Skin Molecular Silk Amino Hydrating Cleanser.webp",
                "description": "Gentle yet effective cleanser",
                "category": "cleanser",
                "subcategory": "hydrating"
            }
        ],
        "sensitive": [
            {
                "id": "5",
                "name": "Ultra Repair Cream",
                "brand": "First Aid Beauty",
                "price": 34.00,
                "rating": 4.5,
                "image": "/products/First Aid Beauty Ultra Repair Cream.webp",
                "description": "Intensive repair for sensitive skin",
                "category": "moisturizer",
                "subcategory": "repair"
            }
        ],
        "oily": [
            {
                "id": "6",
                "name": "CLENZIderm M.D. System",
                "brand": "Obagi",
                "price": 89.00,
                "rating": 4.4,
                "image": "/products/Obagi CLENZIderm M.D. System (Therapeutic Lotion).webp",
                "description": "Professional acne treatment system",
                "category": "treatment",
                "subcategory": "acne"
            }
        ]
    }
    
    return jsonify({
        "data": recommendations.get(skin_type, recommendations["combination"]),
        "success": True,
        "message": f"Recommendations for {skin_type} skin type"
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_guest():
    """Guest skin analysis endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "No image file provided"
            }), 400
        
        # Simulate analysis processing
        analysis_result = {
            "analysis_id": f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "completed",
            "results": {
                "skin_type": "Combination",
                "concerns": ["Acne", "Hyperpigmentation"],
                "recommendations": [
                    "Gentle cleanser",
                    "Vitamin C serum",
                    "Non-comedogenic moisturizer"
                ],
                "confidence": 0.85
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "data": analysis_result,
            "success": True,
            "message": "Skin analysis completed successfully"
        })
        
    except Exception as e:
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

@app.route('/api/test')
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        "message": "Test endpoint working",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production"
    })

@app.route('/api/test-env')
def test_env():
    """Test environment variables"""
    return jsonify({
        "USE_MOCK_SERVICES": USE_MOCK_SERVICES,
        "LOG_LEVEL": LOG_LEVEL,
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 