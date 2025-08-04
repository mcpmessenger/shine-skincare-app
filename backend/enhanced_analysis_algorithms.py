#!/usr/bin/env python3
"""
Enhanced Skin Analysis Algorithms
Comprehensive computer vision and ML algorithms for skin analysis
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
import logging
from skimage import feature, filters, morphology, measure
from scipy import ndimage, stats
import colorsys

logger = logging.getLogger(__name__)

class EnhancedSkinAnalyzer:
    """Advanced skin analysis using computer vision and ML techniques"""
    
    def __init__(self):
        """Initialize the enhanced skin analyzer"""
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Analysis parameters
        self.analysis_params = {
            'acne': {
                'redness_threshold': 0.6,
                'saturation_threshold': 0.4,
                'size_threshold': 0.02,
                'clustering_threshold': 0.1
            },
            'redness': {
                'hue_range': [(0, 10), (170, 180)],
                'saturation_threshold': 0.3,
                'value_threshold': 0.4
            },
            'dark_spots': {
                'luminance_threshold': 0.4,
                'contrast_threshold': 0.2,
                'size_threshold': 0.01
            },
            'texture': {
                'lbp_radius': 3,
                'lbp_points': 8,
                'gabor_frequencies': [0.1, 0.3, 0.5],
                'gabor_angles': [0, 45, 90, 135]
            }
        }
        
        logger.info("✅ Enhanced skin analyzer initialized")
    
    def analyze_face_detection(self, image: np.ndarray) -> Dict:
        """Advanced face detection with quality assessment"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Multi-scale face detection
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                return {
                    'face_detected': False,
                    'confidence': 0.0,
                    'face_count': 0,
                    'quality_metrics': self._calculate_image_quality(gray)
                }
            
            # Get the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Extract face ROI
            face_roi = image[y:y+h, x:x+w]
            face_gray = gray[y:y+h, x:x+w]
            
            # Eye detection within face
            eyes = self.eye_cascade.detectMultiScale(face_gray)
            
            # Calculate face quality metrics
            quality_metrics = self._calculate_face_quality(face_roi, face_gray, len(eyes))
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_face_confidence(faces, quality_metrics, len(eyes))
            
            return {
                'face_detected': True,
                'confidence': confidence,
                'face_count': len(faces),
                'primary_face': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(w * h),
                    'aspect_ratio': float(w / h) if h > 0 else 0
                },
                'eyes_detected': len(eyes),
                'quality_metrics': quality_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Face detection failed: {e}")
            return {
                'face_detected': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_skin_conditions(self, image: np.ndarray, face_roi: Optional[np.ndarray] = None) -> Dict:
        """Comprehensive skin condition analysis"""
        try:
            # Use face ROI if provided, otherwise use full image
            analysis_image = face_roi if face_roi is not None else image
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(analysis_image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(analysis_image, cv2.COLOR_BGR2LAB)
            
            # Analyze different skin conditions
            conditions = {
                'acne': self._analyze_acne(analysis_image, hsv),
                'redness': self._analyze_redness(hsv),
                'dark_spots': self._analyze_dark_spots(lab),
                'texture': self._analyze_texture(analysis_image),
                'pores': self._analyze_pores(analysis_image),
                'wrinkles': self._analyze_wrinkles(analysis_image),
                'pigmentation': self._analyze_pigmentation(lab)
            }
            
            # Calculate overall health score
            health_score = self._calculate_overall_health_score(conditions)
            
            return {
                'conditions': conditions,
                'health_score': health_score,
                'primary_concerns': self._identify_primary_concerns(conditions),
                'severity_levels': self._assess_severity_levels(conditions)
            }
            
        except Exception as e:
            logger.error(f"❌ Skin condition analysis failed: {e}")
            return {
                'conditions': {},
                'health_score': 0.5,
                'error': str(e)
            }
    
    def _analyze_acne(self, image: np.ndarray, hsv: np.ndarray) -> Dict:
        """Advanced acne detection using multiple algorithms"""
        try:
            # Red channel analysis for inflammation
            red_channel = image[:, :, 2]
            red_threshold = np.mean(red_channel) + 1.5 * np.std(red_channel)
            red_regions = red_channel > red_threshold
            
            # Saturation analysis for active acne
            saturation = hsv[:, :, 1]
            sat_threshold = np.mean(saturation) + np.std(saturation)
            sat_regions = saturation > sat_threshold
            
            # Value analysis for brightness
            value = hsv[:, :, 2]
            val_threshold = np.mean(value) + 0.5 * np.std(value)
            val_regions = value > val_threshold
            
            # Combine detections with morphological operations
            acne_mask = red_regions & sat_regions & val_regions
            
            # Morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            acne_mask = cv2.morphologyEx(acne_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            acne_mask = cv2.morphologyEx(acne_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(acne_mask)
            
            # Analyze each component
            acne_spots = []
            total_acne_area = 0
            
            for i in range(1, num_labels):  # Skip background
                area = stats[i, cv2.CC_STAT_AREA]
                if area > 10:  # Minimum size threshold
                    acne_spots.append({
                        'area': area,
                        'centroid': (centroids[i][0], centroids[i][1]),
                        'bounding_box': (
                            stats[i, cv2.CC_STAT_LEFT],
                            stats[i, cv2.CC_STAT_TOP],
                            stats[i, cv2.CC_STAT_WIDTH],
                            stats[i, cv2.CC_STAT_HEIGHT]
                        )
                    })
                    total_acne_area += area
            
            # Calculate metrics
            total_pixels = acne_mask.size
            acne_percentage = total_acne_area / total_pixels
            spot_count = len(acne_spots)
            
            # Determine severity
            severity = 'none'
            if acne_percentage > 0.05 or spot_count > 5:
                severity = 'severe'
            elif acne_percentage > 0.02 or spot_count > 2:
                severity = 'moderate'
            elif acne_percentage > 0.005 or spot_count > 0:
                severity = 'mild'
            
            return {
                'detected': acne_percentage > 0.005,
                'percentage': float(acne_percentage),
                'spot_count': spot_count,
                'severity': severity,
                'confidence': min(1.0, acne_percentage * 20 + spot_count * 0.1),
                'spots': acne_spots
            }
            
        except Exception as e:
            logger.error(f"❌ Acne analysis failed: {e}")
            return {'detected': False, 'percentage': 0.0, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_redness(self, hsv: np.ndarray) -> Dict:
        """Advanced redness detection using HSV color space"""
        try:
            hue = hsv[:, :, 0]
            saturation = hsv[:, :, 1]
            value = hsv[:, :, 2]
            
            # Create redness mask using hue ranges
            redness_mask = np.zeros_like(hue, dtype=bool)
            
            # Red hue ranges (0-10 and 170-180)
            for hue_range in self.analysis_params['redness']['hue_range']:
                lower, upper = hue_range
                if lower <= upper:
                    mask = (hue >= lower) & (hue <= upper)
                else:
                    mask = (hue >= lower) | (hue <= upper)
                redness_mask |= mask
            
            # Apply saturation and value thresholds
            sat_threshold = self.analysis_params['redness']['saturation_threshold']
            val_threshold = self.analysis_params['redness']['value_threshold']
            
            redness_mask &= (saturation > sat_threshold * 255)
            redness_mask &= (value > val_threshold * 255)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            redness_mask = cv2.morphologyEx(redness_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            
            # Calculate metrics
            redness_percentage = np.sum(redness_mask) / redness_mask.size
            
            # Determine severity
            severity = 'none'
            if redness_percentage > 0.15:
                severity = 'severe'
            elif redness_percentage > 0.08:
                severity = 'moderate'
            elif redness_percentage > 0.03:
                severity = 'mild'
            
            return {
                'detected': redness_percentage > 0.03,
                'percentage': float(redness_percentage),
                'severity': severity,
                'confidence': min(1.0, redness_percentage * 10)
            }
            
        except Exception as e:
            logger.error(f"❌ Redness analysis failed: {e}")
            return {'detected': False, 'percentage': 0.0, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_dark_spots(self, lab: np.ndarray) -> Dict:
        """Advanced dark spots detection using LAB color space"""
        try:
            # L channel (lightness)
            l_channel = lab[:, :, 0]
            
            # Calculate local contrast
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(l_channel, -1, kernel)
            local_contrast = np.abs(l_channel - local_mean)
            
            # Create dark spots mask
            l_threshold = np.mean(l_channel) - 1.5 * np.std(l_channel)
            contrast_threshold = np.mean(local_contrast) + np.std(local_contrast)
            
            dark_spots_mask = (l_channel < l_threshold) & (local_contrast > contrast_threshold)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            dark_spots_mask = cv2.morphologyEx(dark_spots_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            dark_spots_mask = cv2.morphologyEx(dark_spots_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dark_spots_mask)
            
            # Analyze spots
            dark_spots = []
            total_dark_area = 0
            
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area > 15:  # Minimum size threshold
                    dark_spots.append({
                        'area': area,
                        'centroid': (centroids[i][0], centroids[i][1]),
                        'bounding_box': (
                            stats[i, cv2.CC_STAT_LEFT],
                            stats[i, cv2.CC_STAT_TOP],
                            stats[i, cv2.CC_STAT_WIDTH],
                            stats[i, cv2.CC_STAT_HEIGHT]
                        )
                    })
                    total_dark_area += area
            
            # Calculate metrics
            dark_percentage = total_dark_area / dark_spots_mask.size
            spot_count = len(dark_spots)
            
            # Determine severity
            severity = 'none'
            if dark_percentage > 0.08 or spot_count > 3:
                severity = 'severe'
            elif dark_percentage > 0.04 or spot_count > 1:
                severity = 'moderate'
            elif dark_percentage > 0.01 or spot_count > 0:
                severity = 'mild'
            
            return {
                'detected': dark_percentage > 0.01,
                'percentage': float(dark_percentage),
                'spot_count': spot_count,
                'severity': severity,
                'confidence': min(1.0, dark_percentage * 15 + spot_count * 0.2),
                'spots': dark_spots
            }
            
        except Exception as e:
            logger.error(f"❌ Dark spots analysis failed: {e}")
            return {'detected': False, 'percentage': 0.0, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_texture(self, image: np.ndarray) -> Dict:
        """Advanced texture analysis using multiple algorithms"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern
            lbp = feature.local_binary_pattern(gray, 8, 1, method='uniform')
            lbp_hist, _ = np.histogram(lbp, bins=10, range=(0, 10))
            lbp_hist = lbp_hist.astype(float) / lbp_hist.sum()
            
            # Texture uniformity
            texture_uniformity = np.std(lbp_hist)
            
            # Gabor filter analysis
            gabor_responses = []
            for frequency in self.analysis_params['texture']['gabor_frequencies']:
                for angle in self.analysis_params['texture']['gabor_angles']:
                    kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 2*np.pi*frequency, 0.5, 0)
                    response = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
                    gabor_responses.append(np.var(response))
            
            gabor_variance = np.mean(gabor_responses)
            
            # Determine texture type
            if texture_uniformity < 0.1 and gabor_variance < 1000:
                texture_type = 'smooth'
            elif texture_uniformity < 0.2 and gabor_variance < 2000:
                texture_type = 'normal'
            else:
                texture_type = 'rough'
            
            return {
                'type': texture_type,
                'uniformity': float(texture_uniformity),
                'gabor_variance': float(gabor_variance),
                'confidence': min(1.0, 1.0 - texture_uniformity)
            }
            
        except Exception as e:
            logger.error(f"❌ Texture analysis failed: {e}")
            return {'type': 'unknown', 'uniformity': 0.0, 'confidence': 0.0}
    
    def _analyze_pores(self, image: np.ndarray) -> Dict:
        """Pore detection using blob detection"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Laplacian of Gaussian for blob detection
            log = cv2.Laplacian(blurred, cv2.CV_64F)
            log = np.absolute(log)
            
            # Threshold to find potential pores
            threshold = np.mean(log) + 2 * np.std(log)
            pore_mask = log > threshold
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            pore_mask = cv2.morphologyEx(pore_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            
            # Find connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(pore_mask)
            
            # Count pores
            pore_count = 0
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if 5 < area < 50:  # Pore size range
                    pore_count += 1
            
            pore_density = pore_count / (image.shape[0] * image.shape[1]) * 10000
            
            # Determine severity
            severity = 'none'
            if pore_density > 50:
                severity = 'severe'
            elif pore_density > 25:
                severity = 'moderate'
            elif pore_density > 10:
                severity = 'mild'
            
            return {
                'detected': pore_count > 0,
                'count': pore_count,
                'density': float(pore_density),
                'severity': severity,
                'confidence': min(1.0, pore_count / 100)
            }
            
        except Exception as e:
            logger.error(f"❌ Pore analysis failed: {e}")
            return {'detected': False, 'count': 0, 'density': 0.0, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_wrinkles(self, image: np.ndarray) -> Dict:
        """Wrinkle detection using edge detection and line detection"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Hough line detection
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
            
            if lines is None:
                return {'detected': False, 'count': 0, 'severity': 'none', 'confidence': 0.0}
            
            # Filter lines by orientation (horizontal and vertical wrinkles)
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
                if abs(angle) < 30:  # Horizontal wrinkles
                    horizontal_lines.append(line[0])
                elif abs(angle - 90) < 30:  # Vertical wrinkles
                    vertical_lines.append(line[0])
            
            total_lines = len(horizontal_lines) + len(vertical_lines)
            
            # Determine severity
            severity = 'none'
            if total_lines > 10:
                severity = 'severe'
            elif total_lines > 5:
                severity = 'moderate'
            elif total_lines > 1:
                severity = 'mild'
            
            return {
                'detected': total_lines > 0,
                'count': total_lines,
                'horizontal_count': len(horizontal_lines),
                'vertical_count': len(vertical_lines),
                'severity': severity,
                'confidence': min(1.0, total_lines / 20)
            }
            
        except Exception as e:
            logger.error(f"❌ Wrinkle analysis failed: {e}")
            return {'detected': False, 'count': 0, 'severity': 'none', 'confidence': 0.0}
    
    def _analyze_pigmentation(self, lab: np.ndarray) -> Dict:
        """Pigmentation analysis using LAB color space"""
        try:
            # A and B channels for color analysis
            a_channel = lab[:, :, 1]  # Green-Red
            b_channel = lab[:, :, 2]  # Blue-Yellow
            
            # Calculate color variance
            a_variance = np.var(a_channel)
            b_variance = np.var(b_channel)
            
            # Overall color variance
            color_variance = (a_variance + b_variance) / 2
            
            # Determine pigmentation level
            if color_variance > 500:
                pigmentation_level = 'high'
            elif color_variance > 200:
                pigmentation_level = 'moderate'
            else:
                pigmentation_level = 'low'
            
            return {
                'level': pigmentation_level,
                'color_variance': float(color_variance),
                'a_variance': float(a_variance),
                'b_variance': float(b_variance),
                'confidence': min(1.0, color_variance / 1000)
            }
            
        except Exception as e:
            logger.error(f"❌ Pigmentation analysis failed: {e}")
            return {'level': 'unknown', 'color_variance': 0.0, 'confidence': 0.0}
    
    def _calculate_face_quality(self, face_roi: np.ndarray, face_gray: np.ndarray, eye_count: int) -> Dict:
        """Calculate comprehensive face quality metrics"""
        try:
            # Brightness
            brightness = np.mean(face_gray)
            
            # Contrast
            contrast = np.std(face_gray)
            
            # Sharpness using Laplacian variance
            laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # Face size score
            face_area = face_roi.shape[0] * face_roi.shape[1]
            size_score = min(1.0, face_area / 50000)
            
            # Eye detection score
            eye_score = min(1.0, eye_count / 2)
            
            # Overall quality score
            overall_score = (
                (brightness / 128) * 0.2 +
                (contrast / 50) * 0.2 +
                (sharpness / 1000) * 0.2 +
                size_score * 0.2 +
                eye_score * 0.2
            )
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'sharpness': float(sharpness),
                'size_score': float(size_score),
                'eye_score': float(eye_score),
                'overall_score': float(overall_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Face quality calculation failed: {e}")
            return {
                'brightness': 0, 'contrast': 0, 'sharpness': 0,
                'size_score': 0, 'eye_score': 0, 'overall_score': 0
            }
    
    def _calculate_face_confidence(self, faces: np.ndarray, quality_metrics: Dict, eye_count: int) -> float:
        """Calculate face detection confidence"""
        try:
            # Base confidence from number of faces
            face_confidence = min(1.0, len(faces) * 0.3)
            
            # Quality contribution
            quality_confidence = quality_metrics.get('overall_score', 0)
            
            # Eye detection contribution
            eye_confidence = min(1.0, eye_count / 2)
            
            # Combined confidence
            confidence = (face_confidence * 0.4 + quality_confidence * 0.4 + eye_confidence * 0.2)
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"❌ Face confidence calculation failed: {e}")
            return 0.0
    
    def _calculate_image_quality(self, gray: np.ndarray) -> Dict:
        """Calculate general image quality metrics"""
        try:
            # Brightness
            brightness = np.mean(gray)
            
            # Contrast
            contrast = np.std(gray)
            
            # Sharpness
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # Noise estimation
            noise = np.std(gray - cv2.GaussianBlur(gray, (5, 5), 0))
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'sharpness': float(sharpness),
                'noise': float(noise),
                'overall_score': min(1.0, (brightness / 128) * (contrast / 50) * (sharpness / 1000))
            }
            
        except Exception as e:
            logger.error(f"❌ Image quality calculation failed: {e}")
            return {'brightness': 0, 'contrast': 0, 'sharpness': 0, 'noise': 0, 'overall_score': 0}
    
    def _calculate_overall_health_score(self, conditions: Dict) -> float:
        """Calculate overall skin health score"""
        try:
            scores = []
            
            # Acne score (inverse)
            if 'acne' in conditions and conditions['acne'].get('detected'):
                acne_score = 1.0 - conditions['acne'].get('percentage', 0.0)
                scores.append(acne_score)
            
            # Redness score (inverse)
            if 'redness' in conditions and conditions['redness'].get('detected'):
                redness_score = 1.0 - conditions['redness'].get('percentage', 0.0)
                scores.append(redness_score)
            
            # Dark spots score (inverse)
            if 'dark_spots' in conditions and conditions['dark_spots'].get('detected'):
                dark_score = 1.0 - conditions['dark_spots'].get('percentage', 0.0)
                scores.append(dark_score)
            
            # Texture score
            if 'texture' in conditions:
                texture_type = conditions['texture'].get('type', 'unknown')
                if texture_type == 'smooth':
                    texture_score = 1.0
                elif texture_type == 'normal':
                    texture_score = 0.7
                else:
                    texture_score = 0.3
                scores.append(texture_score)
            
            # Pores score (inverse)
            if 'pores' in conditions and conditions['pores'].get('detected'):
                pore_density = conditions['pores'].get('density', 0.0)
                pore_score = max(0.0, 1.0 - (pore_density / 100))
                scores.append(pore_score)
            
            # Wrinkles score (inverse)
            if 'wrinkles' in conditions and conditions['wrinkles'].get('detected'):
                wrinkle_count = conditions['wrinkles'].get('count', 0)
                wrinkle_score = max(0.0, 1.0 - (wrinkle_count / 20))
                scores.append(wrinkle_score)
            
            return np.mean(scores) if scores else 0.5
            
        except Exception as e:
            logger.error(f"❌ Health score calculation failed: {e}")
            return 0.5
    
    def _identify_primary_concerns(self, conditions: Dict) -> List[str]:
        """Identify primary skin concerns"""
        concerns = []
        
        for condition, data in conditions.items():
            if isinstance(data, dict) and data.get('detected', False):
                severity = data.get('severity', 'none')
                if severity in ['moderate', 'severe']:
                    concerns.append(f"{condition}_{severity}")
        
        return concerns
    
    def _assess_severity_levels(self, conditions: Dict) -> Dict:
        """Assess severity levels for all conditions"""
        severity_levels = {}
        
        for condition, data in conditions.items():
            if isinstance(data, dict):
                severity_levels[condition] = data.get('severity', 'none')
        
        return severity_levels

def main():
    """Test the enhanced skin analyzer"""
    print("🧠 Testing Enhanced Skin Analyzer")
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Initialize analyzer
    analyzer = EnhancedSkinAnalyzer()
    
    # Test face detection
    face_result = analyzer.analyze_face_detection(test_image)
    print(f"✅ Face detection: {face_result['face_detected']}")
    print(f"🎯 Confidence: {face_result['confidence']:.3f}")
    
    # Test skin conditions
    skin_result = analyzer.analyze_skin_conditions(test_image)
    print(f"✅ Skin analysis completed")
    print(f"📊 Health Score: {skin_result['health_score']:.3f}")
    print(f"🔍 Primary Concerns: {skin_result['primary_concerns']}")

if __name__ == "__main__":
    main() 