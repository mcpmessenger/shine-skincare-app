#!/usr/bin/env python3
"""
Enhanced Face Detection for Shine Skincare App
Provides robust face detection functionality
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enhanced_face_detector(image_data: str, confidence_threshold: float = 0.3) -> Dict:
    """
    Enhanced face detection with multiple detection methods
    """
    try:
        # Decode base64 image
        import base64
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {
                'success': False,
                'error': 'Failed to decode image',
                'faces_detected': 0,
                'confidence': 0.0
            }

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load face cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            return {
                'success': False,
                'error': 'Failed to load face detection model',
                'faces_detected': 0,
                'confidence': 0.0
            }

        # Detect faces with more lenient parameters for better detection
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,  # More sensitive scaling
            minNeighbors=3,    # Lower threshold for detection
            minSize=(20, 20)   # Smaller minimum face size
        )
        
        logger.info(f"🔍 Face detection: Found {len(faces)} potential faces")
        logger.info(f"🔍 Image dimensions: {image.shape[1]}x{image.shape[0]}")
        logger.info(f"🔍 Confidence threshold: {confidence_threshold}")

        if len(faces) == 0:
            return {
                'success': True,
                'faces_detected': 0,
                'confidence': 0.0,
                'message': 'No faces detected'
            }

        # Process detected faces
        face_results = []
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            
            # Calculate confidence based on face size and position (more lenient)
            face_area = w * h
            image_area = image.shape[0] * image.shape[1]
            confidence = min(1.0, (face_area / image_area) * 15)  # Increased multiplier for higher confidence
            
            logger.info(f"🔍 Face {len(face_results)+1}: bbox=({x},{y},{w},{h}), confidence={confidence:.3f}")
            
            if confidence >= confidence_threshold:
                face_results.append({
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'confidence': float(confidence),
                    'center': [int(x + w/2), int(y + h/2)]
                })
                logger.info(f"✅ Face {len(face_results)} accepted with confidence {confidence:.3f}")
            else:
                logger.info(f"❌ Face rejected: confidence {confidence:.3f} < threshold {confidence_threshold}")

        return {
            'success': True,
            'faces_detected': len(face_results),
            'confidence': max([f['confidence'] for f in face_results]) if face_results else 0.0,
            'faces': face_results,
            'image_dimensions': [image.shape[1], image.shape[0]]
        }

    except Exception as e:
        logger.error(f"❌ Face detection error: {e}")
        return {
            'success': False,
            'error': str(e),
            'faces_detected': 0,
            'confidence': 0.0
        } 