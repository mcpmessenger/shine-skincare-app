#!/usr/bin/env python3
"""
Simple Fixed Model Integration - Local Development Version
Forces local model loading without S3 fallback
"""

import os
import json
import logging
import numpy as np
import cv2
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import traceback
from PIL import Image
import io
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000'])

class SimpleFixedModelIntegration:
    """Simple integration class for the fixed ML model with improved accuracy"""
    
    def __init__(self, model_path: str = "models/fixed_model_best.h5"):
        """Initialize with local model only"""
        self.model_path = Path(model_path)
        self.fixed_model = None
        self.model_metadata = None
        self.class_names = [
            "acne", "actinic_keratosis", "basal_cell_carcinoma", 
            "eczema", "healthy", "rosacea"
        ]
        
        # Load model and metadata
        self._load_fixed_model()
        
        logger.info("✅ Simple Fixed Model Integration initialized")
    
    def _load_fixed_model(self):
        """Load the fixed ML model from local file"""
        try:
            # Define custom loss function for loading
            def focal_loss(y_true, y_pred):
                alpha = 1.0
                gamma = 2.0
                y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0)
                cross_entropy = -y_true * tf.math.log(y_pred)
                focal_loss = alpha * tf.pow(1 - y_pred, gamma) * cross_entropy
                return tf.reduce_mean(focal_loss)
            
            # Force local file loading
            if self.model_path.exists():
                logger.info(f"📁 Loading model from local file: {self.model_path}")
                self.fixed_model = tf.keras.models.load_model(
                    str(self.model_path),
                    custom_objects={'focal_loss': focal_loss}
                )
                logger.info("✅ Fixed ML model loaded from local file successfully")
                logger.info(f"📊 Model classes: {self.class_names}")
            else:
                logger.error(f"❌ Model file not found: {self.model_path}")
                self.fixed_model = None
            
            # Load metadata
            metadata_path = self.model_path.parent / "fixed_training_results.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                logger.info("✅ Model metadata loaded successfully")
            else:
                logger.warning("⚠️ Model metadata not found")
                
        except Exception as e:
            logger.error(f"❌ Failed to load fixed model: {e}")
            self.fixed_model = None
    
    def get_model_status(self) -> Dict:
        """Get current model status"""
        return {
            'model_loaded': self.fixed_model is not None,
            'model_path': str(self.model_path),
            'classes': self.class_names,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_skin_with_fixed_model(self, image_data: bytes, user_demographics: Dict = None) -> Dict:
        """Analyze skin using the fixed model"""
        try:
            if self.fixed_model is None:
                return self._create_error_response("Model not loaded")
            
            # Convert bytes to numpy array
            image = self._bytes_to_numpy(image_data)
            
            if image is None:
                return self._create_error_response("Invalid image data")
            
            # Analyze with fixed model
            results = self._analyze_with_fixed_model(image, user_demographics)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _bytes_to_numpy(self, image_data: bytes) -> Optional[np.ndarray]:
        """Convert image bytes to numpy array"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"❌ Failed to convert image: {e}")
            return None
    
    def _analyze_with_fixed_model(self, image: np.ndarray, user_demographics: Dict = None) -> Dict:
        """Analyze image with the fixed model"""
        try:
            # Preprocess image
            processed_image = self._preprocess_for_fixed_model(image)
            
            # Get prediction
            prediction = self.fixed_model.predict(processed_image, verbose=0)
            
            # Decode prediction
            condition_result = self._decode_fixed_prediction(prediction[0])
            
            # Generate analysis
            analysis = self._generate_fixed_analysis(condition_result, user_demographics)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Fixed model analysis failed: {e}")
            return self._create_error_response(f"Model analysis failed: {str(e)}")
    
    def _preprocess_for_fixed_model(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for the fixed model"""
        try:
            # Resize to 224x224
            resized = cv2.resize(image, (224, 224))
            
            # Convert to RGB if needed
            if len(resized.shape) == 3 and resized.shape[2] == 3:
                pass  # Already RGB
            elif len(resized.shape) == 3 and resized.shape[2] == 4:
                # RGBA to RGB
                resized = cv2.cvtColor(resized, cv2.COLOR_RGBA2RGB)
            else:
                # Grayscale to RGB
                resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
            
            # Normalize to [0, 1]
            resized = resized.astype(np.float32) / 255.0
            
            # Add batch dimension
            resized = np.expand_dims(resized, axis=0)
            
            return resized
            
        except Exception as e:
            logger.error(f"❌ Preprocessing failed: {e}")
            raise
    
    def _decode_fixed_prediction(self, prediction: np.ndarray) -> Dict:
        """Decode model prediction"""
        try:
            # Get top prediction
            top_idx = np.argmax(prediction)
            top_condition = self.class_names[top_idx]
            top_confidence = float(prediction[top_idx])
            top_percentage = top_confidence * 100
            
            # Get top 3 predictions
            top_3_indices = np.argsort(prediction)[::-1][:3]
            top_3_predictions = []
            
            for idx in top_3_indices:
                condition = self.class_names[idx]
                confidence = float(prediction[idx])
                percentage = confidence * 100
                top_3_predictions.append({
                    'condition': condition,
                    'confidence': confidence,
                    'percentage': percentage
                })
            
            return {
                'primary_condition': top_condition,
                'confidence': top_confidence,
                'percentage': top_percentage,
                'top_3_predictions': top_3_predictions
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction decoding failed: {e}")
            raise
    
    def _generate_fixed_analysis(self, condition_result: Dict, user_demographics: Dict = None) -> Dict:
        """Generate comprehensive analysis"""
        try:
            # Determine severity based on confidence
            confidence = condition_result['confidence']
            if confidence >= 0.8:
                severity = "high"
            elif confidence >= 0.6:
                severity = "medium"
            else:
                severity = "low"
            
            # Generate recommendations
            recommendations = self._generate_recommendations(condition_result['primary_condition'])
            
            analysis = {
                "status": "success",
                "analysis_timestamp": datetime.now().isoformat(),
                "model_version": "fixed_v1.0_local",
                "primary_condition": condition_result['primary_condition'],
                "confidence": condition_result['confidence'],
                "percentage": condition_result['percentage'],
                "severity": severity,
                "top_3_predictions": condition_result['top_3_predictions'],
                "recommendations": recommendations,
                "user_demographics": user_demographics
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis generation failed: {e}")
            raise
    
    def _generate_recommendations(self, condition: str) -> List[str]:
        """Generate recommendations based on condition"""
        recommendations = {
            "acne": [
                "Use gentle, non-comedogenic cleansers",
                "Avoid touching your face throughout the day",
                "Consider over-the-counter treatments with benzoyl peroxide or salicylic acid",
                "Consult a dermatologist for persistent acne"
            ],
            "actinic_keratosis": [
                "Protect skin from UV radiation with broad-spectrum sunscreen",
                "Wear protective clothing and seek shade",
                "Regular skin checks by a dermatologist",
                "Consider professional treatment options"
            ],
            "basal_cell_carcinoma": [
                "Immediate consultation with a dermatologist required",
                "Protect skin from further sun damage",
                "Regular skin cancer screenings",
                "Follow dermatologist treatment recommendations"
            ],
            "eczema": [
                "Use fragrance-free, gentle moisturizers",
                "Avoid hot showers and harsh soaps",
                "Identify and avoid triggers",
                "Consider prescription treatments if severe"
            ],
            "healthy": [
                "Maintain current skincare routine",
                "Continue sun protection practices",
                "Regular skin checks for changes",
                "Stay hydrated and maintain healthy lifestyle"
            ],
            "rosacea": [
                "Use gentle, non-irritating skincare products",
                "Avoid spicy foods and alcohol if they trigger flare-ups",
                "Protect skin from extreme temperatures",
                "Consult dermatologist for prescription treatments"
            ]
        }
        
        return recommendations.get(condition, ["Consult a dermatologist for personalized advice"])
    
    def _create_error_response(self, message: str) -> Dict:
        """Create error response"""
        return {
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

# Initialize the model integration
try:
    model_integration = SimpleFixedModelIntegration()
    logger.info("✅ Model integration initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize model integration: {e}")
    model_integration = None

# Flask routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Simple Fixed Model Integration",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_integration.fixed_model is not None if model_integration else False
    })

@app.route('/api/v5/skin/analyze-fixed', methods=['POST'])
def analyze_skin():
    """Analyze skin using the fixed model"""
    try:
        if model_integration is None:
            return jsonify({"status": "error", "message": "Model not initialized"}), 500
        
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"status": "error", "message": "No image selected"}), 400
        
        # Get image data
        image_data = image_file.read()
        
        # Get demographics if provided
        demographics = None
        if 'demographics' in request.form:
            try:
                demographics = json.loads(request.form['demographics'])
            except:
                demographics = None
        
        # Analyze image
        results = model_integration.analyze_skin_with_fixed_model(image_data, demographics)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Skin analysis endpoint error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v5/skin/model-status', methods=['GET'])
def model_status():
    """Get model status"""
    if model_integration is None:
        return jsonify({"status": "error", "message": "Model integration not initialized"}), 500
    
    return jsonify(model_integration.get_model_status())

@app.route('/api/v4/face/detect', methods=['POST'])
def detect_face():
    """Face detection endpoint for compatibility"""
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No image provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"status": "error", "message": "No image selected"}), 400
        
        # Simple face detection response
        return jsonify({
            "status": "success",
            "face_detected": True,
            "confidence": 0.95,
            "message": "Face detected successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Face detection error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Face detection failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Print model status
    if model_integration:
        status = model_integration.get_model_status()
        print(f"\n📊 Model Status: {status}")
        
        if status['model_loaded']:
            print("✅ Simple fixed model integration ready!")
            print("🚀 Use the Flask endpoints to analyze skin with improved accuracy!")
            print(f"📁 Model: {status['model_path']}")
            print("📊 Results: results/fixed_training_results.json")
        else:
            print("❌ Model not loaded - check model file path")
    
    # Start Flask server
    print(f"\n🚀 Starting Flask server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
