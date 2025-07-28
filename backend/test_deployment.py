#!/usr/bin/env python3
"""
Test script for Shine Backend Deployment
"""
import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Test the backend health endpoint"""
    urls = [
        "https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com",
        "https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/health",
        "https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest"
    ]
    
    print("🧪 Testing Backend Deployment")
    print("=" * 40)
    
    for url in urls:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ Endpoint is working!")
            else:
                print("❌ Endpoint returned error status")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

def test_analysis_endpoint():
    """Test the skin analysis endpoint"""
    url = "https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com/api/v2/analyze/guest"
    
    print("🔬 Testing Skin Analysis Endpoint")
    print("=" * 40)
    
    try:
        # Test with no image (should still work)
        response = requests.post(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis endpoint working!")
            print(f"Success: {data.get('success', False)}")
            if 'data' in data:
                print(f"Analysis ID: {data['data'].get('image_id', 'N/A')}")
        else:
            print(f"❌ Analysis endpoint failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)

def check_aws_environment():
    """Check AWS environment status"""
    print("☁️ Checking AWS Environment Status")
    print("=" * 40)
    
    try:
        import subprocess
        result = subprocess.run(
            "aws elasticbeanstalk describe-environments --environment-names shine-backend-final --region us-east-1",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ AWS CLI command successful")
            print("Environment status:")
            print(result.stdout)
        else:
            print("❌ AWS CLI command failed")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error checking AWS environment: {e}")
    
    print("\n" + "=" * 40)

def main():
    """Main test function"""
    print("🚀 Shine Backend Deployment Test")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test backend health
    test_backend_health()
    
    # Test analysis endpoint
    test_analysis_endpoint()
    
    # Check AWS environment
    check_aws_environment()
    
    print("🎯 Test completed!")
    print("\n📋 Summary:")
    print("- If all endpoints return 200: ✅ Backend is working")
    print("- If endpoints fail: ❌ Check deployment status")
    print("- If AWS CLI fails: ⚠️ Check AWS credentials")

if __name__ == "__main__":
    main() 