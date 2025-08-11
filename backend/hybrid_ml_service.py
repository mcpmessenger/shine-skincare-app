#!/usr/bin/env python3
"""
Hybrid ML Service for Shine Skincare App
Progressive service that starts simple and adds ML capabilities
"""
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global variables for ML capabilities
ml_model_loaded = False
ml_dependencies_available = False
ml_service_status = "initializing"

def check_ml_dependencies():
    """Check if ML dependencies are available"""
    global ml_dependencies_available
    
    try:
        # Try to import basic ML libraries
        import numpy as np
        import cv2
        logger.info("✅ Basic ML dependencies available")
        
        # Try to import TensorFlow (heaviest dependency)
        try:
            import tensorflow as tf
            logger.info("✅ TensorFlow available")
            ml_dependencies_available = True
            return True
        except ImportError as e:
            logger.warning(f"⚠️ TensorFlow not available: {e}")
            ml_dependencies_available = False
            return False
            
    except ImportError as e:
        logger.warning(f"⚠️ Basic ML dependencies not available: {e}")
        ml_dependencies_available = False
        return False

def load_ml_model():
    """Attempt to load the ML model"""
    global ml_model_loaded, ml_service_status
    
    if not ml_dependencies_available:
        ml_service_status = "dependencies_missing"
        return False
    
    try:
        # Try to import the ML integration
        from simple_fixed_integration import SimpleFixedModelIntegration
        
        # Initialize the ML service
        ml_integration = SimpleFixedModelIntegration()
        
        if ml_integration.fixed_model is not None:
            ml_model_loaded = True
            ml_service_status = "ml_ready"
            logger.info("✅ ML model loaded successfully")
            return True
        else:
            ml_service_status = "model_failed"
            logger.error("❌ ML model failed to load")
            return False
            
    except Exception as e:
        ml_service_status = "ml_error"
        logger.error(f"❌ ML service error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service status"""
    return jsonify({
        'message': 'Shine Skincare App - Hybrid ML Service',
        'version': 'v5.0-hybrid',
        'status': 'healthy',
        'ml_status': ml_service_status,
        'ml_model_loaded': ml_model_loaded,
        'ml_dependencies': ml_dependencies_available,
        'endpoints': [
            'GET /',
            'GET /health',
            'GET /ml/status',
            'POST /api/v5/skin/analyze-fixed (if ML ready)',
            'POST /api/v4/face/detect (if ML ready)'
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ml_status': ml_service_status,
        'message': 'Hybrid ML service is running!'
    })

@app.route('/ml/status', methods=['GET'])
def ml_status():
    """Detailed ML service status"""
    return jsonify({
        'service_status': ml_service_status,
        'ml_model_loaded': ml_model_loaded,
        'ml_dependencies_available': ml_dependencies_available,
        'capabilities': {
            'basic_health': True,
            'ml_inference': ml_model_loaded,
            'face_detection': ml_dependencies_available,
            'skin_analysis': ml_model_loaded
        }
    })

@app.route('/api/v5/skin/analyze-fixed', methods=['POST'])
def analyze_skin_fixed():
    """Skin analysis endpoint with fallback"""
    if not ml_model_loaded:
        return jsonify({
            'error': 'ML service not ready',
            'status': ml_service_status,
            'message': 'Service is starting up or ML dependencies are missing'
        }), 503
    
    try:
        # Import and use ML service
        from simple_fixed_integration import SimpleFixedModelIntegration
        ml_integration = SimpleFixedModelIntegration()
        
        # Handle request (same as original)
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            image_file = request.files['image']
            image_data = image_file.read()
            
            user_demographics = request.form.get('demographics')
            if user_demographics:
                try:
                    import json
                    user_demographics = json.loads(user_demographics)
                except:
                    user_demographics = None
        else:
            data = request.get_json()
            if not data or 'image_data' not in data:
                return jsonify({'error': 'No image data provided'}), 400
            
            try:
                image_data_b64 = data['image_data']
                import base64
                image_data = base64.b64decode(image_data_b64)
            except Exception as e:
                return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
            
            user_demographics = data.get('user_demographics')
        
        # Analyze with ML model
        results = ml_integration.analyze_skin_with_fixed_model(image_data, user_demographics)
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Skin analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v4/face/detect', methods=['POST'])
def detect_face():
    """Face detection endpoint with fallback"""
    if not ml_dependencies_available:
        return jsonify({
            'error': 'Face detection not available',
            'status': ml_service_status,
            'message': 'OpenCV dependencies are missing'
        }), 503
    
    try:
        import cv2
        import numpy as np
        import tempfile
        
        # Handle request
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No image selected'}), 400
            
            # Save uploaded image temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                file.save(tmp_file.name)
                image_path = tmp_file.name
        else:
            data = request.get_json()
            if not data or 'image_data' not in data:
                return jsonify({'error': 'No image data provided'}), 400
            
            # Decode base64 image
            try:
                image_data_b64 = data['image_data']
                import base64
                image_data = base64.b64decode(image_data_b64)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(image_data)
                    image_path = tmp_file.name
            except Exception as e:
                return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        try:
            # Load image and detect faces
            image = cv2.imread(image_path)
            if image is None:
                return jsonify({'error': 'Failed to load image'}), 400
            
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
                faces_data = []
                for (x, y, w, h) in faces:
                    faces_data.append({
                        'bounds': {
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h)
                        },
                        'confidence': 0.95
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
            if 'image_path' in locals() and os.path.exists(image_path):
                os.unlink(image_path)
            raise e
            
    except Exception as e:
        return jsonify({'error': f'Face detection failed: {str(e)}'}), 500

if __name__ == "__main__":
    logger.info("🚀 Starting Hybrid ML Service...")
    
    # Check ML dependencies
    logger.info("🔍 Checking ML dependencies...")
    check_ml_dependencies()
    
    # Try to load ML model
    if ml_dependencies_available:
        logger.info("📊 Attempting to load ML model...")
        load_ml_model()
    else:
        logger.info("⚠️ ML dependencies not available - running in basic mode")
    
    # Log final status
    logger.info(f"📊 Final ML status: {ml_service_status}")
    logger.info(f"🌐 Server will be available at: http://0.0.0.0:5000")
    logger.info(f"🔍 Service endpoints:")
    logger.info(f"   - GET / (status)")
    logger.info(f"   - GET /health (health check)")
    logger.info(f"   - GET /ml/status (ML status)")
    if ml_model_loaded:
        logger.info(f"   - POST /api/v5/skin/analyze-fixed (skin analysis)")
        logger.info(f"   - POST /api/v4/face/detect (face detection)")
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=False)
