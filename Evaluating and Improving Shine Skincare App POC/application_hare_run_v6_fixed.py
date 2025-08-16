#!/usr/bin/env python3
"""
Shine Skin Collective - Hare Run V6 API Gateway
Enhanced ML-powered skin analysis with S3 model management
"""

import os
import base64
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import numpy as np
import cv2
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow frontend access
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001', 'http://127.0.0.1:3002'], supports_credentials=True)

# Service configuration
SERVICE_NAME = "shine-backend-hare-run-v6"
S3_BUCKET = os.getenv('S3_BUCKET', 'shine-skincare-models')
S3_MODEL_KEY = os.getenv('S3_MODEL_KEY', 'ml-models/production/comprehensive_model_best.h5')
LOCAL_MODEL_PATH = os.getenv('MODEL_PATH', './models/fixed_model_best.h5')
PORT = int(os.getenv('PORT', 8000))

# Hare Run V6 Configuration
HARE_RUN_V6_CONFIG = {
    'enabled': True,
    'models': {
        'facial': {
            'primary': 'comprehensive_model_best.h5',
            'backup': 'fixed_model_best.h5',
            'metadata': 'comprehensive_model_best.h5'
        }
    },
    'endpoints': {
        'skin_analysis': '/api/v6/skin/analyze-hare-run',
        'model_status': '/api/v5/skin/model-status'
    },
    'performance': {
        'target_accuracy': '97.13%',
        'max_response_time': '30s',
        'model_size': '214MB'
    }
}

# Initialize S3 client with error handling
try:
    s3_client = boto3.client('s3')
    logger.info("✅ S3 client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize S3 client: {e}")
    s3_client = None

# Initialize advanced analysis systems
try:
    from enhanced_analysis_algorithms import EnhancedSkinAnalyzer
    enhanced_analyzer = EnhancedSkinAnalyzer()
    logger.info("✅ Enhanced skin analyzer initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize enhanced analyzer: {e}")
    enhanced_analyzer = None

# Hare Run V6 Model Manager - LAZY LOADING VERSION
class HareRunV6ModelManager:
    """Manages Hare Run V6 model loading and availability with lazy loading"""
    
    def __init__(self):
        self.models_loaded = False
        self.model_paths = {}
        self.model_metadata = {}
        self._models_loaded = False  # Don't load models during init
    
    def _ensure_models_loaded(self):
        """Lazy load models only when needed"""
        if not self._models_loaded:
            self._load_models()
            self._models_loaded = True
    
    def _load_models(self):
        """Load Hare Run V6 models from local or S3"""
        try:
            # Check local models first
            local_models_dir = Path('./models')
            if local_models_dir.exists():
                self._load_local_models(local_models_dir)
            
            # If local models not available, try S3