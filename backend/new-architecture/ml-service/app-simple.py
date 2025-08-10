"""
Shine Skincare App - ML Model Service (SIMPLIFIED VERSION)
Basic service to get things running first, then add ML later
"""

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
SERVICE_NAME = 'shine-ml-service-simple'
VERSION = '1.0.0-simple'
MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/fixed_model_best.h5')

# Global status
service_ready = True
model_status = "simplified_mode"

def load_model():
    """Simplified model loading - just check if file exists"""
    global service_ready, model_status
    
    try:
        logger.info(f"🔄 Checking model path: {MODEL_PATH}")
        
        # Just check if the file exists for now
        if os.path.exists(MODEL_PATH):
            model_status = "model_file_exists"
            logger.info(f"✅ Model file found at: {MODEL_PATH}")
            return True
        else:
            model_status = "model_file_missing"
            logger.warning(f"⚠️ Model file not found at: {MODEL_PATH}")
            # Don't fail the service - just log warning
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking model: {e}")
        model_status = "error_checking_model"
        # Don't fail the service - just log error
        return True

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
    """Basic health check - always returns healthy"""
    return jsonify({
        'status': 'healthy',
        'service': SERVICE_NAME,
        'version': VERSION,
        'model_status': model_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/model/health')
def model_health():
    """Model health check - simplified version"""
    return jsonify({
        'status': 'healthy',
        'model_status': model_status,
        'service_mode': 'simplified',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze_skin():
    """Simplified skin analysis - returns mock response for now"""
    try:
        # Check if image was provided
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'code': 'MISSING_IMAGE'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'error': 'No image file selected',
                'code': 'NO_FILE_SELECTED'
            }), 400
        
        # For now, just return a success response
        return jsonify({
            'status': 'success',
            'message': 'Image received successfully (simplified mode)',
            'service': SERVICE_NAME,
            'mode': 'simplified',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in simplified analysis: {e}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/status')
def service_status():
    """Service status endpoint"""
    return jsonify({
        'service': SERVICE_NAME,
        'version': VERSION,
        'status': 'running',
        'mode': 'simplified',
        'model_status': model_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'service': SERVICE_NAME,
        'version': VERSION,
        'status': 'running',
        'message': 'Simplified ML Service - Basic functionality only'
    })

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} v{VERSION}")
    logger.info(f"Model path: {MODEL_PATH}")
    
    # Load the model (simplified version)
    if load_model():
        logger.info("🚀 Simplified ML service ready")
    else:
        logger.warning("⚠️ Simplified ML service ready (with warnings)")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
