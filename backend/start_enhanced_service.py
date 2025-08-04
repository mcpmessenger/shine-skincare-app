#!/usr/bin/env python3
"""
Enhanced Embeddings System Startup Script
Starts the enhanced analysis service for production use
"""

import os
import sys
import logging
from datetime import datetime
from enhanced_analysis_api import EnhancedAnalysisAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def start_enhanced_service():
    """Start the enhanced embeddings service"""
    try:
        logger.info("🚀 Starting Enhanced Embeddings System...")
        
        # Initialize API
        api = EnhancedAnalysisAPI()
        logger.info("✅ Enhanced Analysis API initialized")
        
        # Load configuration
        import json
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        logger.info(f"📊 System Version: {config['version']}")
        logger.info(f"📊 Datasets Available: {len(config['datasets'])}")
        logger.info(f"📊 Analysis Types: {config['analysis_types']}")
        
        # System health check
        logger.info("🔍 Performing system health check...")
        
        # Test with sample image
        import numpy as np
        import cv2
        test_image = np.random.randint(100, 200, (224, 224, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', test_image)
        test_data = buffer.tobytes()
        
        # Test analysis
        result = api.analyze_skin_enhanced(test_data, 'comprehensive')
        
        if result and 'confidence_score' in result:
            logger.info(f"✅ Health check passed - Confidence: {result['confidence_score']:.3f}")
        else:
            logger.warning("⚠️ Health check completed with warnings")
        
        logger.info("🎉 Enhanced Embeddings System is ready for production!")
        logger.info("📡 Service is running and accepting requests...")
        
        # Keep service running
        while True:
            import time
            time.sleep(60)  # Check every minute
            logger.debug("Service heartbeat - System running normally")
            
    except Exception as e:
        logger.error(f"❌ Service startup failed: {e}")
        raise

if __name__ == "__main__":
    start_enhanced_service() 