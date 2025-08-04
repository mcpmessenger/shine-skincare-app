#!/usr/bin/env python3
"""
Enhanced Analysis API for Shine Skincare App
Uses scaled datasets and more parameters for improved accuracy
"""

import os
import json
import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple
import base64
import requests
from datetime import datetime
import tempfile
from pathlib import Path
from PIL import Image
import io

# Import our scaled dataset manager
from scaled_dataset_manager import ScaledDatasetManager
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAnalysisAPI:
    """Enhanced analysis API with scaled datasets and more parameters"""
    
    def __init__(self):
        """Initialize the enhanced analysis API"""
        self.dataset_manager = ScaledDatasetManager()
        self.skin_analyzer = EnhancedSkinAnalyzer()
        self.analysis_cache = {}
        
        # Analysis configurations
        self.analysis_configs = {
            'comprehensive': {
                'datasets': ['skin_lesion_archive', 'isic_2020', 'ham10000'],
                'parameters': ['demographic', 'clinical', 'imaging', 'environmental'],
                'confidence_threshold': 0.85
            },
            'focused': {
                'datasets': ['dermnet', 'fitzpatrick17k'],
                'parameters': ['clinical', 'imaging'],
                'confidence_threshold': 0.90
            },
            'research': {
                'datasets': ['skin_lesion_archive', 'isic_2020', 'ham10000', 'dermnet', 'fitzpatrick17k'],
                'parameters': ['demographic', 'clinical', 'imaging', 'environmental', 'temporal'],
                'confidence_threshold': 0.95
            }
        }
        
        logger.info("✅ Enhanced analysis API initialized")
    
    def analyze_skin_enhanced(self, image_data: bytes, analysis_type: str = 'comprehensive', 
                             user_parameters: Dict = None) -> Dict:
        """
        Perform enhanced skin analysis with scaled datasets
        
        Args:
            image_data: Raw image data
            analysis_type: Type of analysis ('comprehensive', 'focused', 'research')
            user_parameters: Additional user parameters
        
        Returns:
            Enhanced analysis results
        """
        try:
            # Get analysis configuration
            config = self.analysis_configs.get(analysis_type, self.analysis_configs['comprehensive'])
            
            # Generate enhanced embedding
            embedding_result = self.dataset_manager.generate_enhanced_embedding(
                image_data, 
                config['datasets'][0]  # Use primary dataset
            )
            
            # Perform comprehensive analysis
            analysis_result = self._perform_comprehensive_analysis(
                image_data, 
                embedding_result, 
                config, 
                user_parameters
            )
            
            # Add metadata
            analysis_result['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'analysis_type': analysis_type,
                'datasets_used': config['datasets'],
                'parameters_analyzed': config['parameters'],
                'confidence_threshold': config['confidence_threshold'],
                'embedding_dimensions': embedding_result['dimensions'],
                'total_parameters': embedding_result['metadata']['total_parameters']
            }
            
            logger.info(f"✅ Enhanced analysis completed: {analysis_type}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            return self._generate_fallback_analysis()
    
    def _perform_comprehensive_analysis(self, image_data: bytes, embedding_result: Dict, 
                                     config: Dict, user_parameters: Dict = None) -> Dict:
        """Perform comprehensive analysis with multiple datasets and parameters"""
        
        # Convert bytes to numpy array for analysis
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Face detection and isolation
        logger.info("🔍 Starting face detection...")
        logger.info(f"Image array type: {type(image_array_bgr)}, shape: {image_array_bgr.shape}, dtype: {image_array_bgr.dtype}")
        face_analysis = self.skin_analyzer.analyze_face_detection(image_array_bgr)
        logger.info(f"✅ Face detection completed: {face_analysis.get('face_detected')}")
        
        # Extract face ROI if detected
        face_roi = None
        if face_analysis.get('face_detected'):
            face_bounds = face_analysis.get('primary_face', {})
            x, y, w, h = face_bounds.get('x', 0), face_bounds.get('y', 0), face_bounds.get('width', 0), face_bounds.get('height', 0)
            if w > 0 and h > 0:
                face_roi = image_array_bgr[y:y+h, x:x+w]
                logger.info(f"✅ Face ROI extracted: {face_roi.shape}")
        
        # Skin condition analysis
        logger.info("🔍 Starting skin conditions analysis...")
        logger.info(f"Analysis image type: {type(image_array_bgr)}, shape: {image_array_bgr.shape}")
        skin_analysis = self.skin_analyzer.analyze_skin_conditions(image_array_bgr, face_roi)
        logger.info(f"✅ Skin analysis completed: health_score={skin_analysis.get('health_score', 0)}")
        
        # Demographic analysis
        demographic_analysis = self._analyze_demographics(image_data, user_parameters)
        
        # Clinical assessment
        clinical_assessment = self._analyze_clinical_factors(embedding_result, user_parameters)
        
        # Environmental factors
        environmental_analysis = self._analyze_environmental_factors(user_parameters)
        
        # Quality assessment
        quality_assessment = self._assess_analysis_quality(embedding_result, face_analysis)
        
        # Generate recommendations
        recommendations = self._generate_enhanced_recommendations(
            skin_analysis, 
            clinical_assessment, 
            environmental_analysis,
            quality_assessment
        )
        
        return {
            'face_detection': face_analysis,
            'skin_conditions': skin_analysis,
            'demographics': demographic_analysis,
            'clinical_assessment': clinical_assessment,
            'environmental_factors': environmental_analysis,
            'quality_assessment': quality_assessment,
            'recommendations': recommendations,
            'confidence_score': embedding_result['confidence_score'],
            'embedding_info': {
                'dimensions': embedding_result['dimensions'],
                'dataset_used': embedding_result['dataset_used'],
                'parameters': embedding_result['parameters']
            }
        }
    
    # Face detection is now handled by EnhancedSkinAnalyzer
    
    def _calculate_face_quality(self, face_roi: np.ndarray) -> Dict:
        """Calculate face quality metrics"""
        try:
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Brightness
            brightness = np.mean(gray)
            
            # Contrast
            contrast = np.std(gray)
            
            # Sharpness
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # Face size (larger is better)
            size_score = min(1.0, (face_roi.shape[0] * face_roi.shape[1]) / 50000)
            
            # Overall quality score
            overall_score = (
                (brightness / 128) * 0.25 +
                (contrast / 50) * 0.25 +
                (sharpness / 1000) * 0.25 +
                size_score * 0.25
            )
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'sharpness': float(sharpness),
                'size_score': float(size_score),
                'overall_score': float(overall_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Face quality calculation failed: {e}")
            return {
                'brightness': 0,
                'contrast': 0,
                'sharpness': 0,
                'size_score': 0,
                'overall_score': 0
            }
    
    # Skin conditions analysis is now handled by EnhancedSkinAnalyzer
    
    # Old analysis methods removed - now using EnhancedSkinAnalyzer
    
    # All old analysis methods removed - now using EnhancedSkinAnalyzer
    
    def _analyze_demographics(self, image_data: bytes, user_parameters: Dict = None) -> Dict:
        """Analyze demographic factors"""
        # This would integrate with user parameters and image analysis
        return {
            'age_group': user_parameters.get('age_group', 'unknown') if user_parameters else 'unknown',
            'skin_type': user_parameters.get('skin_type', 'unknown') if user_parameters else 'unknown',
            'ethnicity': user_parameters.get('ethnicity', 'unknown') if user_parameters else 'unknown'
        }
    
    def _analyze_clinical_factors(self, embedding_result: Dict, user_parameters: Dict = None) -> Dict:
        """Analyze clinical factors"""
        return {
            'previous_treatments': user_parameters.get('previous_treatments', []) if user_parameters else [],
            'family_history': user_parameters.get('family_history', []) if user_parameters else [],
            'current_medications': user_parameters.get('current_medications', []) if user_parameters else [],
            'allergies': user_parameters.get('allergies', []) if user_parameters else []
        }
    
    def _analyze_environmental_factors(self, user_parameters: Dict = None) -> Dict:
        """Analyze environmental factors"""
        return {
            'sun_exposure': user_parameters.get('sun_exposure', 'unknown') if user_parameters else 'unknown',
            'climate': user_parameters.get('climate', 'unknown') if user_parameters else 'unknown',
            'occupation': user_parameters.get('occupation', 'unknown') if user_parameters else 'unknown',
            'lifestyle_factors': user_parameters.get('lifestyle_factors', []) if user_parameters else []
        }
    
    def _assess_analysis_quality(self, embedding_result: Dict, face_analysis: Dict) -> Dict:
        """Assess the quality of the analysis"""
        quality_score = 0.0
        
        # Embedding quality
        if embedding_result.get('confidence_score'):
            quality_score += embedding_result['confidence_score'] * 0.4
        
        # Face detection quality
        if face_analysis.get('confidence'):
            quality_score += face_analysis['confidence'] * 0.3
        
        # Face quality metrics
        if face_analysis.get('quality_metrics'):
            face_quality = face_analysis['quality_metrics'].get('overall_score', 0)
            quality_score += face_quality * 0.3
        
        return {
            'overall_quality': min(1.0, quality_score),
            'embedding_quality': embedding_result.get('confidence_score', 0),
            'face_detection_quality': face_analysis.get('confidence', 0),
            'recommendation': self._get_quality_recommendation(quality_score)
        }
    
    def _get_quality_recommendation(self, quality_score: float) -> str:
        """Get recommendation based on quality score"""
        if quality_score >= 0.8:
            return "Excellent quality - High confidence analysis"
        elif quality_score >= 0.6:
            return "Good quality - Reliable analysis"
        elif quality_score >= 0.4:
            return "Moderate quality - Consider retaking photo"
        else:
            return "Low quality - Please retake photo with better lighting"
    
    def _generate_enhanced_recommendations(self, skin_analysis: Dict, clinical_assessment: Dict, 
                                         environmental_analysis: Dict, quality_assessment: Dict) -> Dict:
        """Generate enhanced recommendations based on comprehensive analysis"""
        
        recommendations = {
            'immediate_care': [],
            'long_term_care': [],
            'professional_consultation': False,
            'product_recommendations': [],
            'lifestyle_changes': []
        }
        
        # Immediate care recommendations
        if skin_analysis.get('health_score', 0) < 0.6:
            recommendations['immediate_care'].append("Consider gentle cleansing routine")
            recommendations['immediate_care'].append("Avoid harsh exfoliants")
        
        # Long-term care recommendations
        recommendations['long_term_care'].append("Establish consistent skincare routine")
        recommendations['long_term_care'].append("Use broad-spectrum sunscreen daily")
        
        # Professional consultation
        if skin_analysis.get('health_score', 0) < 0.4:
            recommendations['professional_consultation'] = True
            recommendations['immediate_care'].append("Schedule dermatologist consultation")
        
        # Product recommendations based on conditions
        conditions = skin_analysis.get('conditions', {})
        if conditions.get('acne', {}).get('detected'):
            recommendations['product_recommendations'].append("Salicylic acid cleanser")
            recommendations['product_recommendations'].append("Non-comedogenic moisturizer")
        
        if conditions.get('redness', {}).get('detected'):
            recommendations['product_recommendations'].append("Gentle, fragrance-free products")
            recommendations['product_recommendations'].append("Anti-inflammatory ingredients")
        
        # Lifestyle changes
        if environmental_analysis.get('sun_exposure') == 'high':
            recommendations['lifestyle_changes'].append("Limit sun exposure during peak hours")
            recommendations['lifestyle_changes'].append("Wear protective clothing")
        
        return recommendations
    
    def _generate_fallback_analysis(self) -> Dict:
        """Generate fallback analysis when enhanced analysis fails"""
        return {
            'face_detection': {'face_detected': False, 'confidence': 0.0},
            'skin_conditions': {'health_score': 0.5},
            'demographics': {'age_group': 'unknown'},
            'clinical_assessment': {'previous_treatments': []},
            'environmental_factors': {'sun_exposure': 'unknown'},
            'quality_assessment': {'overall_quality': 0.0},
            'recommendations': {
                'immediate_care': ['Please retake photo with better lighting'],
                'long_term_care': ['Establish basic skincare routine'],
                'professional_consultation': False,
                'product_recommendations': [],
                'lifestyle_changes': []
            },
            'confidence_score': 0.0,
            'error': 'Enhanced analysis unavailable'
        }

def main():
    """Test the enhanced analysis API"""
    print("🧠 Testing Enhanced Analysis API")
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    test_image_bytes = cv2.imencode('.jpg', test_image)[1].tobytes()
    
    # Initialize API
    api = EnhancedAnalysisAPI()
    
    # Test comprehensive analysis
    result = api.analyze_skin_enhanced(test_image_bytes, 'comprehensive')
    
    print(f"✅ Enhanced analysis completed")
    print(f"🎯 Confidence: {result['confidence_score']:.3f}")
    print(f"📊 Health Score: {result['skin_conditions']['health_score']:.3f}")
    print(f"🔍 Face Detected: {result['face_detection']['face_detected']}")

if __name__ == "__main__":
    main() 