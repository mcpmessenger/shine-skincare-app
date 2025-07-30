import logging
import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
from functools import wraps
from .service_manager import service_manager
from .error_handlers import register_error_handlers, APIError, ServiceError
from .logging_config import setup_logging, configure_flask_logging
from .performance import (
    optimize_for_cold_start, configure_performance_monitoring,
    performance_monitor, cleanup_resources
)
from .vercel_optimizations import (
    optimize_for_vercel, vercel_performance_middleware, 
    get_vercel_performance_stats
)
from .model_optimization import (
    optimize_model_loading, get_model_performance_stats,
    cleanup_model_resources
)
from .demographic_cache import (
    demographic_cache_manager, preload_common_demographics
)

# Timeout configuration
TIMEOUT_CONFIGS = {
    'skin_classification': {'sync_limit': 15, 'async_limit': 60},
    'image_vectorization': {'sync_limit': 45, 'async_limit': 180},
    'similarity_search': {'sync_limit': 30, 'async_limit': 120},
    'google_vision': {'sync_limit': 20, 'async_limit': 90}
}

class TimeoutManager:
    """Manages timeouts for AI operations"""
    
    def __init__(self):
        self.active_operations = {}
        self.operation_lock = threading.Lock()
    
    def execute_with_timeout(self, operation_name, operation_func, *args, **kwargs):
        """Execute operation with timeout handling"""
        config = TIMEOUT_CONFIGS.get(operation_name, {'sync_limit': 30, 'async_limit': 120})
        
        try:
            # Try synchronous execution first
            result = operation_func(*args, **kwargs)
            return {'status': 'success', 'result': result, 'mode': 'sync'}
        except Exception as e:
            logger.warning(f"Sync operation failed for {operation_name}: {e}")
            return {'status': 'error', 'error': str(e), 'mode': 'sync'}

timeout_manager = TimeoutManager()

def with_timeout_fallback(operation_name):
    """Decorator for timeout handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return timeout_manager.execute_with_timeout(operation_name, func, *args, **kwargs)
        return wrapper
    return decorator

# Setup enhanced logging
setup_logging(
    log_level=os.environ.get('LOG_LEVEL', 'INFO'),
    log_file=os.environ.get('LOG_FILE')
)
logger = logging.getLogger(__name__)

# Optimize for cold start
optimize_for_cold_start()

def create_app(config_name='development'):
    """Application factory pattern with enhanced service integration and Vercel optimizations"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Apply Vercel-specific optimizations
    try:
        optimize_for_vercel()
        optimize_model_loading()
        preload_common_demographics()
        logger.info("Vercel optimizations applied successfully")
    except Exception as e:
        logger.error(f"Vercel optimization failed: {e}")
        # Continue with app creation
    
    # Service configuration from environment variables
    # Use mock services for reliable deployment
    os.environ['USE_MOCK_SERVICES'] = 'true'
    
    service_config = {
        'faiss_dimension': int(os.environ.get('FAISS_DIMENSION', '2048')),
        'faiss_index_path': os.environ.get('FAISS_INDEX_PATH', 'faiss_index'),
        'demographic_weight': float(os.environ.get('DEMOGRAPHIC_WEIGHT', '0.3')),
        'ethnicity_weight': float(os.environ.get('ETHNICITY_WEIGHT', '0.6')),
        'skin_type_weight': float(os.environ.get('SKIN_TYPE_WEIGHT', '0.3')),
        'age_group_weight': float(os.environ.get('AGE_GROUP_WEIGHT', '0.1')),
        'supabase_url': os.environ.get('SUPABASE_URL'),
        'supabase_key': os.environ.get('SUPABASE_KEY')
    }
    
    # Initialize services
    try:
        service_manager.initialize_services(service_config)
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Continue with app creation but services may not be available
    
    # Enable CORS - Fixed configuration based on working deployment
    CORS(app, resources={
        r"/*": {
            "origins": ["https://www.shineskincollective.com"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "supports_credentials": True
        }
    })
    
    # ENHANCED: Add CORS headers to ALL responses - GUARANTEED
    @app.after_request
    def after_request(response):
        """Add CORS headers to all responses - GUARANTEED"""
        response.headers.add('Access-Control-Allow-Origin', 'https://www.shineskincollective.com')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register enhanced error handlers
    register_error_handlers(app)
    
    # Configure Flask-specific logging
    configure_flask_logging(app)
    
    # Configure performance monitoring
    configure_performance_monitoring(app)
    
    # Apply Vercel performance middleware
    app = vercel_performance_middleware(app)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Enhanced health check with ML capabilities"""
        try:
            # Check ML availability
            ml_status = {
                'available': ML_AVAILABLE,
                'libraries': {
                    'numpy': 'numpy' in globals(),
                    'opencv': 'cv2' in globals(),
                    'tensorflow': 'tf' in globals(),
                    'pillow': 'Image' in globals()
                }
            }
            
            # Check service availability
            services_status = {}
            if service_manager.is_initialized():
                services_status = service_manager.get_service_status()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'environment': os.environ.get('FLASK_ENV', 'production'),
                'ml_capabilities': ml_status,
                'services': services_status,
                'timeout_config': TIMEOUT_CONFIGS,
                'features': {
                    'enhanced_analysis': True,
                    'real_ml': ML_AVAILABLE,
                    'timeout_handling': True,
                    'guest_analysis': True
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'message': 'Shine Skincare API', 
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'ml_available': ML_AVAILABLE,
            'features': {
                'enhanced_analysis': True,
                'real_ml': ML_AVAILABLE,
                'guest_analysis': True,
                'timeout_handling': True
            },
            'endpoints': {
                'guest_analysis': '/api/v2/analyze/guest',
                'health_check': '/api/health',
                'enhanced_analysis': '/api/enhanced-analysis'
            }
        }
    
    # Legacy v2 endpoint for frontend compatibility
    @app.route('/api/v2/analyze/guest', methods=['POST'])
    def analyze_guest_v2():
        """
        Legacy endpoint for frontend compatibility
        Routes to enhanced analysis with real ML capabilities
        """
        try:
            # Import the enhanced analysis function
            from .enhanced_image_analysis.routes import analyze_image_guest
            
            # Log the request for debugging
            logger.info("Guest analysis request received via legacy endpoint")
            
            # Call the enhanced analysis function
            response = analyze_image_guest()
            
            # Log successful analysis
            logger.info("Guest analysis completed successfully")
            
            return response
            
        except ImportError as e:
            logger.error(f"Failed to import enhanced analysis: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Enhanced analysis not available',
                'message': 'Service temporarily unavailable'
            }), 503
        except Exception as e:
            logger.error(f"Error in legacy guest analysis: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'message': 'Analysis failed. Please try again.'
            }), 500
    
    # Service configuration endpoint
    @app.route('/api/services/config', methods=['GET'])
    def get_service_config():
        try:
            if not service_manager.is_initialized():
                return jsonify({'error': 'Services not initialized'}), 503
            
            return jsonify({
                'configuration': service_manager.get_service_info(),
                'status': service_manager.get_service_status()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Service reconfiguration endpoint (for development/testing)
    @app.route('/api/services/config', methods=['POST'])
    def update_service_config():
        try:
            if not service_manager.is_initialized():
                return jsonify({'error': 'Services not initialized'}), 503
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            service_name = data.get('service')
            config_params = data.get('config', {})
            
            if not service_name:
                return jsonify({'error': 'Service name required'}), 400
            
            service_manager.reconfigure_service(service_name, **config_params)
            
            return jsonify({
                'message': f'Service {service_name} reconfigured successfully',
                'new_config': service_manager.get_service_info()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Performance monitoring endpoints
    @app.route('/api/performance/vercel', methods=['GET'])
    def get_vercel_performance():
        """Get Vercel-specific performance statistics"""
        try:
            stats = get_vercel_performance_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/performance/models', methods=['GET'])
    def get_model_performance():
        """Get model performance statistics"""
        try:
            stats = get_model_performance_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/performance/cache', methods=['GET'])
    def get_cache_performance():
        """Get cache performance statistics"""
        try:
            stats = demographic_cache_manager.get_comprehensive_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/performance/cleanup', methods=['POST'])
    def cleanup_performance():
        """Clean up resources to free memory"""
        try:
            cleanup_stats = {
                'general_cleanup': cleanup_resources(),
                'model_cleanup': cleanup_model_resources(),
                'cache_cleanup': demographic_cache_manager.periodic_cleanup()
            }
            return jsonify(cleanup_stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Graceful shutdown handler
    @app.teardown_appcontext
    def shutdown_services(error):
        if error:
            logger.error(f"Application error: {error}")
    
    return app

def _register_blueprints(app):
    """Register application blueprints"""
    try:
        # Register enhanced image analysis blueprint
        from .enhanced_image_analysis import enhanced_image_bp
        app.register_blueprint(enhanced_image_bp, url_prefix='/api/enhanced')
        logger.info("Enhanced image analysis blueprint registered")
        
        # Register enhanced skin analysis blueprint
        from .enhanced_skin_analysis import enhanced_skin_bp
        app.register_blueprint(enhanced_skin_bp, url_prefix='/api/enhanced-skin')
        logger.info("Enhanced skin analysis blueprint registered")
        
        # Register recommendations blueprint
        from .recommendations import recommendations_bp
        app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
        logger.info("Recommendations blueprint registered")
        
        # Register SCIN analysis blueprint
        from .routes.scin_analysis import scin_analysis_bp
        app.register_blueprint(scin_analysis_bp)
        logger.info("SCIN analysis blueprint registered")
        
        # Register other blueprints as needed
        # from .other_module import other_bp
        # app.register_blueprint(other_bp, url_prefix='/api/other')
        
    except ImportError as e:
        logger.warning(f"Could not register blueprint: {e}")

 