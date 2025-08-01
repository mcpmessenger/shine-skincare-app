#!/usr/bin/env python3
"""
Test script for enhanced skin analysis functionality
"""

import os
import sys
import json
from PIL import Image
import io
import base64

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the enhanced analysis service
from application import enhanced_analysis_service

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 test image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()

def test_enhanced_analysis():
    """Test the enhanced analysis functionality"""
    print("🧪 Testing Enhanced Skin Analysis...")
    
    # Create test image
    test_image_bytes = create_test_image()
    test_image = Image.open(io.BytesIO(test_image_bytes))
    
    print("✅ Test image created")
    
    # Test face detection (will return None since it's not a real face)
    print("🔍 Testing face detection...")
    face_region = enhanced_analysis_service.detect_face_region(test_image_bytes)
    if face_region:
        print(f"✅ Face detected: {face_region}")
    else:
        print("⚠️ No face detected (expected for test image)")
    
    # Test embedding generation (will fail without OpenAI API key)
    print("🧠 Testing embedding generation...")
    embedding = enhanced_analysis_service.generate_image_embedding(test_image)
    if embedding:
        print(f"✅ Embedding generated: {len(embedding)} dimensions")
    else:
        print("⚠️ Embedding generation failed (expected without API key)")
    
    # Test SCIN dataset search
    print("🔍 Testing SCIN dataset search...")
    similar_conditions = enhanced_analysis_service.search_scin_dataset(embedding)
    if similar_conditions:
        print(f"✅ Found {len(similar_conditions)} similar conditions")
        for i, condition in enumerate(similar_conditions):
            print(f"  {i+1}. {condition['condition_type']} ({condition['similarity_score']:.2f})")
    else:
        print("⚠️ No similar conditions found")
    
    # Test analysis generation
    print("📊 Testing analysis generation...")
    analysis_result = enhanced_analysis_service.generate_analysis(similar_conditions)
    if analysis_result:
        print("✅ Analysis generated successfully")
        print(f"  Skin Type: {analysis_result['skin_type']}")
        print(f"  Concerns: {', '.join(analysis_result['concerns'])}")
        print(f"  Recommendations: {len(analysis_result['recommendations'])} items")
    else:
        print("❌ Analysis generation failed")
    
    print("\n🎉 Enhanced analysis test completed!")

if __name__ == "__main__":
    test_enhanced_analysis() 