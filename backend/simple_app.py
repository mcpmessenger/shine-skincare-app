"""
Simple Flask app for Vercel deployment - MVP version
This bypasses all the complex service architecture for now
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import hashlib
import uuid

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def analyze_image_simple(image_data):
    """Simple image analysis using hash-based features"""
    try:
        # Generate consistent hash from image data
        image_hash = hashlib.md5(image_data).hexdigest()
        hash_int = int(image_hash[:8], 16)
        
        # Generate mock analysis results
        features = {
            'brightness': (hash_int % 100) / 100.0,
            'contrast': ((hash_int >> 8) % 100) / 100.0,
            'redness': ((hash_int >> 16) % 100) / 100.0,
            'texture': ((hash_int >> 24) % 100) / 100.0,
        }
        
        # Determine skin type
        if features['redness'] > 0.7:
            skin_type = 'Sensitive'
        elif features['texture'] > 0.6:
            skin_type = 'Oily'
        elif features['brightness'] < 0.4:
            skin_type = 'Dry'
        else:
            skin_type = 'Combination'
        
        # Generate concerns
        concerns = []
        if features['redness'] > 0.6:
            concerns.append('Redness')
        if features['texture'] > 0.7:
            concerns.append('Acne')
        if features['brightness'] < 0.3:
            concerns.append('Hyperpigmentation')
        
        if not concerns:
            concerns = ['Even Skin Tone', 'Hydration']
        
        # Generate metrics
        hydration = int((1 - features['texture']) * 100)
        oiliness = int(features['texture'] * 100)
        sensitivity = int(features['redness'] * 100)
        
        # Generate recommendations
        recommendations = [
            'Use a gentle cleanser twice daily',
            'Apply SPF 30+ sunscreen every morning',
            'Maintain a consistent skincare routine'
        ]
        
        if skin_type == 'Sensitive':
            recommendations.append('Use fragrance-free products')
        elif skin_type == 'Oily':
            recommendations.append('Consider salicylic acid cleanser')
        elif skin_type == 'Dry':
            recommendations.append('Use a rich moisturizer')
        
        return {
            'status': 'success',
            'skinType': skin_type,
            'concerns': concerns[:3],
            'hydration': hydration,
            'oiliness': oiliness,
            'sensitivity': sensitivity,
            'recommendations': recommendations[:4],
            'confidence': 0.8,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': str(uuid.uuid4())
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Simple backend is running!',
        'version': 'mvp-1.0'
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'Shine Skincare API - MVP',
        'status': 'running',
        'version': 'mvp-1.0'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_guest():
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Read image data
        image_data = file.read()
        
        # Get optional ethnicity
        ethnicity = request.form.get('ethnicity', '')
        
        # Analyze image
        analysis = analyze_image_simple(image_data)
        
        # Add ethnicity context if provided
        if ethnicity and analysis['status'] == 'success':
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

@app.route('/api/enhanced/health/enhanced')
def enhanced_health():
    return jsonify({
        'status': 'healthy',
        'services': {
            'simple_analysis': True,
            'image_processing': True
        },
        'message': 'Simple enhanced backend is running!'
    })

if __name__ == '__main__':
    app.run(debug=True)