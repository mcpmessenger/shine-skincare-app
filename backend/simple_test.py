#!/usr/bin/env python3
"""
Simple Backend Connection Test
"""

import requests
import time

def test_backend_connection():
    """Test if the backend is accessible"""
    print("🔍 Testing backend connection...")
    
    try:
        # Try to connect to the backend
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is accessible!")
            print(f"  Status: {data.get('status')}")
            print(f"  Operation: {data.get('operation')}")
            print(f"  Features: {data.get('features')}")
            return True
        else:
            print(f"❌ Backend responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend on localhost:5001")
        print("   Make sure the backend is running with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_analysis_endpoint():
    """Test the analysis endpoint"""
    print("\n🔍 Testing analysis endpoint...")
    
    try:
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        response = requests.post(
            'http://localhost:5001/api/v3/skin/analyze-enhanced',
            json={'image_data': test_image_data},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis endpoint is working!")
            print(f"  Status: {data.get('status')}")
            print(f"  Operation: {data.get('operation')}")
            return True
        else:
            print(f"❌ Analysis endpoint failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to analysis endpoint")
        return False
    except Exception as e:
        print(f"❌ Error testing analysis endpoint: {e}")
        return False

def main():
    """Main test function"""
    print("🧠 Backend Connection Test")
    print("=" * 40)
    
    # Test basic connection
    connection_ok = test_backend_connection()
    
    if connection_ok:
        # Test analysis endpoint
        analysis_ok = test_analysis_endpoint()
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 40)
        print(f"  Backend Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
        print(f"  Analysis Endpoint: {'✅ PASS' if analysis_ok else '❌ FAIL'}")
        
        if connection_ok and analysis_ok:
            print("\n🎉 All tests passed! Your backend is working correctly!")
            print("The frontend should now be able to connect to the backend.")
        else:
            print("\n⚠️ Some tests failed. Check the errors above.")
    else:
        print("\n❌ Backend is not accessible. Please start it with:")
        print("   python app.py")

if __name__ == "__main__":
    main() 