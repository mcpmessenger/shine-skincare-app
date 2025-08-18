#!/usr/bin/env python3
"""
SWAN Production API - Flask-based API for serving the production model
"""

import os
import sys
import json
import logging
import pickle
import gzip
import numpy as np
from pathlib import Path
from datetime import datetime
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SWANProductionAPI:
    """Production API for SWAN skin analysis"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend integration
        
        # Load the production model
        self.model_pipeline = None
        self.load_model()
        
        # Setup routes
        self.setup_routes()
        
        # Performance tracking
        self.request_count = 0
        self.start_time = time.time()
    
    def load_model(self):
        """Load the production model pipeline"""
        try:
            logger.info("🔄 Loading production model...")
            
            model_path = "production-models/swan_production_pipeline.pkl.gz"
            with gzip.open(model_path, "rb") as f:
                self.model_pipeline = pickle.load(f)
            
            logger.info("✅ Production model loaded successfully")
            logger.info(f"   Model type: {self.model_pipeline['model_type']}")
            logger.info(f"   Feature path: {self.model_pipeline['feature_path']}")
            logger.info(f"   Feature dimensions: {self.model_pipeline['feature_dim']}")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            uptime = time.time() - self.start_time
            return jsonify({
                'status': 'healthy',
                'model_loaded': self.model_pipeline is not None,
                'uptime_seconds': uptime,
                'request_count': self.request_count,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/v1/analyze', methods=['POST'])
        def analyze_skin():
            """Main skin analysis endpoint"""
            try:
                start_time = time.time()
                self.request_count += 1
                
                # Get image data
                if 'image' not in request.files:
                    return jsonify({'error': 'No image file provided'}), 400
                
                image_file = request.files['image']
                
                # Get optional demographic parameters
                age = request.form.get('age', type=int)
                ethnicity = request.form.get('ethnicity', type=int)
                gender = request.form.get('gender', type=int)
                
                # Process image
                image_features = self.process_image(image_file)
                if image_features is None:
                    return jsonify({'error': 'Failed to process image'}), 400
                
                # Make prediction
                prediction_result = self.predict(image_features)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Prepare response
                response = {
                    'prediction': prediction_result['prediction'],
                    'confidence': prediction_result['confidence'],
                    'probabilities': prediction_result['probabilities'],
                    'processing_time_ms': round(processing_time * 1000, 2),
                    'request_id': self.request_count,
                    'timestamp': datetime.now().isoformat(),
                    'demographics': {
                        'age': age,
                        'ethnicity': ethnicity,
                        'gender': gender
                    }
                }
                
                logger.info(f"✅ Analysis completed in {processing_time*1000:.2f}ms")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"❌ Error in analysis: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/model-info', methods=['GET'])
        def model_info():
            """Get model information"""
            if self.model_pipeline is None:
                return jsonify({'error': 'Model not loaded'}), 500
            
            return jsonify({
                'model_type': self.model_pipeline['model_type'],
                'feature_path': self.model_pipeline['feature_path'],
                'feature_dimensions': self.model_pipeline['feature_dim'],
                'class_names': self.model_pipeline['class_names'],
                'performance': self.model_pipeline['performance'],
                'training_date': self.model_pipeline['training_date']
            })
        
        @self.app.route('/api/v1/stats', methods=['GET'])
        def get_stats():
            """Get API statistics"""
            uptime = time.time() - self.start_time
            avg_response_time = uptime / max(self.request_count, 1)
            
            return jsonify({
                'total_requests': self.request_count,
                'uptime_seconds': uptime,
                'average_response_time_ms': round(avg_response_time * 1000, 2),
                'requests_per_second': round(self.request_count / max(uptime, 1), 2)
            })
    
    def process_image(self, image_file):
        """Process uploaded image to extract features"""
        try:
            # Read image
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale and resize
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize to 64x64 (matching training data)
            image = image.resize((64, 64))
            image_array = np.array(image)
            
            # Extract features (same as training)
            features = self.extract_cnn_features(image_array)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error processing image: {e}")
            return None
    
    def extract_cnn_features(self, image):
        """Extract CNN-like features from image"""
        try:
            # CNN-like features (simplified, matching training)
            # Use downsampled image + gradient features
            cnn_img = cv2.resize(image, (32, 32))
            grad_x = cv2.Sobel(cnn_img, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(cnn_img, cv2.CV_64F, 0, 1, ksize=3)
            
            cnn_features = np.concatenate([
                cnn_img.flatten() / 255.0,  # 32*32 = 1024
                grad_x.flatten() / np.max(np.abs(grad_x)),  # 1024
                grad_y.flatten() / np.max(np.abs(grad_y))   # 1024
            ])
            
            # Apply PCA transformation (if available)
            if 'cnn_pca' in self.model_pipeline:
                cnn_features = self.model_pipeline['cnn_pca']['pca'].transform(
                    cnn_features.reshape(1, -1)
                ).flatten()
            
            return cnn_features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            return None
    
    def predict(self, features):
        """Make prediction using the loaded model"""
        try:
            if self.model_pipeline is None:
                raise Exception("Model not loaded")
            
            model = self.model_pipeline['model']
            
            # Ensure correct shape
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Make prediction
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Get class names
            class_names = self.model_pipeline['class_names']
            
            return {
                'prediction': class_names[prediction],
                'confidence': float(np.max(probabilities)),
                'probabilities': {
                    class_names[i]: float(prob) for i, prob in enumerate(probabilities)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in prediction: {e}")
            raise
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"🚀 Starting SWAN Production API on {host}:{port}")
        logger.info(f"📊 Model loaded: {self.model_pipeline is not None}")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main execution function"""
    try:
        # Create and run the API
        api = SWANProductionAPI()
        
        # Get configuration from environment or use defaults
        host = os.getenv('SWAN_API_HOST', '0.0.0.0')
        port = int(os.getenv('SWAN_API_PORT', 5000))
        debug = os.getenv('SWAN_API_DEBUG', 'false').lower() == 'true'
        
        # Run the API
        api.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
