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

@app.route('/api/recommendations/trending')
def trending_products():
    return jsonify({
        'products': [
            {
                'id': 1,
                'name': 'Sample Product 1',
                'description': 'This is a sample trending product',
                'price': 29.99,
                'image': '/sample-product-1.jpg'
            },
            {
                'id': 2,
                'name': 'Sample Product 2', 
                'description': 'Another sample trending product',
                'price': 39.99,
                'image': '/sample-product-2.jpg'
            }
        ],
        'message': 'Trending products endpoint working',
        'version': 'simple-1.0'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_guest():
    return jsonify({
        'analysis': {
            'skin_type': 'combination',
            'concerns': ['acne', 'aging'],
            'recommendations': [
                {
                    'id': 1,
                    'name': 'Gentle Cleanser',
                    'description': 'Recommended for combination skin',
                    'price': 24.99
                },
                {
                    'id': 2,
                    'name': 'Moisturizer',
                    'description': 'Hydrating formula for your skin type',
                    'price': 34.99
                }
            ]
        },
        'message': 'Skin analysis completed',
        'version': 'simple-1.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 