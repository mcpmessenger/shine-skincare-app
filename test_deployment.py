#!/usr/bin/env python3
"""
SCIN Integration Deployment Test

This script tests the SCIN integration to ensure it's ready for deployment.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_scin_integration():
    """Test the SCIN integration components"""
    print("🧪 Testing SCIN Integration for Deployment")
    print("=" * 50)
    
    try:
        # Test 1: Import SCIN services
        print("1. Testing imports...")
        from app.services.scin_dataset_service import SCINDatasetService
        from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
        from app.services.scin_integration_manager import SCINIntegrationManager
        print("   ✅ All SCIN services imported successfully")
        
        # Test 2: Initialize services
        print("2. Testing service initialization...")
        scin_service = SCINDatasetService()
        vectorization_service = EnhancedImageVectorizationService()
        integration_manager = SCINIntegrationManager()
        print("   ✅ All services initialized successfully")
        
        # Test 3: Load dataset
        print("3. Testing dataset loading...")
        if scin_service.load_metadata():
            record_count = len(scin_service.merged_df) if scin_service.merged_df is not None else 0
            print(f"   ✅ Dataset loaded successfully: {record_count} records")
        else:
            print("   ❌ Failed to load dataset")
            return False
        
        # Test 4: Test vectorization service
        print("4. Testing vectorization service...")
        if vectorization_service.is_available():
            print("   ✅ Vectorization service ready")
        else:
            print("   ❌ Vectorization service not available")
            return False
        
        # Test 5: Test integration manager
        print("5. Testing integration manager...")
        # Load metadata first
        integration_manager.scin_service.load_metadata()
        print("   ✅ Integration manager initialized")
        
        # Test 6: Test Flask app
        print("6. Testing Flask app...")
        from app import create_app
        app = create_app()
        print("   ✅ Flask app created successfully")
        
        print("\n🎉 All tests passed! SCIN integration is ready for deployment.")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main function"""
    if test_scin_integration():
        print("\n✅ SCIN Integration Deployment Test: PASSED")
        print("🚀 Ready to deploy to GitHub and Vercel!")
        return 0
    else:
        print("\n❌ SCIN Integration Deployment Test: FAILED")
        print("🔧 Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 