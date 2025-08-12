#!/usr/bin/env python3
"""
Enhanced ML Service for Shine Skincare App - Phase 3
Advanced service with performance monitoring, enhanced logging, and S3 optimization
"""
import os
import logging
import time
import psutil
import traceback
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global variables for ML capabilities
ml_model_loaded = False
ml_dependencies_available = False
ml_service_status = "initializing"
performance_metrics = {}
startup_time = time.time()

def get_system_metrics():
    """Get current system performance metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'disk_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'uptime_seconds': int(time.time() - startup_time)
        }
    except Exception as e:
        logger.warning(f"Could not get system metrics: {e}")
        return {}

def check_ml_dependencies():
    """Check if ML dependencies are available with performance timing"""
    global ml_dependencies_available
    
    start_time = time.time()
    try:
        # Try to import basic ML libraries
        import numpy as np
        logger.info("✅ Basic ML dependencies available")
        
        # Try to import TensorFlow (heaviest dependency)
        try:
            import tensorflow as tf
            logger.info("✅ TensorFlow available")
            ml_dependencies_available = True
            
            # Get TensorFlow version and device info
            tf_version = tf.__version__
            gpu_available = len(tf.config.list_physical_devices('GPU')) > 0
            logger.info(f"TensorFlow {tf_version} - GPU: {'Available' if gpu_available else 'CPU Only'}")
            
            return True
        except ImportError as e:
            logger.warning(f"⚠️ TensorFlow not available: {e}")
            ml_dependencies_available = False
            return False
            
    except ImportError as e:
        logger.warning(f"⚠️ Basic ML dependencies not available: {e}")
        ml_dependencies_available = False
        return False
    finally:
        dependency_check_time = time.time() - start_time
        logger.info(f"ML dependency check completed in {dependency_check_time:.2f}s")

def load_ml_model():
    """Attempt to load the ML model with performance monitoring"""
    global ml_model_loaded, ml_service_status
    
    if not ml_dependencies_available:
        ml_service_status = "dependencies_missing"
        return False
    
    start_time = time.time()
    try:
        # Try to import the ML integration
        from simple_fixed_integration import SimpleFixedModelIntegration
        
        # Initialize the ML service
        ml_integration = SimpleFixedModelIntegration()
        
        if ml_integration.fixed_model is not None:
            ml_model_loaded = True
            ml_service_status = "ml_ready"
            logger.info("✅ ML model loaded successfully")
            
            # Record model loading performance
            model_load_time = time.time() - start_time
            performance_metrics['model_load_time'] = model_load_time
            logger.info(f"Model loaded in {model_load_time:.2f}s")
            
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
    """Root endpoint with enhanced service status"""
    system_metrics = get_system_metrics()
    
    return jsonify({
        'message': 'Shine Skincare App - Enhanced ML Service (Phase 3)',
        'version': 'v5.0-enhanced',
        'status': 'healthy',
        'ml_status': ml_service_status,
        'ml_model_loaded': ml_model_loaded,
        'ml_dependencies': ml_dependencies_available,
        'performance_metrics': performance_metrics,
        'system_metrics': system_metrics,
        'endpoints': [
            'GET /',
            'GET /health',
            'GET /ml/status',
            'GET /performance',
            'POST /api/v5/skin/analyze-fixed (if ML ready)',
            'POST /api/v4/face/detect (if ML ready)'
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with system metrics"""
    system_metrics = get_system_metrics()
    
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced ML service is running!',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': system_metrics.get('uptime_seconds', 0),
        'ml_status': ml_service_status
    })

@app.route('/ml/status', methods=['GET'])
def ml_status():
    """Detailed ML service status"""
    return jsonify({
        'ml_service_status': ml_service_status,
        'ml_model_loaded': ml_model_loaded,
        'ml_dependencies_available': ml_dependencies_available,
        'performance_metrics': performance_metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/performance', methods=['GET'])
def performance():
    """Performance metrics endpoint"""
    system_metrics = get_system_metrics()
    
    return jsonify({
        'performance_metrics': performance_metrics,
        'system_metrics': system_metrics,
        'timestamp': datetime.now().isoformat()
    })

# Initialize service immediately
def initialize_service():
    """Initialize the ML service"""
    global ml_model_loaded, ml_dependencies_available, ml_service_status
    
    logger.info("🚀 Initializing Enhanced ML Service...")
    
    # Check ML dependencies
    check_ml_dependencies()
    
    # Attempt to load ML model
    load_ml_model()
    
    logger.info(f"🎯 Enhanced ML Service initialized - Status: {ml_service_status}")

# Initialize immediately
initialize_service()

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced ML Service...")
    logger.info("🌐 Server will be available at: http://0.0.0.0:5000")
    
    # Initialize service
    # check_ml_dependencies() # This line is now handled by initialize_service()
    # load_ml_model() # This line is now handled by initialize_service()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
