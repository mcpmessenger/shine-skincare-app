from flask import Flask, jsonify
from flask_cors import CORS
import os

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Enable CORS - Simplified for debugging
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        from datetime import datetime
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    # Root endpoint
    @app.route('/')
    def root():
        return {'message': 'Shine Skincare API', 'status': 'running'}
    
    # Guest skin analysis endpoint (simplified)
    @app.route('/api/v2/analyze/guest', methods=['POST'])
    def analyze_image_guest():
        try:
            # Simple response for testing
            return jsonify({
                'success': True,
                'data': {
                    'image_id': 'guest_test_123',
                    'analysis': {
                        'skin_type': 'Combination',
                        'concerns': ['Acne', 'Hyperpigmentation'],
                        'hydration': 75,
                        'oiliness': 60,
                        'sensitivity': 30,
                        'recommendations': [
                            'Use a gentle cleanser twice daily',
                            'Apply sunscreen with SPF 30+',
                            'Consider a vitamin C serum'
                        ]
                    },
                    'message': 'Guest analysis completed. Sign up to save your results!'
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app 