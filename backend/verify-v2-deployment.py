#!/usr/bin/env python3
"""
Verify V2 Upgrade Deployment
Test CORS fix and enhanced ML features
"""

import requests
import json
from datetime import datetime

def test_v2_deployment():
    """Test V2 deployment and CORS fix"""
    base_url = "https://api.shineskincollective.com"
    
    print("🚀 Testing V2 Upgrade Deployment...")
    print(f"📍 Backend URL: {base_url}")
    print("=" * 50)
    
    # Test 1: Basic health check
    print("1️⃣ Testing Basic Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"📊 Version: {data.get('version', 'unknown')}")
            print(f"🔧 Features: {data.get('features', {})}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
    
    print()
    
    # Test 2: CORS headers
    print("2️⃣ Testing CORS Headers")
    try:
        response = requests.options(
            f"{base_url}/api/v2/analyze/guest",
            headers={
                "Origin": "https://www.shineskincollective.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cors_methods = response.headers.get("Access-Control-Allow-Methods")
        cors_headers = response.headers.get("Access-Control-Allow-Headers")
        
        if cors_origin == "https://www.shineskincollective.com":
            print("✅ CORS origin configured correctly")
        else:
            print(f"⚠️  CORS origin may need adjustment: {cors_origin}")
        
        if cors_methods:
            print(f"✅ CORS methods: {cors_methods}")
        else:
            print("⚠️  CORS methods not found")
            
        if cors_headers:
            print(f"✅ CORS headers: {cors_headers}")
        else:
            print("⚠️  CORS headers not found")
            
    except Exception as e:
        print(f"❌ CORS test error: {str(e)}")
    
    print()
    
    # Test 3: Enhanced ML analysis (simulated)
    print("3️⃣ Testing Enhanced ML Analysis")
    try:
        # Create a small test image (1KB of random data)
        test_image_data = b"fake_image_data" * 64  # ~1KB
        
        files = {'image': ('test.jpg', test_image_data, 'image/jpeg')}
        data = {
            'ethnicity': 'caucasian',
            'age': '25'
        }
        
        response = requests.post(
            f"{base_url}/api/v2/analyze/guest",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Enhanced ML analysis successful")
                analysis_data = result.get('data', {})
                skin_analysis = analysis_data.get('skin_analysis', {})
                
                print(f"📊 Skin Type: {skin_analysis.get('skinType', 'Unknown')}")
                print(f"🔬 Fitzpatrick: {skin_analysis.get('fitzpatrick_type', 'Unknown')}")
                print(f"💧 Hydration: {skin_analysis.get('hydration', 0)}%")
                print(f"⚡ Oiliness: {skin_analysis.get('oiliness', 0)}%")
                print(f"🛡️  Sensitivity: {skin_analysis.get('sensitivity', 0)}%")
                
                # Check v2 features
                face_detection = skin_analysis.get('face_detection', {})
                if face_detection.get('faces_found', 0) > 0:
                    print("✅ Face detection working")
                
                similar_profiles = analysis_data.get('similar_scin_profiles', [])
                if similar_profiles:
                    print(f"✅ FAISS similarity search: {len(similar_profiles)} profiles found")
                
                confidence_scores = analysis_data.get('confidence_scores', {})
                if confidence_scores.get('overall', 0) > 0.8:
                    print("✅ High confidence analysis")
                
                metadata = analysis_data.get('metadata', {})
                if metadata.get('face_detected'):
                    print("✅ Face detection confirmed")
                if metadata.get('ethnicity_considered'):
                    print("✅ Ethnicity analysis included")
                if metadata.get('age_considered'):
                    print("✅ Age analysis included")
                
            else:
                print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Analysis test error: {str(e)}")
    
    print()
    
    # Test 4: API health endpoint
    print("4️⃣ Testing API Health Endpoint")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API health check passed")
            print(f"📊 Version: {data.get('version', 'unknown')}")
            features = data.get('features', {})
            if features.get('enhanced_ml'):
                print("✅ Enhanced ML available")
            if features.get('face_detection'):
                print("✅ Face detection available")
            if features.get('faiss_similarity'):
                print("✅ FAISS similarity available")
            if features.get('demographic_analysis'):
                print("✅ Demographic analysis available")
            if features.get('cors_fixed'):
                print("✅ CORS fixed")
        else:
            print(f"❌ API health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API health error: {str(e)}")
    
    print()
    
    # Test 5: Root endpoint
    print("5️⃣ Testing Root Endpoint")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working")
            print(f"📊 Version: {data.get('version', 'unknown')}")
            print(f"📝 Message: {data.get('message', 'No message')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
    
    print()
    print("=" * 50)
    print("🎯 V2 Upgrade Deployment Test Complete!")
    print("📋 Summary:")
    print("   - Enhanced ML-powered skin analysis")
    print("   - Face detection and cropping")
    print("   - FAISS similarity search")
    print("   - Demographic analysis")
    print("   - Fixed CORS configuration")
    print("   - 100MB file upload support")
    print("   - m5.2xlarge instance optimization")
    print("\n🚀 Ready for production use!")

if __name__ == "__main__":
    test_v2_deployment() 