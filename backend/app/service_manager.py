import logging
import os
from typing import Optional, Dict, Any
from app.services import (
    GoogleVisionService,
    ImageVectorizationService,
    FAISSService,
    SupabaseService,
    DemographicWeightedSearch,
    EnhancedSkinTypeClassifier
)

# Import production services
try:
    from app.services.production_faiss_service import ProductionFAISSService
    PRODUCTION_FAISS_AVAILABLE = True
except ImportError:
    PRODUCTION_FAISS_AVAILABLE = False
    ProductionFAISSService = None

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Centralized service manager for dependency injection and service lifecycle management
    """
    
    def __init__(self):
        """Initialize the service manager"""
        self._services = {}
        self._initialized = False
        logger.info("Service manager created")
    
    def initialize_services(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize all services with proper dependency injection
        
        Args:
            config: Optional configuration dictionary
        """
        try:
            if self._initialized:
                logger.warning("Services already initialized")
                return
            
            config = config or {}
            logger.info("Initializing services...")
            
            # Initialize core services first
            self._initialize_core_services(config)
            
            # Initialize enhanced services with dependencies
            self._initialize_enhanced_services(config)
            
            # Validate service availability
            self._validate_services()
            
            self._initialized = True
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _initialize_core_services(self, config: Dict[str, Any]) -> None:
        """Initialize core services with fallback to mock implementations and environment-based selection"""
        # Check if we should use mock services (for development/testing)
        use_mock_services = os.environ.get('USE_MOCK_SERVICES', 'false').lower() == 'true'
        
        # Google Vision Service with enhanced fallback
        if use_mock_services:
            logger.info("Using Mock Google Vision service (USE_MOCK_SERVICES=true)")
            from app.services.mock_google_vision_service import MockGoogleVisionService
            self._services['google_vision'] = MockGoogleVisionService()
        else:
            try:
                self._services['google_vision'] = GoogleVisionService()
                logger.info("Google Vision service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Vision service: {e}")
                logger.info("Falling back to Mock Google Vision service")
                from app.services.mock_google_vision_service import MockGoogleVisionService
                self._services['google_vision'] = MockGoogleVisionService()
        
        # Image Vectorization Service with fallback to mock
        if use_mock_services:
            logger.info("Using Mock Vectorization service (USE_MOCK_SERVICES=true)")
            from app.services.mock_vectorization_service import MockVectorizationService
            self._services['vectorization'] = MockVectorizationService()
        else:
            try:
                self._services['vectorization'] = ImageVectorizationService()
                logger.info("Image vectorization service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Image Vectorization service: {e}")
                logger.info("Falling back to Mock Vectorization service")
                from app.services.mock_vectorization_service import MockVectorizationService
                self._services['vectorization'] = MockVectorizationService()
        
        # FAISS Service with production and mock options
        faiss_dimension = config.get('faiss_dimension', 2048)
        faiss_index_path = config.get('faiss_index_path', 'faiss_index')
        
        if use_mock_services:
            logger.info("Using Mock FAISS service (USE_MOCK_SERVICES=true)")
            from app.services.mock_faiss_service import MockFAISSService
            self._services['faiss'] = MockFAISSService(
                dimension=faiss_dimension,
                index_path=faiss_index_path
            )
        else:
            # Try production FAISS first, then regular FAISS, then mock
            faiss_service = None
            
            # Try Production FAISS Service
            if PRODUCTION_FAISS_AVAILABLE and os.environ.get('USE_PRODUCTION_FAISS', 'true').lower() == 'true':
                try:
                    faiss_service = ProductionFAISSService(
                        dimension=faiss_dimension,
                        index_path=faiss_index_path
                    )
                    if faiss_service.is_available():
                        self._services['faiss'] = faiss_service
                        logger.info(f"Production FAISS service initialized (dimension: {faiss_dimension})")
                    else:
                        faiss_service = None
                except Exception as e:
                    logger.warning(f"Failed to initialize Production FAISS service: {e}")
                    faiss_service = None
            
            # Fallback to regular FAISS service
            if faiss_service is None:
                try:
                    self._services['faiss'] = FAISSService(
                        dimension=faiss_dimension,
                        index_path=faiss_index_path
                    )
                    logger.info(f"Regular FAISS service initialized (dimension: {faiss_dimension})")
                except Exception as e:
                    logger.warning(f"Failed to initialize regular FAISS service: {e}")
                    logger.info("Falling back to Mock FAISS service")
                    from app.services.mock_faiss_service import MockFAISSService
                    self._services['faiss'] = MockFAISSService(
                        dimension=faiss_dimension,
                        index_path=faiss_index_path
                    )
        
        # Supabase Service with fallback to mock
        supabase_url = config.get('supabase_url') or os.environ.get('SUPABASE_URL')
        supabase_key = config.get('supabase_key') or os.environ.get('SUPABASE_KEY')
        
        if use_mock_services:
            logger.info("Using Mock Supabase service (USE_MOCK_SERVICES=true)")
            from app.services.mock_supabase_service import MockSupabaseService
            self._services['supabase'] = MockSupabaseService(
                url=supabase_url,
                key=supabase_key
            )
        else:
            try:
                self._services['supabase'] = SupabaseService(
                    url=supabase_url,
                    key=supabase_key
                )
                logger.info("Supabase service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase service: {e}")
                logger.info("Falling back to Mock Supabase service")
                from app.services.mock_supabase_service import MockSupabaseService
                self._services['supabase'] = MockSupabaseService(
                    url=supabase_url,
                    key=supabase_key
                )
    
    def _initialize_enhanced_services(self, config: Dict[str, Any]) -> None:
        """Initialize enhanced services with dependencies"""
        # Enhanced Image Vectorization Service
        try:
            from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
            self._services['enhanced_vectorization'] = EnhancedImageVectorizationService()
            logger.info("Enhanced Image Vectorization service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Enhanced Vectorization service: {e}")
            # Fallback to regular vectorization service
            self._services['enhanced_vectorization'] = self._services.get('vectorization')
        
        # FAISS Service with production fallback
        if use_mock_services:
            logger.info("Using Mock FAISS service (USE_MOCK_SERVICES=true)")
            from app.services.mock_faiss_service import MockFAISSService
            self._services['faiss'] = MockFAISSService()
        else:
            try:
                # Try production FAISS first
                if PRODUCTION_FAISS_AVAILABLE:
                    self._services['faiss'] = ProductionFAISSService()
                    logger.info("Production FAISS service initialized")
                else:
                    self._services['faiss'] = FAISSService()
                    logger.info("Standard FAISS service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize FAISS service: {e}")
                logger.info("Falling back to Mock FAISS service")
                from app.services.mock_faiss_service import MockFAISSService
                self._services['faiss'] = MockFAISSService()
        
        # Supabase Service with fallback to mock
        if use_mock_services:
            logger.info("Using Mock Supabase service (USE_MOCK_SERVICES=true)")
            from app.services.mock_supabase_service import MockSupabaseService
            self._services['supabase'] = MockSupabaseService()
        else:
            try:
                self._services['supabase'] = SupabaseService()
                logger.info("Supabase service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase service: {e}")
                logger.info("Falling back to Mock Supabase service")
                from app.services.mock_supabase_service import MockSupabaseService
                self._services['supabase'] = MockSupabaseService()
        
        # Enhanced Skin Type Classifier
        try:
            google_vision_service = self._services.get('google_vision')
            self._services['skin_classifier'] = EnhancedSkinTypeClassifier(google_vision_service)
            logger.info("Enhanced Skin Type Classifier initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Enhanced Skin Type Classifier: {e}")
            # Create a basic classifier without Google Vision
            self._services['skin_classifier'] = EnhancedSkinTypeClassifier()
        
        # Demographic Search Service with fallback to mock
        if use_mock_services:
            logger.info("Using Mock Demographic Search service (USE_MOCK_SERVICES=true)")
            from app.services.mock_demographic_search_service import MockDemographicSearchService
            self._services['demographic_search'] = MockDemographicSearchService()
        else:
            try:
                faiss_service = self._services.get('faiss')
                self._services['demographic_search'] = DemographicWeightedSearch(faiss_service)
                logger.info("Demographic Search service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Demographic Search service: {e}")
                logger.info("Falling back to Mock Demographic Search service")
                from app.services.mock_demographic_search_service import MockDemographicSearchService
                self._services['demographic_search'] = MockDemographicSearchService()
    
    def _validate_services(self) -> None:
        """Validate that all services are available"""
        service_status = {}
        
        for service_name, service in self._services.items():
            try:
                is_available = service.is_available()
                service_status[service_name] = is_available
                
                if is_available:
                    logger.info(f"✓ {service_name} service is available")
                else:
                    logger.warning(f"⚠ {service_name} service is not available")
                    
            except Exception as e:
                logger.error(f"✗ Error checking {service_name} service: {e}")
                service_status[service_name] = False
        
        # Log overall status
        available_count = sum(service_status.values())
        total_count = len(service_status)
        logger.info(f"Service availability: {available_count}/{total_count} services available")
        
        # Store status for health checks
        self._service_status = service_status
    
    def get_service(self, service_name: str):
        """
        Get a service instance by name
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service not found or not initialized
        """
        if not self._initialized:
            raise ValueError("Services not initialized. Call initialize_services() first.")
        
        if service_name not in self._services:
            available_services = list(self._services.keys())
            raise ValueError(f"Service '{service_name}' not found. Available: {available_services}")
        
        return self._services[service_name]
    
    def get_all_services(self) -> Dict[str, Any]:
        """
        Get all service instances
        
        Returns:
            Dictionary of service name -> service instance
        """
        if not self._initialized:
            raise ValueError("Services not initialized. Call initialize_services() first.")
        
        return self._services.copy()
    
    def get_service_status(self) -> Dict[str, bool]:
        """
        Get the availability status of all services
        
        Returns:
            Dictionary of service name -> availability status
        """
        if not self._initialized:
            return {}
        
        return getattr(self, '_service_status', {})
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get detailed information about all services
        
        Returns:
            Dictionary with service information
        """
        if not self._initialized:
            return {}
        
        info = {}
        
        try:
            # FAISS info
            faiss_service = self._services.get('faiss')
            if faiss_service:
                info['faiss'] = faiss_service.get_index_info()
            
            # Vectorization info
            vectorization_service = self._services.get('vectorization')
            if vectorization_service:
                info['vectorization'] = vectorization_service.get_model_info()
            
            # Demographic search config
            demographic_service = self._services.get('demographic_search')
            if demographic_service:
                info['demographic_search'] = demographic_service.get_configuration()
            
            # Skin classifier info
            classifier_service = self._services.get('skin_classifier')
            if classifier_service:
                info['skin_classifier'] = classifier_service.get_model_info()
                
        except Exception as e:
            logger.error(f"Error getting service info: {e}")
        
        return info
    
    def shutdown_services(self) -> None:
        """Gracefully shutdown all services"""
        logger.info("Shutting down services...")
        
        # In a real implementation, you might need to close connections,
        # save state, etc. For now, we'll just clear the services
        self._services.clear()
        self._initialized = False
        
        logger.info("Services shutdown complete")
    
    def reconfigure_service(self, service_name: str, **kwargs) -> None:
        """
        Reconfigure a specific service
        
        Args:
            service_name: Name of the service to reconfigure
            **kwargs: Configuration parameters
        """
        if not self._initialized:
            raise ValueError("Services not initialized")
        
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")
        
        service = self._services[service_name]
        
        try:
            if service_name == 'demographic_search':
                if 'demographic_weight' in kwargs:
                    service.set_demographic_weight(kwargs['demographic_weight'])
                
                if any(k in kwargs for k in ['ethnicity_weight', 'skin_type_weight', 'age_group_weight']):
                    service.set_demographic_component_weights(
                        kwargs.get('ethnicity_weight', 0.6),
                        kwargs.get('skin_type_weight', 0.3),
                        kwargs.get('age_group_weight', 0.1)
                    )
            
            elif service_name == 'skin_classifier':
                if 'confidence_threshold' in kwargs:
                    service.set_confidence_threshold(kwargs['confidence_threshold'])
            
            logger.info(f"Reconfigured {service_name} service")
            
        except Exception as e:
            logger.error(f"Error reconfiguring {service_name}: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return self._initialized


# Global service manager instance
service_manager = ServiceManager()