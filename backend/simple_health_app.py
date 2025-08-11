#!/usr/bin/env python3
"""
Simple Health Check App for Shine Skincare App
Minimal Flask server that just responds to health checks
"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Shine Skincare App - Health Check Server',
        'version': 'v5.0-health',
        'status': 'healthy',
        'endpoints': [
            'GET /',
            'GET /health'
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Health check server is running!'
    })

if __name__ == "__main__":
    logger.info("🚀 Starting Simple Health Check Server...")
    logger.info("🌐 Server will be available at: http://0.0.0.0:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
