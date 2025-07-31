import os
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class IngredientBasedRecommendations:
    """Service for ingredient-based product recommendations using similar skin profiles"""
    
    def __init__(self):
        """Initialize the ingredient-based recommendations service"""
        
        # Ingredient categories mapped to skin conditions
        self.ingredient_mapping = {
            'acne': {
                'primary_ingredients': ['salicylic_acid', 'benzoyl_peroxide', 'niacinamide'],
                'secondary_ingredients': ['tea_tree_oil', 'zinc', 'sulfur'],
                'avoid_ingredients': ['heavy_oils', 'comedogenic_ingredients']
            },
            'dryness': {
                'primary_ingredients': ['hyaluronic_acid', 'ceramides', 'glycerin'],
                'secondary_ingredients': ['squalane', 'shea_butter', 'jojoba_oil'],
                'avoid_ingredients': ['alcohol', 'fragrance', 'harsh_detergents']
            },
            'redness': {
                'primary_ingredients': ['centella_asiatica', 'aloe_vera', 'green_tea'],
                'secondary_ingredients': ['chamomile', 'licorice_root', 'calendula'],
                'avoid_ingredients': ['fragrance', 'alcohol', 'harsh_exfoliants']
            },
            'hyperpigmentation': {
                'primary_ingredients': ['vitamin_c', 'niacinamide', 'alpha_arbutin'],
                'secondary_ingredients': ['kojic_acid', 'tranexamic_acid', 'licorice_root'],
                'avoid_ingredients': ['fragrance', 'irritating_ingredients']
            },
            'sensitivity': {
                'primary_ingredients': ['centella_asiatica', 'aloe_vera', 'ceramides'],
                'secondary_ingredients': ['chamomile', 'calendula', 'panthenol'],
                'avoid_ingredients': ['fragrance', 'alcohol', 'essential_oils']
            },
            'rosacea': {
                'primary_ingredients': ['centella_asiatica', 'azelaic_acid', 'metronidazole'],
                'secondary_ingredients': ['green_tea', 'chamomile', 'aloe_vera'],
                'avoid_ingredients': ['fragrance', 'alcohol', 'harsh_ingredients']
            },
            'eczema': {
                'primary_ingredients': ['ceramides', 'colloidal_oatmeal', 'panthenol'],
                'secondary_ingredients': ['shea_butter', 'squalane', 'centella_asiatica'],
                'avoid_ingredients': ['fragrance', 'alcohol', 'harsh_detergents']
            }
        }
        
        # Product categories with ingredient requirements
        self.product_categories = {
            'gentle_cleanser': {
                'description': 'Non-stripping cleanser for daily use',
                'required_ingredients': ['glycerin'],
                'avoid_ingredients': ['harsh_detergents', 'fragrance'],
                'suitable_for': ['all_types']
            },
            'hydrating_cleanser': {
                'description': 'Moisturizing cleanser for dry skin',
                'required_ingredients': ['hyaluronic_acid', 'ceramides'],
                'avoid_ingredients': ['harsh_detergents'],
                'suitable_for': ['dry', 'sensitive']
            },
            'acne_cleanser': {
                'description': 'Cleanser with acne-fighting ingredients',
                'required_ingredients': ['salicylic_acid'],
                'avoid_ingredients': ['harsh_detergents'],
                'suitable_for': ['oily', 'acne']
            },
            'lightweight_moisturizer': {
                'description': 'Oil-free moisturizer for oily skin',
                'required_ingredients': ['hyaluronic_acid'],
                'avoid_ingredients': ['heavy_oils'],
                'suitable_for': ['oily', 'combination']
            },
            'rich_moisturizer': {
                'description': 'Nourishing moisturizer for dry skin',
                'required_ingredients': ['ceramides', 'hyaluronic_acid'],
                'avoid_ingredients': ['fragrance'],
                'suitable_for': ['dry', 'sensitive']
            },
            'acne_treatment': {
                'description': 'Targeted treatment for acne',
                'required_ingredients': ['salicylic_acid', 'niacinamide'],
                'avoid_ingredients': ['irritating_ingredients'],
                'suitable_for': ['acne']
            },
            'brightening_serum': {
                'description': 'Serum for hyperpigmentation',
                'required_ingredients': ['vitamin_c', 'niacinamide'],
                'avoid_ingredients': ['fragrance'],
                'suitable_for': ['hyperpigmentation']
            },
            'calming_serum': {
                'description': 'Soothing serum for sensitive skin',
                'required_ingredients': ['centella_asiatica', 'aloe_vera'],
                'avoid_ingredients': ['fragrance', 'alcohol'],
                'suitable_for': ['sensitive', 'redness']
            },
            'barrier_repair': {
                'description': 'Ceramide-rich product for barrier repair',
                'required_ingredients': ['ceramides', 'cholesterol'],
                'avoid_ingredients': ['fragrance'],
                'suitable_for': ['dry', 'sensitive', 'eczema']
            }
        }
    
    def get_recommendations_from_similar_profiles(self, 
                                                similar_results: List[Tuple[str, float]],
                                                skin_conditions: Dict[str, float],
                                                skin_type: str) -> Dict[str, Any]:
        """
        Generate product recommendations based on similar skin profiles and conditions
        
        Args:
            similar_results: List of (profile_id, similarity_score) from FAISS
            skin_conditions: Dict of condition scores from analysis
            skin_type: Determined skin type (Oily, Dry, etc.)
            
        Returns:
            Dictionary with recommended product categories and ingredients
        """
        try:
            logger.info(f"Generating recommendations for {skin_type} skin with {len(similar_results)} similar profiles")
            
            # Extract successful patterns from similar profiles
            successful_patterns = self._extract_successful_patterns(similar_results)
            
            # Determine primary concerns
            primary_concerns = self._determine_primary_concerns(skin_conditions)
            
            # Generate ingredient recommendations
            ingredient_recs = self._generate_ingredient_recommendations(primary_concerns, successful_patterns)
            
            # Generate product category recommendations
            product_recs = self._generate_product_recommendations(skin_type, primary_concerns, ingredient_recs)
            
            # Create personalized recommendations
            personalized_recs = self._create_personalized_recommendations(
                skin_type, primary_concerns, ingredient_recs, product_recs, similar_results
            )
            
            return {
                'status': 'success',
                'skin_type': skin_type,
                'primary_concerns': primary_concerns,
                'recommended_ingredients': ingredient_recs,
                'recommended_products': product_recs,
                'personalized_advice': personalized_recs,
                'similar_profiles_analyzed': len(similar_results),
                'confidence_score': self._calculate_confidence(similar_results),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_successful_patterns(self, similar_results: List[Tuple[str, float]]) -> Dict[str, float]:
        """Extract successful ingredient patterns from similar profiles"""
        # In production, this would query a database of user feedback
        # For now, we'll use mock data based on similarity scores
        
        successful_patterns = {}
        
        for profile_id, similarity_score in similar_results:
            # Higher similarity = more weight to their successful ingredients
            weight = similarity_score
            
            # Mock successful ingredients for this profile
            # In production, this would come from user feedback database
            profile_ingredients = self._get_mock_successful_ingredients(profile_id)
            
            for ingredient, success_rate in profile_ingredients.items():
                if ingredient not in successful_patterns:
                    successful_patterns[ingredient] = 0
                successful_patterns[ingredient] += success_rate * weight
        
        return successful_patterns
    
    def _get_mock_successful_ingredients(self, profile_id: str) -> Dict[str, float]:
        """Get mock successful ingredients for a profile (would be database lookup)"""
        # In production, this would query user feedback database
        # For now, return mock data based on profile ID hash
        
        import hashlib
        hash_val = int(hashlib.md5(profile_id.encode()).hexdigest()[:8], 16)
        
        # Generate consistent mock data based on hash
        np.random.seed(hash_val)
        
        ingredients = ['salicylic_acid', 'hyaluronic_acid', 'niacinamide', 'vitamin_c', 
                     'centella_asiatica', 'ceramides', 'aloe_vera', 'green_tea']
        
        successful = {}
        for ingredient in ingredients:
            # Generate success rate between 0.3 and 0.9
            success_rate = 0.3 + (np.random.random() * 0.6)
            successful[ingredient] = success_rate
        
        return successful
    
    def _determine_primary_concerns(self, skin_conditions: Dict[str, float]) -> List[str]:
        """Determine primary skin concerns from condition scores"""
        concerns = []
        
        # Map conditions to concerns
        condition_to_concern = {
            'acne': 'acne',
            'dryness': 'dryness', 
            'redness': 'redness',
            'hyperpigmentation': 'hyperpigmentation',
            'rosacea': 'redness',
            'eczema': 'dryness',
            'dermatitis': 'sensitivity'
        }
        
        # Add concerns based on condition scores
        for condition, score in skin_conditions.items():
            if score > 0.3:  # Threshold for concern
                concern = condition_to_concern.get(condition, condition)
                if concern not in concerns:
                    concerns.append(concern)
        
        return concerns
    
    def _generate_ingredient_recommendations(self, 
                                           primary_concerns: List[str],
                                           successful_patterns: Dict[str, float]) -> Dict[str, Any]:
        """Generate ingredient recommendations based on concerns and successful patterns"""
        
        recommended_ingredients = {
            'primary': [],
            'secondary': [],
            'avoid': []
        }
        
        # Add ingredients based on concerns
        for concern in primary_concerns:
            if concern in self.ingredient_mapping:
                mapping = self.ingredient_mapping[concern]
                
                # Add primary ingredients
                for ingredient in mapping['primary_ingredients']:
                    if ingredient not in recommended_ingredients['primary']:
                        recommended_ingredients['primary'].append(ingredient)
                
                # Add secondary ingredients
                for ingredient in mapping['secondary_ingredients']:
                    if ingredient not in recommended_ingredients['secondary']:
                        recommended_ingredients['secondary'].append(ingredient)
                
                # Add avoid ingredients
                for ingredient in mapping['avoid_ingredients']:
                    if ingredient not in recommended_ingredients['avoid']:
                        recommended_ingredients['avoid'].append(ingredient)
        
        # Boost ingredients that were successful in similar profiles
        for ingredient, success_score in successful_patterns.items():
            if success_score > 0.5:  # High success rate
                if ingredient not in recommended_ingredients['primary']:
                    recommended_ingredients['primary'].append(ingredient)
        
        return recommended_ingredients
    
    def _generate_product_recommendations(self, 
                                        skin_type: str,
                                        primary_concerns: List[str],
                                        ingredient_recs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate product category recommendations"""
        
        recommended_products = []
        
        # Map skin type to product categories
        skin_type_categories = {
            'Oily': ['gentle_cleanser', 'lightweight_moisturizer'],
            'Dry': ['hydrating_cleanser', 'rich_moisturizer', 'barrier_repair'],
            'Sensitive': ['gentle_cleanser', 'calming_serum', 'barrier_repair'],
            'Combination': ['gentle_cleanser', 'lightweight_moisturizer']
        }
        
        # Add base categories for skin type
        base_categories = skin_type_categories.get(skin_type, ['gentle_cleanser'])
        
        for category in base_categories:
            if category in self.product_categories:
                product_info = self.product_categories[category].copy()
                product_info['category'] = category
                recommended_products.append(product_info)
        
        # Add concern-specific categories
        concern_categories = {
            'acne': ['acne_cleanser', 'acne_treatment'],
            'hyperpigmentation': ['brightening_serum'],
            'redness': ['calming_serum'],
            'sensitivity': ['calming_serum', 'barrier_repair']
        }
        
        for concern in primary_concerns:
            if concern in concern_categories:
                for category in concern_categories[concern]:
                    if category in self.product_categories:
                        product_info = self.product_categories[category].copy()
                        product_info['category'] = category
                        recommended_products.append(product_info)
        
        return recommended_products
    
    def _create_personalized_recommendations(self,
                                           skin_type: str,
                                           primary_concerns: List[str],
                                           ingredient_recs: Dict[str, Any],
                                           product_recs: List[Dict[str, Any]],
                                           similar_results: List[Tuple[str, float]]) -> List[str]:
        """Create personalized advice based on analysis"""
        
        advice = []
        
        # Add skin type specific advice
        type_advice = {
            'Oily': 'Focus on oil-free products and gentle cleansing',
            'Dry': 'Prioritize hydration and barrier repair ingredients',
            'Sensitive': 'Choose fragrance-free products and patch test new items',
            'Combination': 'Use different products for different areas of your face'
        }
        
        if skin_type in type_advice:
            advice.append(type_advice[skin_type])
        
        # Add concern-specific advice
        concern_advice = {
            'acne': 'Use non-comedogenic products and avoid touching your face',
            'dryness': 'Apply moisturizer while skin is still damp',
            'redness': 'Avoid hot water and harsh ingredients',
            'hyperpigmentation': 'Use sunscreen daily and be patient with brightening ingredients',
            'sensitivity': 'Introduce new products slowly and one at a time'
        }
        
        for concern in primary_concerns:
            if concern in concern_advice:
                advice.append(concern_advice[concern])
        
        # Add data-driven advice
        if similar_results:
            confidence = self._calculate_confidence(similar_results)
            if confidence > 0.7:
                advice.append(f'Based on {len(similar_results)} similar skin profiles with high confidence')
            else:
                advice.append(f'Based on {len(similar_results)} similar skin profiles')
        
        return advice
    
    def _calculate_confidence(self, similar_results: List[Tuple[str, float]]) -> float:
        """Calculate confidence score based on similarity results"""
        if not similar_results:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(score for _, score in similar_results) / len(similar_results)
        
        # Boost confidence if we have more similar profiles
        profile_boost = min(len(similar_results) / 5.0, 1.0)
        
        return min(avg_similarity * profile_boost, 1.0)
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return True 