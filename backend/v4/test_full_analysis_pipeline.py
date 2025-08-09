#!/usr/bin/env python3
"""
Test the full analysis pipeline end-to-end
Simulates frontend behavior
"""

import requests
import base64
import cv2
import numpy as np
import json

def create_test_image():
    """Create a test image with a face-like shape"""
    # Create a 600x600 image
    img = np.zeros((600, 600, 3), dtype=np.uint8)
    
    # Draw a face-like oval
    cv2.ellipse(img, (300, 300), (200, 250), 0, 0, 360, (255, 255, 255), -1)
    
    # Draw eyes
    cv2.circle(img, (250, 250), 20, (0, 0, 0), -1)
    cv2.circle(img, (350, 250), 20, (0, 0, 0), -1)
    
    # Draw nose
    cv2.ellipse(img, (300, 300), (10, 20), 0, 0, 360, (0, 0, 0), -1)
    
    # Draw mouth
    cv2.ellipse(img, (300, 380), (30, 15), 0, 0, 180, (0, 0, 0), 3)
    
    return img

def test_full_analysis_pipeline():
    """Test the complete analysis pipeline"""
    print("🚀 Testing full analysis pipeline...")
    
    # Step 1: Create test image
    print("\n1️⃣ Creating test image...")
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    print(f"   ✅ Test image created: {img.shape}")
    
    # Step 2: Test face detection endpoint
    print("\n2️⃣ Testing face detection endpoint...")
    try:
        face_response = requests.post(
            "http://localhost:5000/api/v3/face/detect",
            json={
                "image_data": img_b64,
                "confidence_threshold": 0.3
            },
            timeout=10
        )
        
        if face_response.status_code == 200:
            face_result = face_response.json()
            print(f"   ✅ Face detection successful: {face_result.get('faces_detected', 0)} faces")
            if face_result.get('faces'):
                face = face_result['faces'][0]
                print(f"   📊 Face confidence: {face.get('confidence', 0)}")
                print(f"   📦 Face bounds: {face.get('box', [])}")
        else:
            print(f"   ❌ Face detection failed: {face_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Face detection error: {e}")
        return
    
    # Step 3: Test full skin analysis endpoint
    print("\n3️⃣ Testing full skin analysis endpoint...")
    try:
        analysis_response = requests.post(
            "http://localhost:5000/api/v3/skin/analyze-real",
            json={
                "image_data": img_b64,
                "user_demographics": {
                    "age_category": "25-35",
                    "race_category": "caucasian"
                }
            },
            timeout=30  # Longer timeout for comprehensive analysis
        )
        
        if analysis_response.status_code == 200:
            analysis_result = analysis_response.json()
            print(f"   ✅ Analysis successful: {analysis_result.get('success', False)}")
            
            # Check face detection data
            if 'face_detection' in analysis_result:
                face_detection = analysis_result['face_detection']
                print(f"   📊 Face detection: {face_detection.get('detected', False)}")
                print(f"   📈 Confidence: {face_detection.get('confidence', 0)}")
            
            # Check analysis data
            if 'analysis' in analysis_result:
                analysis_data = analysis_result['analysis']
                print(f"   🧬 Skin type: {analysis_data.get('skin_type', 'unknown')}")
                print(f"   🎯 Concerns: {analysis_data.get('concerns', [])}")
                print(f"   📋 Summary: {analysis_data.get('analysis_summary', 'No summary')}")
                print(f"   💡 Recommendations: {len(analysis_data.get('top_recommendations', []))} items")
            
            # Check version
            print(f"   🔢 Version: {analysis_result.get('version', 'unknown')}")
            
        else:
            print(f"   ❌ Analysis failed: {analysis_response.status_code}")
            print(f"   📄 Response: {analysis_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
        return
    
    # Step 4: Verify the analysis is comprehensive
    print("\n4️⃣ Verifying comprehensive analysis...")
    try:
        # Test the V4 comprehensive endpoint directly
        comprehensive_response = requests.post(
            "http://localhost:5000/api/v4/skin/analyze-comprehensive",
            json={
                "image": img_b64,
                "age": "25-35",
                "ethnicity": "caucasian"
            },
            timeout=30
        )
        
        if comprehensive_response.status_code == 200:
            comprehensive_result = comprehensive_response.json()
            print(f"   ✅ Comprehensive analysis successful: {comprehensive_result.get('success', False)}")
            
            # Check all components
            components = ['face_detection', 'embeddings', 'skin_analysis', 'bias_evaluation', 'recommendations']
            for component in components:
                if component in comprehensive_result:
                    component_data = comprehensive_result[component]
                    success = component_data.get('success', False)
                    print(f"   📊 {component}: {'✅' if success else '❌'}")
                else:
                    print(f"   📊 {component}: ❌ (missing)")
        else:
            print(f"   ❌ Comprehensive analysis failed: {comprehensive_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Comprehensive analysis error: {e}")
    
    print("\n✅ Full analysis pipeline test completed!")

if __name__ == "__main__":
    test_full_analysis_pipeline() 