#!/usr/bin/env python3
"""
Enhanced Image Processing for Shine Skincare App
Provides robust image decoding and validation for face detection
"""

import base64
import numpy as np
import cv2
from PIL import Image
import io
import logging
import traceback
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Enhanced image processing with multiple decoding strategies"""
    
    @staticmethod
    def decode_base64_image(image_data: str) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """
        Decode base64 image data with multiple fallback strategies
        
        Returns:
            Tuple of (image_array, metadata) where image_array is None if decoding failed
        """
        metadata = {
            'original_size': len(image_data),
            'decoding_method': None,
            'image_format': None,
            'dimensions': None,
            'channels': None,
            'error': None
        }
        
        try:
            # Clean the image data - remove data URL prefix if present
            clean_image_data = image_data
            if ',' in image_data:
                clean_image_data = image_data.split(',')[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(clean_image_data)
            metadata['decoded_size'] = len(image_bytes)
            
            # Strategy 1: Try OpenCV decoding (fastest)
            try:
                nparr = np.frombuffer(image_bytes, np.uint8)
                img_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img_array is not None and img_array.size > 0:
                    metadata['decoding_method'] = 'opencv'
                    metadata['dimensions'] = (img_array.shape[1], img_array.shape[0])
                    metadata['channels'] = img_array.shape[2] if len(img_array.shape) > 2 else 1
                    logger.info(f"Successfully decoded image using OpenCV: {metadata['dimensions']}")
                    return img_array, metadata
                else:
                    logger.warning("OpenCV decoding returned None or empty array")
            except Exception as e:
                logger.warning(f"OpenCV decoding failed: {e}")
            
            # Strategy 2: Try PIL/Pillow decoding (more robust)
            try:
                image_stream = io.BytesIO(image_bytes)
                pil_image = Image.open(image_stream)
                
                # Get image format
                metadata['image_format'] = pil_image.format
                metadata['dimensions'] = pil_image.size
                
                # Convert to RGB if necessary
                if pil_image.mode == 'RGBA':
                    # Convert RGBA to RGB with white background
                    background = Image.new('RGB', pil_image.size, (255, 255, 255))
                    background.paste(pil_image, mask=pil_image.split()[-1])
                    pil_image = background
                elif pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Convert PIL Image to numpy array
                img_array = np.array(pil_image)
                
                # Convert RGB to BGR for OpenCV compatibility
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                metadata['decoding_method'] = 'pillow'
                metadata['channels'] = img_array.shape[2] if len(img_array.shape) > 2 else 1
                logger.info(f"Successfully decoded image using Pillow: {metadata['dimensions']}")
                return img_array, metadata
                
            except Exception as e:
                logger.warning(f"Pillow decoding failed: {e}")
            
            # Strategy 3: Try raw numpy decoding (last resort)
            try:
                # This is a very basic fallback that might work for some raw formats
                nparr = np.frombuffer(image_bytes, dtype=np.uint8)
                
                # Try to reshape as a square image (this is speculative)
                size = int(np.sqrt(len(nparr) / 3))
                if size * size * 3 == len(nparr):
                    img_array = nparr.reshape((size, size, 3))
                    metadata['decoding_method'] = 'numpy_raw'
                    metadata['dimensions'] = (size, size)
                    metadata['channels'] = 3
                    logger.info(f"Successfully decoded image using raw numpy: {metadata['dimensions']}")
                    return img_array, metadata
            except Exception as e:
                logger.warning(f"Raw numpy decoding failed: {e}")
            
            # All strategies failed
            metadata['error'] = 'All decoding strategies failed'
            logger.error(f"Failed to decode image with all strategies. Original size: {len(image_data)}, Decoded size: {len(image_bytes)}")
            return None, metadata
            
        except Exception as e:
            metadata['error'] = f'Base64 decoding failed: {str(e)}'
            logger.error(f"Base64 decoding failed: {e}")
            return None, metadata
    
    @staticmethod
    def validate_image(img_array: np.ndarray) -> Dict[str, Any]:
        """Validate decoded image and return quality metrics"""
        validation = {
            'is_valid': False,
            'width': 0,
            'height': 0,
            'channels': 0,
            'total_pixels': 0,
            'is_too_small': False,
            'is_too_large': False,
            'has_valid_dimensions': False,
            'estimated_quality': 'unknown'
        }
        
        try:
            if img_array is None or img_array.size == 0:
                return validation
            
            height, width = img_array.shape[:2]
            channels = img_array.shape[2] if len(img_array.shape) > 2 else 1
            total_pixels = width * height
            
            validation.update({
                'width': width,
                'height': height,
                'channels': channels,
                'total_pixels': total_pixels,
                'is_too_small': width < 100 or height < 100,
                'is_too_large': width > 4000 or height > 4000,
                'has_valid_dimensions': 100 <= width <= 4000 and 100 <= height <= 4000
            })
            
            # Estimate image quality based on various factors
            if validation['has_valid_dimensions'] and channels >= 3:
                # Calculate image sharpness (Laplacian variance)
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if channels > 1 else img_array
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                if laplacian_var > 500:
                    validation['estimated_quality'] = 'high'
                elif laplacian_var > 100:
                    validation['estimated_quality'] = 'medium'
                else:
                    validation['estimated_quality'] = 'low'
                
                validation['is_valid'] = True
            
            return validation
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            validation['error'] = str(e)
            return validation

# Enhanced face detection endpoint function
def enhanced_face_detect_endpoint(image_data: str) -> Dict[str, Any]:
    """Enhanced face detection with robust image processing"""
    try:
        # Use enhanced image processing
        img_array, metadata = ImageProcessor.decode_base64_image(image_data)
        
        if img_array is None:
            return {
                'success': False,
                'error': 'Failed to decode image',
                'details': metadata.get('error', 'Unknown decoding error'),
                'metadata': metadata
            }
        
        # Validate the decoded image
        validation = ImageProcessor.validate_image(img_array)
        
        if not validation['is_valid']:
            return {
                'success': False,
                'error': 'Invalid image',
                'details': 'Image failed validation checks',
                'validation': validation,
                'metadata': metadata
            }
        
        # Import face detection here to avoid circular imports
        from enhanced_face_detection_fixed import enhanced_face_detector as robust_face_detector
        
        # Proceed with face detection using the validated image
        face_detection_result = robust_face_detector(image_data)
        
        # Extract face bounds from the detection result
        face_bounds = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        if face_detection_result.get('faces') and len(face_detection_result['faces']) > 0:
            # Get the first (and presumably largest) face
            first_face = face_detection_result['faces'][0]
            bbox = first_face.get('bbox', [0, 0, 0, 0])
            face_bounds = {
                'x': bbox[0],
                'y': bbox[1], 
                'width': bbox[2],
                'height': bbox[3]
            }
        
        # Include processing metadata in response
        response_data = {
            'success': True,
            'face_detected': face_detection_result.get('faces_detected', 0) > 0,
            'confidence': face_detection_result.get('confidence', 0.0),
            'face_bounds': face_bounds,
            'quality_metrics': face_detection_result.get('quality_metrics', {}),
            'processing_metadata': {
                'decoding_method': metadata['decoding_method'],
                'image_format': metadata.get('image_format'),
                'dimensions': metadata['dimensions'],
                'validation': validation
            }
        }
        
        if response_data['face_detected']:
            response_data['guidance'] = {
                'message': 'Face detected successfully',
                'method': face_detection_result.get('method', 'enhanced_face_detection'),
                'suggestions': [
                    'Ensure good lighting for better analysis',
                    'Keep face centered in the frame',
                    'Avoid shadows and reflections'
                ]
            }
        else:
            response_data['guidance'] = {
                'message': 'No face detected',
                'method': face_detection_result.get('method', 'enhanced_face_detection'),
                'suggestions': [
                    'Ensure a face is clearly visible in the image',
                    'Try adjusting lighting conditions',
                    'Make sure the face is not too small or too large',
                    'Avoid extreme angles or partial occlusion'
                ]
            }
        
        return response_data
        
    except Exception as e:
        logger.error(f"Enhanced face detection error: {e}")
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': f'Face detection failed: {str(e)}',
            'status': 'error'
        } 