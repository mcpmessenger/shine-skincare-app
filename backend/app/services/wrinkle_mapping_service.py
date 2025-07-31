"""
🍎 Operation Apple: Wrinkle Mapping Service

This service provides advanced wrinkle detection and mapping using computer vision
techniques to assess fine lines, deep wrinkles, and aging patterns.
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

logger = logging.getLogger(__name__)

@dataclass
class WrinkleAnalysisResult:
    """Result of wrinkle analysis"""
    forehead_wrinkles: float  # 0.0 to 1.0 severity
    eye_wrinkles: float
    mouth_wrinkles: float
    overall_wrinkle_score: float
    wrinkle_density: float
    aging_pattern: str  # 'minimal', 'moderate', 'advanced'
    confidence_score: float
    analysis_quality: str
    features: Dict[str, Any]

class WrinkleMappingService:
    """
    Advanced wrinkle mapping service using computer vision techniques
    
    This service analyzes wrinkles by:
    1. Detecting fine lines and deep wrinkles
    2. Mapping wrinkle distribution across facial regions
    3. Assessing aging patterns and severity
    4. Providing wrinkle density analysis
    """
    
    def __init__(self):
        """Initialize the wrinkle mapping service"""
        self.wrinkle_thresholds = {
            'minimal': 0.2,
            'moderate': 0.5,
            'advanced': 0.8
        }
        
        # Facial region definitions (relative coordinates)
        self.facial_regions = {
            'forehead': {'y_min': 0.0, 'y_max': 0.3, 'x_min': 0.2, 'x_max': 0.8},
            'eyes': {'y_min': 0.25, 'y_max': 0.45, 'x_min': 0.1, 'x_max': 0.9},
            'mouth': {'y_min': 0.6, 'y_max': 0.85, 'x_min': 0.25, 'x_max': 0.75}
        }
        
        logger.info("🍎 Operation Apple: WrinkleMappingService initialized")
    
    def analyze_wrinkles(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze wrinkles from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing wrinkle analysis results
        """
        try:
            logger.info("🍎 Operation Apple: Starting wrinkle analysis")
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            image_array = np.array(image)
            
            # Perform wrinkle analysis
            wrinkle_result = self._detect_and_analyze_wrinkles(image_array)
            
            # Calculate confidence based on image quality
            confidence = self._calculate_confidence(image_array)
            
            # Create comprehensive result
            result = {
                "forehead_wrinkles": float(f"{wrinkle_result.forehead_wrinkles:.3f}"),
                "eye_wrinkles": float(f"{wrinkle_result.eye_wrinkles:.3f}"),
                "mouth_wrinkles": float(f"{wrinkle_result.mouth_wrinkles:.3f}"),
                "overall_wrinkle_score": float(f"{wrinkle_result.overall_wrinkle_score:.3f}"),
                "wrinkle_density": float(f"{wrinkle_result.wrinkle_density:.3f}"),
                "aging_pattern": wrinkle_result.aging_pattern,
                "confidence_score": float(f"{confidence:.3f}"),
                "analysis_quality": self._assess_analysis_quality(confidence),
                "features": wrinkle_result.features
            }
            
            logger.info(f"🍎 Operation Apple: Wrinkle analysis completed - Score: {result['overall_wrinkle_score']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error during wrinkle analysis: {e}")
            return self._get_fallback_result()
    
    def _detect_and_analyze_wrinkles(self, image_array: np.ndarray) -> WrinkleAnalysisResult:
        """
        Detect and analyze wrinkles using computer vision techniques
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            WrinkleAnalysisResult with detailed analysis
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing to enhance wrinkle detection
            processed = self._preprocess_for_wrinkle_detection(gray)
            
            # Detect wrinkles in different facial regions
            forehead_wrinkles = self._analyze_region_wrinkles(processed, gray.shape, 'forehead')
            eye_wrinkles = self._analyze_region_wrinkles(processed, gray.shape, 'eyes')
            mouth_wrinkles = self._analyze_region_wrinkles(processed, gray.shape, 'mouth')
            
            # Calculate overall wrinkle score
            overall_score = (forehead_wrinkles + eye_wrinkles + mouth_wrinkles) / 3.0
            
            # Calculate wrinkle density
            wrinkle_density = self._calculate_wrinkle_density(processed)
            
            # Determine aging pattern
            aging_pattern = self._determine_aging_pattern(overall_score)
            
            # Create result
            return WrinkleAnalysisResult(
                forehead_wrinkles=forehead_wrinkles,
                eye_wrinkles=eye_wrinkles,
                mouth_wrinkles=mouth_wrinkles,
                overall_wrinkle_score=overall_score,
                wrinkle_density=wrinkle_density,
                aging_pattern=aging_pattern,
                confidence_score=0.85,
                analysis_quality="good",
                features={
                    'forehead_wrinkles': forehead_wrinkles,
                    'eye_wrinkles': eye_wrinkles,
                    'mouth_wrinkles': mouth_wrinkles,
                    'wrinkle_density': wrinkle_density
                }
            )
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in wrinkle detection: {e}")
            return self._get_default_wrinkle_result()
    
    def _preprocess_for_wrinkle_detection(self, gray_image: np.ndarray) -> np.ndarray:
        """Preprocess image for optimal wrinkle detection"""
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # Apply morphological operations to enhance lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))  # Horizontal lines
            
            # Top-hat transform to enhance linear features (wrinkles)
            tophat = cv2.morphologyEx(blurred, cv2.MORPH_TOPHAT, kernel)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                tophat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Remove small noise
            kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_clean)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in preprocessing: {e}")
            return gray_image
    
    def _analyze_region_wrinkles(self, processed_image: np.ndarray, image_shape: Tuple[int, int], region: str) -> float:
        """Analyze wrinkles in a specific facial region"""
        try:
            if region not in self.facial_regions:
                return 0.0
            
            # Get region coordinates
            region_coords = self.facial_regions[region]
            height, width = image_shape
            
            # Calculate pixel coordinates
            y_min = int(region_coords['y_min'] * height)
            y_max = int(region_coords['y_max'] * height)
            x_min = int(region_coords['x_min'] * width)
            x_max = int(region_coords['x_max'] * width)
            
            # Extract region
            region_image = processed_image[y_min:y_max, x_min:x_max]
            
            if region_image.size == 0:
                return 0.0
            
            # Calculate wrinkle density in region
            wrinkle_pixels = np.count_nonzero(region_image)
            total_pixels = region_image.shape[0] * region_image.shape[1]
            
            if total_pixels == 0:
                return 0.0
            
            # Normalize wrinkle density
            wrinkle_density = wrinkle_pixels / total_pixels
            
            # Apply region-specific adjustments
            if region == 'forehead':
                # Forehead wrinkles are typically more prominent
                wrinkle_density *= 1.2
            elif region == 'eyes':
                # Eye wrinkles are often finer
                wrinkle_density *= 0.8
            elif region == 'mouth':
                # Mouth wrinkles can be variable
                wrinkle_density *= 1.0
            
            return float(min(wrinkle_density, 1.0))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in region wrinkle analysis: {e}")
            return 0.0
    
    def _calculate_wrinkle_density(self, processed_image: np.ndarray) -> float:
        """Calculate overall wrinkle density across the entire face"""
        try:
            # Count wrinkle pixels
            wrinkle_pixels = np.count_nonzero(processed_image)
            total_pixels = processed_image.shape[0] * processed_image.shape[1]
            
            if total_pixels == 0:
                return 0.0
            
            # Calculate density
            density = wrinkle_pixels / total_pixels
            
            return float(density)
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in wrinkle density calculation: {e}")
            return 0.0
    
    def _determine_aging_pattern(self, overall_score: float) -> str:
        """Determine aging pattern based on overall wrinkle score"""
        if overall_score <= self.wrinkle_thresholds['minimal']:
            return 'minimal'
        elif overall_score <= self.wrinkle_thresholds['moderate']:
            return 'moderate'
        else:
            return 'advanced'
    
    def _calculate_confidence(self, image_array: np.ndarray) -> float:
        """Calculate confidence score based on image quality for wrinkle detection"""
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Check image sharpness (important for wrinkle detection)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)
            
            # Check image contrast (important for wrinkle visibility)
            contrast = np.std(gray) / 255.0
            contrast_score = min(contrast * 2, 1.0)
            
            # Check image brightness (wrinkles are more visible in good lighting)
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.6) * 2  # Optimal around 0.6
            
            # Combined confidence
            confidence = (sharpness_score + contrast_score + brightness_score) / 3.0
            
            return float(max(0.5, min(0.95, confidence)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in confidence calculation: {e}")
            return 0.7
    
    def _assess_analysis_quality(self, confidence: float) -> str:
        """Assess the quality of the wrinkle analysis"""
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
            "forehead_wrinkles": 0.0,
            "eye_wrinkles": 0.0,
            "mouth_wrinkles": 0.0,
            "overall_wrinkle_score": 0.0,
            "wrinkle_density": 0.0,
            "aging_pattern": "unknown",
            "confidence_score": 0.0,
            "analysis_quality": "poor",
            "features": {}
        }
    
    def _get_default_wrinkle_result(self) -> WrinkleAnalysisResult:
        """Return default wrinkle result for error cases"""
        return WrinkleAnalysisResult(
            forehead_wrinkles=0.0,
            eye_wrinkles=0.0,
            mouth_wrinkles=0.0,
            overall_wrinkle_score=0.0,
            wrinkle_density=0.0,
            aging_pattern="unknown",
            confidence_score=0.5,
            analysis_quality="fair",
            features={}
        ) 