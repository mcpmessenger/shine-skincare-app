#!/usr/bin/env python3
"""
☠️ Operation Skully Backend Service Test
Validates that all critical fixes are working correctly
"""

import sys
import os
import json
import requests
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

def test_product_matching_service():
    """☠️ Test the ProductMatchingService"""
    print("☠️ Testing ProductMatchingService...")
    
    try:
        from app.services.product_matching_service import ProductMatchingService
        
        # Initialize service
        service = ProductMatchingService()
        
        # Test ingredient matching
        test_ingredients = ["hyaluronic_acid", "niacinamide", "ceramides"]
        products = service.match_products_to_ingredients(test_ingredients)
        
        print(f"☠️ Found {len(products)} matching products")
        
        # Verify product structure
        if products:
            product = products[0]
            required_attrs = ['id', 'name', 'brand', 'price', 'match_score', 'matching_ingredients']
            missing_attrs = [attr for attr in required_attrs if not hasattr(product, attr)]
            
            if missing_attrs:
                print(f"❌ Missing attributes: {missing_attrs}")
                return False
            else:
                print(f"✅ Product structure valid: {product.name} (Match: {product.match_score:.2f})")
                return True
        else:
            print("❌ No products found")
            return False
            
    except Exception as e:
        print(f"❌ ProductMatchingService test failed: {e}")
        return False

def test_ingredient_based_recommendations():
    """☠️ Test the IngredientBasedRecommendations service"""
    print("☠️ Testing IngredientBasedRecommendations...")
    
    try:
        from app.services.ingredient_based_recommendations import IngredientBasedRecommendations
        
        # Initialize service
        service = IngredientBasedRecommendations()
        
        # Mock similar results and conditions
        similar_results = [("profile_1", 0.85), ("profile_2", 0.72)]
        conditions_data = {"acne": 0.6, "dryness": 0.3}
        skin_type = "Combination"
        
        # Get recommendations
        recommendations = service.get_recommendations_from_similar_profiles(
            similar_results, conditions_data, skin_type
        )
        
        # Verify response structure
        required_keys = ['recommended_ingredients', 'personalized_advice', 'confidence_score']
        missing_keys = [key for key in required_keys if key not in recommendations]
        
        if missing_keys:
            print(f"❌ Missing keys in recommendations: {missing_keys}")
            return False
        else:
            print(f"✅ Recommendations generated successfully (Confidence: {recommendations.get('confidence_score', 0):.2f})")
            return True
            
    except Exception as e:
        print(f"❌ IngredientBasedRecommendations test failed: {e}")
        return False

def test_enhanced_analysis_integration():
    """☠️ Test the enhanced analysis integration"""
    print("☠️ Testing Enhanced Analysis Integration...")
    
    try:
        from app.enhanced_skin_analysis.routes import _process_enhanced_analysis
        
        # Mock data
        vectorization_result = {
            'status': 'success',
            'vector': [0.1, 0.2, 0.3],
            'skin_conditions': {
                'conditions': {'acne': 0.6, 'dryness': 0.3},
                'primary_condition': 'acne',
                'confidence': 0.85
            }
        }
        
        similar_results = [("profile_1", 0.85), ("profile_2", 0.72)]
        user_id = "test_user"
        
        # Process analysis
        result = _process_enhanced_analysis(vectorization_result, similar_results, user_id)
        
        # Verify result structure
        required_keys = ['status', 'analysis_id', 'products', 'ingredient_analysis']
        missing_keys = [key for key in required_keys if key not in result]
        
        if missing_keys:
            print(f"❌ Missing keys in analysis result: {missing_keys}")
            return False
        else:
            print(f"✅ Analysis integration successful (Products: {len(result.get('products', []))})")
            return True
            
    except Exception as e:
        print(f"❌ Enhanced analysis integration test failed: {e}")
        return False

def test_flask_app_initialization():
    """☠️ Test Flask app initialization"""
    print("☠️ Testing Flask App Initialization...")
    
    try:
        from app import create_app
        
        # Create app
        app = create_app()
        
        # Test basic app properties
        if hasattr(app, 'config') and app.config.get('MAX_CONTENT_LENGTH') == 100 * 1024 * 1024:
            print("✅ Flask app initialized with correct file size limit")
            return True
        else:
            print("❌ Flask app missing required configuration")
            return False
            
    except Exception as e:
        print(f"❌ Flask app initialization test failed: {e}")
        return False

def run_all_tests():
    """☠️ Run all Operation Skully tests"""
    print("☠️ Operation Skully: Starting Backend Service Tests")
    print("=" * 50)
    
    tests = [
        test_flask_app_initialization,
        test_product_matching_service,
        test_ingredient_based_recommendations,
        test_enhanced_analysis_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"☠️ Operation Skully Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Operation Skully backend is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 