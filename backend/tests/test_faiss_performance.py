"""
Performance tests for Production FAISS Service
These tests measure performance with large-scale vector operations
"""
import unittest
import time
import numpy as np
import tempfile
import os
import shutil
from unittest.mock import patch

from app.services.production_faiss_service import ProductionFAISSService


class TestFAISSPerformance(unittest.TestCase):
    """Performance tests for FAISS Service"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.dimension = 512  # Realistic dimension for embeddings
        cls.large_batch_size = 1000
        cls.small_batch_size = 100
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test class"""
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up each test"""
        self.index_path = os.path.join(self.temp_dir, f"perf_test_{int(time.time())}")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_large_batch_addition_performance(self):
        """Test performance of adding large batches of vectors"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False  # Disable auto-save for pure performance measurement
        
        # Generate test data
        vectors = np.random.rand(self.large_batch_size, self.dimension).astype(np.float32)
        image_ids = [f"perf_image_{i}" for i in range(self.large_batch_size)]
        
        # Measure batch addition time
        start_time = time.time()
        results = service.add_vectors_batch(vectors, image_ids)
        batch_time = time.time() - start_time
        
        # Verify results
        self.assertEqual(len(results), self.large_batch_size)
        self.assertTrue(all(results))
        self.assertEqual(len(service.image_ids), self.large_batch_size)
        
        # Performance assertions
        vectors_per_second = self.large_batch_size / batch_time
        print(f"Batch addition: {vectors_per_second:.2f} vectors/second")
        
        # Should be able to add at least 100 vectors per second
        self.assertGreater(vectors_per_second, 100, 
                          f"Batch addition too slow: {vectors_per_second:.2f} vectors/second")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_individual_addition_performance(self):
        """Test performance of adding individual vectors"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Generate test data
        vectors = np.random.rand(self.small_batch_size, self.dimension).astype(np.float32)
        image_ids = [f"individual_image_{i}" for i in range(self.small_batch_size)]
        
        # Measure individual addition time
        start_time = time.time()
        for i, (vector, image_id) in enumerate(zip(vectors, image_ids)):
            result = service.add_vector(vector, image_id)
            self.assertTrue(result)
        individual_time = time.time() - start_time
        
        # Performance assertions
        vectors_per_second = self.small_batch_size / individual_time
        print(f"Individual addition: {vectors_per_second:.2f} vectors/second")
        
        # Should be able to add at least 50 vectors per second individually
        self.assertGreater(vectors_per_second, 50, 
                          f"Individual addition too slow: {vectors_per_second:.2f} vectors/second")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_search_performance_with_large_index(self):
        """Test search performance with large index"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add large number of vectors
        vectors = np.random.rand(self.large_batch_size, self.dimension).astype(np.float32)
        image_ids = [f"search_test_image_{i}" for i in range(self.large_batch_size)]
        
        # Add vectors in batch for setup
        results = service.add_vectors_batch(vectors, image_ids)
        self.assertTrue(all(results))
        
        # Generate query vectors
        num_queries = 100
        query_vectors = np.random.rand(num_queries, self.dimension).astype(np.float32)
        
        # Measure search time
        start_time = time.time()
        for query_vector in query_vectors:
            results = service.search_similar(query_vector, k=10)
            self.assertEqual(len(results), 10)  # Should return top 10
        search_time = time.time() - start_time
        
        # Performance assertions
        searches_per_second = num_queries / search_time
        print(f"Search performance: {searches_per_second:.2f} searches/second on {self.large_batch_size} vectors")
        
        # Should be able to perform at least 10 searches per second
        self.assertGreater(searches_per_second, 10, 
                          f"Search too slow: {searches_per_second:.2f} searches/second")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_save_load_performance(self):
        """Test save and load performance with large index"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Add vectors
        vectors = np.random.rand(self.large_batch_size, self.dimension).astype(np.float32)
        image_ids = [f"save_load_image_{i}" for i in range(self.large_batch_size)]
        
        results = service.add_vectors_batch(vectors, image_ids)
        self.assertTrue(all(results))
        
        # Measure save time
        start_time = time.time()
        save_result = service.save_index()
        save_time = time.time() - start_time
        
        self.assertTrue(save_result)
        print(f"Save time for {self.large_batch_size} vectors: {save_time:.2f} seconds")
        
        # Create new service instance to test loading
        new_service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Measure load time
        start_time = time.time()
        load_result = new_service.load_index()
        load_time = time.time() - start_time
        
        self.assertTrue(load_result)
        self.assertEqual(len(new_service.image_ids), self.large_batch_size)
        print(f"Load time for {self.large_batch_size} vectors: {load_time:.2f} seconds")
        
        # Performance assertions
        # Save and load should complete within reasonable time
        self.assertLess(save_time, 10.0, f"Save too slow: {save_time:.2f} seconds")
        self.assertLess(load_time, 10.0, f"Load too slow: {load_time:.2f} seconds")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_memory_usage_estimation(self):
        """Test memory usage estimation accuracy"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add vectors and check memory estimation
        batch_sizes = [100, 500, 1000]
        
        for batch_size in batch_sizes:
            # Clear index
            service.clear_index()
            
            # Add vectors
            vectors = np.random.rand(batch_size, self.dimension).astype(np.float32)
            image_ids = [f"memory_test_{i}" for i in range(batch_size)]
            
            results = service.add_vectors_batch(vectors, image_ids)
            self.assertTrue(all(results))
            
            # Get stats
            stats = service.get_index_stats()
            estimated_mb = stats['estimated_memory_mb']
            
            # Calculate expected memory usage
            # Each vector: dimension * 4 bytes (float32)
            expected_mb = (batch_size * self.dimension * 4) / (1024 * 1024)
            
            print(f"Batch size {batch_size}: Estimated {estimated_mb:.2f} MB, Expected {expected_mb:.2f} MB")
            
            # Estimation should be reasonably close (within 20% margin)
            self.assertAlmostEqual(estimated_mb, expected_mb, delta=expected_mb * 0.2)
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_concurrent_search_performance(self):
        """Test concurrent search performance"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        import threading
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        service.auto_save = False
        
        # Add vectors for searching
        vectors = np.random.rand(self.large_batch_size, self.dimension).astype(np.float32)
        image_ids = [f"concurrent_image_{i}" for i in range(self.large_batch_size)]
        
        results = service.add_vectors_batch(vectors, image_ids)
        self.assertTrue(all(results))
        
        # Concurrent search test
        num_threads = 4
        searches_per_thread = 25
        results_list = []
        errors_list = []
        
        def search_worker():
            try:
                thread_results = []
                for _ in range(searches_per_thread):
                    query_vector = np.random.rand(self.dimension).astype(np.float32)
                    search_results = service.search_similar(query_vector, k=5)
                    thread_results.append(len(search_results))
                results_list.append(thread_results)
            except Exception as e:
                errors_list.append(e)
        
        # Start concurrent searches
        threads = []
        start_time = time.time()
        
        for _ in range(num_threads):
            thread = threading.Thread(target=search_worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        concurrent_time = time.time() - start_time
        
        # Verify results
        self.assertEqual(len(errors_list), 0, f"Errors in concurrent search: {errors_list}")
        self.assertEqual(len(results_list), num_threads)
        
        total_searches = num_threads * searches_per_thread
        searches_per_second = total_searches / concurrent_time
        
        print(f"Concurrent search: {searches_per_second:.2f} searches/second with {num_threads} threads")
        
        # Should handle concurrent searches efficiently
        self.assertGreater(searches_per_second, 20, 
                          f"Concurrent search too slow: {searches_per_second:.2f} searches/second")
    
    @unittest.skipUnless(os.environ.get('RUN_PERFORMANCE_TESTS') == 'true', 
                        "Performance tests disabled. Set RUN_PERFORMANCE_TESTS=true to enable")
    @patch('app.services.production_faiss_service.FAISS_AVAILABLE', True)
    def test_vector_normalization_performance(self):
        """Test vector normalization performance"""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not available for performance testing")
        
        service = ProductionFAISSService(
            dimension=self.dimension,
            index_path=self.index_path
        )
        
        # Generate test vectors
        num_vectors = 10000
        vectors = np.random.rand(num_vectors, self.dimension).astype(np.float32)
        
        # Measure normalization time
        start_time = time.time()
        normalized_vectors = []
        for vector in vectors:
            normalized = service._normalize_vector(vector)
            normalized_vectors.append(normalized)
        normalization_time = time.time() - start_time
        
        # Verify normalization
        for normalized in normalized_vectors[:10]:  # Check first 10
            norm = np.linalg.norm(normalized)
            self.assertAlmostEqual(norm, 1.0, places=6)
        
        # Performance assertion
        vectors_per_second = num_vectors / normalization_time
        print(f"Vector normalization: {vectors_per_second:.2f} vectors/second")
        
        # Should normalize at least 1000 vectors per second
        self.assertGreater(vectors_per_second, 1000, 
                          f"Normalization too slow: {vectors_per_second:.2f} vectors/second")
    
    def test_performance_with_different_dimensions(self):
        """Test performance scaling with different vector dimensions"""
        dimensions = [128, 256, 512, 1024]
        batch_size = 100
        
        for dim in dimensions:
            with self.subTest(dimension=dim):
                index_path = os.path.join(self.temp_dir, f"dim_test_{dim}")
                
                try:
                    import faiss
                    service = ProductionFAISSService(
                        dimension=dim,
                        index_path=index_path
                    )
                    service.auto_save = False
                    
                    # Generate test data
                    vectors = np.random.rand(batch_size, dim).astype(np.float32)
                    image_ids = [f"dim_{dim}_image_{i}" for i in range(batch_size)]
                    
                    # Measure addition time
                    start_time = time.time()
                    results = service.add_vectors_batch(vectors, image_ids)
                    add_time = time.time() - start_time
                    
                    self.assertTrue(all(results))
                    
                    # Measure search time
                    query_vector = np.random.rand(dim).astype(np.float32)
                    start_time = time.time()
                    search_results = service.search_similar(query_vector, k=10)
                    search_time = time.time() - start_time
                    
                    self.assertEqual(len(search_results), 10)
                    
                    print(f"Dimension {dim}: Add {add_time:.3f}s, Search {search_time:.3f}s")
                    
                    # Performance should scale reasonably with dimension
                    # Higher dimensions should not be exponentially slower
                    self.assertLess(add_time, 5.0, f"Addition too slow for dimension {dim}")
                    self.assertLess(search_time, 1.0, f"Search too slow for dimension {dim}")
                    
                except ImportError:
                    self.skipTest(f"FAISS not available for dimension {dim} test")


if __name__ == '__main__':
    # Print instructions for running performance tests
    print("Performance Test Instructions:")
    print("1. Install FAISS: pip install faiss-cpu")
    print("2. Enable performance tests: export RUN_PERFORMANCE_TESTS=true")
    print("3. Run tests: python -m pytest backend/tests/test_faiss_performance.py -v -s")
    print("Note: Performance tests may take several minutes to complete.")
    print()
    
    unittest.main()