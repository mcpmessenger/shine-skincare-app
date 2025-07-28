#!/usr/bin/env python3
"""
Minimal Flask app with no external dependencies
"""
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def root():
    return {
        'message': 'Shine API - Minimal Version',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat()
    }

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Minimal backend is running!'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze():
    """Minimal guest analysis"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'image_id': f'guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': {
                    'status': 'success',
                    'skinType': 'Combination',
                    'concerns': ['Uneven skin tone', 'Fine lines'],
                    'hydration': 65,
                    'oiliness': 45,
                    'sensitivity': 30,
                    'recommendations': [
                        'Use a gentle cleanser',
                        'Apply SPF daily',
                        'Use a moisturizer'
                    ],
                    'products': [
                        {
                            'name': 'Gentle Cleanser',
                            'price': 25.00,
                            'image': '/products/cleanser.jpg'
                        }
                    ],
                    'confidence': 0.85,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'message': 'Minimal analysis completed!'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 