#!/usr/bin/env python3
""" Enhanced Face Detection for Shine Skincare App
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
        image_bytes = base64.b64decode(image_data.split(
            
        )[1] if 
            
         in image_data else image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

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

        logger.info(f"Face detection: Found {len(faces)} potential faces")
        logger.info(f"Image dimensions: {image.shape[1]}x{image.shape[0]}")

        detected_faces = []
        for (x, y, w, h) in faces:
            # Calculate confidence based on face size relative to image size
            # This is a simplistic confidence score; more advanced methods would use model scores
            confidence = (w * h) / (image.shape[0] * image.shape[1])
            if confidence >= confidence_threshold:
                detected_faces.append({
                    'box': [int(x), int(y), int(w), int(h)],
                    'confidence': float(confidence)
                })

        logger.info(f"Filtered faces (confidence >= {confidence_threshold}): {len(detected_faces)}")

        return {
            'success': True,
            'faces': detected_faces,
            'faces_detected': len(detected_faces),
            'confidence': sum([f['confidence'] for f in detected_faces]) / len(detected_faces) if detected_faces else 0.0
        }

    except Exception as e:
        logger.error(f"Error during face detection: {e}\n{traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'faces_detected': 0,
            'confidence': 0.0
        }


