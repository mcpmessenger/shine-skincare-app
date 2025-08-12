#!/usr/bin/env python3
"""
Test Enhanced ML Service for Shine Skincare App - Phase 3
Simplified version to test basic functionality
"""
import os
import logging
import time
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global variables
startup_time = time.time()

def get_basic_metrics():
    """Get basic system metrics"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'uptime_seconds': int(time.time() - startup_time)
        }
    except ImportError:
        return {
            'cpu_percent': 'psutil not available',
            'memory_percent': 'psutil not available',
            'uptime_seconds': int(time.time() - startup_time)
        }

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic service status"""
    metrics = get_basic_metrics()
    
    return jsonify({
        'message': 'Shine Skincare App - Test Enhanced ML Service (Phase 3)',
        'version': 'v5.0-test',
        'status': 'healthy',
        'basic_metrics': metrics,
        'endpoints': [
            'GET /',
            'GET /health',
            'GET /test'
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check"""
    metrics = get_basic_metrics()
    
    return jsonify({
        'status': 'healthy',
        'message': 'Test Enhanced ML service is running!',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': metrics.get('uptime_seconds', 0)
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'Test endpoint working!',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    logger.info("🚀 Starting Test Enhanced ML Service...")
    logger.info("🌐 Server will be available at: http://0.0.0.0:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
