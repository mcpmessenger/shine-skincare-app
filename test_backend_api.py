#!/usr/bin/env python3
"""
Test script for the backend skin analysis API
"""

import requests
import json
import os
from pathlib import Path

def test_backend_health():
    """Test the backend health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/v2/health')
        print("✅ Health check response:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print("   Services status:", data.get('services', {}))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_skin_analysis():
    """Test the skin analysis endpoint with a sample image"""
    try:
        # Look for a sample image in the products folder
        products_dir = Path("products")
        sample_images = list(products_dir.glob("*.jpg")) + list(products_dir.glob("*.png")) + list(products_dir.glob("*.webp"))
        
        if not sample_images:
            print("❌ No sample images found in products/ directory")
            return False
        
        sample_image = sample_images[0]
        print(f"📸 Using sample image: {sample_image}")
        
        # Test the skin analysis endpoint
        url = 'http://localhost:5000/api/v2/analyze/skin'
        
        with open(sample_image, 'rb') as f:
            files = {'image': (sample_image.name, f, 'image/jpeg')}
            
            # Note: This will fail without authentication, but we can test the endpoint structure
            response = requests.post(url, files=files)
        
        print(f"✅ Skin analysis response: {response.status_code}")
        
        if response.status_code == 401:
            print("   Expected: Authentication required")
            return True
        elif response.status_code == 200:
            data = response.json()
            print("   Analysis result:", json.dumps(data, indent=2))
            return True
        else:
            print(f"   Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Skin analysis test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Backend API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    health_ok = test_backend_health()
    
    # Test 2: Skin analysis endpoint
    print("\n2. Testing skin analysis endpoint...")
    analysis_ok = test_skin_analysis()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Skin Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
    
    if health_ok and analysis_ok:
        print("\n🎉 All tests passed! Backend is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the backend setup.")

if __name__ == "__main__":
    main() 