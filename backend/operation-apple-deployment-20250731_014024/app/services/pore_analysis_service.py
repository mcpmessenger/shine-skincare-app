"""
🍎 Operation Apple: Pore Analysis Service

This service provides advanced pore detection and analysis using computer vision
techniques to assess pore size, distribution, and characteristics.
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
class PoreAnalysisResult:
    """Result of pore analysis"""
    pore_count: int
    pore_density: float  # pores per square pixel
    average_pore_size: float  # in pixels
    pore_size_distribution: str  # 'small', 'medium', 'large'
    pore_clustering: str  # 'scattered', 'clustered', 'uniform'
    confidence_score: float
    analysis_quality: str
    features: Dict[str, Any]

class PoreAnalysisService:
    """
    Advanced pore analysis service using computer vision techniques
    
    This service analyzes pores by:
    1. Detecting individual pores using morphological operations
    2. Measuring pore size and distribution
    3. Analyzing pore clustering patterns
    4. Providing pore characteristics assessment
    """
    
    def __init__(self):
        """Initialize the pore analysis service"""
        self.min_pore_area = 5  # minimum pore area in pixels
        self.max_pore_area = 500  # maximum pore area in pixels
        self.pore_size_thresholds = {
            'small': 20,
            'medium': 50,
            'large': 100
        }
        
        logger.info("🍎 Operation Apple: PoreAnalysisService initialized")
    
    def analyze_pores(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze pores from image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing pore analysis results
        """
        try:
            logger.info("🍎 Operation Apple: Starting pore analysis")
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            image_array = np.array(image)
            
            # Perform pore analysis
            pore_result = self._detect_and_analyze_pores(image_array)
            
            # Calculate confidence based on image quality
            confidence = self._calculate_confidence(image_array)
            
            # Create comprehensive result
            result = {
                "pore_count": pore_result.pore_count,
                "pore_density": float(f"{pore_result.pore_density:.3f}"),
                "average_pore_size": float(f"{pore_result.average_pore_size:.2f}"),
                "pore_size_distribution": pore_result.pore_size_distribution,
                "pore_clustering": pore_result.pore_clustering,
                "confidence_score": float(f"{confidence:.3f}"),
                "analysis_quality": self._assess_analysis_quality(confidence),
                "features": pore_result.features
            }
            
            logger.info(f"🍎 Operation Apple: Pore analysis completed - Count: {result['pore_count']}")
            return result
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error during pore analysis: {e}")
            return self._get_fallback_result()
    
    def _detect_and_analyze_pores(self, image_array: np.ndarray) -> PoreAnalysisResult:
        """
        Detect and analyze pores using computer vision techniques
        
        Args:
            image_array: RGB image as numpy array
            
        Returns:
            PoreAnalysisResult with detailed analysis
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing to enhance pore detection
            processed = self._preprocess_for_pore_detection(gray)
            
            # Detect pores using multiple methods
            pore_contours = self._detect_pores(processed)
            
            # Analyze pore characteristics
            pore_features = self._analyze_pore_characteristics(pore_contours, gray.shape)
            
            # Calculate pore clustering
            clustering = self._analyze_pore_clustering(pore_contours, gray.shape)
            
            # Create result
            return PoreAnalysisResult(
                pore_count=len(pore_contours),
                pore_density=pore_features['density'],
                average_pore_size=pore_features['average_size'],
                pore_size_distribution=pore_features['size_distribution'],
                pore_clustering=clustering,
                confidence_score=0.85,
                analysis_quality="good",
                features=pore_features
            )
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pore detection: {e}")
            return self._get_default_pore_result()
    
    def _preprocess_for_pore_detection(self, gray_image: np.ndarray) -> np.ndarray:
        """Preprocess image for optimal pore detection"""
        try:
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # Apply morphological operations to enhance pores
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            
            # Top-hat transform to enhance dark regions (pores)
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
    
    def _detect_pores(self, processed_image: np.ndarray) -> List[np.ndarray]:
        """Detect individual pores in the processed image"""
        try:
            # Find contours
            contours, _ = cv2.findContours(
                processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by area (pore size constraints)
            valid_pores = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if self.min_pore_area <= area <= self.max_pore_area:
                    # Additional filtering by aspect ratio
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 1
                    
                    # Pores are typically more circular than elongated
                    if aspect_ratio < 3.0:
                        valid_pores.append(contour)
            
            return valid_pores
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pore detection: {e}")
            return []
    
    def _analyze_pore_characteristics(self, pore_contours: List[np.ndarray], image_shape: Tuple[int, int]) -> Dict[str, Any]:
        """Analyze characteristics of detected pores"""
        try:
            if not pore_contours:
                return {
                    'density': 0.0,
                    'average_size': 0.0,
                    'size_distribution': 'none',
                    'size_ranges': {'small': 0, 'medium': 0, 'large': 0},
                    'total_area': 0.0
                }
            
            # Calculate pore areas and sizes
            pore_areas = [cv2.contourArea(contour) for contour in pore_contours]
            pore_sizes = [math.sqrt(area) for area in pore_areas]  # Approximate diameter
            
            # Calculate density
            total_pixels = image_shape[0] * image_shape[1]
            density = len(pore_contours) / total_pixels * 10000  # Normalize
            
            # Calculate average size
            average_size = np.mean(pore_sizes) if pore_sizes else 0.0
            
            # Analyze size distribution
            size_ranges = {'small': 0, 'medium': 0, 'large': 0}
            for size in pore_sizes:
                if size <= self.pore_size_thresholds['small']:
                    size_ranges['small'] += 1
                elif size <= self.pore_size_thresholds['medium']:
                    size_ranges['medium'] += 1
                else:
                    size_ranges['large'] += 1
            
            # Determine dominant size distribution
            max_count = max(size_ranges.values())
            if max_count == 0:
                size_distribution = 'none'
            elif size_ranges['small'] == max_count:
                size_distribution = 'small'
            elif size_ranges['medium'] == max_count:
                size_distribution = 'medium'
            else:
                size_distribution = 'large'
            
            return {
                'density': float(density),
                'average_size': float(average_size),
                'size_distribution': size_distribution,
                'size_ranges': size_ranges,
                'total_area': float(sum(pore_areas)),
                'pore_areas': [float(area) for area in pore_areas],
                'pore_sizes': [float(size) for size in pore_sizes]
            }
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in pore characteristics analysis: {e}")
            return {
                'density': 0.0,
                'average_size': 0.0,
                'size_distribution': 'unknown',
                'size_ranges': {'small': 0, 'medium': 0, 'large': 0},
                'total_area': 0.0
            }
    
    def _analyze_pore_clustering(self, pore_contours: List[np.ndarray], image_shape: Tuple[int, int]) -> str:
        """Analyze the clustering pattern of pores"""
        try:
            if len(pore_contours) < 3:
                return 'scattered'
            
            # Calculate pore centroids
            centroids = []
            for contour in pore_contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    centroids.append((cx, cy))
            
            if len(centroids) < 3:
                return 'scattered'
            
            # Calculate distances between all pairs of pores
            distances = []
            for i in range(len(centroids)):
                for j in range(i + 1, len(centroids)):
                    dist = math.sqrt((centroids[i][0] - centroids[j][0])**2 + 
                                   (centroids[i][1] - centroids[j][1])**2)
                    distances.append(dist)
            
            if not distances:
                return 'scattered'
            
            # Calculate clustering metrics
            avg_distance = np.mean(distances)
            std_distance = np.std(distances)
            
            # Determine clustering pattern
            if std_distance < avg_distance * 0.3:
                return 'uniform'
            elif std_distance > avg_distance * 0.7:
                return 'clustered'
            else:
                return 'scattered'
                
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in clustering analysis: {e}")
            return 'unknown'
    
    def _calculate_confidence(self, image_array: np.ndarray) -> float:
        """Calculate confidence score based on image quality for pore detection"""
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Check image sharpness (important for pore detection)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 1000.0, 1.0)
            
            # Check image contrast (important for pore visibility)
            contrast = np.std(gray) / 255.0
            contrast_score = min(contrast * 2, 1.0)
            
            # Check image resolution (higher resolution = better pore detection)
            height, width = gray.shape
            resolution_score = min((height * width) / (1920 * 1080), 1.0)
            
            # Combined confidence
            confidence = (sharpness_score + contrast_score + resolution_score) / 3.0
            
            return float(max(0.5, min(0.95, confidence)))
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error in confidence calculation: {e}")
            return 0.7
    
    def _assess_analysis_quality(self, confidence: float) -> str:
        """Assess the quality of the pore analysis"""
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
            "pore_count": 0,
            "pore_density": 0.0,
            "average_pore_size": 0.0,
            "pore_size_distribution": "unknown",
            "pore_clustering": "unknown",
            "confidence_score": 0.0,
            "analysis_quality": "poor",
            "features": {}
        }
    
    def _get_default_pore_result(self) -> PoreAnalysisResult:
        """Return default pore result for error cases"""
        return PoreAnalysisResult(
            pore_count=0,
            pore_density=0.0,
            average_pore_size=0.0,
            pore_size_distribution="unknown",
            pore_clustering="unknown",
            confidence_score=0.5,
            analysis_quality="fair",
            features={}
        ) 