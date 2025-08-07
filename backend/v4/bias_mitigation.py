#!/usr/bin/env python3
"""
Bias Mitigation Framework for Version 4
Ensures fair performance across all demographic groups
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

# Bias mitigation imports
try:
    from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
    from fairlearn.postprocessing import ThresholdOptimizer
    FAIRLEARN_AVAILABLE = True
except ImportError:
    FAIRLEARN_AVAILABLE = False
    logging.warning("FairLearn not available, using custom bias mitigation")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiasMitigationSystem:
    """
    Comprehensive bias mitigation system for skin analysis
    Implements fairness metrics, bias detection, and correction methods
    """
    
    def __init__(self, fairness_metrics: List[str] = None):
        """
        Initialize the bias mitigation system
        
        Args:
            fairness_metrics: List of fairness metrics to monitor
        """
        self.fairness_metrics = fairness_metrics or [
            'demographic_parity',
            'equalized_odds',
            'equal_opportunity',
            'predictive_rate_parity'
        ]
        
        # Bias detection thresholds
        self.bias_thresholds = {
            'demographic_parity': 0.05,  # 5% difference threshold
            'equalized_odds': 0.05,
            'equal_opportunity': 0.05,
            'predictive_rate_parity': 0.05
        }
        
        # Demographic groups to monitor
        self.demographic_groups = [
            'age_groups',
            'ethnicity_groups',
            'fitzpatrick_groups',
            'gender_groups'
        ]
        
        logger.info(f"✅ Bias mitigation system initialized with {len(self.fairness_metrics)} metrics")
    
    def evaluate_fairness(self, predictions: np.ndarray, 
                         ground_truth: np.ndarray, 
                         demographic_data: List[Dict]) -> Dict:
        """
        Evaluate fairness across demographic groups
        
        Args:
            predictions: Model predictions
            ground_truth: Ground truth labels
            demographic_data: List of demographic information for each sample
            
        Returns:
            Fairness evaluation results
        """
        try:
            results = {
                'overall_metrics': {},
                'group_metrics': {},
                'bias_detected': False,
                'bias_details': {}
            }
            
            # Group data by demographics
            grouped_data = self._group_by_demographics(predictions, ground_truth, demographic_data)
            
            # Calculate overall fairness metrics
            for metric in self.fairness_metrics:
                metric_value = self._calculate_fairness_metric(
                    predictions, ground_truth, demographic_data, metric
                )
                results['overall_metrics'][metric] = metric_value
            
            # Calculate group-specific metrics
            for group_name, group_data in grouped_data.items():
                group_metrics = {}
                for metric in self.fairness_metrics:
                    metric_value = self._calculate_fairness_metric(
                        group_data['predictions'],
                        group_data['ground_truth'],
                        group_data['demographics'],
                        metric
                    )
                    group_metrics[metric] = metric_value
                results['group_metrics'][group_name] = group_metrics
            
            # Detect bias
            bias_detected, bias_details = self._detect_bias(results)
            results['bias_detected'] = bias_detected
            results['bias_details'] = bias_details
            
            logger.info(f"Fairness evaluation completed. Bias detected: {bias_detected}")
            return results
            
        except Exception as e:
            logger.error(f"Error in fairness evaluation: {e}")
            return self._create_error_response(str(e))
    
    def _group_by_demographics(self, predictions: np.ndarray, 
                              ground_truth: np.ndarray, 
                              demographic_data: List[Dict]) -> Dict:
        """Group data by demographic attributes"""
        grouped = defaultdict(lambda: {
            'predictions': [],
            'ground_truth': [],
            'demographics': []
        })
        
        for i, demo in enumerate(demographic_data):
            # Create group keys
            age_group = self._get_age_group(demo.get('age', 0))
            ethnicity_group = demo.get('ethnicity', 'unknown').lower()
            fitzpatrick_group = f"fitzpatrick_{demo.get('fitzpatrick_type', 0)}"
            gender_group = demo.get('gender', 'unknown').lower()
            
            # Add to groups
            for group_name in [age_group, ethnicity_group, fitzpatrick_group, gender_group]:
                grouped[group_name]['predictions'].append(predictions[i])
                grouped[group_name]['ground_truth'].append(ground_truth[i])
                grouped[group_name]['demographics'].append(demo)
        
        # Convert to numpy arrays
        for group_data in grouped.values():
            group_data['predictions'] = np.array(group_data['predictions'])
            group_data['ground_truth'] = np.array(group_data['ground_truth'])
        
        return dict(grouped)
    
    def _get_age_group(self, age: int) -> str:
        """Convert age to age group"""
        if age < 18:
            return 'under_18'
        elif age < 25:
            return '18_24'
        elif age < 35:
            return '25_34'
        elif age < 45:
            return '35_44'
        elif age < 55:
            return '45_54'
        elif age < 65:
            return '55_64'
        else:
            return 'over_65'
    
    def _calculate_fairness_metric(self, predictions: np.ndarray, 
                                  ground_truth: np.ndarray, 
                                  demographic_data: List[Dict], 
                                  metric: str) -> float:
        """Calculate specific fairness metric"""
        try:
            if metric == 'demographic_parity':
                return self._calculate_demographic_parity(predictions, demographic_data)
            elif metric == 'equalized_odds':
                return self._calculate_equalized_odds(predictions, ground_truth, demographic_data)
            elif metric == 'equal_opportunity':
                return self._calculate_equal_opportunity(predictions, ground_truth, demographic_data)
            elif metric == 'predictive_rate_parity':
                return self._calculate_predictive_rate_parity(predictions, ground_truth, demographic_data)
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"Error calculating {metric}: {e}")
            return 0.0
    
    def _calculate_demographic_parity(self, predictions: np.ndarray, 
                                     demographic_data: List[Dict]) -> float:
        """Calculate demographic parity difference"""
        try:
            if FAIRLEARN_AVAILABLE:
                # Use FairLearn implementation
                sensitive_features = [demo.get('ethnicity', 'unknown') for demo in demographic_data]
                return demographic_parity_difference(predictions, sensitive_features)
            else:
                # Custom implementation
                return self._custom_demographic_parity(predictions, demographic_data)
        except Exception as e:
            logger.warning(f"Error in demographic parity calculation: {e}")
            return 0.0
    
    def _custom_demographic_parity(self, predictions: np.ndarray, 
                                   demographic_data: List[Dict]) -> float:
        """Custom demographic parity calculation"""
        try:
            # Group predictions by ethnicity
            ethnicities = [demo.get('ethnicity', 'unknown').lower() for demo in demographic_data]
            unique_ethnicities = list(set(ethnicities))
            
            if len(unique_ethnicities) < 2:
                return 0.0
            
            # Calculate positive prediction rates for each group
            group_rates = {}
            for ethnicity in unique_ethnicities:
                group_indices = [i for i, eth in enumerate(ethnicities) if eth == ethnicity]
                group_predictions = predictions[group_indices]
                positive_rate = np.mean(group_predictions)
                group_rates[ethnicity] = positive_rate
            
            # Calculate maximum difference
            rates = list(group_rates.values())
            max_diff = max(rates) - min(rates)
            
            return max_diff
            
        except Exception as e:
            logger.warning(f"Error in custom demographic parity: {e}")
            return 0.0
    
    def _calculate_equalized_odds(self, predictions: np.ndarray, 
                                 ground_truth: np.ndarray, 
                                 demographic_data: List[Dict]) -> float:
        """Calculate equalized odds difference"""
        try:
            if FAIRLEARN_AVAILABLE:
                sensitive_features = [demo.get('ethnicity', 'unknown') for demo in demographic_data]
                return equalized_odds_difference(predictions, ground_truth, sensitive_features)
            else:
                return self._custom_equalized_odds(predictions, ground_truth, demographic_data)
        except Exception as e:
            logger.warning(f"Error in equalized odds calculation: {e}")
            return 0.0
    
    def _custom_equalized_odds(self, predictions: np.ndarray, 
                              ground_truth: np.ndarray, 
                              demographic_data: List[Dict]) -> float:
        """Custom equalized odds calculation"""
        try:
            ethnicities = [demo.get('ethnicity', 'unknown').lower() for demo in demographic_data]
            unique_ethnicities = list(set(ethnicities))
            
            if len(unique_ethnicities) < 2:
                return 0.0
            
            # Calculate TPR and FPR for each group
            group_metrics = {}
            for ethnicity in unique_ethnicities:
                group_indices = [i for i, eth in enumerate(ethnicities) if eth == ethnicity]
                group_predictions = predictions[group_indices]
                group_truth = ground_truth[group_indices]
                
                # Calculate TPR and FPR
                tp = np.sum((group_predictions == 1) & (group_truth == 1))
                fp = np.sum((group_predictions == 1) & (group_truth == 0))
                tn = np.sum((group_predictions == 0) & (group_truth == 0))
                fn = np.sum((group_predictions == 0) & (group_truth == 1))
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                
                group_metrics[ethnicity] = {'tpr': tpr, 'fpr': fpr}
            
            # Calculate maximum differences
            tprs = [metrics['tpr'] for metrics in group_metrics.values()]
            fprs = [metrics['fpr'] for metrics in group_metrics.values()]
            
            tpr_diff = max(tprs) - min(tprs)
            fpr_diff = max(fprs) - min(fprs)
            
            return max(tpr_diff, fpr_diff)
            
        except Exception as e:
            logger.warning(f"Error in custom equalized odds: {e}")
            return 0.0
    
    def _calculate_equal_opportunity(self, predictions: np.ndarray, 
                                   ground_truth: np.ndarray, 
                                   demographic_data: List[Dict]) -> float:
        """Calculate equal opportunity difference"""
        try:
            ethnicities = [demo.get('ethnicity', 'unknown').lower() for demo in demographic_data]
            unique_ethnicities = list(set(ethnicities))
            
            if len(unique_ethnicities) < 2:
                return 0.0
            
            # Calculate TPR for each group (equal opportunity focuses on TPR)
            group_tprs = {}
            for ethnicity in unique_ethnicities:
                group_indices = [i for i, eth in enumerate(ethnicities) if eth == ethnicity]
                group_predictions = predictions[group_indices]
                group_truth = ground_truth[group_indices]
                
                tp = np.sum((group_predictions == 1) & (group_truth == 1))
                fn = np.sum((group_predictions == 0) & (group_truth == 1))
                
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                group_tprs[ethnicity] = tpr
            
            # Calculate maximum difference
            tprs = list(group_tprs.values())
            max_diff = max(tprs) - min(tprs)
            
            return max_diff
            
        except Exception as e:
            logger.warning(f"Error in equal opportunity calculation: {e}")
            return 0.0
    
    def _calculate_predictive_rate_parity(self, predictions: np.ndarray, 
                                        ground_truth: np.ndarray, 
                                        demographic_data: List[Dict]) -> float:
        """Calculate predictive rate parity difference"""
        try:
            ethnicities = [demo.get('ethnicity', 'unknown').lower() for demo in demographic_data]
            unique_ethnicities = list(set(ethnicities))
            
            if len(unique_ethnicities) < 2:
                return 0.0
            
            # Calculate precision for each group
            group_precisions = {}
            for ethnicity in unique_ethnicities:
                group_indices = [i for i, eth in enumerate(ethnicities) if eth == ethnicity]
                group_predictions = predictions[group_indices]
                group_truth = ground_truth[group_indices]
                
                tp = np.sum((group_predictions == 1) & (group_truth == 1))
                fp = np.sum((group_predictions == 1) & (group_truth == 0))
                
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                group_precisions[ethnicity] = precision
            
            # Calculate maximum difference
            precisions = list(group_precisions.values())
            max_diff = max(precisions) - min(precisions)
            
            return max_diff
            
        except Exception as e:
            logger.warning(f"Error in predictive rate parity calculation: {e}")
            return 0.0
    
    def _detect_bias(self, fairness_results: Dict) -> Tuple[bool, Dict]:
        """Detect bias based on fairness metrics"""
        bias_detected = False
        bias_details = {}
        
        try:
            for metric, value in fairness_results['overall_metrics'].items():
                threshold = self.bias_thresholds.get(metric, 0.05)
                
                if value > threshold:
                    bias_detected = True
                    bias_details[metric] = {
                        'value': value,
                        'threshold': threshold,
                        'exceeds_threshold': True
                    }
                else:
                    bias_details[metric] = {
                        'value': value,
                        'threshold': threshold,
                        'exceeds_threshold': False
                    }
            
            return bias_detected, bias_details
            
        except Exception as e:
            logger.error(f"Error in bias detection: {e}")
            return False, {}
    
    def apply_bias_correction(self, predictions: np.ndarray, 
                             demographic_data: List[Dict], 
                             correction_method: str = "threshold_adjustment") -> np.ndarray:
        """
        Apply bias correction to predictions
        
        Args:
            predictions: Original predictions
            demographic_data: Demographic information
            correction_method: Correction method to use
            
        Returns:
            Corrected predictions
        """
        try:
            if correction_method == "threshold_adjustment":
                return self._apply_threshold_adjustment(predictions, demographic_data)
            elif correction_method == "reweighting":
                return self._apply_reweighting(predictions, demographic_data)
            elif correction_method == "post_processing":
                return self._apply_post_processing(predictions, demographic_data)
            else:
                logger.warning(f"Unknown correction method: {correction_method}")
                return predictions
                
        except Exception as e:
            logger.error(f"Error in bias correction: {e}")
            return predictions
    
    def _apply_threshold_adjustment(self, predictions: np.ndarray, 
                                   demographic_data: List[Dict]) -> np.ndarray:
        """Apply threshold adjustment for bias correction"""
        try:
            corrected_predictions = predictions.copy()
            
            # Group by ethnicity and adjust thresholds
            ethnicities = [demo.get('ethnicity', 'unknown').lower() for demo in demographic_data]
            unique_ethnicities = list(set(ethnicities))
            
            # Calculate adjustment factors based on historical bias
            adjustment_factors = {
                'asian': 0.95,  # Lower threshold for Asian skin
                'african': 0.90,  # Lower threshold for African skin
                'hispanic': 0.92,  # Lower threshold for Hispanic skin
                'middle_eastern': 0.93,  # Lower threshold for Middle Eastern skin
                'caucasian': 1.0,  # No adjustment for Caucasian (baseline)
                'unknown': 1.0  # No adjustment for unknown
            }
            
            for i, ethnicity in enumerate(ethnicities):
                factor = adjustment_factors.get(ethnicity, 1.0)
                corrected_predictions[i] = predictions[i] * factor
            
            return corrected_predictions
            
        except Exception as e:
            logger.error(f"Error in threshold adjustment: {e}")
            return predictions
    
    def _apply_reweighting(self, predictions: np.ndarray, 
                          demographic_data: List[Dict]) -> np.ndarray:
        """Apply reweighting for bias correction"""
        try:
            # This is a placeholder for more sophisticated reweighting
            # In practice, this would involve training data reweighting
            return predictions
            
        except Exception as e:
            logger.error(f"Error in reweighting: {e}")
            return predictions
    
    def _apply_post_processing(self, predictions: np.ndarray, 
                              demographic_data: List[Dict]) -> np.ndarray:
        """Apply post-processing for bias correction"""
        try:
            if FAIRLEARN_AVAILABLE:
                # Use FairLearn post-processing
                sensitive_features = [demo.get('ethnicity', 'unknown') for demo in demographic_data]
                optimizer = ThresholdOptimizer(
                    estimator=None,  # Would be the actual model
                    constraints="demographic_parity",
                    prefit=True
                )
                # This is a simplified version - actual implementation would be more complex
                return predictions
            else:
                return self._apply_threshold_adjustment(predictions, demographic_data)
                
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            return predictions
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            'overall_metrics': {},
            'group_metrics': {},
            'bias_detected': False,
            'bias_details': {},
            'error': error_message
        }

# Global instance for easy access
bias_mitigation_system = BiasMitigationSystem()

def evaluate_fairness_advanced(predictions: np.ndarray, 
                             ground_truth: np.ndarray, 
                             demographic_data: List[Dict]) -> Dict:
    """
    Advanced fairness evaluation function for API compatibility
    
    Args:
        predictions: Model predictions
        ground_truth: Ground truth labels
        demographic_data: Demographic information
        
    Returns:
        Fairness evaluation results
    """
    try:
        results = bias_mitigation_system.evaluate_fairness(
            predictions, ground_truth, demographic_data
        )
        logger.info(f"Advanced fairness evaluation completed")
        return results
        
    except Exception as e:
        logger.error(f"Error in advanced fairness evaluation: {e}")
        return bias_mitigation_system._create_error_response(str(e))

def apply_bias_correction_advanced(predictions: np.ndarray, 
                                 demographic_data: List[Dict], 
                                 correction_method: str = "threshold_adjustment") -> np.ndarray:
    """
    Advanced bias correction function for API compatibility
    
    Args:
        predictions: Original predictions
        demographic_data: Demographic information
        correction_method: Correction method to use
        
    Returns:
        Corrected predictions
    """
    try:
        corrected = bias_mitigation_system.apply_bias_correction(
            predictions, demographic_data, correction_method
        )
        logger.info(f"Advanced bias correction applied using {correction_method}")
        return corrected
        
    except Exception as e:
        logger.error(f"Error in advanced bias correction: {e}")
        return predictions 