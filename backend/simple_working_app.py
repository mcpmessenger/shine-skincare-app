#!/usr/bin/env python3
"""
Simple working Flask app with the /api/v2/analyze/guest endpoint
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return {'message': 'Shine Skincare API - Simple Working Version', 'status': 'running'}

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Simple backend is working!',
        'version': 'simple-1.0'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    """Simple guest analysis endpoint that always works"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get optional ethnicity
        ethnicity = request.form.get('ethnicity', '')
        
        # Create a simple mock analysis
        analysis = {
            'status': 'success',
            'skinType': 'Combination',
            'concerns': ['Uneven skin tone', 'Fine lines'],
            'hydration': 65,
            'oiliness': 45,
            'sensitivity': 30,
            'recommendations': [
                'Use a gentle cleanser',
                'Apply SPF 30+ daily',
                'Consider a vitamin C serum'
            ],
            'products': [
                {
                    'name': 'Gentle Cleanser',
                    'price': 25.00,
                    'image': '/products/cleanser.jpg'
                },
                {
                    'name': 'SPF 30 Sunscreen',
                    'price': 35.00,
                    'image': '/products/sunscreen.jpg'
                }
            ],
            'confidence': 0.85,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': str(uuid.uuid4())
        }
        
        # Add ethnicity context if provided
        if ethnicity:
            analysis['ethnicity'] = ethnicity
            analysis['ethnicity_considered'] = True
        
        return jsonify({
            'success': True,
            'data': {
                'image_id': f'guest_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}',
                'analysis': analysis,
                'message': 'Simple analysis completed! Sign up to save your results!'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/enhanced/analyze/guest', methods=['POST'])
def analyze_guest_enhanced():
    """Enhanced guest analysis endpoint"""
    return analyze_guest()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 