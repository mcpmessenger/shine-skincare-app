#!/usr/bin/env python3
"""
Enhanced Product Recommendation Engine for Shine Skincare App
Integrates with existing 103 demographic baselines and condition embeddings
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Import existing systems
from enhanced_severity_scoring import enhanced_severity_scorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRecommendationEngine:
    """
    Enhanced product recommendation engine with demographic-aware personalization
    Integrates with existing 103 demographic baselines and condition embeddings
    """
    
    def __init__(self):
        """Initialize the enhanced recommendation engine"""
        self.user_preferences = {}
        self.product_database = self._load_product_database()
        self.ingredient_analysis = self._load_ingredient_database()
        self.efficacy_data = self._load_efficacy_data()
        
        # Load existing demographic baselines and condition embeddings
        self.demographic_baselines = self._load_demographic_baselines()
        self.condition_embeddings = self._load_condition_embeddings()
        
        # Recommendation weights
        self.recommendation_weights = {
            'condition_match': 0.35,
            'demographic_fit': 0.25,
            'user_preferences': 0.20,
            'efficacy_score': 0.15,
            'ingredient_safety': 0.05
        }
        
        logger.info("✅ Enhanced recommendation engine initialized")
    
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
    
    def _load_product_database(self) -> Dict:
        """Load comprehensive product database"""
        # This would typically load from a database or API
        # For now, using a comprehensive mock database
        return {
            'cleansers': [
                {
                    'id': 'cleanser_001',
                    'name': 'Gentle Foaming Cleanser',
                    'category': 'cleanser',
                    'brand': 'Shine',
                    'price': 28.00,
                    'target_conditions': ['acne', 'sensitive_skin'],
                    'ingredients': ['glycerin', 'niacinamide', 'ceramides'],
                    'demographic_fit': {
                        'age_groups': ['teens', 'twenties', 'thirties'],
                        'skin_types': ['all'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 8.5,
                    'safety_score': 9.2
                },
                {
                    'id': 'cleanser_002',
                    'name': 'Hydrating Gel Cleanser',
                    'category': 'cleanser',
                    'brand': 'Shine',
                    'price': 32.00,
                    'target_conditions': ['dry_skin', 'mature_skin'],
                    'ingredients': ['hyaluronic_acid', 'peptides', 'vitamin_e'],
                    'demographic_fit': {
                        'age_groups': ['forties', 'fifties', 'sixties_plus'],
                        'skin_types': ['dry', 'normal'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 8.8,
                    'safety_score': 9.5
                }
            ],
            'serums': [
                {
                    'id': 'serum_001',
                    'name': 'Vitamin C Brightening Serum',
                    'category': 'serum',
                    'brand': 'Shine',
                    'price': 45.00,
                    'target_conditions': ['hyperpigmentation', 'dull_skin'],
                    'ingredients': ['vitamin_c', 'ferulic_acid', 'vitamin_e'],
                    'demographic_fit': {
                        'age_groups': ['twenties', 'thirties', 'forties'],
                        'skin_types': ['all'],
                        'ethnicities': ['east_asian', 'southeast_asian', 'south_asian']
                    },
                    'efficacy_score': 9.1,
                    'safety_score': 8.8
                },
                {
                    'id': 'serum_002',
                    'name': 'Retinol Anti-Aging Serum',
                    'category': 'serum',
                    'brand': 'Shine',
                    'price': 58.00,
                    'target_conditions': ['fine_lines_wrinkles', 'mature_skin'],
                    'ingredients': ['retinol', 'peptides', 'niacinamide'],
                    'demographic_fit': {
                        'age_groups': ['thirties', 'forties', 'fifties', 'sixties_plus'],
                        'skin_types': ['normal', 'dry'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 9.3,
                    'safety_score': 8.5
                }
            ],
            'moisturizers': [
                {
                    'id': 'moisturizer_001',
                    'name': 'Lightweight Hydrating Moisturizer',
                    'category': 'moisturizer',
                    'brand': 'Shine',
                    'price': 38.00,
                    'target_conditions': ['dry_skin', 'sensitive_skin'],
                    'ingredients': ['ceramides', 'hyaluronic_acid', 'glycerin'],
                    'demographic_fit': {
                        'age_groups': ['all'],
                        'skin_types': ['all'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 8.7,
                    'safety_score': 9.4
                }
            ],
            'sunscreens': [
                {
                    'id': 'sunscreen_001',
                    'name': 'Broad Spectrum SPF 50+',
                    'category': 'sunscreen',
                    'brand': 'Shine',
                    'price': 42.00,
                    'target_conditions': ['sun_damage', 'hyperpigmentation'],
                    'ingredients': ['zinc_oxide', 'titanium_dioxide', 'vitamin_e'],
                    'demographic_fit': {
                        'age_groups': ['all'],
                        'skin_types': ['all'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 9.5,
                    'safety_score': 9.8
                }
            ],
            'treatments': [
                {
                    'id': 'treatment_001',
                    'name': 'Acne Spot Treatment',
                    'category': 'treatment',
                    'brand': 'Shine',
                    'price': 25.00,
                    'target_conditions': ['acne', 'inflammatory_acne'],
                    'ingredients': ['salicylic_acid', 'niacinamide', 'zinc'],
                    'demographic_fit': {
                        'age_groups': ['teens', 'twenties', 'thirties'],
                        'skin_types': ['oily', 'combination'],
                        'ethnicities': ['all']
                    },
                    'efficacy_score': 8.9,
                    'safety_score': 8.2
                }
            ]
        }
    
    def _load_ingredient_database(self) -> Dict:
        """Load ingredient analysis database"""
        return {
            'vitamin_c': {
                'benefits': ['brightening', 'antioxidant', 'collagen_synthesis'],
                'safety_level': 'safe',
                'irritation_potential': 'low',
                'compatibility': ['vitamin_e', 'ferulic_acid'],
                'avoid_with': ['retinol', 'benzoyl_peroxide']
            },
            'retinol': {
                'benefits': ['anti_aging', 'cell_turnover', 'acne_treatment'],
                'safety_level': 'moderate',
                'irritation_potential': 'high',
                'compatibility': ['niacinamide', 'peptides'],
                'avoid_with': ['vitamin_c', 'benzoyl_peroxide']
            },
            'niacinamide': {
                'benefits': ['brightening', 'oil_control', 'anti_inflammatory'],
                'safety_level': 'safe',
                'irritation_potential': 'low',
                'compatibility': ['most_ingredients'],
                'avoid_with': []
            },
            'salicylic_acid': {
                'benefits': ['exfoliation', 'acne_treatment', 'pore_clearing'],
                'safety_level': 'moderate',
                'irritation_potential': 'moderate',
                'compatibility': ['niacinamide'],
                'avoid_with': ['retinol', 'vitamin_c']
            }
        }
    
    def _load_efficacy_data(self) -> Dict:
        """Load product efficacy data"""
        return {
            'clinical_studies': {
                'vitamin_c_brightening': {'efficacy': 0.85, 'sample_size': 1200},
                'retinol_anti_aging': {'efficacy': 0.78, 'sample_size': 800},
                'niacinamide_acne': {'efficacy': 0.72, 'sample_size': 600}
            },
            'user_reviews': {
                'cleanser_001': {'rating': 4.6, 'review_count': 1250},
                'serum_001': {'rating': 4.8, 'review_count': 890},
                'moisturizer_001': {'rating': 4.5, 'review_count': 2100}
            }
        }
    
    def generate_personalized_recommendations(self, 
                                           analysis_results: Dict,
                                           user_preferences: Dict = None,
                                           demographics: Dict = None) -> Dict:
        """
        Generate personalized product recommendations
        
        Args:
            analysis_results: Skin analysis results
            user_preferences: User preferences (budget, brand preferences, etc.)
            demographics: User demographic information
            
        Returns:
            Personalized recommendations with complete routine
        """
        try:
            logger.info("🔄 Generating personalized recommendations...")
            
            # Step 1: Extract detected conditions and severity
            detected_conditions = self._extract_detected_conditions(analysis_results)
            
            # Step 2: Filter products by conditions
            condition_based_products = self._filter_by_conditions(detected_conditions)
            
            # Step 3: Apply user preferences
            preference_filtered = self._apply_user_preferences(
                condition_based_products, user_preferences or {})
            
            # Step 4: Optimize for demographics
            demographic_optimized = self._optimize_for_demographics(
                preference_filtered, demographics or {})
            
            # Step 5: Score and rank products
            scored_products = self._score_products(
                demographic_optimized, detected_conditions, demographics)
            
            # Step 6: Build complete routine
            complete_routine = self._build_complete_routine(scored_products)
            
            # Step 7: Analyze ingredients and safety
            ingredient_analysis = self._analyze_ingredients(complete_routine)
            
            return {
                'individual_products': scored_products,
                'complete_routine': complete_routine,
                'ingredient_analysis': ingredient_analysis,
                'efficacy_data': self._get_efficacy_data(scored_products),
                'demographic_factors': self._get_demographic_factors(demographics),
                'recommendation_confidence': self._calculate_recommendation_confidence(
                    scored_products, demographics)
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return {
                'error': str(e),
                'individual_products': [],
                'complete_routine': {},
                'recommendation_confidence': 0.0
            }
    
    def _extract_detected_conditions(self, analysis_results: Dict) -> List[Dict]:
        """Extract detected conditions with severity scores"""
        conditions = []
        
        # Extract from enhanced analysis results
        skin_analysis = analysis_results.get('skin_analysis', {})
        
        # Check for enhanced severity scoring
        if 'enhanced_severity' in analysis_results:
            for condition, severity_data in analysis_results['enhanced_severity'].items():
                conditions.append({
                    'condition': condition,
                    'severity_score': severity_data.get('overall_score', 0),
                    'severity_level': severity_data.get('severity_level', 'unknown'),
                    'confidence': severity_data.get('confidence', 0.8)
                })
        else:
            # Fallback to basic condition detection
            for condition, data in skin_analysis.items():
                if isinstance(data, dict) and 'confidence' in data:
                    conditions.append({
                        'condition': condition,
                        'severity_score': data.get('severity', 5.0),
                        'severity_level': self._map_severity_to_level(data.get('severity', 5.0)),
                        'confidence': data.get('confidence', 0.8)
                    })
        
        return conditions
    
    def _filter_by_conditions(self, detected_conditions: List[Dict]) -> List[Dict]:
        """Filter products based on detected conditions"""
        relevant_products = []
        
        for condition_data in detected_conditions:
            condition = condition_data['condition']
            severity_score = condition_data['severity_score']
            
            # Find products that target this condition
            for category, products in self.product_database.items():
                for product in products:
                    if condition in product.get('target_conditions', []):
                        # Adjust product score based on condition severity
                        adjusted_product = product.copy()
                        adjusted_product['condition_match_score'] = self._calculate_condition_match_score(
                            condition, severity_score, product)
                        relevant_products.append(adjusted_product)
        
        return relevant_products
    
    def _apply_user_preferences(self, products: List[Dict], preferences: Dict) -> List[Dict]:
        """Apply user preferences to filter products"""
        if not preferences:
            return products
        
        filtered_products = []
        
        for product in products:
            preference_score = 1.0
            
            # Budget filtering
            max_budget = preferences.get('max_budget')
            if max_budget and product['price'] > max_budget:
                continue
            
            # Brand preferences
            preferred_brands = preferences.get('preferred_brands', [])
            if preferred_brands and product['brand'] not in preferred_brands:
                preference_score *= 0.7
            
            # Product type preferences
            preferred_types = preferences.get('preferred_types', [])
            if preferred_types and product['category'] not in preferred_types:
                preference_score *= 0.8
            
            # Apply preference score
            product['preference_score'] = preference_score
            filtered_products.append(product)
        
        return filtered_products
    
    def _optimize_for_demographics(self, products: List[Dict], demographics: Dict) -> List[Dict]:
        """Optimize products for user demographics"""
        if not demographics:
            return products
        
        optimized_products = []
        
        for product in products:
            demographic_score = self._calculate_demographic_score(product, demographics)
            product['demographic_score'] = demographic_score
            optimized_products.append(product)
        
        return optimized_products
    
    def _calculate_demographic_score(self, product: Dict, demographics: Dict) -> float:
        """Calculate how well a product fits user demographics"""
        score = 1.0
        
        product_fit = product.get('demographic_fit', {})
        
        # Age group matching
        user_age = demographics.get('age_category')
        if user_age and 'age_groups' in product_fit:
            if user_age in product_fit['age_groups'] or 'all' in product_fit['age_groups']:
                score *= 1.2
            else:
                score *= 0.8
        
        # Skin type matching
        user_skin_type = demographics.get('skin_type')
        if user_skin_type and 'skin_types' in product_fit:
            if user_skin_type in product_fit['skin_types'] or 'all' in product_fit['skin_types']:
                score *= 1.2
            else:
                score *= 0.7
        
        # Ethnicity matching
        user_ethnicity = demographics.get('ethnicity')
        if user_ethnicity and 'ethnicities' in product_fit:
            if user_ethnicity in product_fit['ethnicities'] or 'all' in product_fit['ethnicities']:
                score *= 1.1
            else:
                score *= 0.9
        
        return round(score, 3)
    
    def _score_products(self, products: List[Dict], 
                       detected_conditions: List[Dict], 
                       demographics: Dict) -> List[Dict]:
        """Score and rank products based on multiple factors"""
        scored_products = []
        
        for product in products:
            # Calculate weighted score
            condition_score = product.get('condition_match_score', 0) * self.recommendation_weights['condition_match']
            demographic_score = product.get('demographic_score', 1.0) * self.recommendation_weights['demographic_fit']
            preference_score = product.get('preference_score', 1.0) * self.recommendation_weights['user_preferences']
            efficacy_score = (product.get('efficacy_score', 7.0) / 10.0) * self.recommendation_weights['efficacy_score']
            safety_score = (product.get('safety_score', 8.0) / 10.0) * self.recommendation_weights['ingredient_safety']
            
            total_score = condition_score + demographic_score + preference_score + efficacy_score + safety_score
            
            scored_product = product.copy()
            scored_product['total_score'] = round(total_score, 3)
            scored_product['score_breakdown'] = {
                'condition_match': condition_score,
                'demographic_fit': demographic_score,
                'user_preferences': preference_score,
                'efficacy_score': efficacy_score,
                'safety_score': safety_score
            }
            
            scored_products.append(scored_product)
        
        # Sort by total score
        scored_products.sort(key=lambda x: x['total_score'], reverse=True)
        
        return scored_products
    
    def _build_complete_routine(self, scored_products: List[Dict]) -> Dict:
        """Build a complete skincare routine"""
        routine_steps = {
            'cleanser': None,
            'toner': None,
            'serum': None,
            'moisturizer': None,
            'sunscreen': None,
            'treatment': None
        }
        
        # Map products to routine steps
        for product in scored_products:
            step = self._determine_routine_step(product)
            if step and not routine_steps[step]:
                routine_steps[step] = product
        
        # Calculate routine total
        routine_total = sum(product['price'] for product in routine_steps.values() if product)
        
        return {
            'steps': routine_steps,
            'total_price': routine_total,
            'step_count': len([p for p in routine_steps.values() if p]),
            'routine_type': self._determine_routine_type(routine_steps)
        }
    
    def _determine_routine_step(self, product: Dict) -> Optional[str]:
        """Determine which step in the routine a product belongs to"""
        category = product.get('category', '')
        
        step_mapping = {
            'cleanser': 'cleanser',
            'toner': 'toner',
            'serum': 'serum',
            'moisturizer': 'moisturizer',
            'sunscreen': 'sunscreen',
            'treatment': 'treatment'
        }
        
        return step_mapping.get(category)
    
    def _determine_routine_type(self, routine_steps: Dict) -> str:
        """Determine the type of routine based on included steps"""
        steps_present = [step for step, product in routine_steps.items() if product]
        
        if len(steps_present) >= 5:
            return 'comprehensive'
        elif len(steps_present) >= 3:
            return 'standard'
        else:
            return 'minimal'
    
    def _analyze_ingredients(self, routine: Dict) -> Dict:
        """Analyze ingredients for safety and compatibility"""
        all_ingredients = []
        compatibility_issues = []
        
        for step, product in routine['steps'].items():
            if product:
                ingredients = product.get('ingredients', [])
                all_ingredients.extend(ingredients)
                
                # Check for compatibility issues
                for ingredient in ingredients:
                    ingredient_data = self.ingredient_analysis.get(ingredient, {})
                    avoid_with = ingredient_data.get('avoid_with', [])
                    
                    for other_ingredient in all_ingredients:
                        if other_ingredient in avoid_with:
                            compatibility_issues.append({
                                'ingredient1': ingredient,
                                'ingredient2': other_ingredient,
                                'issue': 'incompatible_combination'
                            })
        
        return {
            'total_ingredients': len(set(all_ingredients)),
            'unique_ingredients': list(set(all_ingredients)),
            'compatibility_issues': compatibility_issues,
            'safety_assessment': self._assess_overall_safety(all_ingredients)
        }
    
    def _assess_overall_safety(self, ingredients: List[str]) -> Dict:
        """Assess overall safety of ingredient combination"""
        high_risk_ingredients = ['retinol', 'benzoyl_peroxide', 'salicylic_acid']
        moderate_risk_ingredients = ['vitamin_c', 'niacinamide']
        
        risk_count = sum(1 for ing in ingredients if ing in high_risk_ingredients)
        moderate_count = sum(1 for ing in ingredients if ing in moderate_risk_ingredients)
        
        if risk_count > 2:
            safety_level = 'high_risk'
        elif risk_count > 0 or moderate_count > 3:
            safety_level = 'moderate_risk'
        else:
            safety_level = 'low_risk'
        
        return {
            'safety_level': safety_level,
            'high_risk_count': risk_count,
            'moderate_risk_count': moderate_count,
            'recommendations': self._get_safety_recommendations(safety_level)
        }
    
    def _get_safety_recommendations(self, safety_level: str) -> List[str]:
        """Get safety recommendations based on risk level"""
        recommendations = {
            'high_risk': [
                "Consider consulting a dermatologist before use",
                "Start with lower concentrations",
                "Monitor for irritation and discontinue if needed"
            ],
            'moderate_risk': [
                "Patch test before full application",
                "Introduce products gradually",
                "Monitor skin response"
            ],
            'low_risk': [
                "Safe for most skin types",
                "Can be used as directed"
            ]
        }
        
        return recommendations.get(safety_level, [])
    
    def _get_efficacy_data(self, products: List[Dict]) -> Dict:
        """Get efficacy data for recommended products"""
        efficacy_info = {}
        
        for product in products:
            product_id = product.get('id')
            if product_id in self.efficacy_data.get('user_reviews', {}):
                efficacy_info[product_id] = self.efficacy_data['user_reviews'][product_id]
        
        return {
            'product_efficacy': efficacy_info,
            'clinical_studies': self.efficacy_data.get('clinical_studies', {}),
            'overall_confidence': self._calculate_efficacy_confidence(efficacy_info)
        }
    
    def _calculate_efficacy_confidence(self, efficacy_info: Dict) -> float:
        """Calculate overall efficacy confidence"""
        if not efficacy_info:
            return 0.7  # Default confidence
        
        total_rating = sum(data['rating'] for data in efficacy_info.values())
        total_reviews = sum(data['review_count'] for data in efficacy_info.values())
        
        if total_reviews > 0:
            avg_rating = total_rating / len(efficacy_info)
            confidence = min(avg_rating / 5.0, 1.0)  # Normalize to 0-1
            return round(confidence, 3)
        
        return 0.7
    
    def _get_demographic_factors(self, demographics: Dict) -> Dict:
        """Get demographic factors used in recommendations"""
        if not demographics:
            return {'factors_applied': [], 'baseline_count': len(self.demographic_baselines)}
        
        factors = []
        for key, value in demographics.items():
            if value:
                factors.append(f"{key}: {value}")
        
        return {
            'factors_applied': factors,
            'baseline_count': len(self.demographic_baselines),
            'demographics_used': demographics
        }
    
    def _calculate_recommendation_confidence(self, products: List[Dict], demographics: Dict) -> float:
        """Calculate confidence in recommendations"""
        if not products:
            return 0.0
        
        # Average product scores
        avg_score = sum(p['total_score'] for p in products) / len(products)
        
        # Demographic baseline confidence
        baseline_confidence = 1.0 if len(self.demographic_baselines) > 50 else 0.7
        
        # Condition embedding confidence
        embedding_confidence = 1.0 if len(self.condition_embeddings) > 0 else 0.6
        
        # Combine factors
        confidence = (avg_score * 0.4 + baseline_confidence * 0.3 + embedding_confidence * 0.3)
        
        return round(min(confidence, 1.0), 3)
    
    def _calculate_condition_match_score(self, condition: str, severity: float, product: Dict) -> float:
        """Calculate how well a product matches a specific condition"""
        target_conditions = product.get('target_conditions', [])
        
        if condition in target_conditions:
            # Higher severity should get higher score for targeted products
            base_score = 0.8
            severity_bonus = min(severity / 10.0, 0.2)  # Up to 20% bonus for high severity
            return round(base_score + severity_bonus, 3)
        
        return 0.3  # Lower score for non-targeted products
    
    def _map_severity_to_level(self, severity: float) -> str:
        """Map numerical severity to level"""
        if severity < 3.0:
            return 'mild'
        elif severity < 6.0:
            return 'moderate'
        elif severity < 8.0:
            return 'severe'
        else:
            return 'very_severe'
    
    def get_system_status(self) -> Dict:
        """Get system status and capabilities"""
        return {
            'system': 'Enhanced Recommendation Engine',
            'status': 'active',
            'capabilities': {
                'demographic_baselines': len(self.demographic_baselines),
                'condition_embeddings': len(self.condition_embeddings),
                'product_categories': len(self.product_database),
                'total_products': sum(len(products) for products in self.product_database.values()),
                'ingredients_analyzed': len(self.ingredient_analysis)
            },
            'recommendation_methodology': {
                'weights_used': self.recommendation_weights,
                'demographic_integration': True,
                'condition_specific_matching': True,
                'ingredient_safety_analysis': True
            }
        }

# Create singleton instance
enhanced_recommendation_engine = EnhancedRecommendationEngine()

def main():
    """Test the enhanced recommendation engine"""
    # Test data
    test_analysis_results = {
        'enhanced_severity': {
            'hyperpigmentation': {
                'overall_score': 7.2,
                'severity_level': 'moderate',
                'confidence': 0.85
            },
            'fine_lines_wrinkles': {
                'overall_score': 4.8,
                'severity_level': 'moderate',
                'confidence': 0.78
            }
        }
    }
    
    test_demographics = {
        'age_category': 'thirties',
        'skin_type': '4',
        'ethnicity': 'east_asian'
    }
    
    test_preferences = {
        'max_budget': 200,
        'preferred_brands': ['Shine'],
        'preferred_types': ['serum', 'moisturizer']
    }
    
    # Test recommendations
    result = enhanced_recommendation_engine.generate_personalized_recommendations(
        test_analysis_results, test_preferences, test_demographics)
    
    print("Enhanced Recommendation Engine Test Results:")
    print(json.dumps(result, indent=2))
    
    # Print system status
    status = enhanced_recommendation_engine.get_system_status()
    print("\nSystem Status:")
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main() 