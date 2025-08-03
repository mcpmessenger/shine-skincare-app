"""
Configuration for Operation Right Brain 🧠 - Backend
Centralized configuration management for the AI-powered skin analysis system.

Author: Manus AI
Date: August 2, 2025
"""

import os
from typing import Optional

class Config:
    """Configuration class for the Operation Right Brain backend."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    # Google Vision API Configuration
    VISION_API_ENABLED = os.getenv('VISION_API_ENABLED', 'True').lower() == 'true'
    VISION_API_TIMEOUT = int(os.getenv('VISION_API_TIMEOUT', '30'))
    
    # Vertex AI Configuration
    VERTEX_AI_ENABLED = os.getenv('VERTEX_AI_ENABLED', 'True').lower() == 'true'
    VERTEX_AI_MODEL_NAME = os.getenv('VERTEX_AI_MODEL_NAME', 'multimodalembedding@001')
    VERTEX_AI_TIMEOUT = int(os.getenv('VERTEX_AI_TIMEOUT', '60'))
    
    # Vector Database Configuration
    VECTOR_DB_ENABLED = os.getenv('VECTOR_DB_ENABLED', 'True').lower() == 'true'
    VECTOR_DB_INDEX_ENDPOINT_ID = os.getenv('VECTOR_DB_INDEX_ENDPOINT_ID')
    VECTOR_DB_DEPLOYED_INDEX_ID = os.getenv('VECTOR_DB_DEPLOYED_INDEX_ID')
    VECTOR_DB_TIMEOUT = int(os.getenv('VECTOR_DB_TIMEOUT', '30'))
    
    # Analysis Configuration
    MAX_IMAGE_SIZE_MB = int(os.getenv('MAX_IMAGE_SIZE_MB', '10'))
    SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
    MAX_ANALYSIS_TIME_SECONDS = int(os.getenv('MAX_ANALYSIS_TIME_SECONDS', '30'))
    
    # SCIN Dataset Configuration
    SCIN_DATASET_PATH = os.getenv('SCIN_DATASET_PATH', './scin-dataset')
    SCIN_EMBEDDINGS_PATH = os.getenv('SCIN_EMBEDDINGS_PATH', './scin-embeddings')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    LOG_FILE = os.getenv('LOG_FILE', 'operation_right_brain.log')
    
    # Security Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per minute
    API_RATE_LIMIT_WINDOW = int(os.getenv('API_RATE_LIMIT_WINDOW', '60'))  # seconds
    
    # Performance Configuration
    WORKER_PROCESSES = int(os.getenv('WORKER_PROCESSES', '4'))
    WORKER_THREADS = int(os.getenv('WORKER_THREADS', '2'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
    
    # Monitoring Configuration
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))
    
    @classmethod
    def validate_config(cls) -> list:
        """
        Validate the configuration and return any issues.
        
        Returns:
            List of configuration issues (empty if valid)
        """
        issues = []
        
        # Required environment variables
        required_vars = [
            'GOOGLE_CLOUD_PROJECT',
            'VECTOR_DB_INDEX_ENDPOINT_ID',
            'VECTOR_DB_DEPLOYED_INDEX_ID'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Validate numeric values
        if cls.MAX_IMAGE_SIZE_MB <= 0:
            issues.append("MAX_IMAGE_SIZE_MB must be positive")
        
        if cls.MAX_ANALYSIS_TIME_SECONDS <= 0:
            issues.append("MAX_ANALYSIS_TIME_SECONDS must be positive")
        
        if cls.API_RATE_LIMIT <= 0:
            issues.append("API_RATE_LIMIT must be positive")
        
        return issues
    
    @classmethod
    def get_google_credentials_path(cls) -> Optional[str]:
        """Get the path to Google Cloud credentials file."""
        return os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return not cls.DEBUG and os.getenv('FLASK_ENV') == 'production'
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database URL for user data."""
        return os.getenv('DATABASE_URL', 'sqlite:///shine_skincare.db')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Stricter security settings for production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://shine-skincare.com').split(',')
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '50'))

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Use test-specific settings
    SCIN_DATASET_PATH = './test-scin-dataset'
    SCIN_EMBEDDINGS_PATH = './test-scin-embeddings'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """
    Get the appropriate configuration based on environment.
    
    Returns:
        Configuration object
    """
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default']) 