"""
🍎 Operation Apple: Pigmentation Analysis Service

This service provides advanced pigmentation analysis using computer vision
techniques to assess skin color uniformity, spots, and discoloration.
"""

import os
import logging
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple
import cv2
from dataclasses import dataclass
import math
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

@dataclass
class PigmentationAnalysisResult:
    """Result of pigmentation analysis"""
    overall_evenness: float  # 0.0 to 1.0 (higher = more even)
    spots_count: int
    discoloration_level: float  # 0.0 to 1.0
    color_uniformity: float  # 0.0 to 1.0
    pigmentation_pattern: str  # 'uniform', 'patchy', 'spotted'
    confidence_score: float
    analysis_quality: str
    features: Dict[str, Any]

class PigmentationAnalysisService:
    """
    Advanced pigmentation analysis service using computer vision techniques
    
    This service analyzes pigmentation by:
    1. Detecting color variations and spots
    2. Assessing skin color uniformity
    3. Analyzing discoloration patterns
    4. Providing pigmentation quality scoring
    """
    
    def __init__(self):
        """Initialize the pigmentation analysis service"""
        self.evenness_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
        
        self.spot_detection_params = {
            'min_area': 10,
            'max_area': 1000,
            'color_threshold': 30
        }
        
        logger.info("🍎 Operation Apple: PigmentationAnalysisService initialized")
    
    def analyze_pigmentation(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze pigmentation from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing pigmentation analysis results
        """
        try:
            logger.info("🍎 Operation Apple: Starting pigmentation analysis")
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            image_array = np.array(image)
            
            # Perform pigmentation analysis
            pigmentation_result = self._analyze_pigmentation_features(image_array)
            
            # Calculate confidence based on image quality
            confidence = self._calculate_confidence(image_array)
            
            # Create comprehensive result
            result = {
                "overall_evenness": float(f"{pigmentation_result.overall_evenness:.3f}"),
                "spots_count": pigmentation_result.spots_count,
                "discoloration_level": float(f"{pigmentation_result.discoloration_level:.3f}"),
                "color_uniformity": float(f"{pigmentation_result.color_uniformity:.3f}"),
                "pigmentation_pattern": pigmentation_result.pigmentation_pattern,
                "confidence_score": float(f"{confidence:.3f}"),
                "analysis_quality": self._assess_analysis_quality(confidence),
                "features": pigmentation_result.features
            }
            
            logger.info(f"🍎 Operation Apple: Pigmentation analysis completed - Evenness: {result['overall_evenness']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error during pigmentation analysis: {e}")
            return self._get_fallback_result()
    
    def _analyze_pigmentation_features(self, image_array: np.ndarray) -> PigmentationAnalysisResult:
        """
        Analyze pigmentation features using computer vision techniques
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            PigmentationAnalysisResult with detailed analysis
        """
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            
            # Analyze color uniformity
            color_uniformity = self._analyze_color_uniformity(image_array)
            
            # Detect spots and discoloration
            spots_count, discoloration_level = self._detect_spots_and_discoloration(image_array)
            
            # Calculate overall evenness
            overall_evenness = self._calculate_overall_evenness(color_uniformity, discoloration_level)
            
            # Determine pigmentation pattern
            pattern = self._determine_pigmentation_pattern(overall_evenness, spots_count)
            
            # Create result
            return PigmentationAnalysisResult(
                overall_evenness=overall_evenness,
                spots_count=spots_count,
                discoloration_level=discoloration_level,
                color_uniformity=color_uniformity,
                pigmentation_pattern=pattern,
                confidence_score=0.85,
                analysis_quality="good",
                features={
                    'color_uniformity': color_uniformity,
                    'spots_count': spots_count,
                    'discoloration_level': discoloration_level,
                    'hsv_variance': self._calculate_hsv_variance(hsv),
                    'lab_variance': self._calculate_lab_variance(lab)
                }
            )
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pigmentation feature analysis: {e}")
            return self._get_default_pigmentation_result()
    
    def _analyze_color_uniformity(self, image_array: np.ndarray) -> float:
        """Analyze color uniformity across the image"""
        try:
            # Convert to LAB color space for better color analysis
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            
            # Calculate color variance in each channel
            l_channel = lab[:, :, 0]
            a_channel = lab[:, :, 1]
            b_channel = lab[:, :, 2]
            
            # Calculate standard deviation of each channel
            l_std = np.std(l_channel)
            a_std = np.std(a_channel)
            b_std = np.std(b_channel)
            
            # Normalize standard deviations
            l_uniformity = 1.0 - min(l_std / 50.0, 1.0)
            a_uniformity = 1.0 - min(a_std / 30.0, 1.0)
            b_uniformity = 1.0 - min(b_std / 30.0, 1.0)
            
            # Weighted average (L channel is more important for skin tone)
            uniformity = (0.5 * l_uniformity + 0.25 * a_uniformity + 0.25 * b_uniformity)
            
            return float(max(0.0, min(1.0, uniformity)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in color uniformity analysis: {e}")
            return 0.5
    
    def _detect_spots_and_discoloration(self, image_array: np.ndarray) -> Tuple[int, float]:
        """Detect spots and calculate discoloration level"""
        try:
            # Convert to HSV for better spot detection
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            
            # Create mask for skin-like colors
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Apply morphological operations to clean the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours in the skin mask
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area to detect spots
            spots = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if (self.spot_detection_params['min_area'] <= area <= 
                    self.spot_detection_params['max_area']):
                    spots.append(contour)
            
            # Calculate discoloration level based on color variance
            discoloration = self._calculate_discoloration_level(image_array, skin_mask)
            
            return len(spots), discoloration
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in spot detection: {e}")
            return 0, 0.0
    
    def _calculate_discoloration_level(self, image_array: np.ndarray, skin_mask: np.ndarray) -> float:
        """Calculate the level of discoloration in the skin"""
        try:
            # Apply skin mask to focus on skin areas
            masked_image = cv2.bitwise_and(image_array, image_array, mask=skin_mask)
            
            # Convert to LAB color space
            lab = cv2.cvtColor(masked_image, cv2.COLOR_RGB2LAB)
            
            # Calculate color variance in skin areas
            l_channel = lab[:, :, 0]
            a_channel = lab[:, :, 1]
            b_channel = lab[:, :, 2]
            
            # Calculate variance for each channel
            l_variance = np.var(l_channel)
            a_variance = np.var(a_channel)
            b_variance = np.var(b_channel)
            
            # Normalize and combine variances
            total_variance = (l_variance + a_variance + b_variance) / 3.0
            discoloration_level = min(total_variance / 1000.0, 1.0)
            
            return float(discoloration_level)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in discoloration calculation: {e}")
            return 0.0
    
    def _calculate_overall_evenness(self, color_uniformity: float, discoloration_level: float) -> float:
        """Calculate overall skin evenness score"""
        try:
            # Evenness is inversely proportional to discoloration
            evenness_from_discoloration = 1.0 - discoloration_level
            
            # Combine color uniformity and discoloration-based evenness
            overall_evenness = (color_uniformity + evenness_from_discoloration) / 2.0
            
            return float(max(0.0, min(1.0, overall_evenness)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in evenness calculation: {e}")
            return 0.5
    
    def _determine_pigmentation_pattern(self, evenness: float, spots_count: int) -> str:
        """Determine the pigmentation pattern based on evenness and spot count"""
        try:
            if evenness >= self.evenness_thresholds['excellent'] and spots_count <= 2:
                return 'uniform'
            elif evenness >= self.evenness_thresholds['good'] and spots_count <= 5:
                return 'patchy'
            else:
                return 'spotted'
                
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pattern determination: {e}")
            return 'unknown'
    
    def _calculate_hsv_variance(self, hsv_image: np.ndarray) -> float:
        """Calculate variance in HSV color space"""
        try:
            # Calculate variance for each channel
            h_variance = np.var(hsv_image[:, :, 0])
            s_variance = np.var(hsv_image[:, :, 1])
            v_variance = np.var(hsv_image[:, :, 2])
            
            # Normalize and combine
            total_variance = (h_variance + s_variance + v_variance) / 3.0
            
            return float(total_variance)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in HSV variance calculation: {e}")
            return 0.0
    
    def _calculate_lab_variance(self, lab_image: np.ndarray) -> float:
        """Calculate variance in LAB color space"""
        try:
            # Calculate variance for each channel
            l_variance = np.var(lab_image[:, :, 0])
            a_variance = np.var(lab_image[:, :, 1])
            b_variance = np.var(lab_image[:, :, 2])
            
            # Normalize and combine
            total_variance = (l_variance + a_variance + b_variance) / 3.0
            
            return float(total_variance)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in LAB variance calculation: {e}")
            return 0.0
    
    def _calculate_confidence(self, image_array: np.ndarray) -> float:
        """Calculate confidence score based on image quality for pigmentation analysis"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            
            # Check image sharpness
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)
            
            # Check color balance (important for pigmentation analysis)
            hsv_variance = self._calculate_hsv_variance(hsv)
            color_balance_score = 1.0 - min(hsv_variance / 10000.0, 1.0)
            
            # Check lighting consistency
            v_channel = hsv[:, :, 2]
            lighting_consistency = 1.0 - min(np.std(v_channel) / 100.0, 1.0)
            
            # Combined confidence
            confidence = (sharpness_score + color_balance_score + lighting_consistency) / 3.0
            
            return float(max(0.5, min(0.95, confidence)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in confidence calculation: {e}")
            return 0.7
    
    def _assess_analysis_quality(self, confidence: float) -> str:
        """Assess the quality of the pigmentation analysis"""
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
            "overall_evenness": 0.5,
            "spots_count": 0,
            "discoloration_level": 0.0,
            "color_uniformity": 0.5,
            "pigmentation_pattern": "unknown",
            "confidence_score": 0.0,
            "analysis_quality": "poor",
            "features": {}
        }
    
    def _get_default_pigmentation_result(self) -> PigmentationAnalysisResult:
        """Return default pigmentation result for error cases"""
        return PigmentationAnalysisResult(
            overall_evenness=0.5,
            spots_count=0,
            discoloration_level=0.0,
            color_uniformity=0.5,
            pigmentation_pattern="unknown",
            confidence_score=0.5,
            analysis_quality="fair",
            features={}
        ) 