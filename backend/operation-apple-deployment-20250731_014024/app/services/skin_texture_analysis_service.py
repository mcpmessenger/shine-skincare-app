"""
🍎 Operation Apple: Skin Texture Analysis Service

This service provides advanced skin texture analysis using computer vision
and machine learning techniques to assess skin smoothness, roughness,
and overall texture quality.
"""

import os
import logging
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
import cv2
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TextureAnalysisResult:
    """Result of skin texture analysis"""
    texture_score: float  # 0.0 to 1.0 (higher = smoother)
    texture_description: str
    roughness_level: str  # 'low', 'medium', 'high'
    smoothness_percentage: float
    confidence_score: float
    analysis_quality: str  # 'excellent', 'good', 'fair', 'poor'
    features: Dict[str, Any]

class SkinTextureAnalysisService:
    """
    Advanced skin texture analysis service using computer vision techniques
    
    This service analyzes skin texture by:
    1. Detecting and measuring surface irregularities
    2. Analyzing pore distribution and size
    3. Assessing overall skin smoothness
    4. Providing texture quality scoring
    """
    
    def __init__(self):
        """Initialize the skin texture analysis service"""
        self.min_confidence = 0.6
        self.max_confidence = 0.95
        self.texture_thresholds = {
            'smooth': 0.8,
            'normal': 0.6,
            'rough': 0.4
        }
        
        logger.info("🍎 Operation Apple: SkinTextureAnalysisService initialized")
    
    def analyze_texture(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze skin texture from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing texture analysis results
        """
        try:
            logger.info("🍎 Operation Apple: Starting skin texture analysis")
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            image_array = np.array(image)
            
            # Perform texture analysis
            texture_result = self._analyze_texture_features(image_array)
            
            # Generate texture description
            description = self._generate_texture_description(texture_result)
            
            # Calculate confidence based on image quality
            confidence = self._calculate_confidence(image_array)
            
            # Create comprehensive result
            result = {
                "texture_score": float(f"{texture_result.texture_score:.3f}"),
                "texture_description": description,
                "roughness_level": texture_result.roughness_level,
                "smoothness_percentage": float(f"{texture_result.smoothness_percentage:.1f}"),
                "confidence_score": float(f"{confidence:.3f}"),
                "analysis_quality": self._assess_analysis_quality(confidence),
                "features": texture_result.features
            }
            
            logger.info(f"🍎 Operation Apple: Texture analysis completed - Score: {result['texture_score']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error during texture analysis: {e}")
            return self._get_fallback_result()
    
    def _analyze_texture_features(self, image_array: np.ndarray) -> TextureAnalysisResult:
        """
        Analyze texture features using computer vision techniques
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            TextureAnalysisResult with detailed analysis
        """
        try:
            # Convert to grayscale for texture analysis
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Calculate texture features
            features = {}
            
            # 1. Local Binary Pattern (LBP) for texture analysis
            lbp_score = self._calculate_lbp_score(blurred)
            features['lbp_score'] = lbp_score
            
            # 2. Gray Level Co-occurrence Matrix (GLCM) features
            glcm_features = self._calculate_glcm_features(blurred)
            features.update(glcm_features)
            
            # 3. Edge density analysis
            edge_density = self._calculate_edge_density(blurred)
            features['edge_density'] = edge_density
            
            # 4. Surface roughness estimation
            roughness = self._estimate_surface_roughness(blurred)
            features['roughness'] = roughness
            
            # 5. Pore detection and analysis
            pore_features = self._analyze_pores(blurred)
            features.update(pore_features)
            
            # Calculate overall texture score
            texture_score = self._calculate_overall_texture_score(features)
            
            # Determine roughness level
            roughness_level = self._determine_roughness_level(texture_score)
            
            # Calculate smoothness percentage
            smoothness_percentage = texture_score * 100
            
            return TextureAnalysisResult(
                texture_score=texture_score,
                texture_description="",  # Will be generated separately
                roughness_level=roughness_level,
                smoothness_percentage=smoothness_percentage,
                confidence_score=0.85,  # Will be calculated separately
                analysis_quality="good",
                features=features
            )
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in texture feature analysis: {e}")
            return self._get_default_texture_result()
    
    def _calculate_lbp_score(self, gray_image: np.ndarray) -> float:
        """Calculate Local Binary Pattern score for texture analysis"""
        try:
            # Simple LBP implementation
            height, width = gray_image.shape
            lbp_image = np.zeros((height, width), dtype=np.uint8)
            
            for i in range(1, height-1):
                for j in range(1, width-1):
                    center = gray_image[i, j]
                    code = 0
                    code |= (gray_image[i-1, j-1] > center) << 7
                    code |= (gray_image[i-1, j] > center) << 6
                    code |= (gray_image[i-1, j+1] > center) << 5
                    code |= (gray_image[i, j+1] > center) << 4
                    code |= (gray_image[i+1, j+1] > center) << 3
                    code |= (gray_image[i+1, j] > center) << 2
                    code |= (gray_image[i+1, j-1] > center) << 1
                    code |= (gray_image[i, j-1] > center) << 0
                    lbp_image[i, j] = code
            
            # Calculate LBP histogram and score
            hist = cv2.calcHist([lbp_image], [0], None, [256], [0, 256])
            hist = hist.flatten() / hist.sum()
            
            # Higher uniformity = smoother texture
            uniformity = np.sum(hist ** 2)
            return min(uniformity, 1.0)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in LBP calculation: {e}")
            return 0.5
    
    def _calculate_glcm_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Calculate Gray Level Co-occurrence Matrix features"""
        try:
            # Simplified GLCM calculation
            height, width = gray_image.shape
            glcm = np.zeros((256, 256), dtype=np.float32)
            
            # Calculate GLCM for horizontal direction
            for i in range(height):
                for j in range(width-1):
                    glcm[gray_image[i, j], gray_image[i, j+1]] += 1
            
            # Normalize
            glcm /= glcm.sum()
            
            # Calculate features
            contrast = np.sum(glcm * np.square(np.arange(256)[:, None] - np.arange(256)))
            homogeneity = np.sum(glcm / (1 + np.square(np.arange(256)[:, None] - np.arange(256))))
            energy = np.sum(glcm ** 2)
            
            return {
                'glcm_contrast': float(contrast),
                'glcm_homogeneity': float(homogeneity),
                'glcm_energy': float(energy)
            }
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in GLCM calculation: {e}")
            return {
                'glcm_contrast': 0.5,
                'glcm_homogeneity': 0.5,
                'glcm_energy': 0.5
            }
    
    def _calculate_edge_density(self, gray_image: np.ndarray) -> float:
        """Calculate edge density as a measure of texture complexity"""
        try:
            # Apply Canny edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Calculate edge density
            edge_pixels = np.count_nonzero(edges)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_density = edge_pixels / total_pixels
            
            return float(edge_density)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in edge density calculation: {e}")
            return 0.1
    
    def _estimate_surface_roughness(self, gray_image: np.ndarray) -> float:
        """Estimate surface roughness using gradient analysis"""
        try:
            # Calculate gradients
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Roughness is inversely proportional to smoothness
            roughness = np.mean(gradient_magnitude) / 255.0
            
            return float(min(roughness, 1.0))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in roughness estimation: {e}")
            return 0.3
    
    def _analyze_pores(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Analyze pore distribution and characteristics"""
        try:
            # Apply morphological operations to detect pores
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            opened = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
            
            # Find contours (potential pores)
            _, thresh = cv2.threshold(opened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size (pores are typically small)
            pore_contours = [c for c in contours if cv2.contourArea(c) < 100]
            
            pore_count = len(pore_contours)
            pore_density = pore_count / (gray_image.shape[0] * gray_image.shape[1]) * 10000
            
            return {
                'pore_count': pore_count,
                'pore_density': float(pore_density),
                'pore_size_distribution': 'small' if pore_density < 50 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pore analysis: {e}")
            return {
                'pore_count': 0,
                'pore_density': 0.0,
                'pore_size_distribution': 'unknown'
            }
    
    def _calculate_overall_texture_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall texture score from all features"""
        try:
            # Weighted combination of features
            weights = {
                'lbp_score': 0.3,
                'glcm_homogeneity': 0.25,
                'glcm_energy': 0.2,
                'edge_density': 0.15,
                'roughness': 0.1
            }
            
            score = 0.0
            total_weight = 0.0
            
            for feature, weight in weights.items():
                if feature in features:
                    # Normalize feature values
                    if feature == 'edge_density':
                        # Lower edge density = smoother
                        normalized_value = 1.0 - min(features[feature], 1.0)
                    elif feature == 'roughness':
                        # Lower roughness = smoother
                        normalized_value = 1.0 - features[feature]
                    else:
                        # Higher values = smoother for other features
                        normalized_value = min(features[feature], 1.0)
                    
                    score += normalized_value * weight
                    total_weight += weight
            
            if total_weight > 0:
                final_score = score / total_weight
            else:
                final_score = 0.5
            
            return float(max(0.0, min(1.0, final_score)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in texture score calculation: {e}")
            return 0.5
    
    def _determine_roughness_level(self, texture_score: float) -> str:
        """Determine roughness level based on texture score"""
        if texture_score >= self.texture_thresholds['smooth']:
            return 'low'
        elif texture_score >= self.texture_thresholds['normal']:
            return 'medium'
        else:
            return 'high'
    
    def _generate_texture_description(self, result: TextureAnalysisResult) -> str:
        """Generate human-readable texture description"""
        try:
            score = result.texture_score
            
            if score >= 0.8:
                return "Exceptionally smooth with minimal texture irregularities"
            elif score >= 0.6:
                return "Smooth with fine texture and minimal roughness"
            elif score >= 0.4:
                return "Moderate texture with some surface irregularities"
            else:
                return "Rough texture with noticeable surface irregularities"
                
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error generating texture description: {e}")
            return "Texture analysis completed"
    
    def _calculate_confidence(self, image_array: np.ndarray) -> float:
        """Calculate confidence score based on image quality"""
        try:
            # Simple confidence calculation based on image properties
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Check image sharpness
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)
            
            # Check image brightness
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # Combined confidence
            confidence = (sharpness_score + brightness_score) / 2.0
            
            return float(max(0.5, min(0.95, confidence)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in confidence calculation: {e}")
            return 0.7
    
    def _assess_analysis_quality(self, confidence: float) -> str:
        """Assess the quality of the analysis based on confidence"""
        if confidence >= 0.9:
            return "excellent"
        elif confidence >= 0.8:
            return "good"
        elif confidence >= 0.7:
            return "fair"
        else:
            return "poor"
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Return fallback result when analysis fails"""
        return {
            "texture_score": 0.5,
            "texture_description": "Analysis unavailable - please try again",
            "roughness_level": "unknown",
            "smoothness_percentage": 50.0,
            "confidence_score": 0.0,
            "analysis_quality": "poor",
            "features": {}
        }
    
    def _get_default_texture_result(self) -> TextureAnalysisResult:
        """Return default texture result for error cases"""
        return TextureAnalysisResult(
            texture_score=0.5,
            texture_description="Default texture analysis",
            roughness_level="medium",
            smoothness_percentage=50.0,
            confidence_score=0.5,
            analysis_quality="fair",
            features={}
        ) 