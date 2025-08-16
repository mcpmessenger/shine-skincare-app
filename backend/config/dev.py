"""
Development Configuration for Shine Skincare Backend
This module contains development-specific settings
"""

import os
from pathlib import Path

# Development Environment Settings
DEBUG = True
TESTING = False
DEVELOPMENT = True

# Server Configuration
HOST = '0.0.0.0'
PORT = 8000
RELOAD = True

# Database and Storage (Development)
S3_BUCKET = os.getenv('S3_BUCKET', 'shine-skincare-models-dev')
S3_MODEL_KEY = os.getenv('S3_MODEL_KEY', 'hare_run_v6/hare_run_v6_facial/best_facial_model.h5')
LOCAL_MODEL_PATH = os.getenv('MODEL_PATH', './models/fixed_model_best.h5')

# Logging Configuration
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/dev.log'

# CORS Settings (Development - more permissive)
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001', 
    'http://localhost:3002',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://127.0.0.1:3002',
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

# Model Configuration
MODEL_CONFIG = {
    'enabled': True,
    'models': {
        'facial': {
            'primary': 'fixed_model_best.h5',
            'backup': 'fixed_model_best.h5',
            'metadata': 'fixed_model_best.h5'
        }
    },
    'endpoints': {
        'skin_analysis': '/api/v6/skin/analyze-hare-run',
        'model_status': '/api/v5/skin/model-status'
    },
    'performance': {
        'target_accuracy': '97.13%',
        'max_response_time': '30s',
        'model_size': '128MB'
    }
}

# Development Utilities
def setup_dev_environment():
    """Set up development environment"""
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Create models directory if it doesn't exist
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['LOG_LEVEL'] = LOG_LEVEL
    
    print(f"✅ Development environment configured:")
    print(f"   Host: {HOST}")
    print(f"   Port: {PORT}")
    print(f"   Debug: {DEBUG}")
    print(f"   Log Level: {LOG_LEVEL}")

def get_dev_config():
    """Get development configuration as dictionary"""
    return {
        'debug': DEBUG,
        'testing': TESTING,
        'development': DEVELOPMENT,
        'host': HOST,
        'port': PORT,
        'reload': RELOAD,
        'log_level': LOG_LEVEL,
        'cors_origins': CORS_ORIGINS,
        'model_config': MODEL_CONFIG
    }
