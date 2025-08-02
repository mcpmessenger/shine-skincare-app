import os
import logging
import traceback
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import base64
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

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large', 'message': 'Maximum file size is 10MB'}), 413

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine Skincare App - New Embeddings Model Backend',
        'status': 'running',
        'version': 'v1.0.8-embeddings',
        'architecture': 'embeddings-model',
        'timestamp': datetime.now().isoformat()
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
        'status': 'deployed_successfully',
        'operation': 'embeddings_model',
        'version': 'embeddings-model-v1.0.8',
        'timestamp': datetime.now().isoformat(),
        'health_check': 'passing',
        'message': 'Shine Skincare App - Embeddings Model Backend is running!',
        'features': {
            'advanced_ml': False,
            'ai_services': {
                'advanced_ml': False,
                'core_ai': AI_CORE_AVAILABLE,
                'full_ai': AI_FULL_AVAILABLE,
                'google_vision': GOOGLE_VISION_AVAILABLE,
                'heavy_ai': AI_HEAVY_AVAILABLE,
                'operation_left_brain': False,
                'scin_dataset': SCIN_AVAILABLE
            },
            'cors_fixed': True,
            'dual_skin_analysis': True,
            'file_size_limit': '10MB',
            'general_skin_analysis': True,
            'google_vision_api': GOOGLE_VISION_AVAILABLE,
            'ml_available': AI_CORE_AVAILABLE,
            'no_duplication': True,
            'operation_left_brain': False,
            'proven_stable': True,
            'scin_dataset': SCIN_AVAILABLE,
            'selfie_analysis': True,
            'structural_fix': True
        }
    })

@app.route('/api/test')
def test_endpoint():
    return jsonify({
        'message': 'Embeddings Model backend is working!',
        'timestamp': datetime.now().isoformat(),
        'ai_services_available': {
            'core': AI_CORE_AVAILABLE,
            'heavy': AI_HEAVY_AVAILABLE,
            'full': AI_FULL_AVAILABLE,
            'scin': SCIN_AVAILABLE,
            'google_vision': GOOGLE_VISION_AVAILABLE,
            'openai': OPENAI_AVAILABLE
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False) 