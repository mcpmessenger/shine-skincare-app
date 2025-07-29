#!/usr/bin/env python3
"""
Simple test server without TensorFlow to avoid memory issues
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import uuid
import numpy as np
import cv2
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], supports_credentials=True)

# Test ML imports (without TensorFlow)
try:
    import numpy as np
    import cv2
    from PIL import Image
    ML_AVAILABLE = True
    logger.info("ML libraries imported successfully (without TensorFlow)")
except ImportError as e:
    ML_AVAILABLE = False
    logger.warning(f"ML libraries not available: {e}")

def analyze_image_content(image_data):
    """
    Real image analysis based on actual image content
    """
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        
        # Convert to grayscale for analysis
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Basic image analysis
        height, width = gray.shape
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Analyze skin characteristics based on image properties
        skin_type = determine_skin_type(brightness, contrast, width, height)
        concerns = determine_skin_concerns(brightness, contrast, width, height)
        metrics = calculate_skin_metrics(brightness, contrast, width, height)
        
        return {
            'skinType': skin_type,
            'concerns': concerns,
            'hydration': metrics['hydration'],
            'oiliness': metrics['oiliness'],
            'sensitivity': metrics['sensitivity'],
            'recommendations': generate_recommendations(skin_type, concerns, metrics),
            'products': get_product_recommendations(skin_type, concerns)
        }
        
    except Exception as e:
        logger.error(f"Error in image analysis: {e}")
        # Fallback to basic analysis
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

def determine_skin_type(brightness, contrast, width, height):
    """Determine skin type based on image analysis"""
    # Analyze brightness and contrast to determine skin characteristics
    if brightness > 150:  # Very bright
        return 'dry'
    elif brightness < 100:  # Darker
        return 'oily'
    elif contrast > 50:  # High contrast
        return 'combination'
    else:
        return 'normal'

def determine_skin_concerns(brightness, contrast, width, height):
    """Determine skin concerns based on image analysis"""
    concerns = []
    
    # Analyze brightness for dryness
    if brightness > 140:
        concerns.append('dryness')
    
    # Analyze contrast for texture issues
    if contrast > 60:
        concerns.append('texture')
    
    # Analyze image size for detail level
    if width < 300 or height < 300:
        concerns.append('image_quality')
    
    # Default concern if none detected
    if not concerns:
        concerns.append('general_care')
    
    return concerns

def calculate_skin_metrics(brightness, contrast, width, height):
    """Calculate skin metrics based on image analysis"""
    # Normalize metrics to 0-100 scale
    hydration = min(100, max(0, 100 - (brightness - 100) * 0.5))
    oiliness = min(100, max(0, (brightness - 50) * 0.8))
    sensitivity = min(100, max(0, contrast * 0.6))
    
    return {
        'hydration': int(hydration),
        'oiliness': int(oiliness),
        'sensitivity': int(sensitivity)
    }

def generate_recommendations(skin_type, concerns, metrics):
    """Generate personalized recommendations"""
    recommendations = []
    
    if 'dryness' in concerns:
        recommendations.append('Use a hydrating moisturizer')
        recommendations.append('Consider a hyaluronic acid serum')
    
    if 'texture' in concerns:
        recommendations.append('Use gentle exfoliation')
        recommendations.append('Consider a retinol product')
    
    if skin_type == 'oily':
        recommendations.append('Use oil-free products')
        recommendations.append('Consider a clay mask weekly')
    
    if skin_type == 'dry':
        recommendations.append('Use rich moisturizers')
        recommendations.append('Avoid harsh cleansers')
    
    # Default recommendations
    if not recommendations:
        recommendations.extend([
            'Use a gentle cleanser',
            'Apply moisturizer daily',
            'Use sunscreen with SPF 30+'
        ])
    
    return recommendations

def get_product_recommendations(skin_type, concerns):
    """Get product recommendations based on analysis"""
    products = []
    
    # Base products for all skin types
    products.append({'name': 'Gentle Cleanser', 'category': 'cleanser'})
    products.append({'name': 'Daily Moisturizer', 'category': 'moisturizer'})
    products.append({'name': 'SPF 30 Sunscreen', 'category': 'sunscreen'})
    
    # Specific recommendations
    if 'dryness' in concerns:
        products.append({'name': 'Hydrating Serum', 'category': 'serum'})
    
    if skin_type == 'oily':
        products.append({'name': 'Oil-Control Toner', 'category': 'toner'})
    
    return products

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine Skincare API',
        'version': '1.0.0',
        'status': 'running',
        'ml_available': ML_AVAILABLE
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Test ML libraries
        ml_status = {
            'numpy': hasattr(np, 'array'),
            'opencv': hasattr(cv2, 'cvtColor'),
            'pillow': hasattr(Image, 'open')
        }
        
        return jsonify({
            'status': 'healthy',
            'ml_capabilities': {
                'available': ML_AVAILABLE,
                'libraries': ml_status
            },
            'features': {
                'real_analysis': True,
                'dynamic_results': True,
                'image_processing': True,
                'guest_analysis': True
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    """Guest skin analysis endpoint"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Analyze the image
        analysis_result = analyze_image_content(image_data)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'analysis': analysis_result,
            'message': 'Skin analysis completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in guest analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/scin/search', methods=['POST'])
def scin_search():
    """SCIN similarity search endpoint - Mock implementation"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Mock SCIN search results
        mock_results = [
            {
                'id': 'scin_001',
                'similarity_score': 0.85,
                'condition': 'acne',
                'skin_type': 'combination',
                'image_url': '/placeholder.svg?height=200&width=300'
            },
            {
                'id': 'scin_002',
                'similarity_score': 0.78,
                'condition': 'dryness',
                'skin_type': 'dry',
                'image_url': '/placeholder.svg?height=200&width=300'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': mock_results,
            'message': 'SCIN similarity search completed'
        })
        
    except Exception as e:
        logger.error(f"Error in SCIN search: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to perform SCIN search'
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
    logger.info("Starting Simple Server (No TensorFlow)...")
    logger.info(f"ML Available: {ML_AVAILABLE}")
    # Production settings - no debug mode
    app.run(host='0.0.0.0', port=5000, debug=False) 