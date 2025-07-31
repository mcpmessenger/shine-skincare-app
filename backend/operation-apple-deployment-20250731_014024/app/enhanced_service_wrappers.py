"""
Enhanced service wrappers with comprehensive error handling, monitoring, and recovery
"""
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from functools import wraps

from app.error_handlers import (
    safe_service_call_with_retry, GoogleVisionError, FAISSError,
    SkinClassificationError, DemographicSearchError, VectorProcessingError
)
from app.error_recovery import error_recovery_manager, with_error_recovery
from app.monitoring import monitor_service_call, get_service_monitor
from app.logging_config import get_service_logger, log_service_operation

logger = logging.getLogger(__name__)


class EnhancedGoogleVisionWrapper:
    """Enhanced wrapper for Google Vision service with error handling and monitoring"""
    
    def __init__(self, google_vision_service):
        self.service = google_vision_service
        self.service_name = 'google_vision'
        self.logger = get_service_logger(self.service_name)
        self.monitor = get_service_monitor(self.service_name)
    
    @monitor_service_call('google_vision')
    @with_error_recovery('google_vision', 'analyze_image_from_bytes')
    def analyze_image_from_bytes(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image with comprehensive error handling and monitoring
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Analysis results with enhanced error handling
        """
        start_time = time.time()
        
        try:
            self.logger.info("Starting Google Vision image analysis")
            
            # Validate input
            if not image_data or len(image_data) == 0:
                raise GoogleVisionError(
                    message="Empty image data provided",
                    details={'data_length': len(image_data) if image_data else 0}
                )
            
            # Check service availability
            if not self.service.is_available():
                raise GoogleVisionError(
                    message="Google Vision service is not available",
                    details={'service_status': 'unavailable'}
                )
            
            # Perform analysis with monitoring
            result = self.service.analyze_image_from_bytes(image_data)
            
            # Validate result
            if not result or result.get('status') == 'error':
                error_msg = result.get('error', 'Unknown analysis error') if result else 'No result returned'
                raise GoogleVisionError(
                    message=f"Analysis failed: {error_msg}",
                    details={'result': result}
                )
            
            duration = time.time() - start_time
            self.logger.info(f"Google Vision analysis completed successfully in {duration:.3f}s")
            
            # Log performance metrics
            log_service_operation(
                self.service_name, 'analyze_image_from_bytes',
                success=True, duration=duration,
                details={'result_status': result.get('status')}
            )
            
            return result
            
        except GoogleVisionError:
            # Re-raise Google Vision specific errors
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Google Vision analysis failed after {duration:.3f}s: {e}")
            
            # Log failure
            log_service_operation(
                self.service_name, 'analyze_image_from_bytes',
                success=False, duration=duration,
                details={'error': str(e)}
            )
            
            raise GoogleVisionError(
                message=f"Image analysis failed: {str(e)}",
                details={'duration': duration, 'original_error': str(e)}
            )
    
    @monitor_service_call('google_vision')
    @with_error_recovery('google_vision', 'detect_faces')
    def detect_faces(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Enhanced face detection with error handling"""
        start_time = time.time()
        
        try:
            self.logger.debug("Starting face detection")
            
            if not self.service.is_available():
                raise GoogleVisionError("Google Vision service unavailable for face detection")
            
            faces = self.service.detect_faces(image_data)
            
            duration = time.time() - start_time
            self.logger.debug(f"Face detection completed: {len(faces)} faces found in {duration:.3f}s")
            
            log_service_operation(
                self.service_name, 'detect_faces',
                success=True, duration=duration,
                details={'faces_found': len(faces)}
            )
            
            return faces
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Face detection failed: {e}")
            
            log_service_operation(
                self.service_name, 'detect_faces',
                success=False, duration=duration,
                details={'error': str(e)}
            )
            
            raise GoogleVisionError(f"Face detection failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check service availability with monitoring"""
        try:
            return self.service.is_available()
        except Exception as e:
            self.logger.warning(f"Error checking Google Vision availability: {e}")
            return False


class EnhancedFAISSWrapper:
    """Enhanced wrapper for FAISS service with error handling and monitoring"""
    
    def __init__(self, faiss_service):
        self.service = faiss_service
        self.service_name = 'faiss'
        self.logger = get_service_logger(self.service_name)
        self.monitor = get_service_monitor(self.service_name)
    
    @monitor_service_call('faiss')
    @with_error_recovery('faiss', 'add_vector')
    def add_vector(self, vector, image_id: str) -> bool:
        """Enhanced vector addition with error handling"""
        start_time = time.time()
        
        try:
            self.logger.debug(f"Adding vector for image {image_id}")
            
            # Validate inputs
            if vector is None:
                raise FAISSError(
                    message="Vector is None",
                    operation="add_vector",
                    details={'image_id': image_id}
                )
            
            if not image_id or not isinstance(image_id, str):
                raise FAISSError(
                    message="Invalid image_id",
                    operation="add_vector",
                    details={'image_id': image_id, 'image_id_type': type(image_id).__name__}
                )
            
            # Check service availability
            if not self.service.is_available():
                raise FAISSError(
                    message="FAISS service is not available",
                    operation="add_vector",
                    details={'service_status': 'unavailable'}
                )
            
            # Add vector with monitoring
            success = self.service.add_vector(vector, image_id)
            
            duration = time.time() - start_time
            
            if success:
                self.logger.debug(f"Vector added successfully for {image_id} in {duration:.3f}s")
                log_service_operation(
                    self.service_name, 'add_vector',
                    success=True, duration=duration,
                    details={'image_id': image_id}
                )
            else:
                self.logger.warning(f"Vector addition failed for {image_id}")
                log_service_operation(
                    self.service_name, 'add_vector',
                    success=False, duration=duration,
                    details={'image_id': image_id, 'reason': 'service_returned_false'}
                )
                
                raise FAISSError(
                    message="Vector addition returned False",
                    operation="add_vector",
                    details={'image_id': image_id}
                )
            
            return success
            
        except FAISSError:
            # Re-raise FAISS specific errors
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Vector addition failed for {image_id}: {e}")
            
            log_service_operation(
                self.service_name, 'add_vector',
                success=False, duration=duration,
                details={'image_id': image_id, 'error': str(e)}
            )
            
            raise FAISSError(
                message=f"Failed to add vector: {str(e)}",
                operation="add_vector",
                details={'image_id': image_id, 'original_error': str(e)}
            )
    
    @monitor_service_call('faiss')
    @with_error_recovery('faiss', 'search_similar')
    def search_similar(self, query_vector, k: int = 5) -> List[Tuple[str, float]]:
        """Enhanced similarity search with error handling"""
        start_time = time.time()
        
        try:
            self.logger.debug(f"Searching for {k} similar vectors")
            
            # Validate inputs
            if query_vector is None:
                raise FAISSError(
                    message="Query vector is None",
                    operation="search_similar",
                    details={'k': k}
                )
            
            if k <= 0 or k > 100:
                raise FAISSError(
                    message=f"Invalid k value: {k}",
                    operation="search_similar",
                    details={'k': k, 'valid_range': '1-100'}
                )
            
            # Check service availability
            if not self.service.is_available():
                raise FAISSError(
                    message="FAISS service is not available",
                    operation="search_similar",
                    details={'service_status': 'unavailable'}
                )
            
            # Perform search
            results = self.service.search_similar(query_vector, k)
            
            duration = time.time() - start_time
            self.logger.debug(f"Similarity search completed: {len(results)} results in {duration:.3f}s")
            
            log_service_operation(
                self.service_name, 'search_similar',
                success=True, duration=duration,
                details={'k': k, 'results_found': len(results)}
            )
            
            return results
            
        except FAISSError:
            # Re-raise FAISS specific errors
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Similarity search failed: {e}")
            
            log_service_operation(
                self.service_name, 'search_similar',
                success=False, duration=duration,
                details={'k': k, 'error': str(e)}
            )
            
            raise FAISSError(
                message=f"Similarity search failed: {str(e)}",
                operation="search_similar",
                details={'k': k, 'original_error': str(e)}
            )
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics with error handling"""
        try:
            return self.service.get_index_stats()
        except Exception as e:
            self.logger.error(f"Failed to get index stats: {e}")
            return {'error': str(e), 'available': False}
    
    def is_available(self) -> bool:
        """Check service availability"""
        try:
            return self.service.is_available()
        except Exception as e:
            self.logger.warning(f"Error checking FAISS availability: {e}")
            return False


class EnhancedSkinClassifierWrapper:
    """Enhanced wrapper for skin classifier service"""
    
    def __init__(self, skin_classifier_service):
        self.service = skin_classifier_service
        self.service_name = 'skin_classifier'
        self.logger = get_service_logger(self.service_name)
        self.monitor = get_service_monitor(self.service_name)
    
    @monitor_service_call('skin_classifier')
    @with_error_recovery('skin_classifier', 'classify_skin_type')
    def classify_skin_type(self, image_data, ethnicity: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced skin type classification with error handling"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting skin classification with ethnicity: {ethnicity}")
            
            # Validate inputs
            if not image_data:
                raise SkinClassificationError(
                    message="No image data provided",
                    classification_stage="input_validation",
                    details={'ethnicity': ethnicity}
                )
            
            # Perform classification
            result = self.service.classify_skin_type(image_data, ethnicity)
            
            # Validate result
            if not result or result.get('error'):
                error_msg = result.get('error', 'Unknown classification error') if result else 'No result returned'
                raise SkinClassificationError(
                    message=f"Classification failed: {error_msg}",
                    classification_stage="classification",
                    details={'ethnicity': ethnicity, 'result': result}
                )
            
            duration = time.time() - start_time
            confidence = result.get('confidence', 0.0)
            
            self.logger.info(f"Skin classification completed in {duration:.3f}s with confidence {confidence:.3f}")
            
            log_service_operation(
                self.service_name, 'classify_skin_type',
                success=True, duration=duration,
                details={
                    'ethnicity': ethnicity,
                    'confidence': confidence,
                    'fitzpatrick_type': result.get('fitzpatrick_type'),
                    'monk_tone': result.get('monk_tone')
                }
            )
            
            return result
            
        except SkinClassificationError:
            # Re-raise skin classification specific errors
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Skin classification failed: {e}")
            
            log_service_operation(
                self.service_name, 'classify_skin_type',
                success=False, duration=duration,
                details={'ethnicity': ethnicity, 'error': str(e)}
            )
            
            raise SkinClassificationError(
                message=f"Skin classification failed: {str(e)}",
                classification_stage="execution",
                details={'ethnicity': ethnicity, 'original_error': str(e)}
            )


class EnhancedDemographicSearchWrapper:
    """Enhanced wrapper for demographic search service"""
    
    def __init__(self, demographic_search_service):
        self.service = demographic_search_service
        self.service_name = 'demographic_search'
        self.logger = get_service_logger(self.service_name)
        self.monitor = get_service_monitor(self.service_name)
    
    @monitor_service_call('demographic_search')
    @with_error_recovery('demographic_search', 'search_with_demographics')
    def search_with_demographics(self, query_vector, user_demographics: Dict[str, Any], 
                               k: int = 10) -> List[Tuple[str, float]]:
        """Enhanced demographic search with error handling"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting demographic search with k={k}")
            
            # Validate inputs
            if query_vector is None:
                raise DemographicSearchError(
                    message="Query vector is None",
                    search_stage="input_validation",
                    details={'k': k, 'demographics': user_demographics}
                )
            
            if not isinstance(user_demographics, dict):
                raise DemographicSearchError(
                    message="Invalid user demographics format",
                    search_stage="input_validation",
                    demographic_data_missing=True,
                    details={'demographics_type': type(user_demographics).__name__}
                )
            
            # Perform search
            results = self.service.search_with_demographics(query_vector, user_demographics, k)
            
            duration = time.time() - start_time
            self.logger.info(f"Demographic search completed: {len(results)} results in {duration:.3f}s")
            
            log_service_operation(
                self.service_name, 'search_with_demographics',
                success=True, duration=duration,
                details={
                    'k': k,
                    'results_found': len(results),
                    'demographics_provided': bool(user_demographics)
                }
            )
            
            return results
            
        except DemographicSearchError:
            # Re-raise demographic search specific errors
            raise
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Demographic search failed: {e}")
            
            log_service_operation(
                self.service_name, 'search_with_demographics',
                success=False, duration=duration,
                details={'k': k, 'error': str(e)}
            )
            
            raise DemographicSearchError(
                message=f"Demographic search failed: {str(e)}",
                search_stage="execution",
                details={'k': k, 'original_error': str(e)}
            )


def create_enhanced_service_wrappers(service_manager):
    """
    Create enhanced service wrappers for all services
    
    Args:
        service_manager: Service manager instance
        
    Returns:
        Dictionary of enhanced service wrappers
    """
    wrappers = {}
    
    try:
        # Google Vision wrapper
        google_vision_service = service_manager.get_service('google_vision')
        if google_vision_service:
            wrappers['google_vision'] = EnhancedGoogleVisionWrapper(google_vision_service)
            logger.info("Created enhanced Google Vision wrapper")
        
        # FAISS wrapper
        faiss_service = service_manager.get_service('faiss')
        if faiss_service:
            wrappers['faiss'] = EnhancedFAISSWrapper(faiss_service)
            logger.info("Created enhanced FAISS wrapper")
        
        # Skin classifier wrapper
        skin_classifier_service = service_manager.get_service('skin_classifier')
        if skin_classifier_service:
            wrappers['skin_classifier'] = EnhancedSkinClassifierWrapper(skin_classifier_service)
            logger.info("Created enhanced skin classifier wrapper")
        
        # Demographic search wrapper
        demographic_search_service = service_manager.get_service('demographic_search')
        if demographic_search_service:
            wrappers['demographic_search'] = EnhancedDemographicSearchWrapper(demographic_search_service)
            logger.info("Created enhanced demographic search wrapper")
        
    except Exception as e:
        logger.error(f"Error creating enhanced service wrappers: {e}")
    
    return wrappers


def health_check_all_services(service_wrappers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform health check on all enhanced service wrappers
    
    Args:
        service_wrappers: Dictionary of enhanced service wrappers
        
    Returns:
        Health check results
    """
    health_results = {
        'overall_status': 'healthy',
        'services': {},
        'timestamp': time.time()
    }
    
    unhealthy_count = 0
    
    for service_name, wrapper in service_wrappers.items():
        try:
            is_available = wrapper.is_available()
            
            service_health = {
                'status': 'healthy' if is_available else 'unhealthy',
                'available': is_available,
                'last_check': time.time()
            }
            
            # Add service-specific health info
            if hasattr(wrapper, 'get_index_stats') and is_available:
                try:
                    service_health['stats'] = wrapper.get_index_stats()
                except Exception as e:
                    service_health['stats_error'] = str(e)
            
            health_results['services'][service_name] = service_health
            
            if not is_available:
                unhealthy_count += 1
                
        except Exception as e:
            health_results['services'][service_name] = {
                'status': 'error',
                'available': False,
                'error': str(e),
                'last_check': time.time()
            }
            unhealthy_count += 1
    
    # Determine overall status
    if unhealthy_count == 0:
        health_results['overall_status'] = 'healthy'
    elif unhealthy_count < len(service_wrappers):
        health_results['overall_status'] = 'degraded'
    else:
        health_results['overall_status'] = 'unhealthy'
    
    health_results['healthy_services'] = len(service_wrappers) - unhealthy_count
    health_results['unhealthy_services'] = unhealthy_count
    health_results['total_services'] = len(service_wrappers)
    
    return health_results