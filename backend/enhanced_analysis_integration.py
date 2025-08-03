#!/usr/bin/env python3
"""
Enhanced Analysis Integration System
Combines SCIN dataset processing with result parameter optimization and product recommendations
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import math

# Import our custom modules
from result_parameter_optimizer import ResultParameterOptimizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAnalysisIntegration:
    def __init__(self):
        self.base_dir = Path("scin_dataset")
        self.processed_data_file = self.base_dir / "processed" / "scin_processed_data.json"
        
        # Initialize components
        self.parameter_optimizer = ResultParameterOptimizer()
        self.scin_data = self._load_scin_data()
        
        # Analysis configuration
        self.analysis_config = {
            "similarity_threshold": 0.75,
            "max_recommendations": 3,
            "confidence_boost": 0.1,
            "condition_weights": {
                "melanoma": 1.0,
                "basal_cell_carcinoma": 0.9,
                "nevus": 0.7,
                "acne": 0.8,
                "rosacea": 0.8,
                "normal": 0.6
            }
        }

    def _load_scin_data(self) -> Dict[str, Any]:
        """Load processed SCIN dataset"""
        try:
            with open(self.processed_data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading SCIN data: {e}")
            return {}

    def analyze_user_image(self, user_embedding: List[float], user_image_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user image against SCIN dataset"""
        logger.info("🔄 Analyzing user image against SCIN dataset...")
        
        # Find similar images in SCIN dataset
        similar_records = self._find_similar_images(user_embedding)
        
        # Calculate condition probabilities
        condition_analysis = self._calculate_condition_probabilities(similar_records)
        
        # Determine primary condition
        primary_condition = self._determine_primary_condition(condition_analysis)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(similar_records, primary_condition)
        
        # Create analysis result
        analysis_result = {
            "condition": primary_condition,
            "confidence": confidence,
            "similar_records": similar_records[:5],  # Top 5 similar records
            "condition_probabilities": condition_analysis,
            "user_metadata": user_image_metadata,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analysis completed - Condition: {primary_condition}, Confidence: {confidence:.2f}")
        return analysis_result

    def _find_similar_images(self, user_embedding: List[float]) -> List[Dict[str, Any]]:
        """Find similar images in SCIN dataset using cosine similarity"""
        similar_records = []
        
        if not self.scin_data.get("records"):
            return similar_records
        
        user_embedding_array = np.array(user_embedding)
        
        for record in self.scin_data["records"]:
            scin_embedding = np.array(record.get("embedding", []))
            
            if len(scin_embedding) == len(user_embedding_array):
                # Calculate cosine similarity
                similarity = self._cosine_similarity(user_embedding_array, scin_embedding)
                
                if similarity > self.analysis_config["similarity_threshold"]:
                    similar_records.append({
                        "record": record,
                        "similarity": similarity,
                        "condition": record.get("condition", "unknown")
                    })
        
        # Sort by similarity (highest first)
        similar_records.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar_records

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def _calculate_condition_probabilities(self, similar_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate probability for each condition based on similar records"""
        condition_scores = {}
        total_weight = 0.0
        
        for record in similar_records:
            condition = record["condition"]
            similarity = record["similarity"]
            weight = similarity * self.analysis_config["condition_weights"].get(condition, 0.5)
            
            condition_scores[condition] = condition_scores.get(condition, 0.0) + weight
            total_weight += weight
        
        # Normalize to probabilities
        if total_weight > 0:
            condition_probabilities = {
                condition: score / total_weight 
                for condition, score in condition_scores.items()
            }
        else:
            condition_probabilities = {"normal": 1.0}
        
        return condition_probabilities

    def _determine_primary_condition(self, condition_probabilities: Dict[str, float]) -> str:
        """Determine the primary condition based on probabilities"""
        if not condition_probabilities:
            return "normal"
        
        # Find condition with highest probability
        primary_condition = max(condition_probabilities.items(), key=lambda x: x[1])[0]
        
        # Apply confidence boost for high-probability conditions
        max_probability = max(condition_probabilities.values())
        if max_probability > 0.6:
            return primary_condition
        elif max_probability > 0.4:
            return primary_condition
        else:
            return "normal"  # Default to normal if no clear condition

    def _calculate_confidence_score(self, similar_records: List[Dict[str, Any]], condition: str) -> float:
        """Calculate confidence score based on similar records and condition"""
        if not similar_records:
            return 0.5
        
        # Calculate average similarity for the primary condition
        condition_similarities = [
            record["similarity"] 
            for record in similar_records 
            if record["condition"] == condition
        ]
        
        if condition_similarities:
            avg_similarity = np.mean(condition_similarities)
            # Boost confidence for high-probability conditions
            confidence = avg_similarity + self.analysis_config["confidence_boost"]
            return min(1.0, confidence)
        else:
            return 0.5

    def generate_comprehensive_report(self, user_embedding: List[float], user_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis report with product recommendations"""
        logger.info("🔄 Generating comprehensive analysis report...")
        
        # Analyze user image
        analysis_result = self.analyze_user_image(user_embedding, user_metadata)
        
        # Optimize parameters and generate recommendations
        comprehensive_report = self.parameter_optimizer.create_comprehensive_report(analysis_result)
        
        # Add SCIN dataset insights
        scin_insights = self._generate_scin_insights(analysis_result)
        comprehensive_report["scin_insights"] = scin_insights
        
        # Add personalized recommendations
        personalized_recommendations = self._generate_personalized_recommendations(analysis_result)
        comprehensive_report["personalized_recommendations"] = personalized_recommendations
        
        # Add follow-up plan
        follow_up_plan = self._generate_follow_up_plan(analysis_result)
        comprehensive_report["follow_up_plan"] = follow_up_plan
        
        logger.info("✅ Comprehensive report generated")
        return comprehensive_report

    def _generate_scin_insights(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights based on SCIN dataset analysis"""
        similar_records = analysis_result.get("similar_records", [])
        condition = analysis_result.get("condition", "normal")
        
        insights = {
            "dataset_comparison": {
                "total_similar_images": len(similar_records),
                "average_similarity": np.mean([r["similarity"] for r in similar_records]) if similar_records else 0.0,
                "condition_distribution": self._get_condition_distribution(similar_records)
            },
            "condition_characteristics": self._get_condition_characteristics(condition),
            "dataset_reliability": self._assess_dataset_reliability(similar_records)
        }
        
        return insights

    def _get_condition_distribution(self, similar_records: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of conditions in similar records"""
        distribution = {}
        for record in similar_records:
            condition = record["condition"]
            distribution[condition] = distribution.get(condition, 0) + 1
        return distribution

    def _get_condition_characteristics(self, condition: str) -> Dict[str, Any]:
        """Get characteristics for a specific condition"""
        characteristics = {
            "melanoma": {
                "prevalence": "Low but serious",
                "typical_features": ["asymmetric", "irregular borders", "color variation"],
                "risk_factors": ["sun exposure", "fair skin", "family history"],
                "prevention": ["sun protection", "regular monitoring", "early detection"]
            },
            "basal_cell_carcinoma": {
                "prevalence": "Most common skin cancer",
                "typical_features": ["pearly bump", "pink growth", "waxy scar"],
                "risk_factors": ["sun exposure", "fair skin", "age"],
                "prevention": ["sun protection", "regular skin checks"]
            },
            "nevus": {
                "prevalence": "Very common",
                "typical_features": ["symmetrical", "regular borders", "uniform color"],
                "risk_factors": ["genetics", "sun exposure"],
                "prevention": ["sun protection", "monitoring changes"]
            },
            "acne": {
                "prevalence": "Very common",
                "typical_features": ["red bumps", "whiteheads", "blackheads"],
                "risk_factors": ["hormones", "stress", "diet"],
                "prevention": ["gentle cleansing", "non-comedogenic products"]
            },
            "rosacea": {
                "prevalence": "Common in adults",
                "typical_features": ["facial redness", "visible blood vessels", "bumps"],
                "risk_factors": ["genetics", "triggers", "age"],
                "prevention": ["avoid triggers", "gentle skincare"]
            },
            "normal": {
                "prevalence": "Healthy skin",
                "typical_features": ["clear skin", "even tone", "no lesions"],
                "risk_factors": ["none"],
                "prevention": ["maintain healthy habits", "sun protection"]
            }
        }
        
        return characteristics.get(condition, {})

    def _assess_dataset_reliability(self, similar_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess reliability of dataset analysis"""
        if not similar_records:
            return {"reliability": "low", "reason": "No similar images found"}
        
        avg_similarity = np.mean([r["similarity"] for r in similar_records])
        num_similar = len(similar_records)
        
        if avg_similarity > 0.8 and num_similar > 3:
            reliability = "high"
        elif avg_similarity > 0.7 and num_similar > 2:
            reliability = "medium"
        else:
            reliability = "low"
        
        return {
            "reliability": reliability,
            "average_similarity": avg_similarity,
            "number_of_similar_images": num_similar,
            "confidence_level": "high" if reliability == "high" else "medium" if reliability == "medium" else "low"
        }

    def _generate_personalized_recommendations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized recommendations based on analysis"""
        condition = analysis_result.get("condition", "normal")
        confidence = analysis_result.get("confidence", 0.0)
        user_metadata = analysis_result.get("user_metadata", {})
        
        # Get user preferences
        skin_type = user_metadata.get("skin_type", "unknown")
        age_group = user_metadata.get("age_group", "adult")
        concerns = user_metadata.get("concerns", [])
        
        personalized = {
            "routine_suggestions": self._generate_routine_suggestions(condition, skin_type),
            "lifestyle_adaptations": self._generate_lifestyle_adaptations(condition, age_group),
            "prevention_strategies": self._generate_prevention_strategies(condition, concerns),
            "monitoring_advice": self._generate_monitoring_advice(condition, confidence)
        }
        
        return personalized

    def _generate_routine_suggestions(self, condition: str, skin_type: str) -> List[str]:
        """Generate routine suggestions based on condition and skin type"""
        routine_templates = {
            "melanoma": [
                "Use broad-spectrum sunscreen daily (SPF 30+)",
                "Apply antioxidant serum for protection",
                "Monitor skin changes regularly",
                "Schedule regular dermatologist visits"
            ],
            "acne": [
                "Use gentle cleanser twice daily",
                "Apply non-comedogenic moisturizer",
                "Use targeted treatment for active breakouts",
                "Avoid touching face throughout the day"
            ],
            "rosacea": [
                "Use gentle, fragrance-free cleanser",
                "Apply soothing moisturizer",
                "Avoid known triggers",
                "Use mineral sunscreen"
            ],
            "normal": [
                "Maintain consistent cleansing routine",
                "Use daily sunscreen",
                "Apply moisturizer as needed",
                "Schedule annual skin checks"
            ]
        }
        
        return routine_templates.get(condition, ["Maintain good skincare habits"])

    def _generate_lifestyle_adaptations(self, condition: str, age_group: str) -> List[str]:
        """Generate lifestyle adaptations"""
        adaptations = {
            "melanoma": [
                "Limit sun exposure, especially 10 AM - 4 PM",
                "Wear protective clothing and hats",
                "Avoid tanning beds",
                "Perform monthly self-examinations"
            ],
            "acne": [
                "Maintain clean phone and pillowcases",
                "Manage stress levels",
                "Avoid picking or squeezing",
                "Use non-comedogenic makeup"
            ],
            "rosacea": [
                "Identify and avoid personal triggers",
                "Manage stress through relaxation",
                "Protect skin from extreme temperatures",
                "Use gentle skincare products"
            ]
        }
        
        return adaptations.get(condition, ["Maintain healthy lifestyle habits"])

    def _generate_prevention_strategies(self, condition: str, concerns: List[str]) -> List[str]:
        """Generate prevention strategies"""
        strategies = {
            "melanoma": [
                "Regular skin examinations",
                "Sun protection education",
                "Early detection awareness",
                "Family history monitoring"
            ],
            "acne": [
                "Consistent skincare routine",
                "Stress management",
                "Dietary considerations",
                "Hygiene practices"
            ],
            "rosacea": [
                "Trigger identification",
                "Gentle skincare practices",
                "Environmental protection",
                "Stress management"
            ]
        }
        
        return strategies.get(condition, ["Maintain preventive care"])

    def _generate_monitoring_advice(self, condition: str, confidence: float) -> Dict[str, Any]:
        """Generate monitoring advice"""
        monitoring_advice = {
            "melanoma": {
                "frequency": "weekly" if confidence > 0.9 else "bi-weekly",
                "method": "Self-examination and professional monitoring",
                "warning_signs": ["Changes in size, shape, color", "Itching or bleeding", "New growths"],
                "professional_visits": "Every 3-6 months"
            },
            "acne": {
                "frequency": "weekly" if confidence > 0.8 else "bi-weekly",
                "method": "Progress tracking and routine adjustment",
                "warning_signs": ["No improvement after 6-8 weeks", "Severe inflammation", "Scarring"],
                "professional_visits": "As needed for severe cases"
            },
            "rosacea": {
                "frequency": "bi-weekly",
                "method": "Symptom tracking and trigger monitoring",
                "warning_signs": ["Increased redness", "New triggers", "Eye irritation"],
                "professional_visits": "Every 6-12 months"
            }
        }
        
        return monitoring_advice.get(condition, {
            "frequency": "monthly",
            "method": "General skin monitoring",
            "warning_signs": ["Any concerning changes"],
            "professional_visits": "Annual check-ups"
        })

    def _generate_follow_up_plan(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate follow-up plan based on analysis results"""
        condition = analysis_result.get("condition", "normal")
        confidence = analysis_result.get("confidence", 0.0)
        
        follow_up_plan = {
            "immediate_actions": self._get_immediate_actions(condition, confidence),
            "short_term_goals": self._get_short_term_goals(condition),
            "long_term_goals": self._get_long_term_goals(condition),
            "success_metrics": self._get_success_metrics(condition),
            "timeline": self._get_follow_up_timeline(condition, confidence)
        }
        
        return follow_up_plan

    def _get_immediate_actions(self, condition: str, confidence: float) -> List[str]:
        """Get immediate actions based on condition and confidence"""
        actions = {
            "melanoma": ["Schedule dermatologist appointment immediately"],
            "basal_cell_carcinoma": ["Schedule dermatologist appointment within 1-2 weeks"],
            "acne": ["Begin gentle treatment regimen", "Purchase recommended products"],
            "rosacea": ["Begin gentle skincare routine", "Identify personal triggers"],
            "normal": ["Continue current routine", "Schedule annual check-up"]
        }
        
        base_actions = actions.get(condition, ["Monitor skin health"])
        
        if confidence < 0.7:
            base_actions.append("Consider professional evaluation for confirmation")
        
        return base_actions

    def _get_short_term_goals(self, condition: str) -> List[str]:
        """Get short-term goals (1-4 weeks)"""
        goals = {
            "melanoma": ["Complete medical evaluation", "Begin protective measures"],
            "acne": ["Establish consistent routine", "See initial improvement"],
            "rosacea": ["Identify triggers", "Establish gentle routine"],
            "normal": ["Maintain healthy habits", "Continue prevention"]
        }
        
        return goals.get(condition, ["Establish healthy skincare routine"])

    def _get_long_term_goals(self, condition: str) -> List[str]:
        """Get long-term goals (3-12 months)"""
        goals = {
            "melanoma": ["Regular monitoring", "Prevention education"],
            "acne": ["Clear skin maintenance", "Prevention of future breakouts"],
            "rosacea": ["Symptom management", "Trigger avoidance"],
            "normal": ["Preventive care", "Skin health maintenance"]
        }
        
        return goals.get(condition, ["Maintain skin health"])

    def _get_success_metrics(self, condition: str) -> List[str]:
        """Get success metrics for condition"""
        metrics = {
            "melanoma": ["No new suspicious lesions", "Regular monitoring compliance"],
            "acne": ["Reduced breakouts", "Improved skin texture"],
            "rosacea": ["Reduced redness", "Fewer flare-ups"],
            "normal": ["Maintained skin health", "Preventive care compliance"]
        }
        
        return metrics.get(condition, ["Improved skin health"])

    def _get_follow_up_timeline(self, condition: str, confidence: float) -> Dict[str, str]:
        """Get follow-up timeline"""
        timeline = {
            "melanoma": {
                "1_week": "Dermatologist appointment",
                "1_month": "Follow-up evaluation",
                "3_months": "Regular monitoring",
                "6_months": "Comprehensive check"
            },
            "acne": {
                "2_weeks": "Progress assessment",
                "1_month": "Routine adjustment",
                "3_months": "Long-term evaluation"
            },
            "rosacea": {
                "2_weeks": "Trigger assessment",
                "1_month": "Routine evaluation",
                "3_months": "Long-term management"
            }
        }
        
        return timeline.get(condition, {
            "1_month": "Routine check",
            "3_months": "Progress assessment",
            "6_months": "Comprehensive evaluation"
        })

if __name__ == "__main__":
    # Example usage
    integration = EnhancedAnalysisIntegration()
    
    # Example user embedding (1408-dimensional)
    example_embedding = [0.1] * 1408  # Placeholder embedding
    
    # Example user metadata
    example_metadata = {
        "skin_type": "type_3",
        "age_group": "adult",
        "concerns": ["acne", "sun damage"],
        "current_routine": "basic"
    }
    
    # Generate comprehensive report
    report = integration.generate_comprehensive_report(example_embedding, example_metadata)
    
    print("📊 Enhanced Analysis Report:")
    print(json.dumps(report, indent=2)) 