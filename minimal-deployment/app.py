import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Simple CORS configuration
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
            "supports_credentials": True
        }
    })

    # Configure file upload limits - increased to handle larger images
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    app.config['MAX_CONTENT_PATH'] = None

    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'error': 'File too large', 
            'message': 'Maximum file size is 50MB',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error', 
            'message': 'An unexpected error occurred',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested endpoint does not exist',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 404

    @app.route('/')
    def root():
        return jsonify({
            'message': 'Shine Skincare App - Minimal Backend',
            'status': 'running',
            'version': 'v1.0-minimal-stable',
            'architecture': 'minimal-deployment',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'file_upload_limit': '50MB',
                'health_endpoints': True,
                'cors_enabled': True,
                'error_handling': True
            }
        })

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'deployment': 'minimal',
            'version': 'v1.0-minimal-stable'
        })

    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'deployed_successfully',
            'operation': 'minimal_backend',
            'version': 'minimal-v1.0-stable',
            'timestamp': datetime.now().isoformat(),
            'health_check': 'passing',
            'message': 'Shine Skincare App - Minimal Backend is running!',
            'features': {
                'basic_api': True,
                'health_endpoints': True,
                'cors_enabled': True,
                'file_upload_limit': '50MB',
                'error_handling': True,
                'stable_deployment': True
            }
        })

    @app.route('/api/test')
    def test_endpoint():
        return jsonify({
            'message': 'Minimal backend is working!',
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'version': 'v1.0-minimal-stable'
        })

    # Add a basic file upload test endpoint
    @app.route('/api/upload-test', methods=['POST'])
    def upload_test():
        try:
            if 'file' not in request.files:
                return jsonify({
                    'error': 'No file provided',
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'error': 'No file selected',
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }), 400
            
            # Basic file validation
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' not in file.filename or \
               file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({
                    'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed.',
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }), 400
            
            return jsonify({
                'message': 'File upload test successful',
                'filename': file.filename,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Upload test error: {str(e)}")
            return jsonify({
                'error': 'Upload test failed',
                'message': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False) 