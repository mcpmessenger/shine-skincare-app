"""
Shine Skincare App - Simplified EB Application
Combines basic Flask app with simplified ML service functionality
Deploy to Elastic Beanstalk for fast, reliable deployment
"""

from flask import Flask, request, jsonify
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

# Create Flask app
application = Flask(__name__)
CORS(application)

# Configuration
SERVICE_NAME = 'shine-backend-simplified'
VERSION = '1.0.0-eb'
MODEL_PATH = os.getenv('MODEL_PATH', '/opt/python/current/app/models/fixed_model_best.h5')

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

@application.before_request
def log_request():
    """Log all incoming requests for monitoring"""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

@application.after_request
def log_response(response):
    """Log all responses for monitoring"""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

@application.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Shine Backend is running!",
        "service": SERVICE_NAME,
        "status": "ok",
        "version": VERSION,
        "mode": "simplified"
    })

@application.route('/health')
def health():
    """Basic health check for EB"""
    return jsonify({
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
        "mode": "simplified"
    })

@application.route('/api/health')
def api_health():
    """API health check"""
    return jsonify({
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
        "mode": "simplified"
    })

@application.route('/ready')
def readiness_check():
    """Service readiness check including ML service dependency"""
    try:
        # For now, just return ready since we're a simplified service
        return jsonify({
            'status': 'ready',
            'service': SERVICE_NAME,
            'ml_service': 'simplified_mode',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        return jsonify({
            'status': 'degraded',
            'service': SERVICE_NAME,
            'ml_service': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@application.route('/ml/health')
def ml_health():
    """ML service health check - simplified version"""
    return jsonify({
        'status': 'healthy',
        'model_status': model_status,
        'service_mode': 'simplified',
        'timestamp': datetime.utcnow().isoformat()
    })

@application.route('/ml/analyze', methods=['POST'])
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

@application.route('/status')
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

@application.route('/api/v5/skin/analyze', methods=['POST'])
def analyze_skin_v5():
    """V5 skin analysis endpoint - simplified version"""
    return analyze_skin()

@application.route('/api/v5/skin/health')
def skin_health_v5():
    """V5 skin health endpoint - simplified version"""
    return ml_health()

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} v{VERSION}")
    logger.info(f"Model path: {MODEL_PATH}")
    
    # Load the model (simplified version)
    if load_model():
        logger.info("🚀 Simplified ML service ready")
    else:
        logger.warning("⚠️ Simplified ML service ready (with warnings)")
    
    application.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
