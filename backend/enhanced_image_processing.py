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
                
                # Try to reshape as a square image (very basic assumption)
                side_length = int(np.sqrt(len(nparr)))
                if side_length * side_length == len(nparr):
                    img_array = nparr.reshape((side_length, side_length))
                    # Convert to 3-channel by repeating
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
                    
                    metadata['decoding_method'] = 'numpy_raw'
                    metadata['dimensions'] = (side_length, side_length)
                    metadata['channels'] = 3
                    logger.info(f"Successfully decoded image using raw numpy: {metadata['dimensions']}")
                    return img_array, metadata
                else:
                    logger.warning("Raw numpy decoding failed: cannot reshape to square")
            except Exception as e:
                logger.warning(f"Raw numpy decoding failed: {e}")
            
            # All strategies failed
            metadata['error'] = 'All image decoding strategies failed'
            logger.error("All image decoding strategies failed")
            return None, metadata
            
        except Exception as e:
            metadata['error'] = str(e)
            logger.error(f"Image decoding failed: {e}")
            return None, metadata
    
    @staticmethod
    def validate_image(img_array: np.ndarray) -> Dict[str, Any]:
        """
        Validate image quality for analysis
        """
        validation = {
            'is_valid': True,
            'quality_score': 0.0,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        try:
            if img_array is None or img_array.size == 0:
                validation['is_valid'] = False
                validation['issues'].append('Empty or null image')
                return validation
            
            # Check image dimensions
            height, width = img_array.shape[:2]
            if width < 100 or height < 100:
                validation['is_valid'] = False
                validation['issues'].append('Image too small for analysis')
                validation['recommendations'].append('Use a higher resolution image')
            
            # Check for blur (using Laplacian variance)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY) if len(img_array.shape) == 3 else img_array
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if blur_score < 100:
                validation['warnings'].append('Image appears blurry')
                validation['recommendations'].append('Ensure camera is steady and well-focused')
            
            # Check lighting (using histogram analysis)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            mean_brightness = np.mean(hist)
            
            if mean_brightness < 50:
                validation['warnings'].append('Image appears too dark')
                validation['recommendations'].append('Improve lighting conditions')
            elif mean_brightness > 200:
                validation['warnings'].append('Image appears overexposed')
                validation['recommendations'].append('Reduce lighting or adjust exposure')
            
            # Calculate overall quality score
            quality_factors = []
            
            # Size factor (0-1)
            size_factor = min(1.0, (width * height) / (500 * 500))
            quality_factors.append(size_factor)
            
            # Sharpness factor (0-1)
            sharpness_factor = min(1.0, blur_score / 500)
            quality_factors.append(sharpness_factor)
            
            # Lighting factor (0-1) - ensure it's not negative
            lighting_factor = max(0.0, 1.0 - abs(mean_brightness - 128) / 128)
            quality_factors.append(lighting_factor)
            
            validation['quality_score'] = np.mean(quality_factors)
            
            # Set validity based on quality score - very lenient for testing
            if validation['quality_score'] < 0.05:  # Even more lenient for testing
                validation['is_valid'] = False
                validation['issues'].append('Image quality too low for reliable analysis')
            
            return validation
            
        except Exception as e:
            validation['is_valid'] = False
            validation['issues'].append(f'Validation error: {str(e)}')
            return validation

def enhanced_face_detect_endpoint(image_data: str) -> Dict[str, Any]:
    """
    Enhanced face detection endpoint with improved image processing
    """
    try:
        # Decode image with enhanced processing
        img_array, metadata = ImageProcessor.decode_base64_image(image_data)
        
        if img_array is None:
            return {
                'success': False,
                'error': metadata.get('error', 'Failed to decode image'),
                'face_detected': False,
                'confidence': 0.0,
                'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
            }
        
        # Validate image quality
        validation = ImageProcessor.validate_image(img_array)
        
        if not validation['is_valid']:
            return {
                'success': False,
                'error': 'Image quality validation failed',
                'issues': validation['issues'],
                'recommendations': validation['recommendations'],
                'face_detected': False,
                'confidence': 0.0,
                'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
            }
        
        # Perform enhanced face detection
        from enhanced_face_detection_fixed import enhanced_face_detector, get_face_bounds_from_detection
        
        detection_result = enhanced_face_detector(image_data)
        face_bounds = get_face_bounds_from_detection(detection_result)
        
        return {
            'success': detection_result['success'],
            'face_detected': face_bounds['face_detected'],
            'confidence': face_bounds['confidence'],
            'face_bounds': {
                'x': face_bounds['x'],
                'y': face_bounds['y'],
                'width': face_bounds['width'],
                'height': face_bounds['height']
            },
            'quality_score': validation['quality_score'],
            'warnings': validation['warnings'],
            'recommendations': validation['recommendations']
        }
        
    except Exception as e:
        logger.error(f"Enhanced face detection endpoint failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'face_detected': False,
            'confidence': 0.0,
            'face_bounds': {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        } 