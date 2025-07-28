"""
Main API entry point for AWS Elastic Beanstalk deployment
"""
import os
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize error variable
error_msg = None

try:
    # For AWS EB deployment, import the main Flask app
    from app import create_app
    app = create_app('production')
    logger.info("Successfully imported create_app and created Flask app")
except Exception as e:
    error_msg = str(e)
    logger.error(f"Failed to create Flask app: {error_msg}")
    # Create a minimal app as fallback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'fallback-healthy', 'error': error_msg}
    
    @app.route('/')
    def root():
        return {'message': 'Shine API - Fallback Mode', 'error': error_msg}
    
    @app.route('/api/test')
    def test():
        return {'message': 'Test endpoint working', 'error': error_msg}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)