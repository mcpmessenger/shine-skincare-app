#!/usr/bin/env python3
"""
Result Parameter Optimizer and Product Recommendation System
Optimizes analysis results and generates product recommendations based on SCIN dataset
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import math

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResultParameterOptimizer:
    def __init__(self):
        self.base_dir = Path("scin_dataset")
        self.processed_data_file = self.base_dir / "processed" / "scin_processed_data.json"
        self.products_dir = Path("../products")
        
        # Load processed SCIN data
        self.scin_data = self._load_scin_data()
        
        # Product database
        self.products_database = self._load_products_database()
        
        # Condition-specific parameters
        self.condition_parameters = {
            "melanoma": {
                "confidence_threshold": 0.90,
                "urgency_level": "immediate",
                "recommendation_priority": "high",
                "product_categories": ["sunscreen", "protective", "medical"],
                "consultation_required": True
            },
            "basal_cell_carcinoma": {
                "confidence_threshold": 0.85,
                "urgency_level": "high",
                "recommendation_priority": "high",
                "product_categories": ["sunscreen", "protective", "medical"],
                "consultation_required": True
            },
            "nevus": {
                "confidence_threshold": 0.80,
                "urgency_level": "low",
                "recommendation_priority": "medium",
                "product_categories": ["sunscreen", "monitoring", "protective"],
                "consultation_required": False
            },
            "acne": {
                "confidence_threshold": 0.75,
                "urgency_level": "medium",
                "recommendation_priority": "medium",
                "product_categories": ["cleanser", "treatment", "moisturizer"],
                "consultation_required": False
            },
            "rosacea": {
                "confidence_threshold": 0.80,
                "urgency_level": "medium",
                "recommendation_priority": "medium",
                "product_categories": ["gentle_cleanser", "soothing", "moisturizer"],
                "consultation_required": False
            },
            "normal": {
                "confidence_threshold": 0.70,
                "urgency_level": "none",
                "recommendation_priority": "low",
                "product_categories": ["maintenance", "prevention"],
                "consultation_required": False
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

    def _load_products_database(self) -> Dict[str, Any]:
        """Load and categorize products database"""
        products_db = {
            "sunscreen": [
                {
                    "name": "EltaMD UV Clear Broad-Spectrum SPF 46",
                    "category": "sunscreen",
                    "suitable_conditions": ["melanoma", "basal_cell_carcinoma", "nevus", "normal"],
                    "ingredients": ["zinc oxide", "niacinamide", "hyaluronic acid"],
                    "benefits": ["broad spectrum protection", "non-comedogenic", "soothing"],
                    "price_range": "mid",
                    "image": "EltaMD UV Clear Broad-Spectrum SPF 46.webp"
                }
            ],
            "cleanser": [
                {
                    "name": "Dermalogica UltraCalming Cleanser",
                    "category": "gentle_cleanser",
                    "suitable_conditions": ["rosacea", "acne", "normal"],
                    "ingredients": ["calendula", "aloe vera", "gentle surfactants"],
                    "benefits": ["soothing", "non-irritating", "calming"],
                    "price_range": "mid",
                    "image": "Dermalogica UltraCalming Cleanser.webp"
                },
                {
                    "name": "Allies of Skin Molecular Silk Amino Hydrating Cleanser",
                    "category": "cleanser",
                    "suitable_conditions": ["acne", "normal"],
                    "ingredients": ["amino acids", "hyaluronic acid", "gentle surfactants"],
                    "benefits": ["hydrating", "gentle", "non-stripping"],
                    "price_range": "high",
                    "image": "Allies of Skin Molecular Silk Amino Hydrating Cleanser.webp"
                }
            ],
            "treatment": [
                {
                    "name": "Obagi CLENZIderm M.D. System",
                    "category": "acne_treatment",
                    "suitable_conditions": ["acne"],
                    "ingredients": ["benzoyl peroxide", "salicylic acid"],
                    "benefits": ["acne fighting", "exfoliating", "clearing"],
                    "price_range": "high",
                    "image": "Obagi CLENZIderm M.D. System (Therapeutic Lotion).webp"
                },
                {
                    "name": "PCA SKIN Pigment Gel Pro",
                    "category": "pigment_treatment",
                    "suitable_conditions": ["melanoma", "nevus", "normal"],
                    "ingredients": ["hydroquinone", "kojic acid", "vitamin c"],
                    "benefits": ["brightening", "evening skin tone", "antioxidant"],
                    "price_range": "high",
                    "image": "PCA SKIN Pigment Gel Pro.jpg"
                }
            ],
            "moisturizer": [
                {
                    "name": "First Aid Beauty Ultra Repair Cream",
                    "category": "moisturizer",
                    "suitable_conditions": ["rosacea", "acne", "normal"],
                    "ingredients": ["colloidal oatmeal", "ceramides", "hyaluronic acid"],
                    "benefits": ["soothing", "repairing", "hydrating"],
                    "price_range": "mid",
                    "image": "First Aid Beauty Ultra Repair Cream.webp"
                },
                {
                    "name": "Naturopathica Calendula Essential Hydrating Cream",
                    "category": "moisturizer",
                    "suitable_conditions": ["rosacea", "normal"],
                    "ingredients": ["calendula", "aloe vera", "vitamin e"],
                    "benefits": ["calming", "hydrating", "soothing"],
                    "price_range": "mid",
                    "image": "Naturopathica Calendula Essential Hydrating Cream.webp"
                }
            ],
            "serum": [
                {
                    "name": "SkinCeuticals C E Ferulic",
                    "category": "antioxidant_serum",
                    "suitable_conditions": ["melanoma", "basal_cell_carcinoma", "nevus", "normal"],
                    "ingredients": ["vitamin c", "vitamin e", "ferulic acid"],
                    "benefits": ["antioxidant protection", "brightening", "anti-aging"],
                    "price_range": "high",
                    "image": "SkinCeuticals C E Ferulic.webp"
                },
                {
                    "name": "TNS Advanced+ Serum",
                    "category": "growth_factor_serum",
                    "suitable_conditions": ["normal", "acne", "rosacea"],
                    "ingredients": ["growth factors", "peptides", "antioxidants"],
                    "benefits": ["anti-aging", "repairing", "regenerating"],
                    "price_range": "high",
                    "image": "TNS® Advanced+ Serum.jpg"
                }
            ]
        }
        
        return products_db

    def optimize_result_parameters(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize result parameters based on SCIN dataset and condition"""
        logger.info("🔄 Optimizing result parameters...")
        
        # Extract condition and confidence from analysis result
        condition = analysis_result.get("condition", "normal")
        confidence = analysis_result.get("confidence", 0.0)
        
        # Get condition-specific parameters
        condition_params = self.condition_parameters.get(condition, {})
        confidence_threshold = condition_params.get("confidence_threshold", 0.75)
        
        # Optimize parameters based on condition and confidence
        optimized_params = {
            "condition": condition,
            "confidence": confidence,
            "confidence_threshold": confidence_threshold,
            "urgency_level": condition_params.get("urgency_level", "medium"),
            "recommendation_priority": condition_params.get("recommendation_priority", "medium"),
            "consultation_required": condition_params.get("consultation_required", False),
            "severity_assessment": self._assess_severity(condition, confidence),
            "reliability_score": self._calculate_reliability_score(confidence, confidence_threshold),
            "action_required": confidence >= confidence_threshold,
            "monitoring_frequency": self._determine_monitoring_frequency(condition, confidence),
            "product_recommendations": self._generate_product_recommendations(condition, confidence),
            "lifestyle_recommendations": self._generate_lifestyle_recommendations(condition),
            "medical_advice": self._generate_medical_advice(condition, confidence)
        }
        
        logger.info(f"✅ Parameters optimized for {condition} (confidence: {confidence:.2f})")
        return optimized_params

    def _assess_severity(self, condition: str, confidence: float) -> str:
        """Assess severity based on condition and confidence"""
        severity_map = {
            "melanoma": "high" if confidence > 0.85 else "medium",
            "basal_cell_carcinoma": "high" if confidence > 0.80 else "medium",
            "nevus": "low",
            "acne": "medium" if confidence > 0.75 else "low",
            "rosacea": "medium" if confidence > 0.80 else "low",
            "normal": "none"
        }
        return severity_map.get(condition, "low")

    def _calculate_reliability_score(self, confidence: float, threshold: float) -> float:
        """Calculate reliability score based on confidence and threshold"""
        if confidence >= threshold:
            return min(1.0, confidence + 0.1)
        else:
            return max(0.0, confidence - 0.2)

    def _determine_monitoring_frequency(self, condition: str, confidence: float) -> str:
        """Determine monitoring frequency based on condition"""
        frequency_map = {
            "melanoma": "weekly" if confidence > 0.90 else "bi-weekly",
            "basal_cell_carcinoma": "bi-weekly" if confidence > 0.85 else "monthly",
            "nevus": "monthly",
            "acne": "weekly" if confidence > 0.80 else "bi-weekly",
            "rosacea": "bi-weekly",
            "normal": "quarterly"
        }
        return frequency_map.get(condition, "monthly")

    def _generate_product_recommendations(self, condition: str, confidence: float) -> List[Dict[str, Any]]:
        """Generate product recommendations based on condition"""
        logger.info(f"🔄 Generating product recommendations for {condition}")
        
        # Get condition parameters
        condition_params = self.condition_parameters.get(condition, {})
        product_categories = condition_params.get("product_categories", [])
        
        recommendations = []
        
        # Generate recommendations for each category
        for category in product_categories:
            category_products = self.products_database.get(category, [])
            
            for product in category_products:
                if condition in product.get("suitable_conditions", []):
                    # Calculate recommendation score
                    recommendation_score = self._calculate_recommendation_score(
                        condition, confidence, product
                    )
                    
                    if recommendation_score > 0.5:  # Only recommend if score > 50%
                        recommendations.append({
                            "product": product,
                            "score": recommendation_score,
                            "reasoning": self._generate_recommendation_reasoning(condition, product),
                            "priority": self._determine_product_priority(condition, product)
                        })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit to top 3 recommendations
        return recommendations[:3]

    def _calculate_recommendation_score(self, condition: str, confidence: float, product: Dict[str, Any]) -> float:
        """Calculate recommendation score for a product"""
        base_score = 0.5
        
        # Condition match bonus
        if condition in product.get("suitable_conditions", []):
            base_score += 0.3
        
        # Confidence bonus
        if confidence > 0.8:
            base_score += 0.2
        
        # Product category match
        condition_params = self.condition_parameters.get(condition, {})
        product_categories = condition_params.get("product_categories", [])
        
        if product.get("category") in product_categories:
            base_score += 0.1
        
        return min(1.0, base_score)

    def _generate_recommendation_reasoning(self, condition: str, product: Dict[str, Any]) -> str:
        """Generate reasoning for product recommendation"""
        reasoning_templates = {
            "melanoma": f"{product['name']} provides essential protection and antioxidant benefits for skin health.",
            "basal_cell_carcinoma": f"{product['name']} offers protective and healing properties for skin concerns.",
            "nevus": f"{product['name']} helps maintain skin health and provides necessary protection.",
            "acne": f"{product['name']} is specifically formulated to address acne concerns with gentle yet effective ingredients.",
            "rosacea": f"{product['name']} is designed for sensitive skin and provides soothing relief for rosacea symptoms.",
            "normal": f"{product['name']} helps maintain healthy skin and provides preventive care."
        }
        
        return reasoning_templates.get(condition, f"{product['name']} is suitable for your skin condition.")

    def _determine_product_priority(self, condition: str, product: Dict[str, Any]) -> str:
        """Determine product priority"""
        high_priority_conditions = ["melanoma", "basal_cell_carcinoma"]
        medium_priority_conditions = ["acne", "rosacea"]
        
        if condition in high_priority_conditions:
            return "high"
        elif condition in medium_priority_conditions:
            return "medium"
        else:
            return "low"

    def _generate_lifestyle_recommendations(self, condition: str) -> List[str]:
        """Generate lifestyle recommendations based on condition"""
        lifestyle_recommendations = {
            "melanoma": [
                "Avoid direct sun exposure between 10 AM and 4 PM",
                "Wear protective clothing and wide-brimmed hats",
                "Use broad-spectrum sunscreen with SPF 30+ daily",
                "Perform regular self-examinations of your skin",
                "Schedule annual dermatologist appointments"
            ],
            "basal_cell_carcinoma": [
                "Limit sun exposure and use protective measures",
                "Wear sunscreen daily, even on cloudy days",
                "Avoid tanning beds and artificial UV exposure",
                "Monitor any changes in existing moles or spots",
                "Seek immediate medical attention for new growths"
            ],
            "nevus": [
                "Use sunscreen daily to protect moles from UV damage",
                "Monitor moles for changes in size, shape, or color",
                "Take photographs to track mole changes over time",
                "Avoid excessive sun exposure",
                "Schedule regular skin checks with a dermatologist"
            ],
            "acne": [
                "Maintain a consistent skincare routine",
                "Avoid touching your face throughout the day",
                "Use non-comedogenic products",
                "Keep your phone and pillowcases clean",
                "Manage stress levels as stress can worsen acne"
            ],
            "rosacea": [
                "Identify and avoid personal triggers (spicy foods, alcohol, etc.)",
                "Use gentle, fragrance-free skincare products",
                "Protect your skin from extreme temperatures",
                "Manage stress through relaxation techniques",
                "Avoid hot showers and harsh scrubbing"
            ],
            "normal": [
                "Maintain a consistent skincare routine",
                "Use sunscreen daily for prevention",
                "Stay hydrated and maintain a healthy diet",
                "Get adequate sleep for skin regeneration",
                "Schedule annual skin checks for early detection"
            ]
        }
        
        return lifestyle_recommendations.get(condition, ["Maintain good skincare habits"])

    def _generate_medical_advice(self, condition: str, confidence: float) -> Dict[str, Any]:
        """Generate medical advice based on condition and confidence"""
        medical_advice = {
            "melanoma": {
                "immediate_action": "Seek immediate dermatologist consultation",
                "urgency": "High - requires immediate medical attention",
                "follow_up": "Biopsy and treatment planning required",
                "monitoring": "Regular dermatologist visits every 3-6 months"
            },
            "basal_cell_carcinoma": {
                "immediate_action": "Schedule dermatologist appointment within 1-2 weeks",
                "urgency": "High - requires medical evaluation",
                "follow_up": "Biopsy and potential surgical removal",
                "monitoring": "Regular skin checks every 6-12 months"
            },
            "nevus": {
                "immediate_action": "Monitor for changes, no immediate action required",
                "urgency": "Low - routine monitoring",
                "follow_up": "Annual dermatologist check-up",
                "monitoring": "Self-examination monthly, professional check annually"
            },
            "acne": {
                "immediate_action": "Start gentle acne treatment regimen",
                "urgency": "Medium - can be managed at home initially",
                "follow_up": "See dermatologist if no improvement in 6-8 weeks",
                "monitoring": "Track progress and adjust treatment as needed"
            },
            "rosacea": {
                "immediate_action": "Begin gentle skincare routine for sensitive skin",
                "urgency": "Medium - can be managed with proper care",
                "follow_up": "Consult dermatologist for prescription treatments if needed",
                "monitoring": "Track triggers and symptoms, adjust routine accordingly"
            },
            "normal": {
                "immediate_action": "Continue current skincare routine",
                "urgency": "None - maintain healthy habits",
                "follow_up": "Annual skin check for prevention",
                "monitoring": "Regular self-examination and professional check-ups"
            }
        }
        
        advice = medical_advice.get(condition, {})
        
        # Adjust advice based on confidence level
        if confidence < 0.7:
            advice["note"] = "Low confidence result - consider professional evaluation for confirmation"
        elif confidence > 0.9:
            advice["note"] = "High confidence result - recommendations are strongly advised"
        
        return advice

    def create_comprehensive_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive analysis report with optimized parameters"""
        logger.info("🔄 Creating comprehensive analysis report...")
        
        # Optimize parameters
        optimized_params = self.optimize_result_parameters(analysis_result)
        
        # Create comprehensive report
        report = {
            "analysis_summary": {
                "condition": optimized_params["condition"],
                "confidence": optimized_params["confidence"],
                "severity": optimized_params["severity_assessment"],
                "reliability": optimized_params["reliability_score"],
                "action_required": optimized_params["action_required"]
            },
            "product_recommendations": optimized_params["product_recommendations"],
            "lifestyle_recommendations": optimized_params["lifestyle_recommendations"],
            "medical_advice": optimized_params["medical_advice"],
            "monitoring_plan": {
                "frequency": optimized_params["monitoring_frequency"],
                "next_check": self._calculate_next_check_date(optimized_params["monitoring_frequency"])
            },
            "risk_assessment": self._assess_risk_level(optimized_params["condition"], optimized_params["confidence"]),
            "generated_timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Comprehensive report created")
        return report

    def _calculate_next_check_date(self, frequency: str) -> str:
        """Calculate next check date based on monitoring frequency"""
        from datetime import datetime, timedelta
        
        today = datetime.now()
        
        frequency_map = {
            "weekly": today + timedelta(days=7),
            "bi-weekly": today + timedelta(days=14),
            "monthly": today + timedelta(days=30),
            "quarterly": today + timedelta(days=90)
        }
        
        next_date = frequency_map.get(frequency, today + timedelta(days=30))
        return next_date.strftime("%Y-%m-%d")

    def _assess_risk_level(self, condition: str, confidence: float) -> str:
        """Assess risk level based on condition and confidence"""
        risk_levels = {
            "melanoma": "high" if confidence > 0.85 else "medium",
            "basal_cell_carcinoma": "high" if confidence > 0.80 else "medium",
            "nevus": "low",
            "acne": "medium" if confidence > 0.75 else "low",
            "rosacea": "medium" if confidence > 0.80 else "low",
            "normal": "none"
        }
        
        return risk_levels.get(condition, "low")

if __name__ == "__main__":
    # Example usage
    optimizer = ResultParameterOptimizer()
    
    # Example analysis result
    example_result = {
        "condition": "acne",
        "confidence": 0.85,
        "image_id": "user_selfie_001"
    }
    
    # Generate comprehensive report
    report = optimizer.create_comprehensive_report(example_result)
    
    print("📊 Comprehensive Analysis Report:")
    print(json.dumps(report, indent=2)) 