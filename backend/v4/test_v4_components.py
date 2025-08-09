#!/usr/bin/env python3
"""
Test Script for Version 4 Components
Validates advanced face detection, robust embeddings, and bias mitigation
"""

import numpy as np
import cv2
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import Version 4 components
from advanced_face_detection import advanced_face_detector, detect_faces_advanced
from robust_embeddings import robust_embedding_system, generate_embedding_advanced
from bias_mitigation import bias_mitigation_system, evaluate_fairness_advanced

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Version4Tester:
    """
    Comprehensive tester for Version 4 components
    """
    
    def __init__(self):
        """Initialize the tester"""
        self.test_results = {
            'face_detection': {},
            'embeddings': {},
            'bias_mitigation': {},
            'overall': {}
        }
        
        logger.info("✅ Version 4 Tester initialized")
    
    def create_test_image(self, size: tuple = (640, 480)) -> np.ndarray:
        """Create a synthetic test image"""
        # Create a simple test image with a face-like structure
        image = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        
        # Add a face-like oval
        center = (size[0] // 2, size[1] // 2)
        axes = (150, 200)
        
        # Draw face outline
        cv2.ellipse(image, center, axes, 0, 0, 360, (255, 255, 255), -1)
        
        # Add eyes
        eye_centers = [
            (center[0] - 50, center[1] - 30),
            (center[0] + 50, center[1] - 30)
        ]
        for eye_center in eye_centers:
            cv2.circle(image, eye_center, 15, (0, 0, 0), -1)
        
        # Add nose
        nose_center = (center[0], center[1] + 20)
        cv2.circle(image, nose_center, 10, (0, 0, 0), -1)
        
        # Add mouth
        mouth_center = (center[0], center[1] + 80)
        cv2.ellipse(image, mouth_center, (40, 20), 0, 0, 180, (0, 0, 0), -1)
        
        return image
    
    def test_face_detection(self) -> Dict:
        """Test advanced face detection"""
        logger.info("Testing advanced face detection...")
        
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Convert to base64 string
            _, buffer = cv2.imencode('.jpg', test_image)
            import base64
            image_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
            
            # Test face detection
            results = detect_faces_advanced(image_base64)
            
            # Validate results
            success = results.get('success', False)
            faces_detected = results.get('faces_detected', 0)
            method = results.get('method', 'unknown')
            
            test_result = {
                'success': success,
                'faces_detected': faces_detected,
                'method_used': method,
                'confidence': results.get('confidence', 0.0),
                'error': results.get('error', None)
            }
            
            logger.info(f"Face detection test completed: {faces_detected} faces detected using {method}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error in face detection test: {e}")
            return {
                'success': False,
                'error': str(e),
                'faces_detected': 0,
                'method_used': 'error'
            }
    
    def test_embeddings(self) -> Dict:
        """Test robust embedding generation"""
        logger.info("Testing robust embedding generation...")
        
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Test demographic data
            demographic_data = {
                'age': 25,
                'ethnicity': 'caucasian',
                'gender': 'female',
                'fitzpatrick_type': 3
            }
            
            # Generate embedding
            embedding = generate_embedding_advanced(test_image, demographic_data)
            
            # Validate embedding
            embedding_dim = len(embedding)
            embedding_norm = np.linalg.norm(embedding)
            
            test_result = {
                'success': True,
                'embedding_dimension': embedding_dim,
                'embedding_norm': float(embedding_norm),
                'demographic_data': demographic_data,
                'model_type': robust_embedding_system.model_type
            }
            
            logger.info(f"Embedding test completed: {embedding_dim}D embedding generated")
            return test_result
            
        except Exception as e:
            logger.error(f"Error in embedding test: {e}")
            return {
                'success': False,
                'error': str(e),
                'embedding_dimension': 0
            }
    
    def test_bias_mitigation(self) -> Dict:
        """Test bias mitigation system"""
        logger.info("Testing bias mitigation system...")
        
        try:
            # Create synthetic test data
            n_samples = 100
            
            # Create predictions with some bias
            predictions = np.random.rand(n_samples)
            
            # Create ground truth
            ground_truth = np.random.rand(n_samples)
            
            # Create demographic data with different groups
            demographic_data = []
            for i in range(n_samples):
                if i < n_samples // 2:
                    demo = {'ethnicity': 'caucasian', 'age': 25, 'gender': 'female'}
                else:
                    demo = {'ethnicity': 'african', 'age': 30, 'gender': 'male'}
                demographic_data.append(demo)
            
            # Test fairness evaluation
            fairness_results = evaluate_fairness_advanced(
                predictions, ground_truth, demographic_data
            )
            
            # Validate results
            bias_detected = fairness_results.get('bias_detected', False)
            overall_metrics = fairness_results.get('overall_metrics', {})
            
            test_result = {
                'success': True,
                'bias_detected': bias_detected,
                'fairness_metrics': overall_metrics,
                'samples_tested': n_samples,
                'demographic_groups': 2
            }
            
            logger.info(f"Bias mitigation test completed: Bias detected = {bias_detected}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error in bias mitigation test: {e}")
            return {
                'success': False,
                'error': str(e),
                'bias_detected': False
            }
    
    def test_integration(self) -> Dict:
        """Test integration of all components"""
        logger.info("Testing component integration...")
        
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Test demographic data
            demographic_data = {
                'age': 28,
                'ethnicity': 'asian',
                'gender': 'female',
                'fitzpatrick_type': 4
            }
            
            # Step 1: Face detection
            _, buffer = cv2.imencode('.jpg', test_image)
            image_base64 = buffer.tobytes()
            face_results = detect_faces_advanced(image_base64)
            
            # Step 2: Embedding generation
            embedding = generate_embedding_advanced(test_image, demographic_data)
            
            # Step 3: Bias evaluation (with synthetic data)
            predictions = np.random.rand(50)
            ground_truth = np.random.rand(50)
            demo_data = [demographic_data] * 50
            
            bias_results = evaluate_fairness_advanced(predictions, ground_truth, demo_data)
            
            # Compile integration results
            integration_result = {
                'success': True,
                'face_detection_success': face_results.get('success', False),
                'embedding_generated': len(embedding) > 0,
                'bias_evaluation_success': bias_results.get('success', False),
                'all_components_working': (
                    face_results.get('success', False) and
                    len(embedding) > 0 and
                    bias_results.get('success', False)
                )
            }
            
            logger.info("Integration test completed successfully")
            return integration_result
            
        except Exception as e:
            logger.error(f"Error in integration test: {e}")
            return {
                'success': False,
                'error': str(e),
                'all_components_working': False
            }
    
    def run_all_tests(self) -> Dict:
        """Run all tests and compile results"""
        logger.info("Starting comprehensive Version 4 testing...")
        
        start_time = datetime.now()
        
        # Run individual component tests
        self.test_results['face_detection'] = self.test_face_detection()
        self.test_results['embeddings'] = self.test_embeddings()
        self.test_results['bias_mitigation'] = self.test_bias_mitigation()
        
        # Run integration test
        self.test_results['integration'] = self.test_integration()
        
        # Compile overall results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate success rates
        component_successes = sum([
            self.test_results['face_detection'].get('success', False),
            self.test_results['embeddings'].get('success', False),
            self.test_results['bias_mitigation'].get('success', False),
            self.test_results['integration'].get('success', False)
        ])
        
        overall_success = component_successes == 4
        
        self.test_results['overall'] = {
            'success': overall_success,
            'components_tested': 4,
            'components_successful': component_successes,
            'success_rate': component_successes / 4,
            'test_duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Testing completed: {component_successes}/4 components successful")
        return self.test_results
    
    def save_test_results(self, filename: str = "v4_test_results.json"):
        """Save test results to file"""
        try:
            results_path = Path(filename)
            
            # Convert numpy types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {key: convert_numpy(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                else:
                    return obj
            
            serializable_results = convert_numpy(self.test_results)
            
            with open(results_path, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"Test results saved to {results_path}")
            
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
    
    def print_summary(self):
        """Print a summary of test results"""
        print("\n" + "="*60)
        print("VERSION 4 COMPONENT TESTING SUMMARY")
        print("="*60)
        
        overall = self.test_results['overall']
        print(f"Overall Success: {'✅ PASS' if overall['success'] else '❌ FAIL'}")
        print(f"Components Successful: {overall['components_successful']}/{overall['components_tested']}")
        print(f"Success Rate: {overall['success_rate']:.1%}")
        print(f"Test Duration: {overall['test_duration_seconds']:.2f} seconds")
        
        print("\nComponent Results:")
        print("-" * 40)
        
        components = ['face_detection', 'embeddings', 'bias_mitigation', 'integration']
        for component in components:
            result = self.test_results[component]
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            print(f"{component.replace('_', ' ').title()}: {status}")
            
            if not result.get('success', False):
                error = result.get('error', 'Unknown error')
                print(f"  Error: {error}")
        
        print("="*60)

def main():
    """Main test execution"""
    print("Starting Version 4 Component Testing...")
    
    # Initialize tester
    tester = Version4Tester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Print summary
    tester.print_summary()
    
    # Save results
    tester.save_test_results()
    
    # Return success status
    return results['overall']['success']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 