#!/usr/bin/env python3
"""
Railway Deployment Test Script
Tests the deployed Railway backend to ensure all services are working
"""

import requests
import json
import sys
from io import BytesIO
from PIL import Image
import time

def test_railway_deployment(base_url):
    """Test Railway deployment endpoints"""
    
    print(f"Testing Railway deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Mode: {health_data.get('mode')}")
            print(f"   Version: {health_data.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ Root endpoint passed")
            print(f"   Message: {root_data.get('message')}")
            print(f"   Mode: {root_data.get('mode')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Enhanced health check
    print("\n3. Testing enhanced health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/enhanced/health/enhanced", timeout=10)
        if response.status_code == 200:
            enhanced_data = response.json()
            print(f"✅ Enhanced health check passed")
            print(f"   Status: {enhanced_data.get('status')}")
            services = enhanced_data.get('services', {})
            for service, status in services.items():
                print(f"   {service}: {'✅' if status else '❌'}")
        else:
            print(f"❌ Enhanced health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced health check error: {e}")
    
    # Test 4: Image Analysis (with test image)
    print("\n4. Testing image analysis endpoint...")
    try:
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='pink')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        files = {'image': ('test.jpg', img_buffer, 'image/jpeg')}
        data = {'ethnicity': 'Mixed'}
        
        response = requests.post(
            f"{base_url}/api/v2/analyze/guest", 
            files=files, 
            data=data, 
            timeout=30
        )
        
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"✅ Image analysis passed")
            if analysis_data.get('success'):
                analysis = analysis_data.get('data', {}).get('analysis', {})
                print(f"   Skin Type: {analysis.get('skinType')}")
                print(f"   Confidence: {analysis.get('confidence')}")
                print(f"   Mode: {analysis.get('mode')}")
            else:
                print(f"   Analysis failed: {analysis_data.get('error')}")
        else:
            print(f"❌ Image analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
    
    print("\n" + "=" * 50)
    print("Deployment test completed!")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_railway_deployment.py <railway_url>")
        print("Example: python test_railway_deployment.py https://your-app.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    test_railway_deployment(base_url)

if __name__ == "__main__":
    main()