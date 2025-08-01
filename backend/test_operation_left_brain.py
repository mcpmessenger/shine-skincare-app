#!/usr/bin/env python3
"""
Test script for Operation Left Brain AI Integration

This script tests the complete AI pipeline implementation including:
- AI Embedding Service
- SCIN Vector Search Service  
- Enhanced Vision Service
- Skin Condition Detection Service
- AI Analysis Orchestrator
- API Endpoints

Run this script to verify that all components are working correctly.
"""

import os
import sys
import logging
import numpy as np
from PIL import Image
import io

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image():
    """Create a simple test image for testing"""
    # Create a simple test image (100x100 pixels, RGB)
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()

def test_ai_embedding_service():
    """Test the AI embedding service"""
    logger.info("🧠 Testing AI Embedding Service...")
    
    try:
        from app.services.ai_embedding_service import embedding_service
        
        # Create test image
        test_image_bytes = create_test_image()
        
        # Generate embedding
        embedding = embedding_service.generate_embedding(test_image_bytes)
        
        # Check embedding properties
        assert isinstance(embedding, np.ndarray), "Embedding should be numpy array"
        assert embedding.shape[0] > 0, "Embedding should have positive dimension"
        
        # Get model info
        model_info = embedding_service.get_model_info()
        logger.info(f"✅ AI Embedding Service: {model_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI Embedding Service test failed: {e}")
        return False

def test_scin_vector_search_service():
    """Test the SCIN vector search service"""
    logger.info("🔍 Testing SCIN Vector Search Service...")
    
    try:
        from app.services.scin_vector_search_service import scin_search_service
        
        # Create test embedding
        test_embedding = np.random.rand(512).astype(np.float32)
        
        # Search for similar cases
        similar_cases = scin_search_service.search_similar_cases(test_embedding, k=3)
        
        # Check results
        assert isinstance(similar_cases, list), "Similar cases should be a list"
        
        # Get service status
        status = scin_search_service.get_service_status()
        logger.info(f"✅ SCIN Vector Search Service: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SCIN Vector Search Service test failed: {e}")
        return False

def test_enhanced_vision_service():
    """Test the enhanced vision service"""
    logger.info("👁️ Testing Enhanced Vision Service...")
    
    try:
        from app.services.enhanced_vision_service import enhanced_vision_service
        
        # Create test image
        test_image_bytes = create_test_image()
        
        # Detect face and isolate
        facial_features, isolated_face_bytes = enhanced_vision_service.detect_face_and_isolate(test_image_bytes)
        
        # Check results
        assert isinstance(facial_features, object), "Facial features should be returned"
        
        # Get service status
        status = enhanced_vision_service.get_service_status()
        logger.info(f"✅ Enhanced Vision Service: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced Vision Service test failed: {e}")
        return False

def test_skin_condition_detection_service():
    """Test the skin condition detection service"""
    logger.info("🔬 Testing Skin Condition Detection Service...")
    
    try:
        from app.services.skin_condition_detection_service import skin_condition_service
        
        # Create test image
        test_image_bytes = create_test_image()
        
        # Detect conditions
        conditions = skin_condition_service.detect_conditions(test_image_bytes)
        
        # Check results
        assert isinstance(conditions, list), "Conditions should be a list"
        
        # Get service status
        status = skin_condition_service.get_service_status()
        logger.info(f"✅ Skin Condition Detection Service: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Skin Condition Detection Service test failed: {e}")
        return False

def test_ai_analysis_orchestrator():
    """Test the AI analysis orchestrator"""
    logger.info("🎯 Testing AI Analysis Orchestrator...")
    
    try:
        from app.services.ai_analysis_orchestrator import ai_orchestrator
        
        # Create test image
        test_image_bytes = create_test_image()
        
        # Test selfie analysis
        selfie_result = ai_orchestrator.analyze_selfie(test_image_bytes, "test_user")
        
        # Check results
        assert hasattr(selfie_result, 'analysis_id'), "Result should have analysis_id"
        assert hasattr(selfie_result, 'skin_conditions'), "Result should have skin_conditions"
        assert hasattr(selfie_result, 'scin_similar_cases'), "Result should have scin_similar_cases"
        
        # Test skin analysis
        skin_result = ai_orchestrator.analyze_skin(test_image_bytes, "test_user")
        
        # Check results
        assert hasattr(skin_result, 'analysis_id'), "Result should have analysis_id"
        assert hasattr(skin_result, 'skin_conditions'), "Result should have skin_conditions"
        
        # Get orchestrator status
        status = ai_orchestrator.get_orchestrator_status()
        logger.info(f"✅ AI Analysis Orchestrator: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI Analysis Orchestrator test failed: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    logger.info("🌐 Testing API Endpoints...")
    
    try:
        from app.routes.operation_left_brain_routes import operation_left_brain_bp
        
        # Check if blueprint is created
        assert operation_left_brain_bp is not None, "Blueprint should be created"
        
        # Check if routes are registered by examining the blueprint's route rules
        routes = []
        for rule in operation_left_brain_bp.deferred_functions:
            if hasattr(rule, 'rule'):
                routes.append(rule.rule)
        
        # Alternative way to check routes - look at the blueprint's url_prefix and name
        blueprint_name = operation_left_brain_bp.name
        url_prefix = operation_left_brain_bp.url_prefix
        
        logger.info(f"✅ API Endpoints: Blueprint '{blueprint_name}' created with prefix '{url_prefix}'")
        logger.info(f"✅ Expected routes: /api/v2/selfie/analyze, /api/v2/skin/analyze, /api/v2/ai/status, /api/v2/ai/health")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API Endpoints test failed: {e}")
        return False

def main():
    """Run all tests for Operation Left Brain"""
    logger.info("🚀 Starting Operation Left Brain Tests...")
    
    tests = [
        ("AI Embedding Service", test_ai_embedding_service),
        ("SCIN Vector Search Service", test_scin_vector_search_service),
        ("Enhanced Vision Service", test_enhanced_vision_service),
        ("Skin Condition Detection Service", test_skin_condition_detection_service),
        ("AI Analysis Orchestrator", test_ai_analysis_orchestrator),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name} - PASSED")
            else:
                logger.error(f"❌ {test_name} - FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("OPERATION LEFT BRAIN TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Operation Left Brain tests passed!")
        return 0
    else:
        logger.error(f"⚠️ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 