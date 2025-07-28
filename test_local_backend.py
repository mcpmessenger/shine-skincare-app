#!/usr/bin/env python3
"""
Test the local backend to ensure it's working properly
"""

import requests
import json
from datetime import datetime

# Local backend URL
LOCAL_BACKEND_URL = "http://localhost:5000"

def test_local_backend():
    """Test the local backend endpoints"""
    print("🚀 Testing Local Backend")
    print("=" * 50)
    print(f"Backend URL: {LOCAL_BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test endpoints
    endpoints = [
        ("/", "GET"),
        ("/api/health", "GET"),
        ("/api/recommendations/trending", "GET"),
        ("/api/recommendations", "GET"),
    ]
    
    successful_tests = 0
    total_tests = len(endpoints)
    
    for endpoint, method in endpoints:
        url = f"{LOCAL_BACKEND_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                print(f"❌ Unsupported method: {method}")
                continue
                
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - Status: {response.status_code}")
                try:
                    result = response.json()
                    print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
                successful_tests += 1
            else:
                print(f"❌ {method} {endpoint} - Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 {method} {endpoint} - Connection Error (backend not running)")
        except Exception as e:
            print(f"💥 {method} {endpoint} - Error: {str(e)}")
    
    print()
    print("=" * 50)
    print(f"📊 Test Results: {successful_tests}/{total_tests} endpoints working")
    
    if successful_tests == total_tests:
        print("🎉 Local backend is working perfectly!")
        print("✅ Ready for frontend integration")
    else:
        print("⚠️  Some endpoints are not working")
        print("🔧 Start the backend with: python run_backend_local.py")
    
    print()
    print("🔗 Frontend Integration:")
    print("   Set NEXT_PUBLIC_API_URL=http://localhost:5000")
    print("   Start frontend with: npm run dev")
    print("   Test full application integration")

if __name__ == "__main__":
    test_local_backend() 