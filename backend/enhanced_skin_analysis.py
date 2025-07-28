import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class EnhancedSkinAnalyzer:
    """Enhanced skin analyzer that performs basic image analysis without external APIs"""
    
    def __init__(self):
        self.skin_types = {
            'oily': {'description': 'Excess oil production, shiny appearance'},
            'dry': {'description': 'Lack of moisture, flaky patches'},
            'combination': {'description': 'Mix of oily and dry areas'},
            'normal': {'description': 'Balanced oil and moisture levels'},
            'sensitive': {'description': 'Easily irritated, reactive skin'}
        }
        
        self.skin_concerns = {
            'acne': 'Breakouts and blemishes',
            'hyperpigmentation': 'Dark spots and uneven tone',
            'fine_lines': 'Early signs of aging',
            'dryness': 'Lack of moisture',
            'redness': 'Inflammation or irritation',
            'large_pores': 'Visible pore size',
            'sun_damage': 'UV damage and spots'
        }
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze skin from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return self._get_fallback_analysis()
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Analyze image characteristics
            analysis = {
                'image_analysis': self._analyze_image_properties(img_rgb),
                'skin_characteristics': self._analyze_skin_characteristics(img_rgb),
                'detected_concerns': self._detect_skin_concerns(img_rgb),
                'recommendations': []
            }
            
            # Generate skin type based on analysis
            skin_type = self._determine_skin_type(analysis)
            analysis['skin_type'] = skin_type
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(skin_type, analysis['detected_concerns'])
            
            # Calculate confidence based on image quality
            analysis['confidence'] = self._calculate_confidence(analysis['image_analysis'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _analyze_image_properties(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze basic image properties"""
        height, width = img.shape[:2]
        
        # Calculate brightness
        brightness = np.mean(img)
        
        # Calculate contrast
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        contrast = np.std(gray)
        
        # Calculate color distribution
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        saturation = np.mean(hsv[:, :, 1])
        value = np.mean(hsv[:, :, 2])
        
        return {
            'width': width,
            'height': height,
            'brightness': float(brightness),
            'contrast': float(contrast),
            'saturation': float(saturation),
            'value': float(value),
            'aspect_ratio': width / height if height > 0 else 1.0
        }
    
    def _analyze_skin_characteristics(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze skin-specific characteristics"""
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        
        # Analyze skin tone
        skin_tone = self._analyze_skin_tone(lab)
        
        # Analyze texture
        texture = self._analyze_texture(img)
        
        # Analyze oiliness (brightness in specific ranges)
        oiliness = self._analyze_oiliness(hsv)
        
        return {
            'skin_tone': skin_tone,
            'texture': texture,
            'oiliness': oiliness,
            'overall_quality': self._assess_image_quality(img)
        }
    
    def _analyze_skin_tone(self, lab_img: np.ndarray) -> Dict[str, Any]:
        """Analyze skin tone using LAB color space"""
        # L channel represents lightness
        l_channel = lab_img[:, :, 0]
        
        # Calculate average lightness
        avg_lightness = np.mean(l_channel)
        
        # Determine skin tone category
        if avg_lightness < 50:
            tone_category = 'dark'
        elif avg_lightness < 70:
            tone_category = 'medium'
        else:
            tone_category = 'light'
        
        return {
            'category': tone_category,
            'lightness': float(avg_lightness),
            'range': 'low' if avg_lightness < 50 else 'medium' if avg_lightness < 70 else 'high'
        }
    
    def _analyze_texture(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze skin texture using edge detection"""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Calculate texture metrics
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Determine texture category
        if edge_density < 0.01:
            texture_type = 'smooth'
        elif edge_density < 0.03:
            texture_type = 'normal'
        else:
            texture_type = 'rough'
        
        return {
            'type': texture_type,
            'density': float(edge_density),
            'smoothness': 1.0 - float(edge_density)
        }
    
    def _analyze_oiliness(self, hsv_img: np.ndarray) -> Dict[str, Any]:
        """Analyze oiliness based on brightness and saturation"""
        # V channel represents brightness
        v_channel = hsv_img[:, :, 2]
        s_channel = hsv_img[:, :, 1]
        
        # High brightness and low saturation can indicate oiliness
        avg_brightness = np.mean(v_channel)
        avg_saturation = np.mean(s_channel)
        
        # Calculate oiliness score
        oiliness_score = (avg_brightness / 255.0) * (1.0 - avg_saturation / 255.0)
        
        if oiliness_score < 0.3:
            oiliness_level = 'low'
        elif oiliness_score < 0.6:
            oiliness_level = 'medium'
        else:
            oiliness_level = 'high'
        
        return {
            'level': oiliness_level,
            'score': float(oiliness_score),
            'brightness': float(avg_brightness),
            'saturation': float(avg_saturation)
        }
    
    def _detect_skin_concerns(self, img: np.ndarray) -> List[str]:
        """Detect potential skin concerns based on image analysis"""
        concerns = []
        
        # Analyze for redness (inflammation)
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        red_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        red_ratio = np.sum(red_mask > 0) / (red_mask.shape[0] * red_mask.shape[1])
        
        if red_ratio > 0.1:
            concerns.append('redness')
        
        # Analyze for dark spots (hyperpigmentation)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        dark_spots = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        dark_ratio = np.sum(dark_spots > 0) / (dark_spots.shape[0] * dark_spots.shape[1])
        
        if dark_ratio > 0.05:
            concerns.append('hyperpigmentation')
        
        # Analyze for texture issues
        texture = self._analyze_texture(img)
        if texture['type'] == 'rough':
            concerns.append('texture_issues')
        
        # Analyze for oiliness
        oiliness = self._analyze_oiliness(hsv)
        if oiliness['level'] == 'high':
            concerns.append('excess_oil')
        elif oiliness['level'] == 'low':
            concerns.append('dryness')
        
        return concerns
    
    def _determine_skin_type(self, analysis: Dict[str, Any]) -> str:
        """Determine skin type based on analysis"""
        concerns = analysis['detected_concerns']
        oiliness = analysis['skin_characteristics']['oiliness']['level']
        
        if 'excess_oil' in concerns:
            return 'oily'
        elif 'dryness' in concerns:
            return 'dry'
        elif 'excess_oil' in concerns and 'dryness' in concerns:
            return 'combination'
        elif 'redness' in concerns:
            return 'sensitive'
        else:
            return 'normal'
    
    def _generate_recommendations(self, skin_type: str, concerns: List[str]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Base recommendations by skin type
        if skin_type == 'oily':
            recommendations.extend([
                'Gentle foaming cleanser',
                'Oil-free moisturizer',
                'Clay mask 1-2 times per week'
            ])
        elif skin_type == 'dry':
            recommendations.extend([
                'Cream-based cleanser',
                'Rich moisturizer with hyaluronic acid',
                'Facial oil for extra hydration'
            ])
        elif skin_type == 'combination':
            recommendations.extend([
                'Balanced cleanser',
                'Lightweight moisturizer',
                'Targeted treatments for different areas'
            ])
        elif skin_type == 'sensitive':
            recommendations.extend([
                'Fragrance-free cleanser',
                'Calming moisturizer',
                'Minimal ingredient products'
            ])
        else:  # normal
            recommendations.extend([
                'Gentle daily cleanser',
                'Lightweight moisturizer',
                'Regular sunscreen'
            ])
        
        # Add concern-specific recommendations
        if 'hyperpigmentation' in concerns:
            recommendations.append('Vitamin C serum for brightening')
        if 'redness' in concerns:
            recommendations.append('Centella or aloe-based products')
        if 'excess_oil' in concerns:
            recommendations.append('Niacinamide serum')
        if 'dryness' in concerns:
            recommendations.append('Hyaluronic acid serum')
        
        return recommendations
    
    def _calculate_confidence(self, image_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score based on image quality"""
        # Base confidence on image quality metrics
        brightness = image_analysis['brightness']
        contrast = image_analysis['contrast']
        
        # Normalize metrics
        brightness_score = min(brightness / 128.0, 1.0)  # Optimal around 128
        contrast_score = min(contrast / 50.0, 1.0)  # Good contrast around 50
        
        # Calculate overall confidence
        confidence = (brightness_score + contrast_score) / 2.0
        
        # Ensure confidence is between 0.5 and 0.95
        confidence = max(0.5, min(0.95, confidence))
        
        return confidence
    
    def _assess_image_quality(self, img: np.ndarray) -> str:
        """Assess overall image quality"""
        height, width = img.shape[:2]
        
        # Check resolution
        if width < 300 or height < 300:
            return 'low'
        elif width < 800 or height < 800:
            return 'medium'
        else:
            return 'high'
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when image processing fails"""
        return {
            'skin_type': 'combination',
            'detected_concerns': ['hyperpigmentation'],
            'recommendations': [
                'Gentle cleanser',
                'Vitamin C serum',
                'Non-comedogenic moisturizer'
            ],
            'confidence': 0.5,
            'image_analysis': {
                'quality': 'unknown',
                'brightness': 0,
                'contrast': 0
            },
            'skin_characteristics': {
                'skin_tone': {'category': 'medium'},
                'texture': {'type': 'normal'},
                'oiliness': {'level': 'medium'}
            }
        } 