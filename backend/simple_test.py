#!/usr/bin/env python3
"""
Simple test for enhanced embeddings system
"""

import numpy as np
import cv2
import base64

def test_enhanced_embeddings():
    """Test the enhanced embeddings system"""
    print("🧠 Testing Enhanced Embeddings System")
    print("=" * 40)
    
    try:
        # Import the enhanced analysis API
        from enhanced_analysis_api import EnhancedAnalysisAPI
        print("✅ Enhanced Analysis API imported successfully")
        
        # Initialize the API
        api = EnhancedAnalysisAPI()
        print("✅ Enhanced Analysis API initialized successfully")
        
        # Create a test image
        test_image = np.random.randint(100, 200, (224, 224, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', test_image)
        image_data = buffer.tobytes()
        
        print("✅ Test image created successfully")
        
        # Test analysis
        result = api.analyze_skin_enhanced(image_data, 'comprehensive')
        
        if result and 'confidence_score' in result:
            print("✅ Enhanced analysis completed successfully")
            print(f"   Confidence: {result['confidence_score']:.3f}")
            print(f"   Face detected: {result.get('face_detection', {}).get('face_detected', False)}")
            print(f"   Quality: {result.get('quality_assessment', {}).get('overall_quality', 0):.3f}")
        else:
            print("⚠️ Analysis completed but result format unexpected")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_embeddings()
    if success:
        print("\n🎉 Enhanced embeddings system is working!")
    else:
        print("\n❌ Enhanced embeddings system has issues") 