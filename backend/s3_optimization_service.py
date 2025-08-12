#!/usr/bin/env python3
"""
S3 Optimization Service for Shine Skincare App - Phase 3
Enhanced S3 operations with caching, retry logic, and performance monitoring
"""
import os
import boto3
import hashlib
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class S3OptimizationService:
    """Enhanced S3 service with optimization features"""
    
    def __init__(self, bucket_name: str = "muse2025", region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.cache_dir = Path("models/cache")
        self.metadata_file = self.cache_dir / "s3_metadata.json"
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client with retry configuration
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            config=boto3.session.Config(
                retries=dict(
                    max_attempts=3,
                    mode='adaptive'
                )
            )
        )
        
        # Load cached metadata
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cached S3 metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load metadata cache: {e}")
        
        return {}
    
    def _save_metadata(self):
        """Save current metadata to cache"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save metadata cache: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate file hash: {e}")
            return ""
    
    def _get_s3_etag(self, key: str) -> Optional[str]:
        """Get S3 object ETag (MD5 hash)"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return response.get('ETag', '').strip('"')
        except ClientError as e:
            logger.warning(f"Could not get S3 ETag for {key}: {e}")
            return None
    
    def download_model_with_cache(self, model_key: str, local_path: str) -> bool:
        """
        Download model from S3 with intelligent caching
        
        Args:
            model_key: S3 key for the model file
            local_path: Local path to save the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        local_file = Path(local_path)
        cache_key = f"{model_key}_{local_file.name}"
        
        try:
            # Check if we have cached metadata
            if cache_key in self.metadata:
                cached_info = self.metadata[cache_key]
                
                # Check if local file exists and matches cached info
                if local_file.exists():
                    local_hash = self._get_file_hash(local_file)
                    if local_hash == cached_info.get('local_hash'):
                        logger.info(f"✅ Model {local_file.name} already exists and matches cache")
                        return True
            
            # Get current S3 ETag
            s3_etag = self._get_s3_etag(model_key)
            if not s3_etag:
                logger.error(f"❌ Could not get S3 ETag for {model_key}")
                return False
            
            # Check if we need to download
            if (cache_key in self.metadata and 
                self.metadata[cache_key].get('s3_etag') == s3_etag and
                local_file.exists()):
                logger.info(f"✅ Model {local_file.name} is up to date")
                return True
            
            # Download the model
            logger.info(f"📥 Downloading model {model_key} to {local_path}")
            start_time = time.time()
            
            self.s3_client.download_file(
                self.bucket_name, 
                model_key, 
                str(local_file)
            )
            
            download_time = time.time() - start_time
            file_size_mb = local_file.stat().st_size / (1024 * 1024)
            
            # Update metadata
            self.metadata[cache_key] = {
                's3_etag': s3_etag,
                'local_hash': self._get_file_hash(local_file),
                'download_time': download_time,
                'file_size_mb': round(file_size_mb, 2),
                'last_updated': time.time()
            }
            self._save_metadata()
            
            logger.info(f"✅ Model downloaded successfully in {download_time:.2f}s ({file_size_mb:.1f}MB)")
            return True
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            return False
        except ClientError as e:
            logger.error(f"❌ S3 error downloading {model_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error downloading {model_key}: {e}")
            return False
    
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models in S3 with metadata"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix="models/"
            )
            
            models = {}
            for obj in response.get('Contents', []):
                key = obj['Key']
                if key.endswith(('.h5', '.pkl', '.joblib')):
                    models[key] = {
                        'size_bytes': obj['Size'],
                        'size_mb': round(obj['Size'] / (1024 * 1024), 2),
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag'].strip('"')
                    }
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Error listing models: {e}")
            return {}
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get current cache status and statistics"""
        try:
            cache_size = sum(
                f.stat().st_size for f in self.cache_dir.rglob('*') 
                if f.is_file()
            )
            
            return {
                'cache_directory': str(self.cache_dir),
                'cache_size_bytes': cache_size,
                'cache_size_mb': round(cache_size / (1024 * 1024), 2),
                'cached_models': len(self.metadata),
                'metadata_file': str(self.metadata_file),
                'last_updated': time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cache status: {e}")
            return {}
    
    def clear_cache(self) -> bool:
        """Clear the model cache"""
        try:
            # Remove cached files
            for file_path in self.cache_dir.glob('*'):
                if file_path.is_file() and file_path.name != 's3_metadata.json':
                    file_path.unlink()
            
            # Clear metadata
            self.metadata = {}
            self._save_metadata()
            
            logger.info("✅ Model cache cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize the service
    s3_service = S3OptimizationService()
    
    # List available models
    models = s3_service.list_available_models()
    print(f"Available models: {json.dumps(models, indent=2)}")
    
    # Get cache status
    cache_status = s3_service.get_cache_status()
    print(f"Cache status: {json.dumps(cache_status, indent=2)}")
