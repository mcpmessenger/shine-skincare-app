#!/usr/bin/env python3
"""
Run Fixed Model Server for Shine Skincare App
Starts the Flask server with the improved ML model
"""
import os
import sys
import cv2
import base64
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from simple_fixed_integration import SimpleFixedModelIntegration
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Initialize the fixed model integration
    fixed_integration = SimpleFixedModelIntegration()
    
    @app.route('/api/v5/skin/analyze-fixed', methods=['POST'])
    def analyze_skin_fixed():
        """Analyze skin using the fixed model"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': 'No image provided'}), 400
            
            image_file = request.files['image']
            image_data = image_file.read()
            
            # Get optional user demographics
            user_demographics = request.form.get('demographics')
            if user_demographics:
                try:
                    import json
                    user_demographics = json.loads(user_demographics)
                except:
                    user_demographics = None
            
            # Analyze with fixed model
            results = fixed_integration.analyze_skin_with_fixed_model(image_data, user_demographics)
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"❌ API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v4/face/detect', methods=['POST'])
    def detect_face():
        """Face detection endpoint"""
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
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    file.save(tmp_file.name)
                    image_path = tmp_file.name
            else:
                # JSON format (from frontend)
                data = request.get_json()
                if not data or 'image_data' not in data:
                    return jsonify({'error': 'No image data provided'}), 400
                
                # Decode base64 image
                try:
                    image_data = data['image_data']
                    image_bytes = base64.b64decode(image_data)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(image_bytes)
                        image_path = tmp_file.name
                except Exception as e:
                    return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
            
            try:
                # Load image and detect faces
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
                if 'image_path' in locals() and os.path.exists(image_path):
                    os.unlink(image_path)
                raise e
                
        except Exception as e:
            return jsonify({'error': f'Face detection failed: {str(e)}'}), 500
    
    @app.route('/api/v5/skin/model-status', methods=['GET'])
    def get_fixed_model_status():
        """Get fixed model status"""
        try:
            status = fixed_integration.get_model_status()
            return jsonify(status)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/v5/skin/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'model_loaded': fixed_integration.fixed_model is not None,
            'timestamp': datetime.now().isoformat(),
            'message': 'Fixed ML model server is running!'
        })
    
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'Shine Skincare App - Fixed ML Model Server',
            'version': 'v5.0',
            'endpoints': [
                'POST /api/v5/skin/analyze-fixed',
                'POST /api/v4/face/detect',
                'GET /api/v5/skin/model-status', 
                'GET /api/v5/skin/health'
            ]
        })
    
    if __name__ == "__main__":
        logger.info("🚀 Starting Fixed Model Server...")
        logger.info("📊 Model loaded: %s", fixed_integration.fixed_model is not None)
        logger.info("🌐 Server will be available at: http://localhost:5000")
        logger.info("📋 Available endpoints:")
        logger.info("   - POST /api/v5/skin/analyze-fixed")
        logger.info("   - POST /api/v4/face/detect")
        logger.info("   - GET /api/v5/skin/model-status")
        logger.info("   - GET /api/v5/skin/health")
        
        app.run(host='0.0.0.0', port=5000, debug=False)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip install flask flask-cors opencv-python")
except Exception as e:
    print(f"❌ Server startup error: {e}")
