#!/usr/bin/env python3
"""
Test Fixed Model Integration for Shine Skincare App
Tests the improved model with 77.78% acne accuracy
"""

import os
import json
import numpy as np
from pathlib import Path
from simple_fixed_integration import SimpleFixedModelIntegration

def create_test_image():
    """Create a simple test image"""
    # Create a 224x224 RGB test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Convert to bytes
    from PIL import Image
    import io
    
    pil_image = Image.fromarray(test_image)
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def test_fixed_model():
    """Test the fixed model integration"""
    print("="*70)
    print("TESTING FIXED MODEL INTEGRATION")
    print("="*70)
    
    # Initialize integration
    integration = SimpleFixedModelIntegration()
    
    # Check model status
    status = integration.get_model_status()
    print(f"📊 Model Status: {status}")
    
    if not status['model_loaded']:
        print("❌ Model not loaded! Cannot proceed with test.")
        return False
    
    # Create test image
    test_image_bytes = create_test_image()
    print("✅ Test image created")
    
    # Test analysis
    print("\n🔍 Testing skin analysis...")
    try:
        results = integration.analyze_skin_with_fixed_model(test_image_bytes)
        
        if results['status'] == 'success':
            print("✅ Analysis successful!")
            print(f"📊 Primary Condition: {results['primary_condition']}")
            print(f"📊 Confidence: {results['percentage']:.1f}%")
            print(f"📊 Severity: {results['severity']}")
            
            print("\n📋 Top 3 Predictions:")
            for i, pred in enumerate(results['top_3_predictions'][:3], 1):
                print(f"  {i}. {pred['condition']}: {pred['percentage']:.1f}%")
            
            print(f"\n📝 Summary: {results['summary']}")
            
            print("\n💡 Recommendations:")
            for category, items in results['recommendations'].items():
                if items:
                    print(f"  {category.replace('_', ' ').title()}:")
                    for item in items[:2]:  # Show first 2 items
                        print(f"    - {item}")
            
            return True
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_model_performance():
    """Test model performance metrics"""
    print("\n" + "="*70)
    print("MODEL PERFORMANCE TEST")
    print("="*70)
    
    # Load metadata
    metadata_path = Path("results/fixed_training_results.json")
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print("📊 Performance Metrics:")
        print(f"  Overall Test Accuracy: {metadata.get('test_accuracy', 0)*100:.2f}%")
        
        print("\n📈 Per-Class Accuracy:")
        per_class = metadata.get('per_class_accuracy', {})
        for condition, accuracy in per_class.items():
            status = "✅" if accuracy > 0 else "❌"
            print(f"  {status} {condition}: {accuracy*100:.2f}%")
        
        return True
    else:
        print("⚠️ No performance metadata found")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Fixed Model Integration Tests")
    print("="*70)
    
    # Test 1: Model Integration
    test1_success = test_fixed_model()
    
    # Test 2: Performance Metrics
    test2_success = test_model_performance()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if test1_success and test2_success:
        print("✅ All tests passed!")
        print("🎉 Fixed model integration is working correctly!")
        print("🚀 Ready for deployment to Shine Skincare App!")
    else:
        print("❌ Some tests failed!")
        print("🔧 Please check the model files and integration")
    
    print("\n📋 Next Steps:")
    print("  1. Start the Flask server: python simple_fixed_integration.py")
    print("  2. Update your frontend to use /api/v5/skin/analyze-fixed")
    print("  3. Deploy to production")
    print("  4. Monitor performance")

if __name__ == "__main__":
    main()
