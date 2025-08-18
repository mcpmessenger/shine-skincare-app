#!/usr/bin/env python3
"""
Product Recommendation Engine for SWAN Initiative
Intelligently matches skin analysis results with appropriate skincare products
"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class ProductRecommendationEngine:
    """Advanced product recommendation engine using skin analysis results"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.products = self._load_product_database()
        self.ingredient_rules = self._load_ingredient_rules()
        self.condition_mappings = self._load_condition_mappings()
        
        logger.info(f"✅ Product recommendation engine initialized with {len(self.products)} products")
    
    def _load_product_database(self) -> List[Dict]:
        """Load the product database from the frontend"""
        try:
            # This would typically come from a database, but for now we'll use the frontend products
            # In production, this should be loaded from Supabase or similar
            products = [
                {
                    'id': 'is-clinical-cleansing',
                    'name': 'iS Clinical Cleansing Complex',
                    'price': 45.00,
                    'category': 'cleanser',
                    'brand': 'iS Clinical',
                    'description': 'Gentle yet effective cleanser with salicylic acid for acne-prone skin',
                    'ingredients': ['salicylic acid', 'glycolic acid', 'vitamin c', 'aloe vera'],
                    'skin_type_compatibility': ['oily', 'combination', 'acne-prone'],
                    'skin_concerns_addressed': ['acne', 'clogged_pores', 'uneven_texture'],
                    'dermatologist_recommended': True,
                    'rating': 4.8
                },
                {
                    'id': 'dermalogica-ultracalming',
                    'name': 'Dermalogica UltraCalming Cleanser',
                    'price': 38.00,
                    'category': 'cleanser',
                    'brand': 'Dermalogica',
                    'description': 'Soothing cleanser for sensitive and reactive skin',
                    'ingredients': ['oat kernel extract', 'colloidal oatmeal', 'aloe vera', 'chamomile'],
                    'skin_type_compatibility': ['sensitive', 'dry', 'reactive'],
                    'skin_concerns_addressed': ['redness', 'irritation', 'sensitivity'],
                    'dermatologist_recommended': True,
                    'rating': 4.7
                },
                {
                    'id': 'skinceuticals-ce-ferulic',
                    'name': 'SkinCeuticals C E Ferulic',
                    'price': 169.00,
                    'category': 'serum',
                    'brand': 'SkinCeuticals',
                    'description': 'Antioxidant serum with vitamin C for brightening and protection',
                    'ingredients': ['vitamin c', 'vitamin e', 'ferulic acid', 'hyaluronic acid'],
                    'skin_type_compatibility': ['all'],
                    'skin_concerns_addressed': ['dark_spots', 'hyperpigmentation', 'aging', 'sun_damage'],
                    'dermatologist_recommended': True,
                    'rating': 4.9
                },
                {
                    'id': 'tns-advanced-serum',
                    'name': 'TNS Advanced+ Serum',
                    'price': 195.00,
                    'category': 'serum',
                    'brand': 'SkinMedica',
                    'description': 'Advanced growth factor serum for anti-aging and skin renewal',
                    'ingredients': ['growth factors', 'peptides', 'hyaluronic acid', 'antioxidants'],
                    'skin_type_compatibility': ['all'],
                    'skin_concerns_addressed': ['aging', 'fine_lines', 'wrinkles', 'texture'],
                    'dermatologist_recommended': True,
                    'rating': 4.8
                },
                {
                    'id': 'pca-skin-pigment-gel',
                    'name': 'PCA SKIN Pigment Gel Pro',
                    'price': 89.00,
                    'category': 'treatment',
                    'brand': 'PCA SKIN',
                    'description': 'Professional-grade treatment for hyperpigmentation and dark spots',
                    'ingredients': ['hydroquinone', 'kojic acid', 'vitamin c', 'niacinamide'],
                    'skin_type_compatibility': ['all'],
                    'skin_concerns_addressed': ['dark_spots', 'hyperpigmentation', 'melasma'],
                    'dermatologist_recommended': True,
                    'rating': 4.6
                },
                {
                    'id': 'first-aid-beauty-repair',
                    'name': 'First Aid Beauty Ultra Repair Cream',
                    'price': 34.00,
                    'category': 'moisturizer',
                    'brand': 'First Aid Beauty',
                    'description': 'Intensive moisturizer for dry, sensitive skin',
                    'ingredients': ['colloidal oatmeal', 'ceramides', 'hyaluronic acid', 'shea butter'],
                    'skin_type_compatibility': ['dry', 'sensitive', 'dehydrated'],
                    'skin_concerns_addressed': ['dryness', 'irritation', 'barrier_damage'],
                    'dermatologist_recommended': True,
                    'rating': 4.7
                },
                {
                    'id': 'eltamd-uv-clear',
                    'name': 'EltaMD UV Clear Broad-Spectrum SPF 46',
                    'price': 39.00,
                    'category': 'sunscreen',
                    'brand': 'EltaMD',
                    'description': 'Oil-free sunscreen with niacinamide for acne-prone skin',
                    'ingredients': ['zinc oxide', 'niacinamide', 'hyaluronic acid', 'vitamin e'],
                    'skin_type_compatibility': ['all', 'acne-prone', 'sensitive'],
                    'skin_concerns_addressed': ['sun_damage', 'acne', 'redness'],
                    'dermatologist_recommended': True,
                    'rating': 4.8
                },
                {
                    'id': 'allies-of-skin-cleanser',
                    'name': 'Allies of Skin Mandelic Pigmentation Corrector',
                    'price': 95.00,
                    'category': 'treatment',
                    'brand': 'Allies of Skin',
                    'description': 'Gentle exfoliating treatment for hyperpigmentation',
                    'ingredients': ['mandelic acid', 'niacinamide', 'vitamin c', 'hyaluronic acid'],
                    'skin_type_compatibility': ['all'],
                    'skin_concerns_addressed': ['dark_spots', 'hyperpigmentation', 'texture'],
                    'dermatologist_recommended': True,
                    'rating': 4.7
                }
            ]
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Failed to load product database: {e}")
            return []
    
    def _load_ingredient_rules(self) -> Dict:
        """Load ingredient-based recommendation rules"""
        return {
            'acne': {
                'beneficial': ['salicylic acid', 'benzoyl peroxide', 'niacinamide', 'zinc', 'tea tree oil'],
                'avoid': ['heavy oils', 'comedogenic ingredients', 'fragrance', 'alcohol'],
                'categories': ['cleanser', 'treatment', 'serum']
            },
            'redness': {
                'beneficial': ['aloe vera', 'chamomile', 'centella asiatica', 'green tea', 'niacinamide'],
                'avoid': ['fragrance', 'alcohol', 'harsh exfoliants', 'hot water'],
                'categories': ['cleanser', 'moisturizer', 'serum']
            },
            'dark_spots': {
                'beneficial': ['vitamin c', 'niacinamide', 'hydroquinone', 'kojic acid', 'alpha arbutin'],
                'avoid': ['irritating ingredients', 'fragrance', 'alcohol'],
                'categories': ['serum', 'treatment', 'moisturizer']
            },
            'texture': {
                'beneficial': ['glycolic acid', 'lactic acid', 'salicylic acid', 'retinol', 'peptides'],
                'avoid': ['harsh scrubs', 'over-exfoliation'],
                'categories': ['treatment', 'serum', 'moisturizer']
            },
            'aging': {
                'beneficial': ['retinol', 'peptides', 'growth factors', 'vitamin c', 'hyaluronic acid'],
                'avoid': ['harsh ingredients', 'fragrance'],
                'categories': ['serum', 'treatment', 'moisturizer']
            },
            'dryness': {
                'beneficial': ['hyaluronic acid', 'ceramides', 'glycerin', 'shea butter', 'squalane'],
                'avoid': ['alcohol', 'harsh cleansers', 'fragrance'],
                'categories': ['moisturizer', 'cleanser', 'serum']
            },
            'sensitivity': {
                'beneficial': ['aloe vera', 'centella asiatica', 'ceramides', 'hyaluronic acid'],
                'avoid': ['fragrance', 'alcohol', 'harsh exfoliants', 'essential oils'],
                'categories': ['cleanser', 'moisturizer', 'serum']
            }
        }
    
    def _load_condition_mappings(self) -> Dict:
        """Load mappings between detected conditions and product categories"""
        return {
            'acne': {
                'primary_category': 'cleanser',
                'secondary_categories': ['treatment', 'serum'],
                'priority': 'high',
                'urgency': 'immediate'
            },
            'redness': {
                'primary_category': 'moisturizer',
                'secondary_categories': ['cleanser', 'serum'],
                'priority': 'medium',
                'urgency': 'short_term'
            },
            'dark_spots': {
                'primary_category': 'serum',
                'secondary_categories': ['treatment', 'moisturizer'],
                'priority': 'medium',
                'urgency': 'long_term'
            },
            'texture': {
                'primary_category': 'treatment',
                'secondary_categories': ['serum', 'moisturizer'],
                'priority': 'medium',
                'urgency': 'medium_term'
            },
            'aging': {
                'primary_category': 'serum',
                'secondary_categories': ['treatment', 'moisturizer'],
                'priority': 'medium',
                'urgency': 'long_term'
            },
            'dryness': {
                'primary_category': 'moisturizer',
                'secondary_categories': ['cleanser', 'serum'],
                'priority': 'high',
                'urgency': 'immediate'
            },
            'sensitivity': {
                'primary_category': 'moisturizer',
                'secondary_categories': ['cleanser', 'serum'],
                'priority': 'high',
                'urgency': 'immediate'
            }
        }
    
    def generate_recommendations(self, skin_analysis: Dict, max_products: int = 6) -> Dict:
        """Generate personalized product recommendations based on skin analysis"""
        try:
            logger.info("🧠 Generating personalized product recommendations...")
            
            # Extract analysis data
            conditions = skin_analysis.get('conditions', {})
            health_score = skin_analysis.get('health_score', 0.5)
            primary_concerns = skin_analysis.get('primary_concerns', [])
            
            # Initialize recommendation structure
            recommendations = {
                'primary_recommendations': [],
                'secondary_recommendations': [],
                'general_recommendations': [],
                'avoid_products': [],
                'skincare_routine': [],
                'analysis_summary': {},
                'confidence_score': 0.0
            }
            
            # Analyze detected conditions and generate recommendations
            detected_conditions = self._analyze_detected_conditions(conditions)
            recommendations['analysis_summary'] = detected_conditions
            
            # Generate product recommendations for each condition
            all_recommendations = []
            for condition, data in detected_conditions.items():
                if data['detected'] and data['severity'] != 'none':
                    condition_recs = self._get_condition_recommendations(
                        condition, data, conditions, health_score
                    )
                    all_recommendations.extend(condition_recs)
            
            # Sort and rank recommendations
            ranked_recommendations = self._rank_recommendations(all_recommendations, health_score)
            
            # Categorize recommendations
            recommendations['primary_recommendations'] = ranked_recommendations[:3]
            recommendations['secondary_recommendations'] = ranked_recommendations[3:6]
            recommendations['general_recommendations'] = self._get_general_recommendations(health_score)
            
            # Generate skincare routine
            recommendations['skincare_routine'] = self._generate_skincare_routine(ranked_recommendations)
            
            # Calculate confidence score
            recommendations['confidence_score'] = self._calculate_recommendation_confidence(
                detected_conditions, health_score
            )
            
            logger.info(f"✅ Generated {len(ranked_recommendations)} product recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            return self._get_fallback_recommendations()
    
    def _analyze_detected_conditions(self, conditions: Dict) -> Dict:
        """Analyze detected skin conditions and their severity"""
        analyzed_conditions = {}
        
        for condition_name, condition_data in conditions.items():
            if isinstance(condition_data, dict) and 'detected' in condition_data:
                analyzed_conditions[condition_name] = {
                    'detected': condition_data.get('detected', False),
                    'severity': condition_data.get('severity', 'none'),
                    'confidence': condition_data.get('confidence', 0.0),
                    'percentage': condition_data.get('percentage', 0.0),
                    'description': self._get_condition_description(condition_name, condition_data)
                }
        
        return analyzed_conditions
    
    def _get_condition_description(self, condition: str, data: Dict) -> str:
        """Get human-readable description of detected condition"""
        descriptions = {
            'acne': f"Detected {data.get('spot_count', 0)} acne spots covering {data.get('percentage', 0):.1%} of the area",
            'redness': f"Redness detected covering {data.get('percentage', 0):.1%} of the area",
            'dark_spots': f"Dark spots detected covering {data.get('percentage', 0):.1%} of the area",
            'texture': f"Texture analysis shows {data.get('type', 'unknown')} skin texture",
            'pores': f"Pore analysis shows {data.get('count', 0)} visible pores",
            'wrinkles': f"Wrinkle analysis shows {data.get('count', 0)} detected lines",
            'pigmentation': f"Pigmentation level: {data.get('level', 'unknown')}"
        }
        
        return descriptions.get(condition, f"Condition {condition} detected")
    
    def _get_condition_recommendations(self, condition: str, condition_data: Dict, 
                                     all_conditions: Dict, health_score: float) -> List[Dict]:
        """Get product recommendations for a specific condition"""
        recommendations = []
        
        # Get condition mapping
        condition_mapping = self.condition_mappings.get(condition, {})
        primary_category = condition_mapping.get('primary_category', 'general')
        
        # Filter products for this condition
        suitable_products = self._filter_products_for_condition(
            condition, condition_data, primary_category
        )
        
        # Score and rank products
        for product in suitable_products:
            score = self._calculate_product_score(product, condition, condition_data, health_score)
            recommendations.append({
                'product': product,
                'score': score,
                'reason': self._get_recommendation_reason(product, condition, condition_data),
                'priority': condition_mapping.get('priority', 'medium'),
                'urgency': condition_mapping.get('urgency', 'medium_term')
            })
        
        return recommendations
    
    def _filter_products_for_condition(self, condition: str, condition_data: Dict, 
                                     primary_category: str) -> List[Dict]:
        """Filter products suitable for a specific condition"""
        suitable_products = []
        
        for product in self.products:
            # Check if product addresses this condition
            if self._product_matches_condition(product, condition, condition_data):
                suitable_products.append(product)
        
        # Sort by category priority
        suitable_products.sort(key=lambda x: (
            x['category'] == primary_category,  # Primary category first
            x['rating'],  # Then by rating
            -x['price']   # Then by price (lower first)
        ), reverse=True)
        
        return suitable_products
    
    def _product_matches_condition(self, product: Dict, condition: str, condition_data: Dict) -> bool:
        """Check if a product matches a specific condition"""
        # Check if product addresses this condition
        if condition in product.get('skin_concerns_addressed', []):
            return True
        
        # Check ingredients for beneficial compounds
        beneficial_ingredients = self.ingredient_rules.get(condition, {}).get('beneficial', [])
        product_ingredients = [ing.lower() for ing in product.get('ingredients', [])]
        
        for beneficial in beneficial_ingredients:
            if any(beneficial in ing for ing in product_ingredients):
                return True
        
        return False
    
    def _calculate_product_score(self, product: Dict, condition: str, 
                               condition_data: Dict, health_score: float) -> float:
        """Calculate a score for how well a product matches the condition"""
        score = 0.0
        
        # Base score from rating
        score += product.get('rating', 0) * 0.2
        
        # Condition match score
        if condition in product.get('skin_concerns_addressed', []):
            score += 0.3
        
        # Ingredient match score
        beneficial_ingredients = self.ingredient_rules.get(condition, {}).get('beneficial', [])
        product_ingredients = [ing.lower() for ing in product.get('ingredients', [])]
        
        ingredient_matches = sum(1 for beneficial in beneficial_ingredients 
                               if any(beneficial in ing for ing in product_ingredients))
        score += min(0.2, ingredient_matches * 0.05)
        
        # Dermatologist recommendation bonus
        if product.get('dermatologist_recommended', False):
            score += 0.1
        
        # Price consideration (prefer mid-range products)
        price = product.get('price', 0)
        if 20 <= price <= 80:
            score += 0.1
        elif price > 100:
            score -= 0.1
        
        # Severity adjustment
        severity = condition_data.get('severity', 'none')
        if severity == 'severe':
            score += 0.1  # Prioritize effective products for severe conditions
        
        return min(1.0, max(0.0, score))
    
    def _get_recommendation_reason(self, product: Dict, condition: str, 
                                 condition_data: Dict) -> str:
        """Generate a human-readable reason for the recommendation"""
        reasons = []
        
        # Condition-specific reasons
        if condition in product.get('skin_concerns_addressed', []):
            reasons.append(f"Specifically formulated for {condition}")
        
        # Ingredient-based reasons
        beneficial_ingredients = self.ingredient_rules.get(condition, {}).get('beneficial', [])
        product_ingredients = [ing.lower() for ing in product.get('ingredients', [])]
        
        for beneficial in beneficial_ingredients:
            if any(beneficial in ing for ing in product_ingredients):
                reasons.append(f"Contains {beneficial} which helps with {condition}")
                break
        
        # General reasons
        if product.get('dermatologist_recommended', False):
            reasons.append("Dermatologist recommended")
        
        if product.get('rating', 0) >= 4.5:
            reasons.append("Highly rated by users")
        
        return "; ".join(reasons) if reasons else "Suitable for your skin concerns"
    
    def _rank_recommendations(self, recommendations: List[Dict], health_score: float) -> List[Dict]:
        """Rank recommendations by score and other factors"""
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Apply health score adjustment
        for rec in recommendations:
            if health_score < 0.6:
                # Prioritize gentle, barrier-repair products for poor skin health
                if any(ing in rec['product'].get('ingredients', []) 
                       for ing in ['ceramides', 'hyaluronic acid', 'aloe vera']):
                    rec['score'] += 0.1
        
        # Re-sort after adjustments
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations
    
    def _get_general_recommendations(self, health_score: float) -> List[str]:
        """Get general skincare recommendations based on health score"""
        if health_score >= 0.8:
            return [
                "Continue your current skincare routine",
                "Maintain good hydration and nutrition",
                "Use broad-spectrum sunscreen daily",
                "Consider preventive anti-aging products"
            ]
        elif health_score >= 0.6:
            return [
                "Focus on gentle, consistent skincare",
                "Address specific concerns with targeted products",
                "Maintain skin barrier health",
                "Use sunscreen to prevent further damage"
            ]
        else:
            return [
                "Consider consulting with a dermatologist",
                "Focus on gentle, barrier-repair products",
                "Avoid harsh ingredients and over-exfoliation",
                "Prioritize hydration and protection"
            ]
    
    def _generate_skincare_routine(self, recommendations: List[Dict]) -> List[Dict]:
        """Generate a complete skincare routine from recommendations"""
        routine = []
        
        # Morning routine
        morning_products = [r for r in recommendations if r['product']['category'] in ['cleanser', 'serum', 'moisturizer', 'sunscreen']]
        if morning_products:
            routine.append({
                'time': 'morning',
                'products': morning_products[:3],  # Limit to 3 products
                'steps': self._generate_routine_steps(morning_products[:3])
            })
        
        # Evening routine
        evening_products = [r for r in recommendations if r['product']['category'] in ['cleanser', 'treatment', 'serum', 'moisturizer']]
        if evening_products:
            routine.append({
                'time': 'evening',
                'products': evening_products[:3],  # Limit to 3 products
                'steps': self._generate_routine_steps(evening_products[:3])
            })
        
        return routine
    
    def _generate_routine_steps(self, products: List[Dict]) -> List[str]:
        """Generate step-by-step routine instructions"""
        steps = []
        
        # Sort products by application order
        category_order = ['cleanser', 'treatment', 'serum', 'moisturizer', 'sunscreen']
        sorted_products = sorted(products, key=lambda x: category_order.index(x['product']['category']))
        
        for i, rec in enumerate(sorted_products):
            product = rec['product']
            step_num = i + 1
            
            if product['category'] == 'cleanser':
                steps.append(f"{step_num}. Cleanse with {product['name']} - apply to damp skin and rinse thoroughly")
            elif product['category'] == 'treatment':
                steps.append(f"{step_num}. Apply {product['name']} - use as directed, typically 2-3 times per week")
            elif product['category'] == 'serum':
                steps.append(f"{step_num}. Apply {product['name']} - use a small amount and gently pat into skin")
            elif product['category'] == 'moisturizer':
                steps.append(f"{step_num}. Moisturize with {product['name']} - apply to slightly damp skin")
            elif product['category'] == 'sunscreen':
                steps.append(f"{step_num}. Apply {product['name']} - use generously and reapply every 2 hours")
        
        return steps
    
    def _calculate_recommendation_confidence(self, detected_conditions: Dict, health_score: float) -> float:
        """Calculate confidence score for recommendations"""
        if not detected_conditions:
            return 0.5  # Neutral confidence if no conditions detected
        
        # Calculate confidence based on condition detection and health score
        condition_confidence = 0.0
        total_conditions = 0
        
        for condition, data in detected_conditions.items():
            if data['detected']:
                condition_confidence += data['confidence']
                total_conditions += 1
        
        if total_conditions > 0:
            avg_condition_confidence = condition_confidence / total_conditions
            # Combine condition confidence with health score
            confidence = (avg_condition_confidence * 0.7) + (health_score * 0.3)
            return min(1.0, max(0.0, confidence))
        
        return health_score
    
    def _get_fallback_recommendations(self) -> Dict:
        """Get fallback recommendations when analysis fails"""
        return {
            'primary_recommendations': [],
            'secondary_recommendations': [],
            'general_recommendations': [
                "Continue your current skincare routine",
                "Use gentle, fragrance-free products",
                "Maintain good hydration and nutrition",
                "Consider consulting with a dermatologist for personalized advice"
            ],
            'avoid_products': [],
            'skincare_routine': [],
            'analysis_summary': {},
            'confidence_score': 0.3,
            'note': 'Fallback recommendations - analysis unavailable'
        }

def main():
    """Test the product recommendation engine"""
    print("🧠 Testing Product Recommendation Engine...")
    
    # Initialize engine
    engine = ProductRecommendationEngine()
    
    # Create test skin analysis
    test_analysis = {
        'conditions': {
            'acne': {
                'detected': True,
                'severity': 'moderate',
                'confidence': 0.8,
                'percentage': 0.12,
                'spot_count': 25
            },
            'redness': {
                'detected': True,
                'severity': 'slight',
                'confidence': 0.6,
                'percentage': 0.08
            }
        },
        'health_score': 0.65
    }
    
    # Generate recommendations
    recommendations = engine.generate_recommendations(test_analysis)
    
    print(f"✅ Generated recommendations with confidence: {recommendations['confidence_score']:.2f}")
    print(f"📦 Primary recommendations: {len(recommendations['primary_recommendations'])}")
    print(f"📦 Secondary recommendations: {len(recommendations['secondary_recommendations'])}")
    print(f"📋 Skincare routine steps: {len(recommendations['skincare_routine'])}")
    
    # Show top recommendation
    if recommendations['primary_recommendations']:
        top_rec = recommendations['primary_recommendations'][0]
        print(f"\n🏆 Top recommendation: {top_rec['product']['name']}")
        print(f"   Score: {top_rec['score']:.2f}")
        print(f"   Reason: {top_rec['reason']}")

if __name__ == "__main__":
    main()
