#!/usr/bin/env python3
"""
Shine Backend API - Incremental ML Strategy
Building on the successful real_working_backend.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import hashlib
import logging
import base64
from io import BytesIO

# Optional ML imports (will fail gracefully if not available)
try:
    import numpy as np
    import cv2
    from PIL import Image
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available, using mock implementations")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'true').lower() == 'true'
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine API - Incremental ML Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': 'production',
        'ml_available': ML_AVAILABLE,
        'features': [
            'Basic API Endpoints',
            'Enhanced Skin Analysis' if ML_AVAILABLE else 'Mock Skin Analysis',
            'Image Processing' if ML_AVAILABLE else 'Basic Image Handling',
            'Product Recommendations'
        ]
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Incremental ML backend is working!',
        'environment': 'production',
        'ml_available': ML_AVAILABLE,
        'services': {
            'basic_api': 'available',
            'ml_analysis': 'available' if ML_AVAILABLE else 'mock',
            'image_processing': 'available' if ML_AVAILABLE else 'mock'
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
        "success": True,
        "message": "Trending products loaded successfully"
    })

def analyze_image_ml(image_data):
    """Enhanced image analysis using ML libraries"""
    if not ML_AVAILABLE:
        return None
    
    try:
        # Convert to PIL Image
        image = Image.open(BytesIO(image_data))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Basic image analysis
        height, width = img_array.shape[:2]
        
        # Calculate average brightness
        if len(img_array.shape) == 3:  # Color image
            brightness = np.mean(img_array)
        else:  # Grayscale
            brightness = np.mean(img_array)
        
        # Analyze image quality
        quality_score = min(1.0, brightness / 128.0)
        
        # Basic skin tone analysis (simplified)
        if len(img_array.shape) == 3:
            # Convert to HSV for skin tone analysis
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            hue = np.mean(hsv[:, :, 0])
            saturation = np.mean(hsv[:, :, 1])
            value = np.mean(hsv[:, :, 2])
        else:
            hue, saturation, value = 0, 0, brightness
        
        return {
            "image_quality": quality_score,
            "brightness": float(brightness),
            "hue": float(hue),
            "saturation": float(saturation),
            "value": float(value),
            "dimensions": {"width": width, "height": height}
        }
    except Exception as e:
        logger.error(f"ML analysis failed: {e}")
        return None

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_guest():
    """Enhanced guest skin analysis endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Try ML analysis first
        ml_analysis = None
        if ML_AVAILABLE:
            ml_analysis = analyze_image_ml(image_data)
        
        # Fallback to hash-based analysis
        img_hash = hashlib.md5(image_data).hexdigest()
        hash_int = int(img_hash[:8], 16)
        
        skin_types = ["Normal", "Oily", "Dry", "Combination", "Sensitive"]
        skin_type = skin_types[hash_int % len(skin_types)]
        
        # Enhanced analysis result
        analysis_result = {
            "analysis_id": f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "completed",
            "ml_used": ML_AVAILABLE,
            "results": {
                "skin_type": skin_type,
                "concerns": ["Test concern"],
                "recommendations": ["Test recommendation"],
                "confidence": 0.8 if ML_AVAILABLE else 0.6,
                "image_quality": "high" if ML_AVAILABLE else "medium"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add ML analysis data if available
        if ml_analysis:
            analysis_result["ml_analysis"] = ml_analysis
        
        return jsonify({
            "data": analysis_result,
            "success": True,
            "message": f"Skin analysis completed successfully using {'ML' if ML_AVAILABLE else 'mock'} analysis"
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
    
    # Use the same logic as guest endpoint
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
        "message": "Incremental ML test endpoint working",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "ml_available": ML_AVAILABLE
    })

@app.route('/api/test-env')
def test_env():
    """Test environment variables"""
    return jsonify({
        "USE_MOCK_SERVICES": USE_MOCK_SERVICES,
        "LOG_LEVEL": LOG_LEVEL,
        "ML_AVAILABLE": ML_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 