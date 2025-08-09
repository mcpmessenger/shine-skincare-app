#!/usr/bin/env python3
"""
Test script to check face detection response format
"""

import cv2
import numpy as np
import base64
import requests
import json

def create_test_image():
    """Create a more realistic test image with better face-like features"""
    # Create a larger image
    img = np.ones((640, 640, 3), dtype=np.uint8) * 128
    
    # Create a more realistic face structure
    # Head outline (oval)
    cv2.ellipse(img, (320, 320), (200, 250), 0, 0, 360, (200, 200, 200), -1)
    
    # Eyes (more realistic)
    cv2.ellipse(img, (250, 250), (30, 20), 0, 0, 360, (255, 255, 255), -1)  # Left eye
    cv2.ellipse(img, (390, 250), (30, 20), 0, 0, 360, (255, 255, 255), -1)  # Right eye
    cv2.circle(img, (250, 250), 10, (0, 0, 0), -1)  # Left pupil
    cv2.circle(img, (390, 250), 10, (0, 0, 0), -1)  # Right pupil
    
    # Nose
    cv2.ellipse(img, (320, 320), (15, 25), 0, 0, 360, (180, 180, 180), -1)
    
    # Mouth (more realistic)
    cv2.ellipse(img, (320, 400), (60, 30), 0, 0, 180, (100, 100, 100), -1)
    
    # Add some shading to make it more realistic
    cv2.ellipse(img, (320, 200), (150, 200), 0, 0, 360, (150, 150, 150), 2)
    
    return img

def test_face_detection_format():
    """Test the face detection endpoint and check response format"""
    print("🧪 Testing face detection response format...")

    # Create test image
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    # Test data
    test_data = {
        "image_data": img_b64,
        "confidence_threshold": 0.3
    }

    try:
        # Test V3 endpoint
        print("Testing V3 face detection endpoint...")
        response = requests.post(
            "http://localhost:5000/api/v3/face/detect",
            json=test_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ V3 Face Detection Response Format:")
            print(f"   Full response: {json.dumps(result, indent=2)}")
            
            # Check what fields are available
            print(f"\n📋 Response field analysis:")
            print(f"   success: {result.get('success', 'NOT FOUND')}")
            print(f"   faces_detected: {result.get('faces_detected', 'NOT FOUND')}")
            print(f"   method: {result.get('method', 'NOT FOUND')}")
            print(f"   version: {result.get('version', 'NOT FOUND')}")
            
            if 'faces' in result:
                print(f"   faces array: {len(result['faces'])} faces")
                for i, face in enumerate(result['faces']):
                    print(f"     Face {i+1}: {face}")
            else:
                print(f"   faces: NOT FOUND")
                
            # Check if this matches frontend expectations
            print(f"\n🔍 Frontend compatibility check:")
            expected_fields = ['success', 'faces_detected', 'faces']
            missing_fields = [field for field in expected_fields if field not in result]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All expected fields present")
                
            # Check face detection structure
            if result.get('faces') and len(result['faces']) > 0:
                face = result['faces'][0]
                expected_face_fields = ['box', 'confidence']
                missing_face_fields = [field for field in expected_face_fields if field not in face]
                
                if missing_face_fields:
                    print(f"   ❌ Missing face fields: {missing_face_fields}")
                else:
                    print(f"   ✅ Face structure is correct")
                    print(f"   📊 Face confidence: {face.get('confidence', 'N/A')}")
                    print(f"   📦 Face box: {face.get('box', 'N/A')}")
            else:
                print(f"   ⚠️ No faces detected or faces array is empty")
                
        else:
            print(f"❌ V3 Face Detection failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error testing face detection format: {e}")

def test_skin_analysis_with_face_detection():
    """Test the skin analysis endpoint to check if it includes face detection data"""
    print("\n🧪 Testing skin analysis with face detection...")

    # Create test image
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    # Test data
    test_data = {
        "image_data": img_b64,
        "user_demographics": {
            "age_category": "25-35",
            "race_category": "caucasian"
        }
    }

    try:
        # Test V3 skin analysis endpoint
        print("Testing V3 skin analysis endpoint...")
        response = requests.post(
            "http://localhost:5000/api/v3/skin/analyze-real",
            json=test_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ V3 Skin Analysis Response:")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Version: {result.get('version', 'NOT FOUND')}")
            
            # Check for face detection data
            if 'face_detection' in result:
                face_detection = result['face_detection']
                print(f"   ✅ Face detection data found:")
                print(f"      Detected: {face_detection.get('detected', False)}")
                print(f"      Confidence: {face_detection.get('confidence', 0)}")
                print(f"      Face bounds: {face_detection.get('face_bounds', {})}")
            else:
                print(f"   ❌ No face detection data in response")
            
            # Check for analysis data
            if 'analysis' in result:
                print(f"   ✅ Analysis data found")
            else:
                print(f"   ❌ No analysis data in response")
                
        else:
            print(f"❌ V3 Skin Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error testing skin analysis: {e}")

def test_simple_face_detection():
    """Test just face detection without full skin analysis"""
    print("\n🧪 Testing simple face detection...")

    # Create test image
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    try:
        # Test direct face detection
        print("Testing direct face detection...")
        response = requests.post(
            "http://localhost:5000/api/v3/face/detect",
            json={
                "image_data": img_b64,
                "confidence_threshold": 0.3
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct Face Detection Response:")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Faces Detected: {result.get('faces_detected', 0)}")
            print(f"   Method: {result.get('method', 'unknown')}")
            
            if result.get('faces') and len(result['faces']) > 0:
                face = result['faces'][0]
                print(f"   Face Box: {face.get('box', [])}")
                print(f"   Face Confidence: {face.get('confidence', 0)}")
                
                # Test if we can create the face detection data format
                face_detection_data = {
                    'detected': True,
                    'confidence': face.get('confidence', 0),
                    'face_bounds': {
                        'x': face['box'][0],
                        'y': face['box'][1],
                        'width': face['box'][2],
                        'height': face['box'][3]
                    }
                }
                print(f"   ✅ Face detection data format: {face_detection_data}")
            else:
                print(f"   ❌ No faces detected")
        else:
            print(f"❌ Direct face detection failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error in simple face detection test: {e}")

if __name__ == "__main__":
    print("🚀 Starting face detection format tests...")
    test_face_detection_format()
    test_simple_face_detection()
    test_skin_analysis_with_face_detection()
    print("\n✅ Face detection format tests completed!") 