#!/usr/bin/env python3
"""
Test script for enhanced image analysis services
"""

import os
import sys
import tempfile
import json
import requests
from PIL import Image
import numpy as np

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_services_initialization():
    """Test service initialization"""
    print("🔧 Testing service initialization...")
    
    try:
        from app.services import (
            GoogleVisionService, 
            ImageVectorizationService, 
            FAISSService, 
            SupabaseService
        )
        
        # Initialize services
        google_vision = GoogleVisionService()
        vectorization = ImageVectorizationService()
        faiss_service = FAISSService()
        supabase = SupabaseService()
        
        print(f"✅ Google Vision Service: {'Available' if google_vision.is_available() else 'Not Available'}")
        print(f"✅ Vectorization Service: {'Available' if vectorization.is_available() else 'Not Available'}")
        print(f"✅ FAISS Service: {'Available' if faiss_service.is_available() else 'Not Available'}")
        print(f"✅ Supabase Service: {'Available' if supabase.is_available() else 'Not Available'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    print("🖼️ Creating test image...")
    
    # Create a simple test image
    img = Image.new('RGB', (224, 224), color='red')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        img.save(tmp_file.name, 'JPEG')
        tmp_path = tmp_file.name
    
    print(f"✅ Test image created: {tmp_path}")
    return tmp_path

def test_vectorization_service():
    """Test image vectorization"""
    print("🧠 Testing image vectorization...")
    
    try:
        from app.services import ImageVectorizationService
        
        vectorization = ImageVectorizationService()
        if not vectorization.is_available():
            print("⚠️ Vectorization service not available, skipping test")
            return False
        
        # Create test image
        test_image_path = create_test_image()
        
        # Test vectorization
        vector = vectorization.vectorize_image(test_image_path)
        
        if vector is not None:
            print(f"✅ Vectorization successful: {vector.shape}")
            print(f"✅ Feature dimension: {vectorization.get_feature_dimension()}")
            
            # Clean up
            os.unlink(test_image_path)
            return True
        else:
            print("❌ Vectorization failed")
            return False
            
    except Exception as e:
        print(f"❌ Vectorization test failed: {e}")
        return False

def test_faiss_service():
    """Test FAISS similarity search"""
    print("🔍 Testing FAISS similarity search...")
    
    try:
        from app.services import FAISSService, ImageVectorizationService
        
        faiss_service = FAISSService()
        vectorization = ImageVectorizationService()
        
        if not faiss_service.is_available() or not vectorization.is_available():
            print("⚠️ FAISS or vectorization service not available, skipping test")
            return False
        
        # Create test images
        test_image_paths = []
        for i in range(3):
            img = Image.new('RGB', (224, 224), color=f'rgb({i*100}, {i*50}, {i*25})')
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                img.save(tmp_file.name, 'JPEG')
                test_image_paths.append(tmp_file.name)
        
        # Vectorize images
        vectors = []
        image_ids = []
        
        for i, path in enumerate(test_image_paths):
            vector = vectorization.vectorize_image(path)
            if vector is not None:
                vectors.append(vector)
                image_id = f"test_image_{i}"
                image_ids.append(image_id)
                
                # Add to FAISS index
                success = faiss_service.add_vector(vector, image_id)
                print(f"✅ Added image {image_id} to FAISS index: {success}")
        
        if len(vectors) > 1:
            # Test similarity search
            query_vector = vectors[0]
            similar_results = faiss_service.search_similar(query_vector, k=2)
            
            print(f"✅ Similarity search successful: {len(similar_results)} results")
            for image_id, distance in similar_results:
                print(f"   - {image_id}: distance={distance:.4f}")
            
            # Clean up
            for path in test_image_paths:
                os.unlink(path)
            
            return True
        else:
            print("❌ Not enough vectors for similarity search")
            return False
            
    except Exception as e:
        print(f"❌ FAISS test failed: {e}")
        return False

def test_google_vision_service():
    """Test Google Vision AI service"""
    print("👁️ Testing Google Vision AI...")
    
    try:
        from app.services import GoogleVisionService
        
        google_vision = GoogleVisionService()
        if not google_vision.is_available():
            print("⚠️ Google Vision service not available, skipping test")
            return False
        
        # Create test image
        test_image_path = create_test_image()
        
        # Test analysis
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        result = google_vision.analyze_image_from_bytes(image_data)
        
        if result.get('status') == 'success':
            print("✅ Google Vision analysis successful")
            print(f"   - Face detection: {result['results'].get('face_detection', {}).get('faces_found', 0)} faces")
            print(f"   - Labels found: {result['results'].get('label_detection', {}).get('labels_found', 0)}")
            
            # Clean up
            os.unlink(test_image_path)
            return True
        else:
            print(f"❌ Google Vision analysis failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Google Vision test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("🌐 Testing API endpoints...")
    
    base_url = "http://localhost:5000/api/v2"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   - Services status: {data.get('services', {})}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running, skipping API tests")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Services Test Suite")
    print("=" * 50)
    
    tests = [
        ("Service Initialization", test_services_initialization),
        ("Image Vectorization", test_vectorization_service),
        ("FAISS Similarity Search", test_faiss_service),
        ("Google Vision AI", test_google_vision_service),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced services are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 