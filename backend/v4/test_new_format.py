#!/usr/bin/env python3
"""
Test the new response format from V3 skin analysis endpoint
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

def test_new_format():
    """Test the new response format"""
    print("🧪 Testing new response format...")
    
    # Create test image
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    
    try:
        # Test the V3 skin analysis endpoint
        response = requests.post(
            "http://localhost:5000/api/v3/skin/analyze-real",
            json={
                "image_data": img_b64,
                "user_demographics": {
                    "age_category": "25-35",
                    "race_category": "caucasian"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received successfully")
            print(f"📊 Status: {result.get('status', 'NOT FOUND')}")
            print(f"📋 Response keys: {list(result.keys())}")
            
            # Check for expected fields
            expected_fields = ['status', 'face_detection', 'skin_analysis', 'similarity_search', 'recommendations']
            for field in expected_fields:
                if field in result:
                    print(f"   ✅ {field}: Found")
                else:
                    print(f"   ❌ {field}: Missing")
            
            # Check face detection
            if 'face_detection' in result:
                fd = result['face_detection']
                print(f"   📊 Face detection: {fd.get('detected', False)}")
                print(f"   📈 Confidence: {fd.get('confidence', 0)}")
            
            # Check skin analysis
            if 'skin_analysis' in result:
                sa = result['skin_analysis']
                print(f"   🧬 Health score: {sa.get('overall_health_score', 0)}")
                print(f"   🎯 Texture: {sa.get('texture', 'unknown')}")
                print(f"   📊 Analysis confidence: {sa.get('analysis_confidence', 0)}")
            
            # Check recommendations
            if 'recommendations' in result:
                recs = result['recommendations']
                print(f"   💡 Immediate care: {len(recs.get('immediate_care', []))} items")
                print(f"   📋 Long term care: {len(recs.get('long_term_care', []))} items")
            
            print(f"\n📄 Full response structure:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_new_format() 