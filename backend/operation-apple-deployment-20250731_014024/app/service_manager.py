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
            
            # 🍎 Operation Apple: Initialize advanced analysis services
            self._initialize_operation_apple_services(config)
            
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
        use_mock_services = os.environ.get('USE_MOCK_SERVICES', 'false').lower() == 'true'
        
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
    
    def _initialize_operation_apple_services(self, config: Dict[str, Any]) -> None:
        """🍎 Operation Apple: Initialize advanced analysis services"""
        try:
            logger.info("🍎 Operation Apple: Initializing advanced analysis services...")
            
            # Skin Texture Analysis Service
            try:
                from app.services.skin_texture_analysis_service import SkinTextureAnalysisService
                self._services['skin_texture_analysis'] = SkinTextureAnalysisService()
                logger.info("🍎 Operation Apple: Skin Texture Analysis service initialized")
            except Exception as e:
                logger.warning(f"🍎 Operation Apple: Failed to initialize Skin Texture Analysis service: {e}")
                self._services['skin_texture_analysis'] = None
            
            # Pore Analysis Service
            try:
                from app.services.pore_analysis_service import PoreAnalysisService
                self._services['pore_analysis'] = PoreAnalysisService()
                logger.info("🍎 Operation Apple: Pore Analysis service initialized")
            except Exception as e:
                logger.warning(f"🍎 Operation Apple: Failed to initialize Pore Analysis service: {e}")
                self._services['pore_analysis'] = None
            
            # Wrinkle Mapping Service
            try:
                from app.services.wrinkle_mapping_service import WrinkleMappingService
                self._services['wrinkle_mapping'] = WrinkleMappingService()
                logger.info("🍎 Operation Apple: Wrinkle Mapping service initialized")
            except Exception as e:
                logger.warning(f"🍎 Operation Apple: Failed to initialize Wrinkle Mapping service: {e}")
                self._services['wrinkle_mapping'] = None
            
            # Pigmentation Analysis Service
            try:
                from app.services.pigmentation_analysis_service import PigmentationAnalysisService
                self._services['pigmentation_analysis'] = PigmentationAnalysisService()
                logger.info("🍎 Operation Apple: Pigmentation Analysis service initialized")
            except Exception as e:
                logger.warning(f"🍎 Operation Apple: Failed to initialize Pigmentation Analysis service: {e}")
                self._services['pigmentation_analysis'] = None
            
            # Analysis Orchestrator Service
            try:
                from app.services.analysis_orchestrator import AnalysisOrchestrator
                self._services['analysis_orchestrator'] = AnalysisOrchestrator(self)
                logger.info("🍎 Operation Apple: Analysis Orchestrator service initialized")
            except Exception as e:
                logger.warning(f"🍎 Operation Apple: Failed to initialize Analysis Orchestrator service: {e}")
                self._services['analysis_orchestrator'] = None
            
            logger.info("🍎 Operation Apple: Advanced analysis services initialization completed")
            
        except Exception as e:
            logger.error(f"🍎 Operation Apple: Error initializing advanced analysis services: {e}")
    
    def _validate_services(self) -> None:
        """Validate that all services are available"""
        service_status = {}
        
        for service_name, service in self._services.items():
            try:
                # Skip None services (failed initializations)
                if service is None:
                    service_status[service_name] = False
                    logger.warning(f"⚠ {service_name} service is None (failed initialization)")
                    continue
                
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
        Get a service by name
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance or None if not found
        """
        if not self._initialized:
            logger.warning("Services not initialized. Call initialize_services() first.")
            return None
        
        service = self._services.get(service_name)
        if service is None:
            logger.warning(f"Service '{service_name}' not found or failed to initialize")
        return service
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all available services"""
        if not self._initialized:
            logger.warning("Services not initialized. Call initialize_services() first.")
            return {}
        
        return self._services.copy()
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of all services"""
        if not self._initialized:
            return {}
        
        return getattr(self, '_service_status', {})
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get detailed information about all services"""
        if not self._initialized:
            return {}
        
        service_info = {}
        for service_name, service in self._services.items():
            try:
                if service is None:
                    service_info[service_name] = {
                        'available': False,
                        'error': 'Service failed to initialize'
                    }
                    continue
                
                is_available = service.is_available()
                service_info[service_name] = {
                    'available': is_available,
                    'type': type(service).__name__,
                    'module': type(service).__module__
                }
                
                # Add service-specific information if available
                if hasattr(service, 'get_info'):
                    try:
                        service_info[service_name].update(service.get_info())
                    except Exception as e:
                        service_info[service_name]['error'] = str(e)
                        
            except Exception as e:
                service_info[service_name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return service_info
    
    def shutdown_services(self) -> None:
        """Shutdown all services gracefully"""
        logger.info("Shutting down services...")
        
        for service_name, service in self._services.items():
            try:
                if service is not None and hasattr(service, 'shutdown'):
                    service.shutdown()
                    logger.info(f"✓ {service_name} service shut down")
            except Exception as e:
                logger.error(f"✗ Error shutting down {service_name} service: {e}")
        
        self._services.clear()
        self._initialized = False
        logger.info("All services shut down")
    
    def reconfigure_service(self, service_name: str, **kwargs) -> None:
        """
        Reconfigure a specific service
        
        Args:
            service_name: Name of the service to reconfigure
            **kwargs: Configuration parameters
        """
        if not self._initialized:
            logger.warning("Services not initialized. Call initialize_services() first.")
            return
        
        service = self._services.get(service_name)
        if service is None:
            logger.warning(f"Service '{service_name}' not found")
            return
        
        try:
            if hasattr(service, 'reconfigure'):
                service.reconfigure(**kwargs)
                logger.info(f"✓ {service_name} service reconfigured")
            else:
                logger.warning(f"Service '{service_name}' does not support reconfiguration")
        except Exception as e:
            logger.error(f"✗ Error reconfiguring {service_name} service: {e}")
    
    def is_initialized(self) -> bool:
        """Check if services are initialized"""
        return self._initialized


# Global service manager instance
service_manager = ServiceManager()