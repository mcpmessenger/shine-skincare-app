#!/usr/bin/env python3
"""
Debug script for comprehensive analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import V4 components
from advanced_face_detection import advanced_face_detector, detect_faces_advanced
from robust_embeddings import robust_embedding_system, generate_embedding_advanced
from bias_mitigation import bias_mitigation_system, evaluate_fairness_advanced, apply_bias_correction_advanced

# Import existing components
from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
from enhanced_recommendation_engine import EnhancedRecommendationEngine
from enhanced_severity_scoring import EnhancedSeverityScoring

def create_test_image():
    """Create a test image with a face-like shape"""
    # Create a 600x600 image
    img = np.zeros((600, 600, 3), dtype=np.uint8)
    
    # Draw a face-like oval
    cv2.ellipse(img, (300, 300), (200, 250), 0, 0, 360, (255, 255, 255), -1)
    
    # Draw eyes
    cv2.circle(img, (250, 250), 20, (0, 0, 0), -1)
    cv2.circle(img, (350, 250), 20, (0, 0, 0), -1)
    
    # Draw nose
    cv2.ellipse(img, (300, 300), (10, 20), 0, 0, 360, (0, 0, 0), -1)
    
    # Draw mouth
    cv2.ellipse(img, (300, 380), (30, 15), 0, 0, 180, (0, 0, 0), 3)
    
    return img

def test_components_step_by_step():
    """Test each component step by step"""
    print("🔍 Testing V4 components step by step...")
    
    # Step 1: Create test image
    print("\n1️⃣ Creating test image...")
    img = create_test_image()
    print(f"   ✅ Test image created: {img.shape}")
    
    # Step 2: Test face detection
    print("\n2️⃣ Testing face detection...")
    try:
        # Convert image to base64
        _, buffer = cv2.imencode('.jpg', img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        face_results = detect_faces_advanced(img_b64, confidence_threshold=0.3)
        print(f"   ✅ Face detection: {face_results.get('success', False)}")
        print(f"   📊 Faces detected: {face_results.get('faces_detected', 0)}")
        if face_results.get('faces'):
            print(f"   📦 First face: {face_results['faces'][0]}")
    except Exception as e:
        print(f"   ❌ Face detection failed: {e}")
        return
    
    # Step 3: Test embedding system
    print("\n3️⃣ Testing embedding system...")
    try:
        # Test with a small face crop
        face_crop = img[100:200, 100:200]  # Simple crop for testing
        embedding = generate_embedding_advanced(face_crop, None)
        print(f"   ✅ Embedding generated: {len(embedding)} dimensions")
    except Exception as e:
        print(f"   ❌ Embedding failed: {e}")
        return
    
    # Step 4: Test analysis algorithms
    print("\n4️⃣ Testing analysis algorithms...")
    try:
        analysis_algorithms = EnhancedSkinAnalyzer()
        analysis = analysis_algorithms.analyze_skin_conditions(img)
        print(f"   ✅ Analysis completed: {len(analysis)} results")
        print(f"   📊 Analysis keys: {list(analysis.keys())}")
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        return
    
    # Step 5: Test severity scoring
    print("\n5️⃣ Testing severity scoring...")
    try:
        severity_scorer = EnhancedSeverityScoring()
        severity = severity_scorer.calculate_severity(analysis)
        print(f"   ✅ Severity scoring completed: {len(severity)} scores")
    except Exception as e:
        print(f"   ❌ Severity scoring failed: {e}")
        return
    
    # Step 6: Test recommendation engine
    print("\n6️⃣ Testing recommendation engine...")
    try:
        recommendation_engine = EnhancedRecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(analysis, None)
        print(f"   ✅ Recommendations generated: {len(recommendations)} items")
    except Exception as e:
        print(f"   ❌ Recommendations failed: {e}")
        return
    
    # Step 7: Test bias mitigation
    print("\n7️⃣ Testing bias mitigation...")
    try:
        # Create dummy data for bias testing
        predictions = [0.7, 0.8, 0.6]
        ground_truth = [0.5, 0.5, 0.5]
        demo_data = [{'age': '25-35', 'race': 'caucasian'}] * 3
        
        bias_results = evaluate_fairness_advanced(
            np.array(predictions),
            np.array(ground_truth),
            demo_data
        )
        print(f"   ✅ Bias evaluation completed: {len(bias_results)} metrics")
    except Exception as e:
        print(f"   ❌ Bias evaluation failed: {e}")
        return
    
    print("\n✅ All components tested successfully!")

def test_comprehensive_analysis():
    """Test the comprehensive analysis system"""
    print("\n🧪 Testing comprehensive analysis system...")
    
    try:
        from enhanced_analysis_api_v4 import Version4AnalysisSystem
        
        # Initialize the system
        v4_system = Version4AnalysisSystem()
        print("   ✅ V4 Analysis System initialized")
        
        # Create test image
        img = create_test_image()
        print(f"   ✅ Test image created: {img.shape}")
        
        # Test comprehensive analysis
        results = v4_system.perform_comprehensive_analysis(img, {'age': '25-35'})
        print(f"   ✅ Comprehensive analysis completed: {results.get('success', False)}")
        
        if results.get('success'):
            print(f"   📊 Analysis keys: {list(results.keys())}")
            if 'analysis' in results:
                print(f"   📋 Analysis data keys: {list(results['analysis'].keys())}")
        else:
            print(f"   ❌ Analysis failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Comprehensive analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting V4 component debugging...")
    test_components_step_by_step()
    test_comprehensive_analysis()
    print("\n✅ Debugging completed!") 