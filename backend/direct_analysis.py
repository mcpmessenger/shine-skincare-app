#!/usr/bin/env python3
"""
Direct Analysis Script
Bypasses Flask server and directly uses enhanced analysis algorithms
"""

import numpy as np
import cv2
import base64
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
from scaled_dataset_manager import ScaledDatasetManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_skin_directly(image_data_base64: str) -> dict:
    """
    Analyze skin directly without Flask server
    
    Args:
        image_data_base64: Base64 encoded image data
        
    Returns:
        Analysis results
    """
    try:
        # Decode base64 image
        if image_data_base64.startswith('data:image'):
            image_data_base64 = image_data_base64.split(',')[1]
        
        image_bytes = base64.b64decode(image_data_base64)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_array = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
        
        # Convert to BGR for OpenCV
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Initialize analyzers
        skin_analyzer = EnhancedSkinAnalyzer()
        dataset_manager = ScaledDatasetManager()
        
        # Perform face detection
        logger.info("🔍 Starting face detection...")
        face_analysis = skin_analyzer.analyze_face_detection(image_array_bgr)
        logger.info(f"✅ Face detection completed: {face_analysis.get('face_detected')}")
        
        # Get face ROI if detected
        face_roi = None
        if face_analysis.get('face_detected'):
            face_bounds = face_analysis.get('face_bounds', {})
            x, y, w, h = face_bounds.get('x', 0), face_bounds.get('y', 0), face_bounds.get('width', 0), face_bounds.get('height', 0)
            if w > 0 and h > 0:
                face_roi = image_array_bgr[y:y+h, x:x+w]
        
        # Perform skin analysis
        logger.info("🔍 Starting skin conditions analysis...")
        skin_analysis = skin_analyzer.analyze_skin_conditions(image_array_bgr, face_roi)
        logger.info(f"✅ Skin analysis completed: health_score={skin_analysis.get('health_score', 0)}")
        
        # Generate enhanced embedding
        logger.info("🧠 Generating enhanced embedding...")
        try:
            embedding_result = dataset_manager.generate_enhanced_embedding(image_bytes)
            logger.info("✅ Enhanced embedding generated successfully")
        except Exception as e:
            logger.warning(f"⚠️ Enhanced embedding failed: {e}")
            embedding_result = {
                'embedding': [],
                'dataset_used': 'fallback',
                'confidence_score': 0.1
            }
        
        # Compile results
        result = {
            'status': 'success',
            'face_detection': face_analysis,
            'skin_conditions': skin_analysis,
            'enhanced_embedding': embedding_result,
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        logger.info("✅ Analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'face_detection': {'face_detected': False, 'error': str(e)},
            'skin_conditions': {'health_score': 0, 'error': str(e)},
            'enhanced_embedding': {'embedding': [], 'error': str(e)}
        }

if __name__ == '__main__':
    # Test with a random image
    print("🧪 Testing direct analysis...")
    
    # Create a test image
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', test_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Analyze
    result = analyze_skin_directly(img_base64)
    
    print("📊 Results:")
    print(f"Status: {result.get('status')}")
    print(f"Face detected: {result.get('face_detection', {}).get('face_detected')}")
    print(f"Health score: {result.get('skin_conditions', {}).get('health_score', 0)}")
    print(f"Primary concerns: {result.get('skin_conditions', {}).get('primary_concerns', [])}")
    print(f"Embedding confidence: {result.get('enhanced_embedding', {}).get('confidence_score', 0)}") 