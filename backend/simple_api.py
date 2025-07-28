"""
Minimal API entry point for AWS Elastic Beanstalk deployment
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine Skincare API - Simple Version',
        'status': 'running',
        'version': 'simple-1.0'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'version': 'simple-1.0'
    })

@app.route('/api/test')
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'version': 'simple-1.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 