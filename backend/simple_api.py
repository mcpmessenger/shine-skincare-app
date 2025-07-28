"""
Minimal API entry point for AWS Elastic Beanstalk deployment
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine Skincare API - Minimal Version',
        'status': 'running',
        'version': 'minimal-1.0'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'version': 'minimal-1.0'
    })

@app.route('/api/test')
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'timestamp': '2025-07-27'
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting minimal app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 