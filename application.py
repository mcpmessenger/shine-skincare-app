#!/usr/bin/env python3
"""
Elastic Beanstalk entry point for the Shine Skincare API
"""

from flask import Flask, jsonify
import os

# Create Flask application
application = Flask(__name__)

@application.route('/')
def hello():
    return jsonify({
        'message': 'Hello from Shine Skincare API!', 
        'status': 'running',
        'environment': 'production'
    })

@application.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'shine-api',
        'environment_vars_count': len([k for k in os.environ.keys() if not k.startswith('_')])
    })

@application.route('/api/test')
def test():
    return jsonify({
        'message': 'API endpoint working',
        'environment_variables': {
            'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'NOT SET',
            'GOOGLE_CLIENT_ID': 'SET' if os.environ.get('GOOGLE_CLIENT_ID') else 'NOT SET',
            'SUPABASE_URL': 'SET' if os.environ.get('SUPABASE_URL') else 'NOT SET'
        }
    })

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=8000) 