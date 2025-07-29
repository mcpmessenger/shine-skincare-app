#!/usr/bin/env python3
"""
Basic Flask server without OpenCV for testing deployment
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import uuid
import numpy as np
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000', 
    'http://127.0.0.1:3000',
    'https://app.shineskincollective.com',
    'https://www.shineskincollective.com',
    'https://shineskincollective.com',
    'https://main.d3oid65kfbmqt4.amplifyapp.com'
], supports_credentials=True)

# Test basic imports
try:
    import numpy as np
    from PIL import Image
    BASIC_ML_AVAILABLE = True
    logger.info("Basic ML libraries imported successfully")
except ImportError as e:
    BASIC_ML_AVAILABLE = False
    logger.warning(f"Basic ML libraries not available: {e}")

def analyze_image_content_basic(image_data):
    """
    Basic image analysis without OpenCV
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Basic image analysis
        height, width = img_array.shape[:2]
        brightness = np.mean(img_array)
        
        # Simple skin type determination
        if brightness > 150:
            skin_type = 'dry'
        elif brightness < 100:
            skin_type = 'oily'
        else:
            skin_type = 'combination'
        
        # Basic concerns
        concerns = ['general_care']
        if skin_type == 'dry':
            concerns.append('hydration')
        elif skin_type == 'oily':
            concerns.append('oil_control')
        
        # Basic metrics
        metrics = {
            'hydration': 50 if skin_type == 'dry' else 70,
            'oiliness': 70 if skin_type == 'oily' else 30,
            'sensitivity': 30
        }
        
        return {
            'skinType': skin_type,
            'concerns': concerns,
            'hydration': metrics['hydration'],
            'oiliness': metrics['oiliness'],
            'sensitivity': metrics['sensitivity'],
            'recommendations': [
                'Use a gentle cleanser',
                'Apply moisturizer daily',
                'Use sunscreen with SPF 30+'
            ],
            'products': [
                {'name': 'Gentle Cleanser', 'category': 'cleanser'},
                {'name': 'Hydrating Moisturizer', 'category': 'moisturizer'},
                {'name': 'SPF 30 Sunscreen', 'category': 'sunscreen'}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in basic image analysis: {e}")
        # Fallback response
        return {
            'skinType': 'combination',
            'concerns': ['general_care'],
            'hydration': 50,
            'oiliness': 50,
            'sensitivity': 30,
            'recommendations': [
                'Use a gentle cleanser',
                'Apply moisturizer daily',
                'Use sunscreen with SPF 30+'
            ],
            'products': [
                {'name': 'Gentle Cleanser', 'category': 'cleanser'},
                {'name': 'Hydrating Moisturizer', 'category': 'moisturizer'},
                {'name': 'SPF 30 Sunscreen', 'category': 'sunscreen'}
            ]
        }

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine Skincare API - Basic Version',
        'status': 'running',
        'version': '1.0.0',
        'ml_available': BASIC_ML_AVAILABLE
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Basic server is running',
        'ml_available': BASIC_ML_AVAILABLE,
        'timestamp': '2025-07-29T09:00:00Z'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest_basic():
    """Basic skin analysis endpoint without OpenCV"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Perform basic analysis
        analysis_result = analyze_image_content_basic(image_data)
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': 'Basic skin analysis completed successfully',
            'analysis_type': 'basic'
        })
        
    except Exception as e:
        logger.error(f"Error in basic analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to perform basic analysis'
        }), 500

@app.route('/api/recommendations/trending')
def get_trending_products():
    """Get trending products"""
    try:
        trending_products = [
            {
                'id': '1',
                'name': 'HydraBoost Serum',
                'brand': 'AquaGlow',
                'price': 39.99,
                'rating': 4.5,
                'image_urls': ['/placeholder.svg?height=200&width=300'],
                'description': 'A powerful hydrating serum infused with hyaluronic acid and ceramides.',
                'category': 'serum',
                'subcategory': 'hydrating',
                'ingredients': ['Hyaluronic Acid', 'Ceramides', 'Niacinamide'],
                'currency': 'USD',
                'availability_status': 'available',
                'review_count': 127
            },
            {
                'id': '2',
                'name': 'Vitamin C Brightening Cream',
                'brand': 'GlowEssence',
                'price': 29.99,
                'rating': 4.3,
                'image_urls': ['/placeholder.svg?height=200&width=300'],
                'description': 'Brightening cream with stable vitamin C and antioxidants.',
                'category': 'cream',
                'subcategory': 'brightening',
                'ingredients': ['Vitamin C', 'Niacinamide', 'Hyaluronic Acid'],
                'currency': 'USD',
                'availability_status': 'available',
                'review_count': 89
            }
        ]
        
        return jsonify({
            'success': True,
            'data': trending_products,
            'message': 'Trending products retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error getting trending products: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve trending products'
        }), 500

if __name__ == '__main__':
    logger.info("Starting Basic Server...")
    logger.info(f"Basic ML Available: {BASIC_ML_AVAILABLE}")
    # Production settings - no debug mode
    app.run(host='0.0.0.0', port=5000, debug=False)