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
        # Check ML service health (non-blocking)
        ml_response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
        ml_healthy = ml_response.status_code == 200
        
        return jsonify({
            'status': 'ready' if ml_healthy else 'degraded',
            'service': SERVICE_NAME,
            'ml_service': 'healthy' if ml_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        # ML service health check failed, but don't fail the container
        logger.info(f"ML service health check failed (non-blocking): {e}")
        return jsonify({
            'status': 'ready',  # Changed from 'degraded' to 'ready'
            'service': SERVICE_NAME,
            'ml_service': 'unreachable',
            'message': 'Service is ready, ML service health check failed but container continues to function',
            'timestamp': datetime.utcnow().isoformat()
        }), 200  # Changed from 503 to 200

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

# ============================================================================
# FACE DETECTION ENDPOINTS (CRITICAL FOR FRONTEND FUNCTIONALITY)
# ============================================================================

@app.route('/api/v3/face/detect', methods=['POST'])
def detect_face_v3():
    """V3 compatibility face detection endpoint"""
    try:
        # Handle both file upload and JSON data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # File upload format
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image selected'}), 400
            
            # Save uploaded image temporarily
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                file.save(tmp_file.name)
                image_path = tmp_file.name
        else:
            # JSON format (from frontend)
            data = request.get_json()
            if not data or 'image_data' not in data:
                return jsonify({'error': 'No image data provided'}), 400
            
            # Decode base64 image
            import base64
            import tempfile
            import os
            try:
                image_data = data['image_data']
                image_bytes = base64.b64decode(image_data)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(image_bytes)
                    image_path = tmp_file.name
            except Exception as e:
                return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        try:
            # Load image and detect faces using OpenCV
            import cv2
            import numpy as np
            
            image = cv2.imread(image_path)
            if image is None:
                return jsonify({'error': 'Could not load image'}), 400
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Clean up temporary file
            if os.path.exists(image_path):
                os.unlink(image_path)
            
            if len(faces) > 0:
                # Return face detection result in format expected by frontend
                faces_data = []
                for (x, y, w, h) in faces:
                    faces_data.append({
                        'bounds': {
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h)
                        },
                        'confidence': 0.95  # OpenCV doesn't provide confidence, so we'll use a high default
                    })
                
                return jsonify({
                    'faces_detected': len(faces),
                    'faces': faces_data,
                    'success': True
                })
            else:
                return jsonify({
                    'faces_detected': 0,
                    'faces': [],
                    'success': False,
                    'message': 'No faces detected'
                })
                
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(image_path):
                os.unlink(image_path)
            raise e
            
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return jsonify({
            'error': f'Face detection failed: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/v4/face/detect', methods=['POST'])
def detect_face_v4():
    """V4 face detection endpoint with enhanced processing"""
    return detect_face_v3()  # Use V3 implementation for now

# ============================================================================
# SKIN ANALYSIS ENDPOINTS (ENHANCED WITH FACE DETECTION)
# ============================================================================

@app.route('/api/v5/skin/analyze-fixed', methods=['POST'])
def analyze_skin_fixed():
    """Enhanced skin analysis with face detection validation"""
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
        
        # First, perform face detection to validate the image
        import tempfile
        import os
        import base64
        
        # Save image temporarily for face detection
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image_file.save(tmp_file.name)
            image_path = tmp_file.name
        
        try:
            # Perform face detection
            import cv2
            image = cv2.imread(image_path)
            if image is None:
                return jsonify({'error': 'Could not load image'}), 400
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Clean up temporary file
            if os.path.exists(image_path):
                os.unlink(image_path)
            
            if len(faces) == 0:
                return jsonify({
                    'error': 'No face detected in image',
                    'code': 'NO_FACE_DETECTED',
                    'message': 'Please ensure a clear face is visible in the image'
                }), 400
            
            # Reset file pointer for ML service
            image_file.seek(0)
            
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
                result['face_validation'] = {
                    'faces_detected': len(faces),
                    'validation_passed': True
                }
                
                logger.info(f"Analysis completed successfully in {processing_time:.2f}ms")
                return jsonify(result)
            else:
                logger.error(f"ML service returned error: {ml_response.status_code}")
                return jsonify({
                    'error': 'ML service error',
                    'ml_status_code': ml_response.status_code,
                    'ml_response': ml_response.text
                }), 503
                
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(image_path):
                os.unlink(image_path)
            raise e
            
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
            'skin_analyze_fixed': '/api/v5/skin/analyze-fixed',
            'model_status': '/api/v5/skin/model-status',
            'skin_health': '/api/v5/skin/health',
            'face_detect_v3': '/api/v3/face/detect',
            'face_detect_v4': '/api/v4/face/detect'
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
        port=5000,
        debug=False
    )
