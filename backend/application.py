# Shine Skincare App - Combined Simplified Backend for Elastic Beanstalk
# This combines simplified ML service and API Gateway functionality in one app
# Updated: 2025-08-10 - Simplified for direct EB deployment with S3 model storage

import os
import json
import logging
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app - Elastic Beanstalk expects this exact variable name
app = Flask(__name__)
CORS(app)

# Configuration
SERVICE_NAME = "shine-backend-combined"
S3_BUCKET = os.getenv('S3_BUCKET', 'shine-ml-models-2025')
S3_MODEL_KEY = os.getenv('S3_MODEL_KEY', 'fixed_model_best.h5')
LOCAL_MODEL_PATH = os.getenv('MODEL_PATH', './models/fixed_model_best.h5')  # Use relative path in current directory
PORT = int(os.getenv('PORT', 8000))

# Initialize S3 client with error handling
try:
    s3_client = boto3.client('s3')
    logger.info("S3 client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {e}")
    s3_client = None

def download_model_from_s3():
    """Download model file from S3 if it doesn't exist locally"""
    try:
        if s3_client is None:
            logger.error("S3 client not available")
            return False
            
        if not os.path.exists(LOCAL_MODEL_PATH):
            # Ensure directory exists
            os.makedirs(os.path.dirname(LOCAL_MODEL_PATH), exist_ok=True)
            
            logger.info(f"Downloading model from S3: s3://{S3_BUCKET}/{S3_MODEL_KEY}")
            logger.info(f"Local path: {LOCAL_MODEL_PATH}")
            logger.info(f"S3 client type: {type(s3_client)}")
            
            # Test S3 access first
            try:
                logger.info("Testing S3 access by listing bucket contents...")
                response = s3_client.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=5)
                logger.info(f"S3 bucket listing successful: {len(response.get('Contents', []))} objects found")
                
                # Check if our model exists
                model_exists = any(obj['Key'] == S3_MODEL_KEY for obj in response.get('Contents', []))
                logger.info(f"Model file exists in S3: {model_exists}")
                
            except Exception as e:
                logger.error(f"S3 access test failed: {e}")
                return False
            
            # Download the model
            logger.info("Starting model download...")
            s3_client.download_file(S3_BUCKET, S3_MODEL_KEY, LOCAL_MODEL_PATH)
            
            # Verify download
            if os.path.exists(LOCAL_MODEL_PATH):
                file_size = os.path.getsize(LOCAL_MODEL_PATH)
                file_size_mb = file_size / (1024 * 1024)
                logger.info(f"Model downloaded successfully to {LOCAL_MODEL_PATH}")
                logger.info(f"Downloaded file size: {file_size_mb:.1f} MB")
                return True
            else:
                logger.error("Model file not found after download attempt")
                return False
        else:
            file_size = os.path.getsize(LOCAL_MODEL_PATH)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"Model already exists at {LOCAL_MODEL_PATH}")
            logger.info(f"Existing file size: {file_size_mb:.1f} MB")
            return True
    except Exception as e:
        logger.error(f"Failed to download model from S3: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        return False

# Health check endpoints
@app.route('/health')
def health():
    """Basic health check"""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "message": "Backend service is running"
    })

@app.route('/api/health')
def api_health():
    """API health check"""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "message": "API is responding"
    })

@app.route('/ready')
def readiness_check():
    """Readiness check - checks if all components are ready"""
    try:
        # Check if model file exists
        model_exists = os.path.exists(LOCAL_MODEL_PATH)
        
        # If model doesn't exist, try to download it
        if not model_exists:
            model_exists = download_model_from_s3()

        return jsonify({
            "status": "ready" if model_exists else "not_ready",
            "service": SERVICE_NAME,
            "model_available": model_exists,
            "model_path": LOCAL_MODEL_PATH,
            "s3_location": f"s3://{S3_BUCKET}/{S3_MODEL_KEY}",
            "s3_client_available": s3_client is not None,
            "message": "Service is ready" if model_exists else "Model file not found"
        })
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "error",
            "service": SERVICE_NAME,
            "error": str(e)
        }), 500

# ML Service endpoints
@app.route('/ml/health')
def ml_health():
    """ML service health check"""
    try:
        model_exists = os.path.exists(LOCAL_MODEL_PATH)
        return jsonify({
            "status": "healthy" if model_exists else "unhealthy",
            "service": "ml-service",
            "model_available": model_exists,
            "model_path": LOCAL_MODEL_PATH,
            "s3_location": f"s3://{S3_BUCKET}/{S3_MODEL_KEY}",
            "s3_client_available": s3_client is not None
        })
    except Exception as e:
        logger.error(f"ML health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "service": "ml-service",
            "error": str(e)
        }), 500

@app.route('/ml/analyze', methods=['POST'])
def ml_analyze():
    """ML analysis endpoint (simplified for now)"""
    try:
        # For now, return a mock response
        # TODO: Implement actual ML analysis when ready
        return jsonify({
            "status": "success",
            "service": "ml-service",
            "message": "Analysis completed (mock response)",
            "result": {
                "skin_condition": "healthy",
                "confidence": 0.95,
                "recommendations": ["Continue current routine", "Stay hydrated"]
            }
        })
    except Exception as e:
        logger.error(f"ML analysis failed: {e}")
        return jsonify({
            "status": "error",
            "service": "ml-service",
            "error": str(e)
        }), 500

# API Gateway endpoints
@app.route('/api/v5/skin/analyze', methods=['POST'])
def skin_analyze():
    """Main skin analysis endpoint"""
    try:
        # For now, return a mock response
        # TODO: Implement actual ML analysis when ready
        return jsonify({
            "status": "success",
            "message": "Skin analysis completed",
            "data": {
                "analysis_id": "mock_123",
                "skin_condition": "healthy",
                "severity": "low",
                "confidence": 0.95,
                "recommendations": [
                    "Continue current skincare routine",
                    "Stay hydrated",
                    "Use sunscreen daily"
                ],
                "timestamp": "2025-01-01T00:00:00Z"
            }
        })
    except Exception as e:
        logger.error(f"Skin analysis failed: {e}")
        return jsonify({
            "status": "error",
            "message": "Analysis failed",
            "error": str(e)
        }), 500

@app.route('/api/v5/skin/health')
def skin_health():
    """Skin analysis service health check"""
    try:
        model_exists = os.path.exists(LOCAL_MODEL_PATH)
        return jsonify({
            "status": "healthy" if model_exists else "unhealthy",
            "service": "skin-analysis",
            "model_available": model_exists,
            "version": "v5",
            "s3_location": f"s3://{S3_BUCKET}/{S3_MODEL_KEY}",
            "s3_client_available": s3_client is not None
        })
    except Exception as e:
        logger.error(f"Skin health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "service": "skin-analysis",
            "error": str(e)
        }), 500

@app.route('/debug/download-model')
def debug_download_model():
    """Debug endpoint to manually trigger model download"""
    try:
        logger.info("Manual model download triggered via debug endpoint")
        
        # Check current status
        model_exists = os.path.exists(LOCAL_MODEL_PATH)
        logger.info(f"Current model status - exists: {model_exists}")
        
        if model_exists:
            file_size = os.path.getsize(LOCAL_MODEL_PATH)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"Existing model file size: {file_size_mb:.1f} MB")
        
        # Try to download
        success = download_model_from_s3()
        
        # Check final status
        final_model_exists = os.path.exists(LOCAL_MODEL_PATH)
        final_file_size = os.path.getsize(LOCAL_MODEL_PATH) if final_model_exists else 0
        final_file_size_mb = final_file_size / (1024 * 1024) if final_model_exists else 0
        
        return jsonify({
            "status": "success" if success else "failed",
            "service": SERVICE_NAME,
            "initial_model_exists": model_exists,
            "final_model_exists": final_model_exists,
            "download_success": success,
            "model_path": LOCAL_MODEL_PATH,
            "s3_location": f"s3://{S3_BUCKET}/{S3_MODEL_KEY}",
            "s3_client_available": s3_client is not None,
            "initial_file_size_mb": round(file_size_mb, 2) if model_exists else 0,
            "final_file_size_mb": round(final_file_size_mb, 2) if final_model_exists else 0,
            "message": "Model download completed" if success else "Model download failed"
        })
    except Exception as e:
        logger.error(f"Debug download endpoint failed: {e}")
        return jsonify({
            "status": "error",
            "service": SERVICE_NAME,
            "error": str(e),
            "error_type": str(type(e))
        }), 500

@app.route('/debug/test-s3')
def debug_test_s3():
    """Debug endpoint to test basic S3 connectivity"""
    try:
        logger.info("S3 connectivity test triggered")
        
        if s3_client is None:
            return jsonify({
                "status": "error",
                "message": "S3 client not available",
                "s3_client_available": False
            }), 500
        
        # Test 1: List buckets
        try:
            logger.info("Testing S3: Listing buckets...")
            buckets = s3_client.list_buckets()
            bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
            logger.info(f"Successfully listed {len(bucket_names)} buckets")
        except Exception as e:
            logger.error(f"Failed to list buckets: {e}")
            return jsonify({
                "status": "error",
                "message": "Failed to list S3 buckets",
                "error": str(e),
                "test": "list_buckets"
            }), 500
        
        # Test 2: Check if our specific bucket exists
        try:
            logger.info(f"Testing S3: Checking bucket {S3_BUCKET}...")
            s3_client.head_bucket(Bucket=S3_BUCKET)
            logger.info(f"Bucket {S3_BUCKET} exists and is accessible")
        except Exception as e:
            logger.error(f"Failed to access bucket {S3_BUCKET}: {e}")
            return jsonify({
                "status": "error",
                "message": f"Failed to access bucket {S3_BUCKET}",
                "error": str(e),
                "test": "head_bucket"
            }), 500
        
        # Test 3: List objects in our bucket
        try:
            logger.info(f"Testing S3: Listing objects in bucket {S3_BUCKET}...")
            objects = s3_client.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=10)
            object_count = len(objects.get('Contents', []))
            object_names = [obj['Key'] for obj in objects.get('Contents', [])]
            logger.info(f"Successfully listed {object_count} objects in bucket")
        except Exception as e:
            logger.error(f"Failed to list objects in bucket {S3_BUCKET}: {e}")
            return jsonify({
                "status": "error",
                "message": f"Failed to list objects in bucket {S3_BUCKET}",
                "error": str(e),
                "test": "list_objects"
            }), 500
        
        # Test 4: Check if our model file exists
        try:
            logger.info(f"Testing S3: Checking if model file {S3_MODEL_KEY} exists...")
            s3_client.head_object(Bucket=S3_BUCKET, Key=S3_MODEL_KEY)
            logger.info(f"Model file {S3_MODEL_KEY} exists in S3")
            model_exists = True
        except Exception as e:
            logger.error(f"Failed to check model file {S3_MODEL_KEY}: {e}")
            model_exists = False
        
        return jsonify({
            "status": "success",
            "message": "S3 connectivity test completed",
            "s3_client_available": True,
            "bucket_accessible": True,
            "bucket_name": S3_BUCKET,
            "objects_count": object_count,
            "sample_objects": object_names[:5],  # First 5 objects
            "model_file_exists": model_exists,
            "model_key": S3_MODEL_KEY,
            "tests_passed": ["list_buckets", "head_bucket", "list_objects"]
        })
        
    except Exception as e:
        logger.error(f"S3 connectivity test failed: {e}")
        return jsonify({
            "status": "error",
            "message": "S3 connectivity test failed",
            "error": str(e),
            "error_type": str(type(e))
        }), 500

@app.route('/debug/disk-space')
def debug_disk_space():
    """Debug endpoint to check disk space"""
    try:
        import shutil
        
        # Check disk space for the current directory
        total, used, free = shutil.disk_usage('.')
        
        # Convert to GB
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        
        # Check disk space for the models directory
        models_dir = os.path.dirname(LOCAL_MODEL_PATH)
        try:
            os.makedirs(models_dir, exist_ok=True)
            models_total, models_used, models_free = shutil.disk_usage(models_dir)
            models_free_gb = models_free / (1024**3)
        except Exception as e:
            models_free_gb = "Error: " + str(e)
        
        return jsonify({
            "status": "success",
            "message": "Disk space check completed",
            "current_directory": {
                "path": os.getcwd(),
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "free_percent": round((free / total) * 100, 2)
            },
            "models_directory": {
                "path": models_dir,
                "free_gb": models_free_gb
            },
            "model_file_size_mb": 224,  # Known size from S3
            "sufficient_space": free_gb > 0.5  # Need at least 500MB for 224MB model
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Disk space check failed",
            "error": str(e),
            "error_type": str(type(e))
        }), 500

# Root endpoint
@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Shine Skincare Backend API",
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/health",
            "ready": "/ready",
            "ml_health": "/ml/health",
            "ml_analyze": "/ml/analyze",
            "skin_analyze": "/api/v5/skin/analyze",
            "skin_health": "/api/v5/skin/health",
            "debug_download": "/debug/download-model",
            "debug_test_s3": "/debug/test-s3",
            "debug_disk_space": "/debug/disk-space"
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} on port {PORT}")
    logger.info(f"Model path: {LOCAL_MODEL_PATH}")
    logger.info(f"S3 location: s3://{S3_BUCKET}/{S3_MODEL_KEY}")
    
    # Download model at startup
    download_model_from_s3()
    
    app.run(debug=False, host='0.0.0.0', port=PORT)