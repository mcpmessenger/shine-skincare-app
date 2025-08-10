"""
Shine Skincare App - ML Model Service

Dedicated TensorFlow inference service for skin analysis.
Pre-embedded model for fast startup and high performance.
"""

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
import json
import numpy as np
from PIL import Image
import io
import base64

# Import our ML model integration
from ml_integration import SkinAnalysisModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
SERVICE_NAME = 'shine-ml-service'
VERSION = '1.0.0'
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/fixed_model_best.h5')

# Global model instance
skin_model = None
model_loaded = False
model_load_time = None

def load_model():
    """Load the ML model on service startup"""
    global skin_model, model_loaded, model_load_time
    
    try:
        logger.info(f"🔄 Loading ML model from: {MODEL_PATH}")
        start_time = time.time()
        
        skin_model = SkinAnalysisModel(MODEL_PATH)
        
        if skin_model.is_ready():
            model_loaded = True
            model_load_time = time.time() - start_time
            logger.info(f"✅ Model loaded successfully in {model_load_time:.2f} seconds")
            return True
        else:
            logger.error("❌ Model failed to load properly")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        return False

@app.before_request
def log_request():
    """Log all incoming requests for monitoring"""
    current_app.logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all responses for monitoring"""
    current_app.logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

@app.route('/health')
def health_check():
    """Basic health check for load balancer and ECS"""
    return jsonify({
        'status': 'healthy',
        'service': SERVICE_NAME,
        'version': VERSION,
        'model_loaded': model_loaded,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/model/health')
def model_health():
    """Detailed model health check"""
    if not model_loaded or skin_model is None:
        return jsonify({
            'status': 'unhealthy',
            'model_loaded': False,
            'error': 'Model not loaded',
            'timestamp': datetime.utcnow().isoformat()
        }), 503
    
    try:
        # Test model with a simple prediction
        test_input = np.random.random((1, 224, 224, 3)).astype(np.float32)
        prediction = skin_model.predict(test_input)
        
        return jsonify({
            'status': 'healthy',
            'model_loaded': True,
            'model_ready': True,
            'model_path': MODEL_PATH,
            'load_time_seconds': model_load_time,
            'test_prediction_shape': prediction.shape if prediction is not None else None,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return jsonify({
            'status': 'degraded',
            'model_loaded': True,
            'model_ready': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/analyze', methods=['POST'])
def analyze_skin():
    """Analyze skin image using the ML model"""
    if not model_loaded:
        return jsonify({
            'error': 'ML model not ready',
            'code': 'MODEL_NOT_READY'
        }), 503
    
    start_time = time.time()
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'code': 'MISSING_IMAGE'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'error': 'No image file selected',
                'code': 'EMPTY_FILENAME'
            }), 400
        
        # Process image
        logger.info(f"Processing image: {image_file.filename}")
        
        # Read and preprocess image
        image_data = image_file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        image_array = np.array(image).astype(np.float32) / 255.0
        
        # Add batch dimension
        image_batch = np.expand_dims(image_array, axis=0)
        
        # Make prediction
        logger.info("Running ML inference...")
        prediction_start = time.time()
        
        result = skin_model.analyze_skin(image_batch)
        
        prediction_time = (time.time() - prediction_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # Add timing information
        result['processing_time_ms'] = round(total_time, 2)
        result['inference_time_ms'] = round(prediction_time, 2)
        result['analysis_timestamp'] = datetime.utcnow().isoformat()
        
        logger.info(f"Analysis completed in {total_time:.2f}ms (inference: {prediction_time:.2f}ms)")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error during skin analysis: {e}")
        return jsonify({
            'error': 'Analysis failed',
            'code': 'ANALYSIS_ERROR',
            'details': str(e)
        }), 500

@app.route('/model/info')
def model_info():
    """Get detailed model information"""
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded',
            'code': 'MODEL_NOT_LOADED'
        }), 503
    
    try:
        info = skin_model.get_model_info()
        info['service'] = SERVICE_NAME
        info['version'] = VERSION
        info['timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({
            'error': 'Failed to get model info',
            'code': 'INFO_ERROR',
            'details': str(e)
        }), 500

@app.route('/status')
def service_status():
    """Comprehensive service status endpoint"""
    return jsonify({
        'service': SERVICE_NAME,
        'version': VERSION,
        'status': 'running',
        'model_loaded': model_loaded,
        'model_path': MODEL_PATH,
        'load_time_seconds': model_load_time,
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/health',
            'model_health': '/model/health',
            'analyze': '/analyze',
            'model_info': '/model/info'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'code': 'NOT_FOUND',
        'available_endpoints': [
            '/health',
            '/model/health',
            '/analyze',
            '/model/info',
            '/status'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} v{VERSION}")
    logger.info(f"Model path: {MODEL_PATH}")
    
    # Load the ML model
    if load_model():
        logger.info("🚀 ML service ready for inference")
    else:
        logger.error("❌ Failed to load ML model - service will not function properly")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
