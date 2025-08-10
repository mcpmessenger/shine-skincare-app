"""
Shine Skincare App - API Gateway Service

Lightweight Flask API service for handling HTTP requests, validation,
and routing to the ML Model Service. Designed for fast startup and
high availability.
"""

from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import requests
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
ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://ml-service:5000')
SERVICE_NAME = 'shine-api-gateway'
VERSION = '1.0.0'

# Health check counter for monitoring
health_check_count = 0

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
    global health_check_count
    health_check_count += 1
    
    return jsonify({
        'status': 'healthy',
        'service': SERVICE_NAME,
        'version': VERSION,
        'timestamp': datetime.utcnow().isoformat(),
        'check_count': health_check_count
    })

@app.route('/ready')
def readiness_check():
    """Service readiness check including ML service dependency"""
    try:
        # Check ML service health
        ml_response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
        ml_healthy = ml_response.status_code == 200
        
        return jsonify({
            'status': 'ready' if ml_healthy else 'degraded',
            'service': SERVICE_NAME,
            'ml_service': 'healthy' if ml_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.warning(f"ML service health check failed: {e}")
        return jsonify({
            'status': 'degraded',
            'service': SERVICE_NAME,
            'ml_service': 'unreachable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/api/v5/skin/analyze', methods=['POST'])
def analyze_skin():
    """Route skin analysis requests to ML service"""
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
        
        # Forward request to ML service
        logger.info(f"Forwarding analysis request to ML service: {ML_SERVICE_URL}")
        
        ml_response = requests.post(
            f"{ML_SERVICE_URL}/analyze",
            files={'image': image_file},
            data=request.form,
            timeout=300  # 5 minute timeout for ML processing
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        if ml_response.status_code == 200:
            result = ml_response.json()
            result['api_gateway_processing_time_ms'] = round(processing_time, 2)
            result['analysis_timestamp'] = datetime.utcnow().isoformat()
            
            logger.info(f"Analysis completed successfully in {processing_time:.2f}ms")
            return jsonify(result)
        else:
            logger.error(f"ML service returned error: {ml_response.status_code}")
            return jsonify({
                'error': 'ML service error',
                'ml_status_code': ml_response.status_code,
                'ml_response': ml_response.text
            }), 503
            
    except requests.exceptions.Timeout:
        logger.error("ML service request timed out")
        return jsonify({
            'error': 'ML service timeout',
            'code': 'ML_TIMEOUT'
        }), 504
        
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to ML service")
        return jsonify({
            'error': 'ML service unavailable',
            'code': 'ML_UNREACHABLE'
        }), 503
        
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {e}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/v5/skin/model-status')
def model_status():
    """Get ML model status from ML service"""
    try:
        ml_response = requests.get(f"{ML_SERVICE_URL}/model/health", timeout=10)
        
        if ml_response.status_code == 200:
            return jsonify(ml_response.json())
        else:
            return jsonify({
                'error': 'ML service error',
                'ml_status_code': ml_response.status_code
            }), 503
            
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        return jsonify({
            'error': 'Cannot reach ML service',
            'code': 'ML_UNREACHABLE'
        }), 503

@app.route('/api/v5/skin/health')
def skin_health():
    """Comprehensive health check for skin analysis service"""
    try:
        # Check ML service health
        ml_response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
        ml_healthy = ml_response.status_code == 200
        
        # Check model status
        model_response = requests.get(f"{ML_SERVICE_URL}/model/health", timeout=10)
        model_ready = model_response.status_code == 200 and model_response.json().get('model_loaded', False)
        
        overall_status = 'healthy' if (ml_healthy and model_ready) else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'service': SERVICE_NAME,
            'ml_service': 'healthy' if ml_healthy else 'unhealthy',
            'model_ready': model_ready,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': SERVICE_NAME,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/status')
def service_status():
    """Comprehensive service status endpoint"""
    return jsonify({
        'service': SERVICE_NAME,
        'version': VERSION,
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'health': '/health',
            'ready': '/ready',
            'skin_analyze': '/api/v5/skin/analyze',
            'model_status': '/api/v5/skin/model-status',
            'skin_health': '/api/v5/skin/health'
        },
        'ml_service_url': ML_SERVICE_URL
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'code': 'NOT_FOUND',
        'available_endpoints': [
            '/health',
            '/ready',
            '/api/v5/skin/analyze',
            '/api/v5/skin/model-status',
            '/api/v5/skin/health',
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
    logger.info(f"ML Service URL: {ML_SERVICE_URL}")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )
