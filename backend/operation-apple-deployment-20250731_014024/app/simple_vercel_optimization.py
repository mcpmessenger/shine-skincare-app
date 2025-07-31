"""
Simplified Vercel optimizations - only the essentials
"""
import os
import time
import logging
from functools import lru_cache
import threading

logger = logging.getLogger(__name__)


class SimpleVercelOptimizer:
    """Essential Vercel optimizations only"""
    
    def __init__(self):
        self.cold_start_time = time.time()
        self.initialized = False
    
    def is_cold_start(self) -> bool:
        """Check if this is a cold start (first 30 seconds)"""
        return time.time() - self.cold_start_time < 30
    
    def optimize_for_cold_start(self):
        """Essential cold start optimizations"""
        if self.initialized:
            return
        
        logger.info("Applying essential Vercel optimizations...")
        
        # Pre-import critical modules
        try:
            import numpy as np
            import json
            logger.debug("Pre-imported essential modules")
        except ImportError as e:
            logger.warning(f"Could not pre-import modules: {e}")
        
        # Set memory-efficient environment variables
        os.environ.setdefault('OMP_NUM_THREADS', '2')
        os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
        
        self.initialized = True
        logger.info("Essential Vercel optimizations complete")


# Simple caching with LRU
@lru_cache(maxsize=100)
def cached_demographic_similarity(ethnicity1, skin_type1, age_group1, 
                                 ethnicity2, skin_type2, age_group2):
    """Simple cached demographic similarity calculation"""
    score = 0.0
    if ethnicity1 == ethnicity2:
        score += 0.4
    if skin_type1 == skin_type2:
        score += 0.3
    if age_group1 == age_group2:
        score += 0.3
    return score


# Memory-efficient configuration
def get_vercel_config():
    """Get memory-efficient configuration for Vercel"""
    return {
        'faiss_dimension': 128,  # Reduced for memory efficiency
        'max_cache_size': 50,    # Smaller cache
        'batch_size': 16,        # Smaller batches
        'max_workers': 2         # Limit concurrency
    }


# Global optimizer
vercel_optimizer = SimpleVercelOptimizer()


def apply_vercel_optimizations():
    """Apply essential Vercel optimizations"""
    vercel_optimizer.optimize_for_cold_start()


def configure_vercel_app(app):
    """Configure Flask app for Vercel deployment"""
    
    @app.before_first_request
    def initialize_vercel():
        """Initialize on first request"""
        apply_vercel_optimizations()
    
    @app.route('/api/vercel/health')
    def vercel_health():
        """Simple health check for Vercel"""
        from flask import jsonify
        return jsonify({
            'status': 'healthy',
            'cold_start': vercel_optimizer.is_cold_start(),
            'initialized': vercel_optimizer.initialized
        })
    
    return app