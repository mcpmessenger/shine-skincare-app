#!/usr/bin/env python3
"""
Simple Flask Server for Face Detection
Fixes the 500 error on face detection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import base64
import logging
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the skin analyzer
skin_analyzer = EnhancedSkinAnalyzer()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Simple Flask server is running',
        'face_detection_available': True
    })

@app.route('/api/v3/face/detect', methods=['POST'])
def detect_face():
    """Face detection endpoint"""
    try:
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({
                'error': 'Missing image_data',
                'fallback_available': True
            }), 400
        
        # Decode base64 image
        image_data = data['image_data']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_array = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
        
        # Convert to BGR for OpenCV
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Perform face detection
        logger.info("🔍 Starting face detection...")
        face_analysis = skin_analyzer.analyze_face_detection(image_array_bgr)
        logger.info(f"✅ Face detection completed: {face_analysis.get('face_detected')}")
        
        return jsonify(face_analysis)
        
    except Exception as e:
        logger.error(f"❌ Face detection error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'fallback_available': True,
            'details': str(e)
        }), 500

@app.route('/api/v3/skin/analyze-enhanced-embeddings', methods=['POST'])
def analyze_skin_enhanced():
    """Enhanced skin analysis endpoint"""
    try:
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({
                'error': 'Missing image_data',
                'fallback_available': True
            }), 400
        
        # Decode base64 image
        image_data = data['image_data']
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_array = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
        
        # Convert to BGR for OpenCV
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Perform face detection
        logger.info("🔍 Starting face detection...")
        face_analysis = skin_analyzer.analyze_face_detection(image_array_bgr)
        logger.info(f"✅ Face detection completed: {face_analysis.get('face_detected')}")
        
        # Get face ROI if detected
        face_roi = None
        if face_analysis.get('face_detected'):
            face_bounds = face_analysis.get('face_bounds', {})
            x, y, w, h = face_bounds.get('x', 0), face_bounds.get('y', 0), face_bounds.get('width', 0), face_bounds.get('height', 0)
            if w > 0 and h > 0:
                face_roi = image_array_bgr[y:y+h, x:x+w]
        
        # Perform skin analysis
        logger.info("🔍 Starting skin conditions analysis...")
        skin_analysis = skin_analyzer.analyze_skin_conditions(image_array_bgr, face_roi)
        logger.info(f"✅ Skin analysis completed: health_score={skin_analysis.get('health_score', 0)}")
        
        # Compile results
        result = {
            'status': 'success',
            'face_detection': face_analysis,
            'skin_conditions': skin_analysis,
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Skin analysis error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'fallback_available': True,
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Flask Server...")
    print("📍 Server will run on http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False) 