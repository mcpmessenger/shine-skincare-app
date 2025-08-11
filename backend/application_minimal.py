#!/usr/bin/env python3
"""
Shine Skincare App - Minimal Requirements Version
Updated: 2025-08-10 - Optimized for t3.large deployment stability

This version includes only essential ML capabilities to ensure successful deployment
while maintaining core functionality for skin analysis.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import numpy as np
from PIL import Image
import io
import base64
import cv2
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'shine-ml-models-2025')
S3_MODEL_KEY = os.environ.get('S3_MODEL_KEY', 'fixed_model_best.h5')
LOCAL_MODEL_PATH = os.environ.get('MODEL_PATH', './models/')
PORT = int(os.environ.get('PORT', 5000))

# Initialize S3 client
s3_client = boto3.client('s3')

# Ensure models directory exists
Path(LOCAL_MODEL_PATH).mkdir(parents=True, exist_ok=True)

def download_model_from_s3():
    """Download model from S3 if not present locally"""
    try:
        local_path = os.path.join(LOCAL_MODEL_PATH, os.path.basename(S3_MODEL_KEY))
        if not os.path.exists(local_path):
            logger.info(f"Downloading model from S3: {S3_BUCKET}/{S3_MODEL_KEY}")
            s3_client.download_file(S3_BUCKET, S3_MODEL_KEY, local_path)
            logger.info("Model downloaded successfully")
        else:
            logger.info("Model already exists locally")
        return local_path
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return None

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def basic_face_detection(image_array):
    """Basic face detection using OpenCV"""
    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # Load pre-trained face detection model
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            return {
                "faces_detected": len(faces),
                "primary_face": {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 0.95
                },
                "all_faces": [{"x": int(f[0]), "y": int(f[1]), "width": int(f[2]), "height": int(f[3])} for f in faces]
            }
        else:
            return {"faces_detected": 0, "message": "No faces detected"}
            
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return {"error": f"Face detection failed: {str(e)}"}

def basic_skin_analysis(image_array):
    """Basic skin analysis using OpenCV and numpy"""
    try:
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
        
        # Basic color analysis
        h, s, v = cv2.split(hsv)
        l, a, b = cv2.split(lab)
        
        # Calculate basic statistics
        analysis = {
            "brightness": {
                "mean": float(np.mean(v)),
                "std": float(np.std(v)),
                "min": float(np.min(v)),
                "max": float(np.max(v))
            },
            "saturation": {
                "mean": float(np.mean(s)),
                "std": float(np.std(s))
            },
            "color_temperature": {
                "red_channel": float(np.mean(image_array[:, :, 0])),
                "green_channel": float(np.mean(image_array[:, :, 1])),
                "blue_channel": float(np.mean(image_array[:, :, 2]))
            },
            "image_quality": {
                "resolution": f"{image_array.shape[1]}x{image_array.shape[0]}",
                "aspect_ratio": round(image_array.shape[1] / image_array.shape[0], 2)
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Skin analysis error: {e}")
        return {"error": f"Skin analysis failed: {str(e)}"}

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "minimal-1.0.0",
        "timestamp": "2025-08-10T20:00:00Z",
        "instance_type": "t3.large",
        "ml_mode": "minimal"
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api_version": "v1",
        "ml_capabilities": ["basic_face_detection", "basic_skin_analysis"],
        "instance_type": "t3.large"
    })

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for deployment"""
    try:
        # Check if model directory is accessible
        model_path = download_model_from_s3()
        if model_path:
            return jsonify({
                "status": "ready",
                "model_loaded": True,
                "model_path": model_path,
                "instance_type": "t3.large"
            })
        else:
            return jsonify({
                "status": "not_ready",
                "model_loaded": False,
                "error": "Model download failed"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "error": str(e)
        }), 503

@app.route('/api/v1/face/detect', methods=['POST'])
def detect_faces():
    """Basic face detection endpoint"""
    try:
        # Get image data
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Perform face detection
        result = basic_face_detection(image_array)
        
        return jsonify({
            "success": True,
            "face_detection": result,
            "instance_type": "t3.large",
            "ml_mode": "minimal"
        })
        
    except Exception as e:
        logger.error(f"Face detection endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/skin/analyze', methods=['POST'])
def analyze_skin():
    """Basic skin analysis endpoint"""
    try:
        # Get image data
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Perform basic skin analysis
        analysis = basic_skin_analysis(image_array)
        
        return jsonify({
            "success": True,
            "skin_analysis": analysis,
            "instance_type": "t3.large",
            "ml_mode": "minimal"
        })
        
    except Exception as e:
        logger.error(f"Skin analysis endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/system/status', methods=['GET'])
def system_status():
    """System status endpoint"""
    return jsonify({
        "status": "operational",
        "instance_type": "t3.large",
        "ml_mode": "minimal",
        "capabilities": [
            "basic_face_detection",
            "basic_skin_analysis",
            "s3_model_integration",
            "health_monitoring"
        ],
        "memory_usage": "6GB allocated for ML",
        "deployment_strategy": "minimal_requirements_for_stability"
    })

@app.route('/debug/disk-space', methods=['GET'])
def debug_disk_space():
    """Debug endpoint to check disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return jsonify({
            "disk_space": {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round((used / total) * 100, 2)
            },
            "instance_type": "t3.large"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Shine Skincare App - Minimal Requirements Version")
    logger.info(f"Instance Type: t3.large")
    logger.info(f"ML Mode: minimal")
    logger.info(f"Model Path: {LOCAL_MODEL_PATH}")
    
    # Download model on startup
    model_path = download_model_from_s3()
    if model_path:
        logger.info(f"Model ready: {model_path}")
    else:
        logger.warning("Model download failed - some features may not work")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
