#!/usr/bin/env python3
"""
Minimal test backend to isolate the analysis endpoint issue
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Test backend is working!'
    })

@app.route('/api/v2/analyze/guest', methods=['POST'])
def analyze_skin_guest():
    """Simple test analysis endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "No image file provided"
            }), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        # Simple analysis
        img_hash = hashlib.md5(image_data).hexdigest()
        hash_int = int(img_hash[:8], 16)
        
        skin_types = ["Normal", "Oily", "Dry", "Combination", "Sensitive"]
        skin_type = skin_types[hash_int % len(skin_types)]
        
        analysis_result = {
            "analysis_id": f"test_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "completed",
            "results": {
                "skin_type": skin_type,
                "concerns": ["Test concern"],
                "recommendations": ["Test recommendation"],
                "confidence": 0.8,
                "image_quality": "medium"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify({
            "data": analysis_result,
            "success": True,
            "message": "Test analysis completed successfully"
        })
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 