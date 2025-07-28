from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
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
    
    # Enable CORS - Simplified for debugging
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
    
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
        from datetime import datetime
        
        try:
            service_status = service_manager.get_service_status()
            service_info = service_manager.get_service_info()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'services': service_status,
                'service_info': service_info,
                'services_initialized': service_manager.is_initialized()
            })
        except Exception as e:
            return jsonify({
                'status': 'degraded',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        return {'message': 'Shine Skincare API', 'status': 'running'}
    
    # Legacy v2 endpoint for frontend compatibility
    @app.route('/api/v2/analyze/guest', methods=['POST'])
    def analyze_guest_v2():
        """
        Legacy endpoint for frontend compatibility
        Redirects to enhanced analysis endpoint
        """
        try:
            from .enhanced_image_analysis.routes import analyze_image_guest
            return analyze_image_guest()
        except Exception as e:
            logger.error(f"Error in legacy guest analysis: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
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
        
        # Register recommendations blueprint
        from .recommendations import recommendations_bp
        app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
        logger.info("Recommendations blueprint registered")
        
        # Register other blueprints as needed
        # from .other_module import other_bp
        # app.register_blueprint(other_bp, url_prefix='/api/other')
        
    except ImportError as e:
        logger.warning(f"Could not register blueprint: {e}")

 