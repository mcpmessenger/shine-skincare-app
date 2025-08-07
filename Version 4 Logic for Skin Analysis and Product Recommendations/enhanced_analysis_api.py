#!/usr/bin/env python3
""" Enhanced Analysis API for Shine Skincare App
Provides normalized skin analysis using healthy baselines and condition matching
"""

import os
import json
import logging
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback

# Import our integrated analysis system
from integrated_skin_analysis import IntegratedSkinAnalysis

# Import enhanced face detection
from enhanced_face_detection_fixed import enhanced_face_detector as robust_face_detector
# Import enhanced image processing
from enhanced_image_processing import enhanced_face_detect_endpoint

# Import enhanced systems
from enhanced_severity_scoring import enhanced_severity_scorer
from enhanced_recommendation_engine import enhanced_recommendation_engine
from real_skin_analysis import RealSkinAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to Python types for JSON serialization"""
    try:
        # Handle numpy arrays and scalars
        if hasattr(obj, 'dtype'):
            if obj.dtype.kind == 'i':  # integer types
                return int(obj)
            elif obj.dtype.kind == 'f':  # float types
                return float(obj)
            elif obj.dtype.kind == 'b':  # boolean types
                return bool(obj)
            elif obj.dtype.kind == 'U':  # unicode string types
                return str(obj)
            else:
                return obj.tolist()
        # Handle specific numpy scalar types
        elif isinstance(obj, (np.integer, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Handle nested structures
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(element) for element in obj]
        else:
            return obj
    except Exception as e:
        logger.error(f"Error converting numpy type: {e}")
        return str(obj) # Fallback to string representation

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Initialize the integrated skin analysis system
integrated_analysis = IntegratedSkinAnalysis()

@app.route('/api/v3/skin/analyze-real', methods=['POST'])
def analyze_skin_real():
    logger.info("Received request for /api/v3/skin/analyze-real")
    if 'image' not in request.json:
        logger.error("No image provided in request")
        return jsonify({"status": "error", "message": "No image provided"}), 400

    image_data = request.json['image']
    age = request.json.get('age')
    ethnicity = request.json.get('ethnicity')
    gender = request.json.get('gender')

    try:
        # Decode the image
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Failed to decode image")
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400

        logger.info(f"Image decoded successfully. Shape: {img.shape}")

        # Perform integrated analysis
        analysis_results = integrated_analysis.perform_analysis(
            img, age=age, ethnicity=ethnicity, gender=gender
        )

        # Convert numpy types for JSON serialization
        json_compatible_results = json.loads(json.dumps(analysis_results, default=convert_numpy_types))

        logger.info("Analysis complete. Returning results.")
        return jsonify({"status": "success", "data": json_compatible_results})

    except Exception as e:
        logger.error(f"Error during skin analysis: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/face/detect', methods=['POST'])
def detect_face_endpoint():
    logger.info("Received request for /api/v3/face/detect")
    if 'image' not in request.json:
        logger.error("No image provided for face detection")
        return jsonify({"status": "error", "message": "No image provided"}), 400

    image_data = request.json['image']

    try:
        # Decode the image
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Failed to decode image for face detection")
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400

        logger.info(f"Image decoded successfully for face detection. Shape: {img.shape}")

        # Perform face detection using the robust detector
        faces = robust_face_detector(img)

        # Convert numpy types for JSON serialization
        json_compatible_faces = json.loads(json.dumps(faces, default=convert_numpy_types))

        logger.info(f"Face detection complete. Found {len(faces)} faces.")
        return jsonify({"status": "success", "faces": json_compatible_faces})

    except Exception as e:
        logger.error(f"Error during face detection: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    logger.info("Received request for /api/v2/analyze/guest")
    if 'image' not in request.json:
        logger.error("No image provided for guest analysis")
        return jsonify({"status": "error", "message": "No image provided"}), 400

    image_data = request.json['image']
    age = request.json.get('age')
    ethnicity = request.json.get('ethnicity')
    gender = request.json.get('gender')

    try:
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Failed to decode image for guest analysis")
            return jsonify({"status": "error", "message": "Failed to decode image"}), 400

        logger.info(f"Image decoded successfully for guest analysis. Shape: {img.shape}")

        # Perform integrated analysis for guest users
        analysis_results = integrated_analysis.perform_analysis(
            img, age=age, ethnicity=ethnicity, gender=gender
        )

        json_compatible_results = json.loads(json.dumps(analysis_results, default=convert_numpy_types))

        logger.info("Guest analysis complete. Returning results.")
        return jsonify({"status": "success", "data": json_compatible_results})

    except Exception as e:
        logger.error(f"Error during guest analysis: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ai/search', methods=['POST'])
def ai_search():
    logger.info("Received request for /api/ai/search")
    data = request.json
    query_embedding = data.get('query_embedding')
    top_k = data.get('top_k', 5)

    if not query_embedding:
        logger.error("No query embedding provided for AI search")
        return jsonify({"status": "error", "message": "No query embedding provided"}), 400

    try:
        # Assuming RealSkinAnalysis has a method for similarity search
        search_results = integrated_analysis.perform_similarity_search(query_embedding, top_k)
        json_compatible_results = json.loads(json.dumps(search_results, default=convert_numpy_types))
        logger.info("AI search complete. Returning results.")
        return jsonify({"status": "success", "results": json_compatible_results})
    except Exception as e:
        logger.error(f"Error during AI search: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/recommendations/trending', methods=['GET'])
def get_trending_recommendations():
    logger.info("Received request for /api/recommendations/trending")
    try:
        trending_products = enhanced_recommendation_engine.get_trending_products()
        json_compatible_products = json.loads(json.dumps(trending_products, default=convert_numpy_types))
        logger.info("Trending recommendations complete. Returning results.")
        return jsonify({"status": "success", "products": json_compatible_products})
    except Exception as e:
        logger.error(f"Error getting trending recommendations: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Received request for /health")
    try:
        # Basic health check: check if integrated_analysis is initialized
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "integrated_analysis_initialized": integrated_analysis is not None
        }
        logger.info("Health check successful.")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check failed: {e}\n{traceback.format_exc()}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health_check():
    logger.info("Received request for /api/health")
    try:
        # More detailed API health check, potentially checking dependencies
        api_status = {
            "api_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "face_detection_module": "ok" if robust_face_detector else "not_loaded",
            "image_processing_module": "ok" if enhanced_face_detect_endpoint else "not_loaded",
            "recommendation_engine": "ok" if enhanced_recommendation_engine else "not_loaded",
            "real_skin_analysis_module": "ok" if RealSkinAnalysis else "not_loaded",
            "integrated_analysis_system": "ok" if integrated_analysis else "not_loaded"
        }
        logger.info("API health check successful.")
        return jsonify(api_status)
    except Exception as e:
        logger.error(f"API health check failed: {e}\n{traceback.format_exc()}")
        return jsonify({"api_status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


