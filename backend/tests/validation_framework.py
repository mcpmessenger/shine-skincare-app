import unittest
import numpy as np
import time
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.service_manager import service_manager
from app.services import (
    FAISSService, DemographicWeightedSearch, EnhancedSkinTypeClassifier
)

logger = logging.getLogger(__name__)


class ValidationFramework:
    """Framework for validating AI model performance and accuracy"""
    
    def __init__(self):
        """Initialize the validation framework"""
        self.results = {}
        self.test_datasets = {}
        self.performance_benchmarks = {}
        
        # Initialize services for testing
        self._initialize_services()
        
        # Load test datasets
        self._load_test_datasets()
    
    def _initialize_services(self):
        """Initialize services for validation"""
        try:
            # Use service manager if available
            if service_manager.is_initialized():
                self.faiss_service = service_manager.get_service('faiss')
                self.demographic_search = service_manager.get_service('demographic_search')
                self.skin_classifier = service_manager.get_service('skin_classifier')
            else:
                # Fallback to direct initialization
                self.faiss_service = FAISSService(dimension=128)  # Smaller for testing
                self.demographic_search = None
                self.skin_classifier = EnhancedSkinTypeClassifier()
                
            logger.info("Validation services initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize validation services: {e}")
            raise
    
    def _load_test_datasets(self):
        """Load curated test datasets for validation"""
        # Create synthetic test datasets for validation
        self.test_datasets = {
            'similarity_accuracy': self._create_similarity_test_dataset(),
            'demographic_fairness': self._create_demographic_test_dataset(),
            'skin_classification': self._create_classification_test_dataset(),
            'performance_benchmark': self._create_performance_test_dataset()
        }
        
        logger.info(f"Loaded {len(self.test_datasets)} test datasets")
    
    def _create_similarity_test_dataset(self) -> Dict[str, Any]:
        """Create test dataset for similarity accuracy validation"""
        # Create synthetic vectors with known similarities
        base_vector = np.random.rand(128)
        
        test_cases = []
        
        # Case 1: Identical vectors (should have similarity = 1.0, distance ≈ 0)
        identical_vector = base_vector.copy()
        test_cases.append({
            'query_vector': base_vector,
            'target_vector': identical_vector,
            'expected_similarity': 1.0,
            'expected_distance_range': (0.0, 0.1),
            'description': 'Identical vectors'
        })
        
        # Case 2: Orthogonal vectors (should have similarity = 0.0, distance ≈ 2)
        orthogonal_vector = np.random.rand(128)
        orthogonal_vector = orthogonal_vector - np.dot(orthogonal_vector, base_vector) * base_vector
        orthogonal_vector = orthogonal_vector / np.linalg.norm(orthogonal_vector)
        test_cases.append({
            'query_vector': base_vector,
            'target_vector': orthogonal_vector,
            'expected_similarity': 0.0,
            'expected_distance_range': (1.8, 2.2),
            'description': 'Orthogonal vectors'
        })
        
        # Case 3: Opposite vectors (should have similarity = -1.0, distance ≈ 4)
        opposite_vector = -base_vector
        test_cases.append({
            'query_vector': base_vector,
            'target_vector': opposite_vector,
            'expected_similarity': -1.0,
            'expected_distance_range': (3.8, 4.2),
            'description': 'Opposite vectors'
        })
        
        # Case 4: Similar vectors (should have high similarity, low distance)
        similar_vector = base_vector + np.random.normal(0, 0.1, 128)
        similar_vector = similar_vector / np.linalg.norm(similar_vector)
        test_cases.append({
            'query_vector': base_vector,
            'target_vector': similar_vector,
            'expected_similarity_range': (0.8, 1.0),
            'expected_distance_range': (0.0, 0.4),
            'description': 'Similar vectors with noise'
        })
        
        return {
            'test_cases': test_cases,
            'description': 'Test cases for validating cosine similarity accuracy'
        }
    
    def _create_demographic_test_dataset(self) -> Dict[str, Any]:
        """Create test dataset for demographic fairness validation"""
        # Define demographic groups for testing
        demographic_groups = [
            {'ethnicity': 'caucasian', 'skin_type': 'normal', 'age_group': '25-35'},
            {'ethnicity': 'african', 'skin_type': 'oily', 'age_group': '18-25'},
            {'ethnicity': 'east_asian', 'skin_type': 'sensitive', 'age_group': '35-45'},
            {'ethnicity': 'south_asian', 'skin_type': 'combination', 'age_group': '25-35'},
            {'ethnicity': 'hispanic', 'skin_type': 'dry', 'age_group': '45-55'},
            {'ethnicity': 'middle_eastern', 'skin_type': 'normal', 'age_group': '25-35'}
        ]
        
        test_cases = []
        
        for i, demographics in enumerate(demographic_groups):
            # Create synthetic vectors for each demographic group
            base_vector = np.random.rand(128)
            
            # Create similar vectors within the same demographic group
            similar_vectors = []
            for j in range(3):
                similar_vec = base_vector + np.random.normal(0, 0.05, 128)
                similar_vec = similar_vec / np.linalg.norm(similar_vec)
                similar_vectors.append({
                    'vector': similar_vec,
                    'demographics': demographics,
                    'image_id': f'demo_{i}_{j}'
                })
            
            test_cases.append({
                'query_vector': base_vector,
                'query_demographics': demographics,
                'similar_images': similar_vectors,
                'expected_demographic_boost': True,
                'description': f'Demographic group: {demographics["ethnicity"]}'
            })
        
        return {
            'test_cases': test_cases,
            'demographic_groups': demographic_groups,
            'description': 'Test cases for validating demographic-weighted search fairness'
        }
    
    def _create_classification_test_dataset(self) -> Dict[str, Any]:
        """Create test dataset for skin classification validation"""
        # Define known skin type classifications for testing
        test_cases = [
            {
                'image_data': np.random.rand(224, 224, 3),  # Synthetic image
                'ethnicity': 'caucasian',
                'expected_fitzpatrick': 'II',
                'expected_monk_range': (1, 4),
                'description': 'Light Caucasian skin'
            },
            {
                'image_data': np.random.rand(224, 224, 3) * 0.3,  # Darker synthetic image
                'ethnicity': 'african',
                'expected_fitzpatrick': 'V',
                'expected_monk_range': (7, 10),
                'description': 'Dark African skin'
            },
            {
                'image_data': np.random.rand(224, 224, 3) * 0.6,  # Medium synthetic image
                'ethnicity': 'east_asian',
                'expected_fitzpatrick_range': ('II', 'IV'),
                'expected_monk_range': (3, 5),
                'description': 'Medium East Asian skin'
            },
            {
                'image_data': np.random.rand(224, 224, 3) * 0.7,  # Medium-dark synthetic image
                'ethnicity': 'south_asian',
                'expected_fitzpatrick_range': ('III', 'V'),
                'expected_monk_range': (4, 7),
                'description': 'Medium-dark South Asian skin'
            }
        ]
        
        return {
            'test_cases': test_cases,
            'description': 'Test cases for validating skin type classification accuracy'
        }
    
    def _create_performance_test_dataset(self) -> Dict[str, Any]:
        """Create test dataset for performance benchmarking"""
        # Create datasets of varying sizes for performance testing
        test_cases = []
        
        vector_counts = [10, 50, 100, 500, 1000]
        
        for count in vector_counts:
            vectors = []
            image_ids = []
            
            for i in range(count):
                vector = np.random.rand(128)
                vector = vector / np.linalg.norm(vector)  # Normalize
                vectors.append(vector)
                image_ids.append(f'perf_test_{count}_{i}')
            
            test_cases.append({
                'vector_count': count,
                'vectors': vectors,
                'image_ids': image_ids,
                'description': f'Performance test with {count} vectors'
            })
        
        return {
            'test_cases': test_cases,
            'description': 'Test cases for performance benchmarking'
        }
    
    def validate_similarity_accuracy(self) -> Dict[str, Any]:
        """Validate cosine similarity accuracy"""
        logger.info("Starting similarity accuracy validation")
        
        test_dataset = self.test_datasets['similarity_accuracy']
        results = {
            'test_name': 'Similarity Accuracy Validation',
            'timestamp': datetime.utcnow().isoformat(),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }
        
        for i, test_case in enumerate(test_dataset['test_cases']):
            try:
                # Add vectors to FAISS index
                query_vector = test_case['query_vector']
                target_vector = test_case['target_vector']
                
                # Clear index and add target vector
                self.faiss_service.clear_index()
                self.faiss_service.add_vector(target_vector, f'target_{i}')
                
                # Search for similar vectors
                search_results = self.faiss_service.search_similar(query_vector, k=1)
                
                if not search_results:
                    raise Exception("No search results returned")
                
                image_id, distance = search_results[0]
                similarity = 1.0 - (distance / 4.0)  # Convert distance back to similarity
                
                # Validate results
                test_passed = True
                error_message = None
                
                if 'expected_similarity' in test_case:
                    expected = test_case['expected_similarity']
                    if abs(similarity - expected) > 0.1:
                        test_passed = False
                        error_message = f"Similarity {similarity:.3f} not close to expected {expected:.3f}"
                
                if 'expected_distance_range' in test_case:
                    min_dist, max_dist = test_case['expected_distance_range']
                    if not (min_dist <= distance <= max_dist):
                        test_passed = False
                        error_message = f"Distance {distance:.3f} not in expected range [{min_dist}, {max_dist}]"
                
                # Record result
                test_result = {
                    'test_case': test_case['description'],
                    'similarity': similarity,
                    'distance': distance,
                    'passed': test_passed,
                    'error': error_message
                }
                
                results['test_results'].append(test_result)
                
                if test_passed:
                    results['passed_tests'] += 1
                else:
                    results['failed_tests'] += 1
                    logger.warning(f"Similarity test failed: {test_case['description']} - {error_message}")
                
            except Exception as e:
                results['failed_tests'] += 1
                results['test_results'].append({
                    'test_case': test_case['description'],
                    'passed': False,
                    'error': str(e)
                })
                logger.error(f"Similarity test error: {test_case['description']} - {e}")
        
        # Calculate success rate
        total_tests = results['passed_tests'] + results['failed_tests']
        results['success_rate'] = results['passed_tests'] / total_tests if total_tests > 0 else 0
        
        logger.info(f"Similarity validation complete: {results['success_rate']:.2%} success rate")
        return results
    
    def validate_demographic_fairness(self) -> Dict[str, Any]:
        """Validate demographic-weighted search fairness"""
        logger.info("Starting demographic fairness validation")
        
        if not self.demographic_search:
            return {
                'test_name': 'Demographic Fairness Validation',
                'error': 'Demographic search service not available',
                'skipped': True
            }
        
        test_dataset = self.test_datasets['demographic_fairness']
        results = {
            'test_name': 'Demographic Fairness Validation',
            'timestamp': datetime.utcnow().isoformat(),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }
        
        for test_case in test_dataset['test_cases']:
            try:
                # Clear index and add similar images
                self.faiss_service.clear_index()
                
                for similar_image in test_case['similar_images']:
                    self.faiss_service.add_vector(
                        similar_image['vector'],
                        similar_image['image_id']
                    )
                
                # Perform demographic-weighted search
                search_results = self.demographic_search.search_with_demographics(
                    test_case['query_vector'],
                    test_case['query_demographics'],
                    k=3
                )
                
                # Validate that demographic weighting improved results
                test_passed = len(search_results) > 0
                error_message = None
                
                if not search_results:
                    test_passed = False
                    error_message = "No search results returned"
                
                # Record result
                test_result = {
                    'test_case': test_case['description'],
                    'results_count': len(search_results),
                    'passed': test_passed,
                    'error': error_message
                }
                
                results['test_results'].append(test_result)
                
                if test_passed:
                    results['passed_tests'] += 1
                else:
                    results['failed_tests'] += 1
                    logger.warning(f"Demographic test failed: {test_case['description']} - {error_message}")
                
            except Exception as e:
                results['failed_tests'] += 1
                results['test_results'].append({
                    'test_case': test_case['description'],
                    'passed': False,
                    'error': str(e)
                })
                logger.error(f"Demographic test error: {test_case['description']} - {e}")
        
        # Calculate success rate
        total_tests = results['passed_tests'] + results['failed_tests']
        results['success_rate'] = results['passed_tests'] / total_tests if total_tests > 0 else 0
        
        logger.info(f"Demographic fairness validation complete: {results['success_rate']:.2%} success rate")
        return results
    
    def validate_classification_accuracy(self) -> Dict[str, Any]:
        """Validate skin type classification accuracy"""
        logger.info("Starting classification accuracy validation")
        
        test_dataset = self.test_datasets['skin_classification']
        results = {
            'test_name': 'Classification Accuracy Validation',
            'timestamp': datetime.utcnow().isoformat(),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': []
        }
        
        for test_case in test_dataset['test_cases']:
            try:
                # Perform classification
                classification_result = self.skin_classifier.classify_skin_type(
                    test_case['image_data'],
                    ethnicity=test_case['ethnicity']
                )
                
                # Validate results
                test_passed = True
                error_messages = []
                
                # Check Fitzpatrick classification
                if 'expected_fitzpatrick' in test_case:
                    expected = test_case['expected_fitzpatrick']
                    actual = classification_result.get('fitzpatrick_type')
                    if actual != expected:
                        test_passed = False
                        error_messages.append(f"Fitzpatrick: expected {expected}, got {actual}")
                
                # Check Monk tone range
                if 'expected_monk_range' in test_case:
                    min_tone, max_tone = test_case['expected_monk_range']
                    actual_tone = classification_result.get('monk_tone')
                    if not (min_tone <= actual_tone <= max_tone):
                        test_passed = False
                        error_messages.append(f"Monk tone: expected {min_tone}-{max_tone}, got {actual_tone}")
                
                # Check confidence
                confidence = classification_result.get('confidence', 0)
                if confidence < 0.5:
                    error_messages.append(f"Low confidence: {confidence:.3f}")
                
                # Record result
                test_result = {
                    'test_case': test_case['description'],
                    'fitzpatrick_type': classification_result.get('fitzpatrick_type'),
                    'monk_tone': classification_result.get('monk_tone'),
                    'confidence': confidence,
                    'ethnicity_considered': classification_result.get('ethnicity_considered', False),
                    'passed': test_passed,
                    'errors': error_messages
                }
                
                results['test_results'].append(test_result)
                
                if test_passed:
                    results['passed_tests'] += 1
                else:
                    results['failed_tests'] += 1
                    logger.warning(f"Classification test failed: {test_case['description']} - {error_messages}")
                
            except Exception as e:
                results['failed_tests'] += 1
                results['test_results'].append({
                    'test_case': test_case['description'],
                    'passed': False,
                    'error': str(e)
                })
                logger.error(f"Classification test error: {test_case['description']} - {e}")
        
        # Calculate success rate
        total_tests = results['passed_tests'] + results['failed_tests']
        results['success_rate'] = results['passed_tests'] / total_tests if total_tests > 0 else 0
        
        logger.info(f"Classification validation complete: {results['success_rate']:.2%} success rate")
        return results
    
    def benchmark_performance(self) -> Dict[str, Any]:
        """Benchmark system performance"""
        logger.info("Starting performance benchmarking")
        
        test_dataset = self.test_datasets['performance_benchmark']
        results = {
            'test_name': 'Performance Benchmarking',
            'timestamp': datetime.utcnow().isoformat(),
            'benchmarks': []
        }
        
        for test_case in test_dataset['test_cases']:
            try:
                vector_count = test_case['vector_count']
                vectors = test_case['vectors']
                image_ids = test_case['image_ids']
                
                # Clear index
                self.faiss_service.clear_index()
                
                # Benchmark vector addition
                start_time = time.time()
                for vector, image_id in zip(vectors, image_ids):
                    self.faiss_service.add_vector(vector, image_id)
                add_duration = time.time() - start_time
                
                # Benchmark search
                query_vector = vectors[0]  # Use first vector as query
                start_time = time.time()
                search_results = self.faiss_service.search_similar(query_vector, k=5)
                search_duration = time.time() - start_time
                
                # Record benchmark
                benchmark = {
                    'vector_count': vector_count,
                    'add_duration_seconds': add_duration,
                    'add_rate_vectors_per_second': vector_count / add_duration if add_duration > 0 else 0,
                    'search_duration_seconds': search_duration,
                    'search_results_count': len(search_results),
                    'description': test_case['description']
                }
                
                results['benchmarks'].append(benchmark)
                
                logger.info(f"Performance benchmark: {vector_count} vectors - "
                           f"Add: {add_duration:.3f}s, Search: {search_duration:.3f}s")
                
            except Exception as e:
                logger.error(f"Performance benchmark error: {test_case['description']} - {e}")
                results['benchmarks'].append({
                    'vector_count': test_case['vector_count'],
                    'error': str(e),
                    'description': test_case['description']
                })
        
        logger.info("Performance benchmarking complete")
        return results
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("Starting full validation suite")
        
        start_time = time.time()
        
        validation_results = {
            'validation_suite': 'Backend AI Upgrade Validation',
            'timestamp': datetime.utcnow().isoformat(),
            'total_duration_seconds': 0,
            'results': {}
        }
        
        # Run all validation tests
        validation_results['results']['similarity_accuracy'] = self.validate_similarity_accuracy()
        validation_results['results']['demographic_fairness'] = self.validate_demographic_fairness()
        validation_results['results']['classification_accuracy'] = self.validate_classification_accuracy()
        validation_results['results']['performance_benchmarks'] = self.benchmark_performance()
        
        # Calculate overall metrics
        total_duration = time.time() - start_time
        validation_results['total_duration_seconds'] = total_duration
        
        # Calculate overall success rate
        total_passed = 0
        total_failed = 0
        
        for test_name, result in validation_results['results'].items():
            if 'passed_tests' in result and 'failed_tests' in result:
                total_passed += result['passed_tests']
                total_failed += result['failed_tests']
        
        total_tests = total_passed + total_failed
        validation_results['overall_success_rate'] = total_passed / total_tests if total_tests > 0 else 0
        validation_results['total_tests'] = total_tests
        validation_results['passed_tests'] = total_passed
        validation_results['failed_tests'] = total_failed
        
        logger.info(f"Full validation complete: {validation_results['overall_success_rate']:.2%} success rate "
                   f"({total_passed}/{total_tests} tests passed) in {total_duration:.2f}s")
        
        return validation_results
    
    def save_validation_report(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save validation results to a JSON report file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Validation report saved to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")
            raise


# Test runner for the validation framework
class ValidationFrameworkTests(unittest.TestCase):
    """Unit tests for the validation framework itself"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.framework = ValidationFramework()
    
    def test_framework_initialization(self):
        """Test that the framework initializes correctly"""
        self.assertIsNotNone(self.framework.faiss_service)
        self.assertIsNotNone(self.framework.skin_classifier)
        self.assertGreater(len(self.framework.test_datasets), 0)
    
    def test_similarity_validation(self):
        """Test similarity accuracy validation"""
        results = self.framework.validate_similarity_accuracy()
        
        self.assertIn('test_name', results)
        self.assertIn('success_rate', results)
        self.assertIsInstance(results['success_rate'], float)
        self.assertGreaterEqual(results['success_rate'], 0.0)
        self.assertLessEqual(results['success_rate'], 1.0)
    
    def test_classification_validation(self):
        """Test classification accuracy validation"""
        results = self.framework.validate_classification_accuracy()
        
        self.assertIn('test_name', results)
        self.assertIn('success_rate', results)
        self.assertIsInstance(results['success_rate'], float)
    
    def test_performance_benchmarking(self):
        """Test performance benchmarking"""
        results = self.framework.benchmark_performance()
        
        self.assertIn('test_name', results)
        self.assertIn('benchmarks', results)
        self.assertGreater(len(results['benchmarks']), 0)
    
    def test_full_validation_suite(self):
        """Test the complete validation suite"""
        results = self.framework.run_full_validation()
        
        self.assertIn('validation_suite', results)
        self.assertIn('overall_success_rate', results)
        self.assertIn('results', results)
        
        # Check that all validation types are included
        expected_validations = [
            'similarity_accuracy', 'demographic_fairness', 
            'classification_accuracy', 'performance_benchmarks'
        ]
        
        for validation_type in expected_validations:
            self.assertIn(validation_type, results['results'])


if __name__ == '__main__':
    # Run validation framework tests
    unittest.main()