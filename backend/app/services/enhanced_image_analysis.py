import os
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from PIL import Image
import cv2
from sklearn.cluster import KMeans
from sklearn.feature_extraction import image as skimage

logger = logging.getLogger(__name__)

class EnhancedImageAnalysisService:
    """Enhanced image analysis service for medical skin condition detection"""
    
    def __init__(self):
        """Initialize the enhanced analysis service"""
        self.condition_models = {
            'acne': self._analyze_acne,
            'eczema': self._analyze_eczema,
            'psoriasis': self._analyze_psoriasis,
            'rosacea': self._analyze_rosacea,
            'melasma': self._analyze_melasma
        }
        
        logger.info("Enhanced Image Analysis Service initialized")
    
    def analyze_medical_condition(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze image for medical skin conditions
        
        Args:
            image: PIL Image object
            
        Returns:
            Analysis result with condition details
        """
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Extract features
            features = self._extract_skin_features(img_array)
            
            # Analyze for different conditions
            condition_scores = {}
            for condition_name, analyzer_func in self.condition_models.items():
                score = analyzer_func(img_array, features)
                condition_scores[condition_name] = score
            
            # Determine primary condition
            primary_condition = max(condition_scores, key=condition_scores.get)
            confidence = condition_scores[primary_condition]
            
            # Generate detailed analysis
            analysis_result = {
                'primary_condition': primary_condition,
                'confidence': confidence,
                'features': features,
                'condition_scores': condition_scores,
                'description': self._generate_condition_description(primary_condition, confidence),
                'treatments': self._get_recommended_treatments(primary_condition, confidence)
            }
            
            logger.info(f"Medical analysis completed: {primary_condition} (confidence: {confidence:.2f})")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Medical analysis failed: {e}")
            return {
                'primary_condition': 'unknown',
                'confidence': 0.0,
                'features': [],
                'description': 'Unable to analyze image',
                'treatments': []
            }
    
    def _extract_skin_features(self, img_array: np.ndarray) -> Dict[str, Any]:
        """
        Extract skin-specific features from image
        
        Args:
            img_array: Image as numpy array
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            
            # Color analysis
            features['mean_rgb'] = np.mean(img_array, axis=(0, 1))
            features['std_rgb'] = np.std(img_array, axis=(0, 1))
            features['mean_hsv'] = np.mean(hsv, axis=(0, 1))
            features['std_hsv'] = np.std(hsv, axis=(0, 1))
            
            # Texture analysis using Local Binary Patterns
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            features['texture_variance'] = np.var(gray)
            features['texture_entropy'] = self._calculate_entropy(gray)
            
            # Edge detection for lesion boundaries
            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = np.sum(edges > 0) / edges.size
            
            # Color clustering for lesion detection
            features['color_clusters'] = self._analyze_color_clusters(img_array)
            
            # Skin tone analysis
            features['skin_tone'] = self._analyze_skin_tone(hsv)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            features = {}
        
        return features
    
    def _analyze_acne(self, img_array: np.ndarray, features: Dict[str, Any]) -> float:
        """Analyze image for acne characteristics"""
        try:
            score = 0.0
            
            # Check for red spots (inflammation)
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            red_mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
            red_ratio = np.sum(red_mask > 0) / red_mask.size
            score += red_ratio * 0.4
            
            # Check for texture irregularities
            if features.get('texture_variance', 0) > 1000:
                score += 0.3
            
            # Check for edge density (pimple boundaries)
            if features.get('edge_density', 0) > 0.1:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Acne analysis failed: {e}")
            return 0.0
    
    def _analyze_eczema(self, img_array: np.ndarray, features: Dict[str, Any]) -> float:
        """Analyze image for eczema characteristics"""
        try:
            score = 0.0
            
            # Check for dry, scaly patches
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            texture_score = features.get('texture_variance', 0) / 1000
            score += min(texture_score, 0.4)
            
            # Check for redness
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            red_mask = cv2.inRange(hsv, (0, 30, 30), (10, 255, 255))
            red_ratio = np.sum(red_mask > 0) / red_mask.size
            score += red_ratio * 0.3
            
            # Check for irregular patterns
            if features.get('edge_density', 0) > 0.05:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Eczema analysis failed: {e}")
            return 0.0
    
    def _analyze_psoriasis(self, img_array: np.ndarray, features: Dict[str, Any]) -> float:
        """Analyze image for psoriasis characteristics"""
        try:
            score = 0.0
            
            # Check for thick, scaly patches
            texture_score = features.get('texture_variance', 0) / 1500
            score += min(texture_score, 0.5)
            
            # Check for silvery scales (bright areas)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            bright_mask = gray > np.mean(gray) + np.std(gray)
            bright_ratio = np.sum(bright_mask) / bright_mask.size
            score += bright_ratio * 0.3
            
            # Check for well-defined boundaries
            if features.get('edge_density', 0) > 0.08:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Psoriasis analysis failed: {e}")
            return 0.0
    
    def _analyze_rosacea(self, img_array: np.ndarray, features: Dict[str, Any]) -> float:
        """Analyze image for rosacea characteristics"""
        try:
            score = 0.0
            
            # Check for facial redness
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            red_mask = cv2.inRange(hsv, (0, 40, 40), (15, 255, 255))
            red_ratio = np.sum(red_mask > 0) / red_mask.size
            score += red_ratio * 0.6
            
            # Check for visible blood vessels
            if features.get('edge_density', 0) > 0.12:
                score += 0.4
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Rosacea analysis failed: {e}")
            return 0.0
    
    def _analyze_melasma(self, img_array: np.ndarray, features: Dict[str, Any]) -> float:
        """Analyze image for melasma characteristics"""
        try:
            score = 0.0
            
            # Check for brown patches
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            brown_mask = cv2.inRange(hsv, (10, 30, 30), (25, 255, 255))
            brown_ratio = np.sum(brown_mask > 0) / brown_mask.size
            score += brown_ratio * 0.7
            
            # Check for even distribution
            if features.get('texture_variance', 0) < 500:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Melasma analysis failed: {e}")
            return 0.0
    
    def _calculate_entropy(self, gray_image: np.ndarray) -> float:
        """Calculate image entropy for texture analysis"""
        try:
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            hist = hist / hist.sum()
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            return entropy
        except Exception as e:
            logger.error(f"Entropy calculation failed: {e}")
            return 0.0
    
    def _analyze_color_clusters(self, img_array: np.ndarray) -> List[Dict[str, Any]]:
        """Analyze color clusters in the image"""
        try:
            # Reshape image for clustering
            pixels = img_array.reshape(-1, 3)
            
            # Use K-means to find dominant colors
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            clusters = []
            for i, center in enumerate(kmeans.cluster_centers_):
                cluster_mask = kmeans.labels_ == i
                cluster_ratio = np.sum(cluster_mask) / len(cluster_mask)
                
                clusters.append({
                    'color': center.tolist(),
                    'ratio': cluster_ratio,
                    'cluster_id': i
                })
            
            return sorted(clusters, key=lambda x: x['ratio'], reverse=True)
            
        except Exception as e:
            logger.error(f"Color cluster analysis failed: {e}")
            return []
    
    def _analyze_skin_tone(self, hsv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze skin tone characteristics"""
        try:
            # Extract skin tone from HSV
            skin_mask = cv2.inRange(hsv_image, (0, 20, 70), (20, 255, 255))
            skin_pixels = hsv_image[skin_mask > 0]
            
            if len(skin_pixels) > 0:
                mean_hue = np.mean(skin_pixels[:, 0])
                mean_saturation = np.mean(skin_pixels[:, 1])
                mean_value = np.mean(skin_pixels[:, 2])
                
                return {
                    'mean_hue': mean_hue,
                    'mean_saturation': mean_saturation,
                    'mean_value': mean_value,
                    'skin_ratio': np.sum(skin_mask > 0) / skin_mask.size
                }
            else:
                return {
                    'mean_hue': 0,
                    'mean_saturation': 0,
                    'mean_value': 0,
                    'skin_ratio': 0
                }
                
        except Exception as e:
            logger.error(f"Skin tone analysis failed: {e}")
            return {}
    
    def _generate_condition_description(self, condition: str, confidence: float) -> str:
        """Generate detailed description of the identified condition"""
        descriptions = {
            'acne': f"Analysis indicates acne with {confidence:.1%} confidence. Characterized by inflammation, redness, and potential comedones.",
            'eczema': f"Analysis suggests eczema with {confidence:.1%} confidence. Shows signs of dry, scaly patches with potential inflammation.",
            'psoriasis': f"Analysis indicates psoriasis with {confidence:.1%} confidence. Characterized by thick, scaly patches with well-defined boundaries.",
            'rosacea': f"Analysis suggests rosacea with {confidence:.1%} confidence. Shows facial redness and potential visible blood vessels.",
            'melasma': f"Analysis indicates melasma with {confidence:.1%} confidence. Characterized by brown patches with even distribution."
        }
        
        return descriptions.get(condition, f"Analysis completed with {confidence:.1%} confidence.")
    
    def _get_recommended_treatments(self, condition: str, confidence: float) -> List[str]:
        """Get recommended treatments based on condition and confidence"""
        treatments = {
            'acne': [
                "Gentle cleansing with non-comedogenic products",
                "Topical treatments with benzoyl peroxide or salicylic acid",
                "Avoid touching or picking at affected areas",
                "Consider consulting a dermatologist for severe cases"
            ],
            'eczema': [
                "Moisturize regularly with fragrance-free products",
                "Avoid hot showers and harsh soaps",
                "Use gentle, hypoallergenic skincare products",
                "Consider topical corticosteroids for flare-ups"
            ],
            'psoriasis': [
                "Keep skin moisturized with thick creams",
                "Avoid triggers like stress and cold weather",
                "Consider phototherapy or prescription treatments",
                "Consult a dermatologist for management plan"
            ],
            'rosacea': [
                "Use gentle, non-irritating skincare products",
                "Avoid triggers like spicy foods and alcohol",
                "Protect skin from sun exposure",
                "Consider prescription treatments for severe cases"
            ],
            'melasma': [
                "Use broad-spectrum sunscreen daily",
                "Consider topical treatments with hydroquinone",
                "Avoid excessive sun exposure",
                "Consult a dermatologist for advanced treatments"
            ]
        }
        
        if confidence < 0.5:
            return ["Consider consulting a dermatologist for accurate diagnosis"]
        
        return treatments.get(condition, ["Consult a healthcare professional for proper diagnosis and treatment"]) 