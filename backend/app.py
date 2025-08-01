import os
import logging
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import base64
import json
import time
import hashlib
import io
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI flags
AI_CORE_AVAILABLE = False
AI_HEAVY_AVAILABLE = False
AI_FULL_AVAILABLE = False
SCIN_AVAILABLE = False
GOOGLE_VISION_AVAILABLE = False
OPENAI_AVAILABLE = False

# Step 1: Try core AI libraries (proven working)
try:
    import numpy as np
    from PIL import Image
    import io
    AI_CORE_AVAILABLE = True
    logger.info("✅ Core AI libraries (NumPy, Pillow) loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Core AI libraries not available: {e}")

# Step 2: Try OpenCV (proven working)
if AI_CORE_AVAILABLE:
    try:
        import cv2
        AI_HEAVY_AVAILABLE = True
        logger.info("✅ OpenCV loaded successfully")
    except ImportError as e:
        logger.warning(f"❌ OpenCV not available: {e}")

# Step 3: Try heavy AI libraries (proven working - from successful deployments)
if AI_HEAVY_AVAILABLE:
    try:
        import faiss
        import timm
        import transformers
        import torch
        AI_FULL_AVAILABLE = True
        logger.info("✅ Heavy AI libraries (FAISS, TIMM, Transformers, PyTorch) loaded successfully")
    except ImportError as e:
        logger.warning(f"❌ Heavy AI libraries not available: {e}")

# Step 4: Try SCIN dataset integration (proven working)
if AI_FULL_AVAILABLE:
    try:
        import gcsfs
        import google.auth
        import sklearn
        import joblib
        SCIN_AVAILABLE = True
        logger.info("✅ SCIN dataset integration loaded successfully")
    except ImportError as e:
        logger.warning(f"❌ SCIN dataset integration not available: {e}")

# Step 5: Try Google Vision API (for face isolation)
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
    logger.info("✅ Google Vision API loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Google Vision API not available: {e}")

# Step 6: Try OpenAI API (for embeddings)
try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("✅ OpenAI API loaded successfully")
except ImportError as e:
    logger.warning(f"❌ OpenAI API not available: {e}")

def create_app():
    app = Flask(__name__)

    # Simple CORS configuration - NO duplication (proven approach)
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],  # Allow all origins for testing
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
            "supports_credentials": True
        }
    })

    # Configure file upload limits (reduced to 10MB to prevent 413 errors)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
    app.config['MAX_CONTENT_PATH'] = None

    # Error handlers
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'error': 'File too large',
            'message': 'Maximum file size is 10MB'
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

    # Import all the service classes and routes from the original application
    from application import (
        LightweightEmbeddingService, 
        EnhancedSkinAnalysisService,
        _generate_product_recommendations
    )

    # Initialize services
    embedding_service = LightweightEmbeddingService()
    enhanced_analysis_service = EnhancedSkinAnalysisService()

    # Routes
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Shine Skincare API',
            'version': 'v3.0',
            'status': 'operational',
            'features': {
                'enhanced_analysis': True,
                'openai_integration': OPENAI_AVAILABLE,
                'google_vision': GOOGLE_VISION_AVAILABLE,
                'scin_dataset': SCIN_AVAILABLE
            }
        })

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'ai_services': {
                'core': AI_CORE_AVAILABLE,
                'heavy': AI_HEAVY_AVAILABLE,
                'full': AI_FULL_AVAILABLE,
                'scin': SCIN_AVAILABLE,
                'google_vision': GOOGLE_VISION_AVAILABLE,
                'openai': OPENAI_AVAILABLE
            }
        })

    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'ai_services': {
                'core': AI_CORE_AVAILABLE,
                'heavy': AI_HEAVY_AVAILABLE,
                'full': AI_FULL_AVAILABLE,
                'scin': SCIN_AVAILABLE,
                'google_vision': GOOGLE_VISION_AVAILABLE,
                'openai': OPENAI_AVAILABLE
            }
        })

    @app.route('/api/v2/embedding/search-fast', methods=['POST', 'OPTIONS'])
    def fast_embedding_search():
        if request.method == 'OPTIONS':
            return Response(status=200)
        
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            # Read image bytes
            image_bytes = file.read()
            
            # Extract features
            features = embedding_service.extract_features(image_bytes)
            
            # Search similar conditions
            similar_conditions = embedding_service.search_similar(features)
            
            return jsonify({
                'success': True,
                'similar_conditions': similar_conditions,
                'features_extracted': True,
                'search_completed': True
            })
            
        except Exception as e:
            logger.error(f"Fast embedding search error: {str(e)}")
            return jsonify({'error': 'Search failed', 'details': str(e)}), 500

    @app.route('/api/v2/skin/analyze', methods=['POST', 'OPTIONS'])
    def analyze_skin_v2():
        if request.method == 'OPTIONS':
            return Response(status=200)
        
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            # Read image bytes
            image_bytes = file.read()
            
            # Extract features
            features = embedding_service.extract_features(image_bytes)
            
            # Analyze skin characteristics
            analysis = embedding_service._analyze_skin_characteristics(features)
            
            # Generate recommendations
            recommendations = _generate_product_recommendations(analysis['skin_type'], analysis['concerns'])
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'recommendations': recommendations,
                'features_extracted': True
            })
            
        except Exception as e:
            logger.error(f"Skin analysis error: {str(e)}")
            return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

    @app.route('/api/v3/skin/analyze-enhanced', methods=['POST', 'OPTIONS'])
    def analyze_skin_enhanced():
        if request.method == 'OPTIONS':
            return Response(status=200)
        
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            # Get optional parameters
            age = request.form.get('age')
            ethnicity = request.form.get('ethnicity')
            
            # Read image bytes
            image_bytes = file.read()
            
            # Detect face region
            face_region = enhanced_analysis_service.detect_face_region(image_bytes)
            
            if not face_region:
                return jsonify({'error': 'No face detected in image'}), 400
            
            # Crop to face
            image = Image.open(io.BytesIO(image_bytes))
            cropped_image = enhanced_analysis_service.crop_to_face(image, face_region)
            
            # Generate embedding
            embedding_data = enhanced_analysis_service.generate_image_embedding(cropped_image)
            
            # Search SCIN dataset
            similar_conditions = enhanced_analysis_service.search_scin_dataset(embedding_data)
            
            # Generate analysis
            analysis_result = enhanced_analysis_service.generate_analysis(similar_conditions, age, ethnicity)
            
            # Generate product recommendations
            products = _generate_product_recommendations(analysis_result['skin_type'], analysis_result['concerns'])
            
            # Calculate metrics
            metrics = {
                'confidence_score': analysis_result['confidence_score'],
                'similar_conditions_found': len(analysis_result['similar_conditions']),
                'face_detected': True,
                'face_isolated': True
            }
            
            return jsonify({
                'success': True,
                'analysis': {
                    'skin_type': analysis_result['skin_type'],
                    'concerns': analysis_result['concerns'],
                    'recommendations': analysis_result['recommendations'],
                    'metrics': metrics,
                    'confidence_score': analysis_result['confidence_score'],
                    'similar_conditions': analysis_result['similar_conditions']
                },
                'products': products,
                'face_detected': True,
                'ai_processed': True,
                'enhanced_features': {
                    'openai_embeddings': OPENAI_AVAILABLE,
                    'google_vision': GOOGLE_VISION_AVAILABLE,
                    'scin_dataset': True,
                    'face_isolation': True
                }
            })
            
        except Exception as e:
            logger.error(f"Enhanced skin analysis error: {str(e)}")
            return jsonify({'error': 'Enhanced analysis failed', 'details': str(e)}), 500

    @app.route('/api/scin/search', methods=['POST', 'OPTIONS'])
    def scin_search_fallback():
        if request.method == 'OPTIONS':
            return Response(status=200)
        
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image file provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image file selected'}), 400
            
            # Read image bytes
            image_bytes = file.read()
            
            # Extract features
            features = embedding_service.extract_features(image_bytes)
            
            # Search similar conditions
            similar_conditions = embedding_service.search_similar(features)
            
            return jsonify({
                'success': True,
                'similar_conditions': similar_conditions,
                'features_extracted': True,
                'search_completed': True
            })
            
        except Exception as e:
            logger.error(f"SCIN search error: {str(e)}")
            return jsonify({'error': 'Search failed', 'details': str(e)}), 500

    @app.route('/api/test', methods=['GET'])
    def test_endpoint():
        return jsonify({
            'message': 'API is working',
            'timestamp': datetime.now().isoformat(),
            'ai_services': {
                'core': AI_CORE_AVAILABLE,
                'heavy': AI_HEAVY_AVAILABLE,
                'full': AI_FULL_AVAILABLE,
                'scin': SCIN_AVAILABLE,
                'google_vision': GOOGLE_VISION_AVAILABLE,
                'openai': OPENAI_AVAILABLE
            }
        })

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False) 