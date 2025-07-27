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

# Setup enhanced logging
setup_logging(
    log_level=os.environ.get('LOG_LEVEL', 'INFO'),
    log_file=os.environ.get('LOG_FILE')
)
logger = logging.getLogger(__name__)

# Optimize for cold start
optimize_for_cold_start()

def create_app(config_name='development'):
    """Application factory pattern with enhanced service integration"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Service configuration from environment variables
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
        
        # Register other blueprints as needed
        # from .other_module import other_bp
        # app.register_blueprint(other_bp, url_prefix='/api/other')
        
    except ImportError as e:
        logger.warning(f"Could not register blueprint: {e}")

 