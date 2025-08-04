#!/usr/bin/env python3
"""
Enhanced Flask Application for Shine Skincare App
Main application with integrated skin analysis capabilities
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback

# Import our integrated analysis API
from enhanced_analysis_api import app as analysis_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main Flask app
app = Flask(__name__)
CORS(app)

# Register the analysis API blueprint
app.register_blueprint(analysis_app, url_prefix='/api/v3')

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Shine Skincare App - Enhanced Analysis API',
        'version': '3.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'analysis_status': '/api/v3/skin/status',
            'normalized_analysis': '/api/v3/skin/analyze-normalized',
            'basic_analysis': '/api/v3/skin/analyze-basic',
            'face_detection': '/api/v3/skin/face-detect'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'features': {
            'integrated_analysis': True,
            'demographic_normalization': True,
            'healthy_baselines': True,
            'condition_matching': True
        }
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        'error': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🚀 Starting Shine Skincare App on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 