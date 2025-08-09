#!/usr/bin/env python3
"""
Test script for face detection
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

def test_face_detection():
    """Test the face detection endpoint"""
    print("🧪 Testing face detection...")

    # Create test image
    img = create_test_image()
    _, buffer = cv2.imencode('.jpg', img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    # Test data
    test_data = {
        "image_data": img_b64,
        "confidence_threshold": 0.3  # Lower threshold for testing
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
            print(f"✅ V3 Face Detection Response:")
            print(f"   Success: {result.get('success', False)}")
            print(f"   Faces Detected: {result.get('faces_detected', 0)}")
            print(f"   Method: {result.get('method', 'unknown')}")

            if result.get('faces'):
                for i, face in enumerate(result['faces']):
                    print(f"   Face {i+1}: Box={face.get('box')}, Confidence={face.get('confidence', 0):.3f}")
            else:
                print("   No faces detected in the test image")
        else:
            print(f"❌ V3 Face Detection failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error testing face detection: {e}")

def test_face_detection_direct():
    """Test face detection directly without API"""
    print("\n🔍 Testing face detection directly...")
    
    try:
        # Import the face detection module directly
        from advanced_face_detection import detect_faces_advanced
        
        # Create test image
        img = create_test_image()
        _, buffer = cv2.imencode('.jpg', img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        # Test direct function call
        results = detect_faces_advanced(img_b64, confidence_threshold=0.3)
        
        print(f"Direct Face Detection Results:")
        print(f"   Success: {results.get('success', False)}")
        print(f"   Faces Detected: {results.get('faces_detected', 0)}")
        print(f"   Method: {results.get('method', 'unknown')}")
        
        if results.get('faces'):
            for i, face in enumerate(results['faces']):
                print(f"   Face {i+1}: Box={face.get('box')}, Confidence={face.get('confidence', 0):.3f}")
        else:
            print("   No faces detected in direct test")
            
    except Exception as e:
        print(f"❌ Error in direct face detection test: {e}")

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")

    try:
        response = requests.get("http://localhost:5000/health", timeout=5)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Check Response:")
            print(f"   Status: {result.get('status')}")
            print(f"   Version: {result.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error testing health: {e}")

if __name__ == "__main__":
    print("🚀 Starting face detection tests...")
    test_health()
    print()
    test_face_detection()
    print()
    test_face_detection_direct()
    print("\n✅ Face detection tests completed!") 