"""
Memory-efficient model loading and inference optimizations for Vercel deployment
"""
import os
import logging
import time
import threading
from typing import Dict, Any, Optional, Union, List
from functools import lru_cache
import pickle
import gzip
from contextlib import contextmanager

from app.performance import measure_performance, performance_monitor
from app.vercel_optimizations import MemoryOptimizer, vercel_cached

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading and memory optimization"""
    
    def __init__(self):
        self.loaded_models = {}
        self.model_metadata = {}
        self.memory_usage = {}
        self._lock = threading.RLock()
        self.lazy_loading = True
        self.model_compression = True
    
    @contextmanager
    def model_context(self, model_name: str):
        """Context manager for temporary model loading"""
        model = None
        try:
            model = self.get_model(model_name)
            yield model
        finally:
            if model and self.lazy_loading:
                # Optionally unload model after use to save memory
                self._maybe_unload_model(model_name)
    
    def get_model(self, model_name: str, force_reload: bool = False):
        """Get model with lazy loading and memory optimization"""
        with self._lock:
            if not force_reload and model_name in self.loaded_models:
                logger.debug(f"Using cached model: {model_name}")
                return self.loaded_models[model_name]
            
            logger.info(f"Loading model: {model_name}")
            start_time = time.time()
            
            try:
                model = self._load_model(model_name)
                load_time = time.time() - start_time
                
                # Store model and metadata
                self.loaded_models[model_name] = model
                self.model_metadata[model_name] = {
                    'load_time': load_time,
                    'loaded_at': time.time(),
                    'access_count': 1,
                    'last_accessed': time.time()
                }
                
                # Track memory usage
                self._update_memory_usage(model_name)
                
                logger.info(f"Model {model_name} loaded in {load_time:.3f}s")
                performance_monitor.record_metric(
                    f'model_load_time_{model_name}', load_time, 'seconds'
                )
                
                return model
                
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                raise
    
    def _load_model(self, model_name: str):
        """Load specific model based on name"""
        if model_name == 'faiss_index':
            return self._load_faiss_model()
        elif model_name == 'skin_classifier':
            return self._load_skin_classifier_model()
        elif model_name == 'demographic_weights':
            return self._load_demographic_weights()
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def _load_faiss_model(self):
        """Load FAISS index with memory optimization"""
        try:
            import faiss
            import numpy as np
            
            # Use memory-efficient configuration
            config = MemoryOptimizer.get_memory_efficient_config()
            dimension = config['faiss_dimension']
            
            # Create lightweight index for cold starts
            if self._is_cold_start():
                logger.info("Creating lightweight FAISS index for cold start")
                index = faiss.IndexFlatIP(dimension)
                
                # Add some dummy vectors to initialize
                dummy_vectors = np.random.rand(10, dimension).astype(np.float32)
                dummy_vectors = dummy_vectors / np.linalg.norm(dummy_vectors, axis=1, keepdims=True)
                index.add(dummy_vectors)
                
                return {
                    'index': index,
                    'dimension': dimension,
                    'is_lightweight': True,
                    'vector_count': 10
                }
            
            # Load full index if available
            index_path = os.environ.get('FAISS_INDEX_PATH', 'faiss_index.index')
            if os.path.exists(index_path):
                logger.info(f"Loading FAISS index from {index_path}")
                index = faiss.read_index(index_path)
                
                return {
                    'index': index,
                    'dimension': index.d,
                    'is_lightweight': False,
                    'vector_count': index.ntotal
                }
            else:
                # Create new index
                logger.info("Creating new FAISS index")
                index = faiss.IndexFlatIP(dimension)
                
                return {
                    'index': index,
                    'dimension': dimension,
                    'is_lightweight': False,
                    'vector_count': 0
                }
                
        except ImportError:
            logger.warning("FAISS not available, using mock index")
            return self._create_mock_faiss_index()
    
    def _load_skin_classifier_model(self):
        """Load skin classifier with memory optimization"""
        # For now, return a lightweight classifier configuration
        # In production, this would load actual ML models
        
        classifier_config = {
            'fitzpatrick_scale': {
                'I': {'description': 'Always burns, never tans', 'range': (0, 10)},
                'II': {'description': 'Usually burns, tans minimally', 'range': (11, 20)},
                'III': {'description': 'Sometimes burns, tans gradually', 'range': (21, 30)},
                'IV': {'description': 'Burns minimally, always tans well', 'range': (31, 40)},
                'V': {'description': 'Very rarely burns, tans very easily', 'range': (41, 50)},
                'VI': {'description': 'Never burns, always tans darkly', 'range': (51, 60)}
            },
            'monk_scale': {
                'ranges': [(i, i+5) for i in range(1, 11)],
                'descriptions': [f'Monk Scale Tone {i}' for i in range(1, 11)]
            },
            'ethnicity_adjustments': {
                'caucasian': {'fitzpatrick_bias': -0.5, 'monk_bias': -1.0},
                'african': {'fitzpatrick_bias': 1.5, 'monk_bias': 3.0},
                'east_asian': {'fitzpatrick_bias': 0.0, 'monk_bias': 0.5},
                'south_asian': {'fitzpatrick_bias': 0.5, 'monk_bias': 1.5},
                'hispanic': {'fitzpatrick_bias': 0.2, 'monk_bias': 1.0},
                'middle_eastern': {'fitzpatrick_bias': 0.3, 'monk_bias': 1.2}
            },
            'confidence_thresholds': {
                'high': 0.8,
                'medium': 0.6,
                'low': 0.4
            }
        }
        
        return classifier_config
    
    def _load_demographic_weights(self):
        """Load demographic weighting configuration"""
        return {
            'ethnicity_weight': 0.4,
            'skin_type_weight': 0.3,
            'age_group_weight': 0.3,
            'similarity_threshold': 0.7,
            'boost_factor': 1.5,
            'demographic_combinations': {
                ('caucasian', 'normal', '25-35'): 1.0,
                ('african', 'oily', '18-25'): 1.0,
                ('east_asian', 'sensitive', '25-35'): 1.0,
                # Add more combinations as needed
            }
        }
    
    def _create_mock_faiss_index(self):
        """Create mock FAISS index for testing"""
        return {
            'index': None,
            'dimension': 128,
            'is_lightweight': True,
            'is_mock': True,
            'vector_count': 0
        }
    
    def _is_cold_start(self) -> bool:
        """Check if this is a cold start"""
        from app.vercel_optimizations import vercel_optimizer
        return vercel_optimizer.is_cold_start()
    
    def _update_memory_usage(self, model_name: str):
        """Update memory usage tracking for model"""
        try:
            from app.vercel_optimizations import get_memory_usage
            memory_info = get_memory_usage()
            
            self.memory_usage[model_name] = {
                'timestamp': time.time(),
                'memory_mb': memory_info.get('rss_mb', 0),
                'model_name': model_name
            }
            
        except Exception as e:
            logger.warning(f"Could not track memory usage for {model_name}: {e}")
    
    def _maybe_unload_model(self, model_name: str):
        """Conditionally unload model to save memory"""
        if not self.lazy_loading:
            return
        
        with self._lock:
            if model_name not in self.model_metadata:
                return
            
            metadata = self.model_metadata[model_name]
            
            # Unload if not accessed recently and memory pressure is high
            time_since_access = time.time() - metadata['last_accessed']
            
            if time_since_access > 300:  # 5 minutes
                try:
                    memory_info = get_memory_usage()
                    if memory_info.get('percent', 0) > 80:  # High memory usage
                        logger.info(f"Unloading model {model_name} due to memory pressure")
                        del self.loaded_models[model_name]
                        del self.model_metadata[model_name]
                        self.memory_usage.pop(model_name, None)
                        
                        # Force garbage collection
                        import gc
                        gc.collect()
                        
                except Exception as e:
                    logger.warning(f"Error during model unloading: {e}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model loading and usage statistics"""
        with self._lock:
            stats = {
                'loaded_models': list(self.loaded_models.keys()),
                'model_count': len(self.loaded_models),
                'metadata': self.model_metadata.copy(),
                'memory_usage': self.memory_usage.copy(),
                'lazy_loading': self.lazy_loading,
                'model_compression': self.model_compression
            }
            
            # Calculate total memory usage
            total_memory = sum(
                usage.get('memory_mb', 0) 
                for usage in self.memory_usage.values()
            )
            stats['total_memory_mb'] = total_memory
            
            return stats
    
    def cleanup_unused_models(self) -> int:
        """Clean up unused models to free memory"""
        with self._lock:
            current_time = time.time()
            models_to_remove = []
            
            for model_name, metadata in self.model_metadata.items():
                time_since_access = current_time - metadata['last_accessed']
                
                # Remove models not accessed in last 10 minutes
                if time_since_access > 600:
                    models_to_remove.append(model_name)
            
            for model_name in models_to_remove:
                logger.info(f"Cleaning up unused model: {model_name}")
                self.loaded_models.pop(model_name, None)
                self.model_metadata.pop(model_name, None)
                self.memory_usage.pop(model_name, None)
            
            if models_to_remove:
                import gc
                gc.collect()
            
            return len(models_to_remove)


class InferenceOptimizer:
    """Optimizes model inference for memory efficiency"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.batch_size = 32
        self.max_batch_wait_time = 0.1  # 100ms
        self.pending_requests = []
        self._batch_lock = threading.Lock()
    
    @measure_performance('optimized_inference')
    def run_inference(self, model_name: str, input_data: Any, **kwargs) -> Any:
        """Run optimized inference"""
        with self.model_manager.model_context(model_name) as model:
            if model is None:
                raise ValueError(f"Model {model_name} not available")
            
            # Update access tracking
            if model_name in self.model_manager.model_metadata:
                self.model_manager.model_metadata[model_name]['last_accessed'] = time.time()
                self.model_manager.model_metadata[model_name]['access_count'] += 1
            
            # Run model-specific inference
            if model_name == 'faiss_index':
                return self._run_faiss_inference(model, input_data, **kwargs)
            elif model_name == 'skin_classifier':
                return self._run_classification_inference(model, input_data, **kwargs)
            elif model_name == 'demographic_weights':
                return self._run_demographic_inference(model, input_data, **kwargs)
            else:
                raise ValueError(f"Unknown inference type for model: {model_name}")
    
    def _run_faiss_inference(self, model: Dict[str, Any], query_vector, **kwargs) -> List:
        """Run FAISS similarity search"""
        index = model['index']
        k = kwargs.get('k', 5)
        
        if model.get('is_mock', False):
            # Return mock results
            return [(f'mock_result_{i}', 0.9 - i * 0.1) for i in range(k)]
        
        if index is None:
            return []
        
        try:
            import numpy as np
            
            # Ensure query vector is properly formatted
            if not isinstance(query_vector, np.ndarray):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # Normalize vector for cosine similarity
            query_vector = query_vector / np.linalg.norm(query_vector, axis=1, keepdims=True)
            
            # Search
            distances, indices = index.search(query_vector, k)
            
            # Convert to results format
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx != -1:  # Valid result
                    similarity = 1.0 - (distance / 4.0)  # Convert distance to similarity
                    results.append((f'image_{idx}', similarity))
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS inference error: {e}")
            return []
    
    def _run_classification_inference(self, model: Dict[str, Any], image_data, **kwargs) -> Dict[str, Any]:
        """Run skin type classification"""
        ethnicity = kwargs.get('ethnicity', 'unknown')
        
        try:
            # Simulate classification based on image properties
            # In production, this would use actual ML models
            
            import numpy as np
            
            if isinstance(image_data, np.ndarray):
                # Calculate average brightness as a proxy for skin tone
                brightness = np.mean(image_data)
                
                # Normalize brightness to 0-1 range
                normalized_brightness = min(max(brightness, 0), 1)
            else:
                # Default brightness for non-array data
                normalized_brightness = 0.5
            
            # Apply ethnicity adjustments
            ethnicity_adjustments = model.get('ethnicity_adjustments', {})
            adjustment = ethnicity_adjustments.get(ethnicity, {'fitzpatrick_bias': 0, 'monk_bias': 0})
            
            # Calculate Fitzpatrick type (I-VI)
            fitzpatrick_score = (normalized_brightness * 60) + adjustment['fitzpatrick_bias']
            fitzpatrick_score = max(0, min(60, fitzpatrick_score))
            
            fitzpatrick_scale = model['fitzpatrick_scale']
            fitzpatrick_type = 'III'  # Default
            
            for ftype, info in fitzpatrick_scale.items():
                if info['range'][0] <= fitzpatrick_score <= info['range'][1]:
                    fitzpatrick_type = ftype
                    break
            
            # Calculate Monk scale (1-10)
            monk_score = (normalized_brightness * 10) + adjustment['monk_bias']
            monk_tone = max(1, min(10, int(monk_score)))
            
            # Calculate confidence based on how clear the classification is
            confidence = 0.8 - abs(normalized_brightness - 0.5)  # Higher confidence for extreme values
            confidence = max(0.4, min(0.95, confidence))
            
            return {
                'fitzpatrick_type': fitzpatrick_type,
                'fitzpatrick_description': fitzpatrick_scale[fitzpatrick_type]['description'],
                'monk_tone': monk_tone,
                'monk_description': f'Monk Scale Tone {monk_tone}',
                'confidence': confidence,
                'ethnicity_considered': ethnicity != 'unknown',
                'brightness_score': normalized_brightness
            }
            
        except Exception as e:
            logger.error(f"Classification inference error: {e}")
            return {
                'fitzpatrick_type': 'III',
                'fitzpatrick_description': 'Sometimes burns, tans gradually',
                'monk_tone': 5,
                'monk_description': 'Monk Scale Tone 5',
                'confidence': 0.5,
                'ethnicity_considered': False,
                'error': str(e)
            }
    
    def _run_demographic_inference(self, model: Dict[str, Any], demographics: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Calculate demographic weights"""
        try:
            ethnicity = demographics.get('ethnicity', 'unknown')
            skin_type = demographics.get('skin_type', 'normal')
            age_group = demographics.get('age_group', '25-35')
            
            # Get base weights
            ethnicity_weight = model.get('ethnicity_weight', 0.4)
            skin_type_weight = model.get('skin_type_weight', 0.3)
            age_group_weight = model.get('age_group_weight', 0.3)
            
            # Check for pre-calculated combinations
            combination_key = (ethnicity, skin_type, age_group)
            combinations = model.get('demographic_combinations', {})
            
            if combination_key in combinations:
                base_weight = combinations[combination_key]
            else:
                # Calculate base weight
                base_weight = 1.0
            
            # Apply boost factor for exact matches
            boost_factor = model.get('boost_factor', 1.5)
            similarity_threshold = model.get('similarity_threshold', 0.7)
            
            return {
                'ethnicity_weight': ethnicity_weight,
                'skin_type_weight': skin_type_weight,
                'age_group_weight': age_group_weight,
                'base_weight': base_weight,
                'boost_factor': boost_factor,
                'similarity_threshold': similarity_threshold,
                'demographics': demographics
            }
            
        except Exception as e:
            logger.error(f"Demographic inference error: {e}")
            return {
                'ethnicity_weight': 0.4,
                'skin_type_weight': 0.3,
                'age_group_weight': 0.3,
                'base_weight': 1.0,
                'boost_factor': 1.5,
                'similarity_threshold': 0.7,
                'error': str(e)
            }
    
    @vercel_cached(ttl=300, compress=True)
    def cached_inference(self, model_name: str, input_hash: str, **kwargs) -> Any:
        """Cached inference for repeated requests"""
        # This would be called with a hash of the input data
        # The actual input data would be passed separately
        return self.run_inference(model_name, kwargs.get('input_data'), **kwargs)


# Global instances
model_manager = ModelManager()
inference_optimizer = InferenceOptimizer(model_manager)


@lru_cache(maxsize=128)
def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get cached model configuration"""
    return MemoryOptimizer.get_memory_efficient_config()


def optimize_model_loading():
    """Apply model loading optimizations"""
    logger.info("Applying model loading optimizations...")
    
    try:
        # Pre-load essential models during cold start
        if model_manager._is_cold_start():
            logger.info("Pre-loading essential models for cold start")
            
            # Load lightweight models
            model_manager.get_model('demographic_weights')
            model_manager.get_model('skin_classifier')
            
            # Only load FAISS if needed
            if os.environ.get('PRELOAD_FAISS', 'false').lower() == 'true':
                model_manager.get_model('faiss_index')
        
        # Configure memory-efficient settings
        config = MemoryOptimizer.get_memory_efficient_config()
        
        # Set batch size for inference
        inference_optimizer.batch_size = config.get('batch_size', 32)
        
        logger.info("Model loading optimizations applied successfully")
        
    except Exception as e:
        logger.error(f"Model loading optimization failed: {e}")
        raise


def get_model_performance_stats() -> Dict[str, Any]:
    """Get comprehensive model performance statistics"""
    return {
        'model_manager': model_manager.get_model_stats(),
        'inference_optimizer': {
            'batch_size': inference_optimizer.batch_size,
            'max_batch_wait_time': inference_optimizer.max_batch_wait_time,
            'pending_requests': len(inference_optimizer.pending_requests)
        },
        'memory_config': get_model_config('default'),
        'timestamp': time.time()
    }


def cleanup_model_resources():
    """Clean up model resources to free memory"""
    logger.info("Cleaning up model resources...")
    
    try:
        # Clean up unused models
        cleaned_models = model_manager.cleanup_unused_models()
        
        # Force garbage collection
        import gc
        collected_objects = gc.collect()
        
        # Get memory usage after cleanup
        from app.vercel_optimizations import get_memory_usage
        memory_usage = get_memory_usage()
        
        cleanup_stats = {
            'cleaned_models': cleaned_models,
            'gc_collected': collected_objects,
            'memory_usage': memory_usage,
            'timestamp': time.time()
        }
        
        logger.info(f"Model cleanup complete: {cleaned_models} models cleaned, "
                   f"{collected_objects} objects collected")
        
        return cleanup_stats
        
    except Exception as e:
        logger.error(f"Model cleanup failed: {e}")
        return {'error': str(e), 'timestamp': time.time()}


# Optimized inference functions
def optimized_faiss_search(query_vector, k: int = 5) -> List:
    """Optimized FAISS similarity search"""
    return inference_optimizer.run_inference('faiss_index', query_vector, k=k)


def optimized_skin_classification(image_data, ethnicity: str = 'unknown') -> Dict[str, Any]:
    """Optimized skin type classification"""
    return inference_optimizer.run_inference('skin_classifier', image_data, ethnicity=ethnicity)


def optimized_demographic_weighting(demographics: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized demographic weight calculation"""
    return inference_optimizer.run_inference('demographic_weights', demographics)