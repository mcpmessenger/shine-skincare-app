
# Enhanced ML API Integration for Shine Skincare App

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tempfile
import os
import json

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.json_encoder = NumpyEncoder

# Initialize enhanced ML integration
try:
    from ml_api_integration import EnhancedMLIntegration
    ml_integration = EnhancedMLIntegration()
    print("✅ Enhanced ML integration loaded successfully")
except Exception as e:
    print(f"⚠️ Enhanced ML integration failed to load: {e}")
    ml_integration = None

@app.route('/api/v4/skin/analyze-enhanced', methods=['POST'])
def analyze_skin_enhanced():
    """Enhanced skin analysis endpoint"""
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
            # Analyze the image
            if ml_integration and ml_integration.enhanced_model:
                # Read the image file as bytes
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                result = ml_integration.analyze_skin_enhanced(image_bytes)
            else:
                # Use fallback analysis
                try:
                    from real_skin_analysis import RealSkinAnalysis
                    analyzer = RealSkinAnalysis()
                    result = analyzer.analyze_skin(image_path)
                    result['model_type'] = 'fallback'
                except Exception as e:
                    return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
            
            # Clean up temporary file
            if os.path.exists(image_path):
                os.unlink(image_path)
            
            return jsonify(result)
            
        except Exception as e:
            # Clean up temporary file on error
            if 'image_path' in locals() and os.path.exists(image_path):
                os.unlink(image_path)
            raise e
            
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

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

@app.route('/api/v4/system/enhanced-status', methods=['GET'])
def get_enhanced_status():
    """Get enhanced ML system status"""
    try:
        if ml_integration:
            return jsonify({
                'status': 'available',
                'model_loaded': ml_integration.enhanced_model is not None,
                'message': 'Enhanced ML model is ready'
            })
        else:
            return jsonify({
                'status': 'unavailable',
                'model_loaded': False,
                'message': 'Enhanced ML model not loaded'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'model_loaded': False,
            'message': f'Error checking status: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced API Server...")
    print("📡 Available endpoints:")
    print("   - POST /api/v4/skin/analyze-enhanced")
    print("   - POST /api/v4/face/detect")
    print("   - GET  /api/v4/system/enhanced-status")
    app.run(host='0.0.0.0', port=5000, debug=True)
