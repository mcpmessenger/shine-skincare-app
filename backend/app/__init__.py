from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from celery import Celery
import os
# from dotenv import load_dotenv

# Temporarily comment out dotenv loading to avoid corrupted .env file
# load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
celery = Celery()

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(f'config.{config_name.capitalize()}Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.auth import auth_bp
    from app.image_analysis import image_bp
    from app.recommendations import recommendations_bp
    from app.payments import payments_bp
    from app.mcp import mcp_bp
    from app.enhanced_image_analysis import enhanced_image_bp
    from app.simple_skin_analysis import simple_skin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(image_bp, url_prefix='/api/analysis')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(mcp_bp, url_prefix='/api/mcp')
    app.register_blueprint(enhanced_image_bp, url_prefix='/api/v2')
    app.register_blueprint(simple_skin_bp, url_prefix='/api/simple')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        from datetime import datetime
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def create_celery(app):
    """Create Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery 