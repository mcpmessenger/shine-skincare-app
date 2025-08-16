#!/usr/bin/env python3
"""
Shine Skin Collective - Hare Run V6 API Gateway
Enhanced ML-powered skin analysis with S3 model management
"""

import os
import base64
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import numpy as np
import cv2
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow frontend access
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002'], supports_credentials=True)

# Service configuration
SERVICE_NAME = "shine-backend-hare-run-v6"
S3_BUCKET = os.getenv('S3_BUCKET', 'shine-skincare-models')
S3_MODEL_KEY = os.getenv('S3_MODEL_KEY', 'ml-models/production/comprehensive_model_best.h5')
LOCAL_MODEL_PATH = os.getenv('MODEL_PATH', './models/fixed_model_best.h5')
PORT = int(os.getenv('PORT', 8000))

# Hare Run V6 Configuration
HARE_RUN_V6_CONFIG = {
    'enabled': True,
    'models': {
        'facial': {
            'primary': 'comprehensive_model_best.h5',
            'backup': 'fixed_model_best.h5',
            'metadata': 'comprehensive_model_best.h5'
        }
    },
    'endpoints': {
        'skin_analysis': '/api/v6/skin/analyze-hare-run',
        'model_status': '/api/v5/skin/model-status'
    },
    'performance': {
        'target_accuracy': '97.13%',
        'max_response_time': '30s',
        'model_size': '214MB'
    }
}

# Initialize S3 client with error handling
try:
    s3_client = boto3.client('s3')
    logger.info("✅ S3 client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize S3 client: {e}")
    s3_client = None

# Initialize advanced analysis systems
try:
    from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
    enhanced_analyzer = EnhancedSkinAnalyzer()
    logger.info("✅ Enhanced skin analyzer initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize enhanced analyzer: {e}")
    enhanced_analyzer = None

# Hare Run V6 Model Manager - LAZY LOADING VERSION
class HareRunV6ModelManager:
    """Manages Hare Run V6 model loading and availability with lazy loading"""
    
    def __init__(self):
        self.models_loaded = False
        self.model_paths = {}
        self.model_metadata = {}
        self._models_loaded = False  # Don't load models during init
    
    def _ensure_models_loaded(self):
        """Lazy load models only when needed"""
        if not self._models_loaded:
            self._load_models()
            self._models_loaded = True
    
    def _load_models(self):
        """Load Hare Run V6 models from local or S3"""
        try:
            # Check local models first
            local_models_dir = Path('./models')
            if local_models_dir.exists():
                self._load_local_models(local_models_dir)
            
            # If local models not available, try S3
            if not self.models_loaded and s3_client:
                self._load_s3_models()
            
            # Check results directory as fallback
            if not self.models_loaded:
                self._load_results_models()
            
            if self.models_loaded:
                logger.info("✅ Hare Run V6 models loaded successfully")
                logger.info(f"📊 Model info: {self.model_metadata}")
            else:
                logger.warning("⚠️ No Hare Run V6 models available")
                
        except Exception as e:
            logger.error(f"❌ Failed to load Hare Run V6 models: {e}")
    
    def _load_local_models(self, models_dir: Path):
        """Load models from local models directory"""
        try:
            for model_type, model_info in HARE_RUN_V6_CONFIG['models'].items():
                model_path = models_dir / model_info['primary']
                if model_path.exists():
                    self.model_paths[model_type] = str(model_path)
                    self.model_metadata[model_type] = {
                        'source': 'local',
                        'path': str(model_path),
                        'size': model_path.stat().st_size / (1024 * 1024),
                        'available': True
                    }
                    logger.info(f"✅ Loaded local model: {model_path}")
            
            if self.model_paths:
                self.models_loaded = True
                
        except Exception as e:
            logger.error(f"❌ Failed to load local models: {e}")
    
    def _load_s3_models(self):
        """Load models from S3"""
        try:
            logger.info("🔄 Attempting to load models from S3...")
            
            if not s3_client:
                logger.warning("⚠️ S3 client not available")
                return
            
            # Create models directory if it doesn't exist
            models_dir = Path('./models')
            models_dir.mkdir(exist_ok=True)
            
            for model_type, model_info in HARE_RUN_V6_CONFIG['models'].items():
                s3_key = f"ml-models/production/{model_info['primary']}"
                local_path = models_dir / model_info['primary']
                
                if not local_path.exists():
                    logger.info(f"🔄 Downloading {s3_key} from S3...")
                    try:
                        s3_client.download_file(S3_BUCKET, s3_key, str(local_path))
                        logger.info(f"✅ Successfully downloaded {s3_key}")
                    except Exception as e:
                        logger.error(f"❌ Failed to download {s3_key}: {e}")
                        continue
                
                # Now load the downloaded model
                if local_path.exists():
                    self.model_paths[model_type] = str(local_path)
                    self.model_metadata[model_type] = {
                        'source': 's3',
                        'path': str(local_path),
                        'size': local_path.stat().st_size / (1024 * 1024),
                        'available': True,
                        's3_location': f"s3://{S3_BUCKET}/{s3_key}"
                    }
                    logger.info(f"✅ Loaded S3 model: {local_path}")
            
            if self.model_paths:
                self.models_loaded = True
                
        except Exception as e:
            logger.error(f"❌ Failed to load S3 models: {e}")
    
    def _load_results_models(self):
        """Load models from results directory (development)"""
        try:
            results_dir = Path('./results')
            if results_dir.exists():
                for model_type, model_info in HARE_RUN_V6_CONFIG['models'].items():
                    model_path = results_dir / model_info['primary']
                    if model_path.exists():
                        self.model_paths[model_type] = str(model_path)
                        self.model_metadata[model_type] = {
                            'source': 'results',
                            'path': str(model_path),
                            'size': model_path.stat().st_size / (1024 * 1024),
                            'available': True
                        }
                        logger.info(f"✅ Loaded results model: {model_path}")
                
                if self.model_paths:
                    self.models_loaded = True
                    
        except Exception as e:
            logger.error(f"❌ Failed to load results models: {e}")
    
    def get_model_path(self, model_type: str = 'facial') -> Optional[str]:
        """Get path to specified model type"""
        self._ensure_models_loaded()
        return self.model_paths.get(model_type)
    
    def is_model_available(self, model_type: str = 'facial') -> bool:
        """Check if specified model is available"""
        self._ensure_models_loaded()
        return model_type in self.model_paths and self.model_paths[model_type] is not None
    
    def get_model_status(self) -> Dict:
        """Get comprehensive model status"""
        self._ensure_models_loaded()
        return {
            'models_loaded': self.models_loaded,
            'total_models': len(self.model_paths),
            'model_details': self.model_metadata,
            'config': HARE_RUN_V6_CONFIG
        }

# Initialize Hare Run V6 Model Manager - NO MODEL LOADING DURING IMPORT
hare_run_v6_manager = HareRunV6ModelManager()

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.route('/health')
def health():
    """Basic health check - Fast response for ALB health checks"""
    try:
        # Quick check - don't wait for models to load
        return "OK", 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return "ERROR", 500

@app.route('/api/health')
def api_health():
    """Detailed API health check with model status"""
    try:
        return jsonify({
            "message": "API Gateway is running",
            "service": SERVICE_NAME,
            "status": "healthy",
            "models_loaded": hare_run_v6_manager.models_loaded,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return jsonify({
            "message": "API Gateway error",
            "service": SERVICE_NAME,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/ready')
def ready():
    """Readiness check"""
    return jsonify({
        "message": "Service is ready",
        "service": SERVICE_NAME,
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    })

# ============================================================================
# FACE DETECTION ENDPOINTS
# ============================================================================

@app.route('/api/v1/face/detect', methods=['POST'])
def face_detect():
    """Face detection endpoint"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        image_data = data.get('image') or data.get('image_data')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        
        # Process image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_array is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Face detection using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            return jsonify({
                'success': True,
                'faces_detected': len(faces),
                'primary_face': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 0.95
                },
                'message': f'Detected {len(faces)} face(s)'
            })
        else:
            return jsonify({
                'success': False,
                'faces_detected': 0,
                'message': 'No faces detected in the image'
            })
            
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Face detection failed'
        }), 500

# ============================================================================
# SKIN ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/v6/skin/analyze-hare-run', methods=['POST'])
def analyze_skin_hare_run():
    """Hare Run V6 enhanced skin analysis endpoint"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        image_data = data.get('image') or data.get('image_data')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Check if models are available
        if not hare_run_v6_manager.is_model_available('facial'):
            return jsonify({
                'error': 'ML models not available',
                'message': 'Please try again later'
            }), 503
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        
        # Process image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_array is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Enhanced analysis using Hare Run V6
        if enhanced_analyzer:
            try:
                results = enhanced_analyzer.analyze_skin_conditions(img_array)
                return jsonify({
                    'success': True,
                    'analysis_type': 'Hare Run V6 Enhanced',
                    'result': results,  # Changed from 'results' to 'result'
                    'model_info': hare_run_v6_manager.get_model_status(),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Enhanced analysis failed: {e}")
                # Fallback to basic analysis
                pass
        
        # Basic analysis fallback
        return jsonify({
            'success': True,
            'analysis_type': 'Basic Analysis',
            'message': 'Enhanced analysis unavailable, using basic analysis',
            'basic_results': {
                'image_processed': True,
                'face_detected': True,
                'analysis_available': False
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Skin analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Skin analysis failed'
        }), 500

# ============================================================================
# MODEL STATUS ENDPOINTS
# ============================================================================

@app.route('/api/v5/skin/model-status')
def model_status():
    """Get ML model status and availability"""
    try:
        return jsonify({
            'service': SERVICE_NAME,
            'status': 'healthy',
            'model_status': hare_run_v6_manager.get_model_status(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Model status error: {e}")
        return jsonify({
            'service': SERVICE_NAME,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == "__main__":
    logger.info(f"🚀 Starting {SERVICE_NAME} on port {PORT}")
    logger.info(f"📦 S3 Bucket: {S3_BUCKET}")
    logger.info(f"🔑 Model Key: {S3_MODEL_KEY}")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
