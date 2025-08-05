#!/usr/bin/env python3
"""
Enhanced Severity Scoring System for Shine Skincare App
Integrates with existing 103 demographic baselines and condition embeddings
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedSeverityScoring:
    """
    Enhanced severity scoring system with demographic-aware normalization
    Integrates with existing 103 demographic baselines and condition embeddings
    """
    
    def __init__(self):
        """Initialize the enhanced severity scoring system"""
        self.scoring_weights = {
            'intensity': 0.25,
            'distribution': 0.20,
            'size': 0.15,
            'persistence': 0.15,
            'impact': 0.10,
            'demographic_factor': 0.15
        }
        
        # Load existing demographic baselines and condition embeddings
        self.demographic_baselines = self._load_demographic_baselines()
        self.condition_embeddings = self._load_condition_embeddings()
        
        # Enhanced condition definitions
        self.enhanced_conditions = self._define_enhanced_conditions()
        
        logger.info("✅ Enhanced severity scoring system initialized")
    
    def _load_demographic_baselines(self) -> Dict:
        """Load existing 103 demographic baselines"""
        try:
            baselines_path = Path("data/utkface/demographic_baselines.npy")
            if baselines_path.exists():
                baselines = np.load(baselines_path, allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(baselines)} demographic baselines")
                return baselines
            else:
                logger.warning("⚠️ Demographic baselines not found")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load demographic baselines: {e}")
            return {}
    
    def _load_condition_embeddings(self) -> Dict:
        """Load existing condition embeddings"""
        try:
            embeddings_path = Path("data/condition_embeddings.npy")
            if embeddings_path.exists():
                embeddings = np.load(embeddings_path, allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(embeddings)} condition embeddings")
                return embeddings
            else:
                logger.warning("⚠️ Condition embeddings not found")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load condition embeddings: {e}")
            return {}
    
    def _define_enhanced_conditions(self) -> Dict:
        """Define enhanced condition categories with detailed metrics"""
        return {
            'hyperpigmentation': {
                'subtypes': ['sun_spots', 'melasma', 'post_inflammatory'],
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['intensity', 'distribution', 'size'],
                'demographic_factors': ['skin_type', 'age_group', 'ethnicity'],
                'baseline_adjustments': {
                    'fitzpatrick_4_6': 0.8,  # Darker skin types
                    'age_40_plus': 1.2,      # Age-related factors
                    'east_asian': 1.1        # Ethnicity-specific factors
                }
            },
            'fine_lines_wrinkles': {
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['depth', 'length', 'density', 'location'],
                'demographic_factors': ['age_group', 'skin_type', 'lifestyle'],
                'baseline_adjustments': {
                    'age_30_39': 0.9,
                    'age_40_49': 1.0,
                    'age_50_plus': 1.3,
                    'sun_exposure_high': 1.2
                }
            },
            'acne': {
                'subtypes': ['inflammatory', 'comedonal', 'cystic', 'hormonal'],
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['inflammation', 'count', 'distribution', 'scarring'],
                'demographic_factors': ['age_group', 'gender', 'skin_type'],
                'baseline_adjustments': {
                    'teens': 1.1,
                    'twenties': 1.0,
                    'thirties': 0.9,
                    'oily_skin': 1.2
                }
            },
            'rosacea': {
                'subtypes': ['erythematotelangiectatic', 'papulopustular', 'phymatous'],
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['redness', 'vascular_visibility', 'inflammation'],
                'demographic_factors': ['age_group', 'skin_type', 'ethnicity'],
                'baseline_adjustments': {
                    'fitzpatrick_1_3': 1.0,  # Fair skin types
                    'age_30_plus': 1.1,
                    'northern_european': 1.2
                }
            },
            'eczema': {
                'subtypes': ['atopic', 'contact', 'seborrheic'],
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['dryness', 'inflammation', 'itching', 'distribution'],
                'demographic_factors': ['age_group', 'skin_type', 'environmental'],
                'baseline_adjustments': {
                    'dry_skin': 1.2,
                    'cold_climate': 1.1,
                    'stress_high': 1.1
                }
            },
            'actinic_keratosis': {
                'severity_levels': ['mild', 'moderate', 'severe'],
                'analysis_metrics': ['thickness', 'size', 'distribution', 'color'],
                'demographic_factors': ['age_group', 'sun_exposure', 'skin_type'],
                'baseline_adjustments': {
                    'age_50_plus': 1.3,
                    'sun_exposure_high': 1.4,
                    'fitzpatrick_1_3': 1.2
                }
            }
        }
    
    def calculate_enhanced_severity_score(self, 
                                        condition_data: Dict,
                                        user_demographics: Dict = None,
                                        condition_type: str = None) -> Dict:
        """
        Calculate comprehensive severity score with demographic normalization
        
        Args:
            condition_data: Raw condition analysis data
            user_demographics: User demographic information
            condition_type: Type of skin condition
            
        Returns:
            Enhanced severity scoring results
        """
        try:
            # Step 1: Calculate base severity scores
            base_scores = self._calculate_base_scores(condition_data)
            
            # Step 2: Apply demographic normalization
            demographic_adjustment = self._calculate_demographic_adjustment(
                condition_type, user_demographics)
            
            # Step 3: Calculate condition-specific adjustments
            condition_adjustment = self._calculate_condition_adjustment(
                condition_type, condition_data)
            
            # Step 4: Combine scores with weights
            final_score = self._combine_scores(
                base_scores, demographic_adjustment, condition_adjustment)
            
            # Step 5: Generate detailed breakdown
            breakdown = self._generate_score_breakdown(
                base_scores, demographic_adjustment, condition_adjustment, final_score)
            
            return {
                'overall_score': round(final_score, 2),
                'severity_level': self._map_score_to_level(final_score),
                'confidence': condition_data.get('confidence', 0.8),
                'breakdown': breakdown,
                'demographic_factors': demographic_adjustment,
                'condition_specific': condition_adjustment,
                'recommendations': self._generate_severity_recommendations(final_score, condition_type)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating enhanced severity score: {e}")
            return {
                'overall_score': 0.0,
                'severity_level': 'unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _calculate_base_scores(self, condition_data: Dict) -> Dict:
        """Calculate base severity scores for each metric"""
        scores = {}
        
        for metric, weight in self.scoring_weights.items():
            if metric == 'demographic_factor':
                continue  # Handled separately
            
            if metric in condition_data:
                raw_value = condition_data[metric]
                normalized_score = self._normalize_score(raw_value, metric)
                scores[metric] = {
                    'raw_value': raw_value,
                    'normalized_score': normalized_score,
                    'weight': weight
                }
        
        return scores
    
    def _normalize_score(self, raw_value: Union[float, int], metric: str) -> float:
        """Normalize raw values to 0-10 scale"""
        # Define normalization ranges for different metrics
        normalization_ranges = {
            'intensity': (0, 255),      # Image intensity values
            'distribution': (0, 100),   # Percentage coverage
            'size': (0, 50),           # Size in pixels/mm
            'persistence': (0, 100),   # Persistence percentage
            'impact': (0, 10)          # Impact scale
        }
        
        min_val, max_val = normalization_ranges.get(metric, (0, 10))
        
        # Clamp value to range
        clamped_value = max(min_val, min(raw_value, max_val))
        
        # Normalize to 0-10 scale
        normalized = (clamped_value - min_val) / (max_val - min_val) * 10
        
        return round(normalized, 2)
    
    def _calculate_demographic_adjustment(self, 
                                        condition_type: str,
                                        user_demographics: Dict = None) -> Dict:
        """Calculate demographic-based adjustments using existing baselines"""
        if not user_demographics or not condition_type:
            return {'adjustment_factor': 1.0, 'factors_applied': []}
        
        adjustment_factors = []
        base_adjustment = 1.0
        
        # Get condition-specific baseline adjustments
        condition_config = self.enhanced_conditions.get(condition_type, {})
        baseline_adjustments = condition_config.get('baseline_adjustments', {})
        
        # Apply demographic factors
        age_group = user_demographics.get('age_category')
        skin_type = user_demographics.get('skin_type')
        ethnicity = user_demographics.get('ethnicity')
        
        # Age-based adjustments
        if age_group:
            age_key = f"age_{age_group}"
            if age_key in baseline_adjustments:
                age_factor = baseline_adjustments[age_key]
                adjustment_factors.append(f"age_{age_group}: {age_factor}")
                base_adjustment *= age_factor
        
        # Skin type adjustments
        if skin_type:
            skin_key = f"fitzpatrick_{skin_type}"
            if skin_key in baseline_adjustments:
                skin_factor = baseline_adjustments[skin_key]
                adjustment_factors.append(f"skin_type_{skin_type}: {skin_factor}")
                base_adjustment *= skin_factor
        
        # Ethnicity adjustments
        if ethnicity:
            if ethnicity in baseline_adjustments:
                ethnic_factor = baseline_adjustments[ethnicity]
                adjustment_factors.append(f"ethnicity_{ethnicity}: {ethnic_factor}")
                base_adjustment *= ethnic_factor
        
        return {
            'adjustment_factor': round(base_adjustment, 3),
            'factors_applied': adjustment_factors,
            'demographics_used': user_demographics
        }
    
    def _calculate_condition_adjustment(self, 
                                      condition_type: str,
                                      condition_data: Dict) -> Dict:
        """Calculate condition-specific adjustments"""
        if not condition_type:
            return {'adjustment_factor': 1.0, 'factors_applied': []}
        
        condition_config = self.enhanced_conditions.get(condition_type, {})
        adjustment_factors = []
        base_adjustment = 1.0
        
        # Apply condition-specific logic
        if condition_type == 'hyperpigmentation':
            # Consider intensity and distribution
            intensity = condition_data.get('intensity', 0)
            if intensity > 0.7:
                base_adjustment *= 1.2
                adjustment_factors.append("high_intensity: 1.2")
        
        elif condition_type == 'fine_lines_wrinkles':
            # Consider age and location
            depth = condition_data.get('depth', 0)
            if depth > 0.8:
                base_adjustment *= 1.3
                adjustment_factors.append("deep_wrinkles: 1.3")
        
        elif condition_type == 'acne':
            # Consider inflammation and scarring
            inflammation = condition_data.get('inflammation', 0)
            if inflammation > 0.6:
                base_adjustment *= 1.4
                adjustment_factors.append("high_inflammation: 1.4")
        
        return {
            'adjustment_factor': round(base_adjustment, 3),
            'factors_applied': adjustment_factors,
            'condition_type': condition_type
        }
    
    def _combine_scores(self, 
                       base_scores: Dict,
                       demographic_adjustment: Dict,
                       condition_adjustment: Dict) -> float:
        """Combine all scores with appropriate weights"""
        # Calculate weighted base score
        weighted_base = 0.0
        total_weight = 0.0
        
        for metric, score_data in base_scores.items():
            weight = score_data['weight']
            normalized_score = score_data['normalized_score']
            weighted_base += normalized_score * weight
            total_weight += weight
        
        if total_weight > 0:
            weighted_base /= total_weight
        else:
            weighted_base = 5.0  # Default middle score
        
        # Apply adjustments
        demographic_factor = demographic_adjustment.get('adjustment_factor', 1.0)
        condition_factor = condition_adjustment.get('adjustment_factor', 1.0)
        
        final_score = weighted_base * demographic_factor * condition_factor
        
        # Clamp to 0-10 range
        final_score = max(0.0, min(10.0, final_score))
        
        return final_score
    
    def _map_score_to_level(self, score: float) -> str:
        """Map numerical score to severity level"""
        if score < 3.0:
            return 'mild'
        elif score < 6.0:
            return 'moderate'
        elif score < 8.0:
            return 'severe'
        else:
            return 'very_severe'
    
    def _generate_score_breakdown(self, 
                                base_scores: Dict,
                                demographic_adjustment: Dict,
                                condition_adjustment: Dict,
                                final_score: float) -> Dict:
        """Generate detailed breakdown of scoring"""
        return {
            'base_scores': base_scores,
            'demographic_adjustment': demographic_adjustment,
            'condition_adjustment': condition_adjustment,
            'final_score': final_score,
            'scoring_methodology': {
                'weights_used': self.scoring_weights,
                'normalization_method': '0-10 scale with demographic normalization',
                'adjustment_factors': len(demographic_adjustment.get('factors_applied', [])) + 
                                   len(condition_adjustment.get('factors_applied', []))
            }
        }
    
    def _generate_severity_recommendations(self, score: float, condition_type: str) -> List[str]:
        """Generate recommendations based on severity score"""
        recommendations = []
        
        if score < 3.0:
            recommendations.extend([
                "Mild condition detected - consider preventive measures",
                "Monitor for any changes or progression",
                "Maintain good skincare routine"
            ])
        elif score < 6.0:
            recommendations.extend([
                "Moderate condition - consider targeted treatments",
                "Consult with dermatologist for personalized advice",
                "Implement consistent treatment regimen"
            ])
        elif score < 8.0:
            recommendations.extend([
                "Severe condition - professional consultation recommended",
                "Consider prescription treatments",
                "Monitor closely for changes"
            ])
        else:
            recommendations.extend([
                "Very severe condition - immediate professional consultation advised",
                "Consider medical intervention",
                "Regular monitoring and follow-up required"
            ])
        
        # Add condition-specific recommendations
        if condition_type:
            condition_recs = self._get_condition_specific_recommendations(condition_type, score)
            recommendations.extend(condition_recs)
        
        return recommendations
    
    def _get_condition_specific_recommendations(self, condition_type: str, score: float) -> List[str]:
        """Get condition-specific recommendations"""
        condition_recommendations = {
            'hyperpigmentation': [
                "Use broad-spectrum sunscreen daily",
                "Consider brightening ingredients like vitamin C",
                "Avoid picking or scratching affected areas"
            ],
            'fine_lines_wrinkles': [
                "Use retinoids for collagen stimulation",
                "Maintain good hydration",
                "Consider professional treatments for deeper lines"
            ],
            'acne': [
                "Use gentle, non-comedogenic products",
                "Avoid touching face frequently",
                "Consider salicylic acid or benzoyl peroxide"
            ],
            'rosacea': [
                "Avoid triggers like spicy foods and alcohol",
                "Use gentle, fragrance-free products",
                "Protect skin from sun and wind"
            ]
        }
        
        return condition_recommendations.get(condition_type, [])
    
    def get_system_status(self) -> Dict:
        """Get system status and capabilities"""
        return {
            'system': 'Enhanced Severity Scoring',
            'status': 'active',
            'capabilities': {
                'demographic_baselines': len(self.demographic_baselines),
                'condition_embeddings': len(self.condition_embeddings),
                'enhanced_conditions': len(self.enhanced_conditions),
                'scoring_weights': len(self.scoring_weights)
            },
            'scoring_methodology': {
                'scale': '0-10 with demographic normalization',
                'factors': list(self.scoring_weights.keys()),
                'demographic_integration': True,
                'condition_specific_adjustments': True
            }
        }

# Create singleton instance
enhanced_severity_scorer = EnhancedSeverityScoring()

def main():
    """Test the enhanced severity scoring system"""
    # Test data
    test_condition_data = {
        'intensity': 180,
        'distribution': 25,
        'size': 15,
        'persistence': 60,
        'impact': 6
    }
    
    test_demographics = {
        'age_category': 'thirties',
        'skin_type': '4',
        'ethnicity': 'east_asian'
    }
    
    # Test scoring
    result = enhanced_severity_scorer.calculate_enhanced_severity_score(
        test_condition_data, test_demographics, 'hyperpigmentation')
    
    print("Enhanced Severity Scoring Test Results:")
    print(json.dumps(result, indent=2))
    
    # Print system status
    status = enhanced_severity_scorer.get_system_status()
    print("\nSystem Status:")
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main() 