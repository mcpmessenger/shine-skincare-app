"""
Integrated Analysis Pipeline - Complete AI service integration for skin analysis

This module provides a comprehensive pipeline that integrates all AI services:
- Google Vision Service for image analysis
- Skin Classifier Service for skin type classification
- Demographic Search Service for similar profile matching
- FAISS Vector Database for similarity search
- Enhanced recommendation generation
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result from the integrated analysis pipeline"""
    success: bool
    analysis_id: str
    processing_time: float
    vision_analysis: Dict[str, Any]
    skin_classification: Dict[str, Any]
    demographic_matches: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_scores: Dict[str, float]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'analysis_id': self.analysis_id,
            'processing_time': self.processing_time,
            'vision_analysis': self.vision_analysis,
            'skin_classification': self.skin_classification,
            'demographic_matches': self.demographic_matches,
            'recommendations': self.recommendations,
            'confidence_scores': self.confidence_scores,
            'error_message': self.error_message
        }


class IntegratedAnalysisPipeline:
    """
    Integrated pipeline that orchestrates all AI services for comprehensive skin analysis
    """
    
    def __init__(self, service_manager):
        """Initialize the pipeline with service manager"""
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, 
                     image_data: bytes, 
                     analysis_id: str,
                     user_id: str,
                     ethnicity: Optional[str] = None,
                     analysis_type: str = 'comprehensive') -> PipelineResult:
        """
        Run the complete analysis pipeline on an image
        
        Args:
            image_data: Raw image bytes
            analysis_id: Unique identifier for this analysis
            user_id: User identifier
            ethnicity: Optional ethnicity information
            analysis_type: Type of analysis to perform
            
        Returns:
            PipelineResult with all analysis results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting integrated analysis pipeline for {analysis_id}")
            
            # Step 1: Google Vision Analysis
            vision_result = self._run_vision_analysis(image_data, analysis_id)
            if not vision_result['success']:
                return self._create_error_result(
                    analysis_id, start_time, 
                    f"Vision analysis failed: {vision_result.get('error', 'Unknown error')}"
                )
            
            # Step 2: Skin Classification
            skin_result = self._run_skin_classification(image_data, analysis_id, ethnicity)
            if not skin_result['success']:
                return self._create_error_result(
                    analysis_id, start_time,
                    f"Skin classification failed: {skin_result.get('error', 'Unknown error')}"
                )
            
            # Step 3: Demographic Search
            demographic_result = self._run_demographic_search(
                vision_result['data'], skin_result['data'], analysis_id, ethnicity
            )
            
            # Step 4: Generate Recommendations
            recommendations = self._generate_recommendations(
                vision_result['data'], 
                skin_result['data'], 
                demographic_result.get('data', [])
            )
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                vision_result['data'],
                skin_result['data'],
                demographic_result.get('data', [])
            )
            
            processing_time = time.time() - start_time
            
            self.logger.info(f"Integrated analysis pipeline completed for {analysis_id} in {processing_time:.2f}s")
            
            return PipelineResult(
                success=True,
                analysis_id=analysis_id,
                processing_time=processing_time,
                vision_analysis=vision_result['data'],
                skin_classification=skin_result['data'],
                demographic_matches=demographic_result.get('data', []),
                recommendations=recommendations,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error in integrated analysis pipeline {analysis_id}: {str(e)}")
            return self._create_error_result(analysis_id, start_time, str(e))
    
    def _run_vision_analysis(self, image_data: bytes, analysis_id: str) -> Dict[str, Any]:
        """Run Google Vision analysis"""
        try:
            self.logger.info(f"Running vision analysis for {analysis_id}")
            
            google_vision_service = self.service_manager.get_service('google_vision')
            if not google_vision_service or not google_vision_service.is_available():
                return {'success': False, 'error': 'Google Vision service not available'}
            
            result = google_vision_service.analyze_image_from_bytes(image_data)
            
            if result.get('status') == 'success':
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'error': result.get('error', 'Vision analysis failed')}
                
        except Exception as e:
            self.logger.error(f"Error in vision analysis for {analysis_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_skin_classification(self, image_data: bytes, analysis_id: str, ethnicity: Optional[str]) -> Dict[str, Any]:
        """Run skin classification"""
        try:
            self.logger.info(f"Running skin classification for {analysis_id}")
            
            skin_classifier_service = self.service_manager.get_service('skin_classifier')
            if not skin_classifier_service or not skin_classifier_service.is_available():
                return {'success': False, 'error': 'Skin classifier service not available'}
            
            result = skin_classifier_service.classify_skin_type(
                image_data, 
                ethnicity=ethnicity if ethnicity else None
            )
            
            if result:
                return {'success': True, 'data': result}
            else:
                return {'success': False, 'error': 'Skin classification failed'}
                
        except Exception as e:
            self.logger.error(f"Error in skin classification for {analysis_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _run_demographic_search(self, vision_data: Dict, skin_data: Dict, analysis_id: str, ethnicity: Optional[str]) -> Dict[str, Any]:
        """Run demographic search for similar profiles"""
        try:
            self.logger.info(f"Running demographic search for {analysis_id}")
            
            demographic_search_service = self.service_manager.get_service('demographic_search')
            if not demographic_search_service or not demographic_search_service.is_available():
                self.logger.warning(f"Demographic search service not available for {analysis_id}")
                return {'success': False, 'data': [], 'error': 'Service not available'}
            
            # Extract features for demographic search
            search_features = {
                'skin_type': skin_data.get('fitzpatrick_type', 'III'),
                'ethnicity': ethnicity,
                'age_group': 'adult',  # Default for now
                'vision_features': vision_data.get('results', {})
            }
            
            result = demographic_search_service.search_similar_profiles(search_features)
            
            return {'success': True, 'data': result or []}
                
        except Exception as e:
            self.logger.error(f"Error in demographic search for {analysis_id}: {str(e)}")
            return {'success': False, 'data': [], 'error': str(e)}
    
    def _generate_recommendations(self, vision_data: Dict, skin_data: Dict, demographic_data: List) -> List[str]:
        """Generate comprehensive recommendations based on all analysis results"""
        recommendations = []
        
        # Base recommendations from skin classification
        fitzpatrick_type = skin_data.get('fitzpatrick_type', 'III')
        concerns = skin_data.get('concerns', [])
        
        # Fitzpatrick-specific recommendations
        if fitzpatrick_type in ['I', 'II']:
            recommendations.extend([
                'Use SPF 50+ sunscreen daily - your fair skin is highly susceptible to UV damage',
                'Consider gentle, fragrance-free products to avoid irritation',
                'Use a rich moisturizer to combat natural dryness'
            ])
        elif fitzpatrick_type in ['III', 'IV']:
            recommendations.extend([
                'Use SPF 30+ sunscreen daily for optimal protection',
                'Consider vitamin C serum for brightening and antioxidant protection',
                'Maintain consistent hydration with a balanced moisturizer'
            ])
        elif fitzpatrick_type in ['V', 'VI']:
            recommendations.extend([
                'Use SPF 30+ sunscreen daily - darker skin still needs UV protection',
                'Consider products with niacinamide to address hyperpigmentation',
                'Use gentle exfoliation to maintain even skin tone'
            ])
        
        # Concern-specific recommendations
        concern_lower = [c.lower() for c in concerns]
        if 'acne' in concern_lower:
            recommendations.append('Consider salicylic acid cleanser for acne-prone skin')
        
        if 'hyperpigmentation' in concern_lower:
            recommendations.append('Use products with kojic acid or arbutin for dark spots')
        
        if 'sensitivity' in concern_lower:
            recommendations.append('Patch test all new products and avoid harsh ingredients')
        
        if 'dryness' in concern_lower:
            recommendations.append('Use a hydrating serum with hyaluronic acid')
        
        if 'oiliness' in concern_lower:
            recommendations.append('Consider oil-free, non-comedogenic products')
        
        # Demographic-based recommendations
        if demographic_data:
            recommendations.append('Based on similar skin profiles, consider a gentle retinol product')
        
        # Vision analysis-based recommendations
        vision_results = vision_data.get('results', {})
        if vision_results.get('face_detection', {}).get('faces_found', 0) > 0:
            recommendations.append('Focus on targeted treatments for facial skin care')
        
        # Remove duplicates and limit to top 6 recommendations
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:6]
    
    def _calculate_confidence_scores(self, vision_data: Dict, skin_data: Dict, demographic_data: List) -> Dict[str, float]:
        """Calculate confidence scores for different aspects of the analysis"""
        scores = {}
        
        # Vision confidence
        scores['vision'] = vision_data.get('confidence', 0.8)
        
        # Skin classification confidence
        scores['skin_classification'] = skin_data.get('confidence', 0.8)
        
        # Demographic confidence (based on number and quality of matches)
        if demographic_data:
            avg_similarity = sum(match.get('similarity_score', 0.5) for match in demographic_data) / len(demographic_data)
            scores['demographic'] = min(avg_similarity, 0.9)
        else:
            scores['demographic'] = 0.5
        
        # Overall confidence (weighted average)
        scores['overall'] = (
            scores['vision'] * 0.3 +
            scores['skin_classification'] * 0.5 +
            scores['demographic'] * 0.2
        )
        
        return scores
    
    def _create_error_result(self, analysis_id: str, start_time: float, error_message: str) -> PipelineResult:
        """Create an error result"""
        processing_time = time.time() - start_time
        
        return PipelineResult(
            success=False,
            analysis_id=analysis_id,
            processing_time=processing_time,
            vision_analysis={},
            skin_classification={},
            demographic_matches=[],
            recommendations=[],
            confidence_scores={'overall': 0.0},
            error_message=error_message
        )
    
    def get_pipeline_health(self) -> Dict[str, Any]:
        """Get health status of all pipeline services"""
        services = ['google_vision', 'skin_classifier', 'demographic_search', 'faiss']
        health_status = {}
        
        for service_name in services:
            try:
                service = self.service_manager.get_service(service_name)
                if service:
                    health_status[service_name] = {
                        'available': service.is_available(),
                        'status': 'healthy' if service.is_available() else 'unhealthy'
                    }
                else:
                    health_status[service_name] = {
                        'available': False,
                        'status': 'not_found'
                    }
            except Exception as e:
                health_status[service_name] = {
                    'available': False,
                    'status': 'error',
                    'error': str(e)
                }
        
        overall_healthy = all(status.get('available', False) for status in health_status.values())
        
        return {
            'overall_status': 'healthy' if overall_healthy else 'degraded',
            'services': health_status,
            'timestamp': datetime.utcnow().isoformat()
        }