#!/usr/bin/env python3
"""
☠️ Operation Skully Simple Smoke Test
Tests core services without complex dependencies
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

def test_product_matching():
    """☠️ Test ProductMatchingService"""
    print("☠️ Testing ProductMatchingService...")
    
    try:
        from app.services.product_matching_service import ProductMatchingService
        
        service = ProductMatchingService()
        test_ingredients = ["hyaluronic_acid", "niacinamide", "ceramides"]
        products = service.match_products_to_ingredients(test_ingredients)
        
        if products:
            print(f"✅ Found {len(products)} matching products")
            print(f"✅ Top match: {products[0].name} (Score: {products[0].match_score:.2f})")
            return True
        else:
            print("❌ No products found")
            return False
            
    except Exception as e:
        print(f"❌ ProductMatchingService failed: {e}")
        return False

def test_ingredient_recommendations():
    """☠️ Test IngredientBasedRecommendations"""
    print("☠️ Testing IngredientBasedRecommendations...")
    
    try:
        from app.services.ingredient_based_recommendations import IngredientBasedRecommendations
        
        service = IngredientBasedRecommendations()
        similar_results = [("profile_1", 0.85), ("profile_2", 0.72)]
        conditions_data = {"acne": 0.6, "dryness": 0.3}
        skin_type = "Combination"
        
        recommendations = service.get_recommendations_from_similar_profiles(
            similar_results, conditions_data, skin_type
        )
        
        if 'recommended_ingredients' in recommendations:
            print(f"✅ Generated recommendations (Confidence: {recommendations.get('confidence_score', 0):.2f})")
            return True
        else:
            print("❌ Failed to generate recommendations")
            return False
            
    except Exception as e:
        print(f"❌ IngredientBasedRecommendations failed: {e}")
        return False

def test_analysis_id_generation():
    """☠️ Test analysis ID generation"""
    print("☠️ Testing Analysis ID Generation...")
    
    try:
        import uuid
        
        # Generate a test analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Test localStorage key format
        storage_key = f"analysis_{analysis_id}"
        
        print(f"✅ Generated analysis ID: {analysis_id}")
        print(f"✅ Storage key format: {storage_key}")
        return True
        
    except Exception as e:
        print(f"❌ Analysis ID generation failed: {e}")
        return False

def test_url_encoding():
    """☠️ Test URL encoding for analysis ID"""
    print("☠️ Testing URL Encoding...")
    
    try:
        import urllib.parse
        
        test_analysis_id = "test-analysis-id-123"
        encoded_id = urllib.parse.quote(test_analysis_id)
        decoded_id = urllib.parse.unquote(encoded_id)
        
        print(f"✅ Original: {test_analysis_id}")
        print(f"✅ Encoded: {encoded_id}")
        print(f"✅ Decoded: {decoded_id}")
        
        if decoded_id == test_analysis_id:
            print("✅ URL encoding/decoding working correctly")
            return True
        else:
            print("❌ URL encoding/decoding failed")
            return False
            
    except Exception as e:
        print(f"❌ URL encoding test failed: {e}")
        return False

def main():
    """☠️ Run all simple Operation Skully tests"""
    print("☠️ Operation Skully: Simple Smoke Test")
    print("=" * 40)
    
    tests = [
        test_product_matching,
        test_ingredient_recommendations,
        test_analysis_id_generation,
        test_url_encoding
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
    
    print("=" * 40)
    print(f"☠️ Operation Skully Simple Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All core Operation Skully functionality working!")
        print("☠️ Ready for deployment!")
        return True
    else:
        print("❌ Some core functionality needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 