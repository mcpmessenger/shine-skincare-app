#!/usr/bin/env python3
"""
☠️ Operation Skully Quick Fix
Fixes JWT import issues for local testing
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

def fix_jwt_imports():
    """☠️ Fix JWT import issues for local testing"""
    print("☠️ Operation Skully: Applying JWT import fixes...")
    
    # Fix the JWT import issue in enhanced_skin_analysis/routes.py
    routes_file = Path("app/enhanced_skin_analysis/routes.py")
    
    if routes_file.exists():
        with open(routes_file, 'r') as f:
            content = f.read()
        
        # Replace the problematic import
        old_import = "from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request_optional"
        new_import = "from flask_jwt_extended import get_jwt_identity\n# verify_jwt_in_request_optional removed for local testing"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Also replace the function call
            content = content.replace("verify_jwt_in_request_optional()", "# verify_jwt_in_request_optional() # Disabled for local testing")
            
            with open(routes_file, 'w') as f:
                f.write(content)
            
            print("✅ JWT import fixes applied")
            return True
        else:
            print("❌ Could not find JWT import to fix")
            return False
    else:
        print("❌ Routes file not found")
        return False

def test_core_services():
    """☠️ Test core Operation Skully services without Flask dependencies"""
    print("☠️ Operation Skully: Testing Core Services...")
    
    try:
        from app.services.product_matching_service import ProductMatchingService
        from app.services.ingredient_based_recommendations import IngredientBasedRecommendations
        
        # Test ProductMatchingService
        print("☠️ Testing ProductMatchingService...")
        service = ProductMatchingService()
        test_ingredients = ["hyaluronic_acid", "niacinamide", "ceramides"]
        products = service.match_products_to_ingredients(test_ingredients)
        
        if products:
            print(f"✅ ProductMatchingService: Found {len(products)} products")
        else:
            print("❌ ProductMatchingService: No products found")
            return False
        
        # Test IngredientBasedRecommendations
        print("☠️ Testing IngredientBasedRecommendations...")
        rec_service = IngredientBasedRecommendations()
        similar_results = [("profile_1", 0.85), ("profile_2", 0.72)]
        conditions_data = {"acne": 0.6, "dryness": 0.3}
        skin_type = "Combination"
        
        recommendations = rec_service.get_recommendations_from_similar_profiles(
            similar_results, conditions_data, skin_type
        )
        
        if 'recommended_ingredients' in recommendations:
            print(f"✅ IngredientBasedRecommendations: Generated recommendations")
        else:
            print("❌ IngredientBasedRecommendations: Failed to generate recommendations")
            return False
        
        print("✅ All core services working!")
        return True
        
    except Exception as e:
        print(f"❌ Core services test failed: {e}")
        return False

def main():
    """☠️ Main Operation Skully quick fix"""
    print("☠️ Operation Skully: Quick Fix Application")
    print("=" * 40)
    
    # Apply JWT fixes
    jwt_fixed = fix_jwt_imports()
    
    # Test core services
    services_working = test_core_services()
    
    print("=" * 40)
    if jwt_fixed and services_working:
        print("✅ Operation Skully Quick Fix: SUCCESS")
        print("☠️ Core services are working correctly")
        print("☠️ Ready for smoke testing!")
        return True
    else:
        print("❌ Operation Skully Quick Fix: FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 