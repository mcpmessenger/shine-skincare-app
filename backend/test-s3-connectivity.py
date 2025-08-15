#!/usr/bin/env python3
"""
Test S3 connectivity and model availability for Hare Run V6
"""

import boto3
import os
from pathlib import Path

def test_s3_connectivity():
    """Test S3 connectivity and list available models"""
    print("🔍 Testing S3 connectivity for Hare Run V6...")
    
    # S3 configuration
    s3_bucket = os.getenv('S3_BUCKET', 'shine-skincare-models')
    s3_model_key = os.getenv('S3_MODEL_KEY', 'hare_run_v6/hare_run_v6_facial/best_facial_model.h5')
    
    print(f"📦 S3 Bucket: {s3_bucket}")
    print(f"🔑 Model Key: {s3_model_key}")
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        print("✅ S3 client initialized successfully")
        
        # Test bucket access
        response = s3_client.head_bucket(Bucket=s3_bucket)
        print(f"✅ Bucket '{s3_bucket}' accessible")
        
        # List objects in ml-models/production/
        prefix = "ml-models/production/"
        response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prefix, MaxKeys=10)
        
        if 'Contents' in response:
            print(f"📋 Found {len(response['Contents'])} objects in {prefix}:")
            for obj in response['Contents']:
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"   📁 {obj['Key']} ({size_mb:.1f} MB)")
        else:
            print(f"⚠️  No objects found in {prefix}")
        
        # Check specific model file
        try:
            response = s3_client.head_object(Bucket=s3_bucket, Key=s3_model_key)
            size_mb = response['ContentLength'] / (1024 * 1024)
            print(f"✅ Model file found: {s3_model_key} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"❌ Model file not found: {s3_model_key}")
            print(f"   Error: {e}")
        
    except Exception as e:
        print(f"❌ S3 connectivity test failed: {e}")
        return False
    
    return True

def test_local_models():
    """Check for local models"""
    print("\n🔍 Checking local models...")
    
    models_dir = Path('./models')
    if models_dir.exists():
        print(f"✅ Models directory exists: {models_dir}")
        for model_file in models_dir.glob('*.h5'):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"   📁 {model_file.name} ({size_mb:.1f} MB)")
    else:
        print("⚠️  Local models directory not found")
    
    results_dir = Path('./results')
    if results_dir.exists():
        print(f"✅ Results directory exists: {results_dir}")
        for model_file in results_dir.glob('*.h5'):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"   📁 {model_file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    print("🚀 Hare Run V6 S3 Connectivity Test")
    print("=" * 50)
    
    # Test S3
    s3_ok = test_s3_connectivity()
    
    # Test local models
    test_local_models()
    
    print("\n" + "=" * 50)
    if s3_ok:
        print("✅ S3 connectivity test completed successfully")
    else:
        print("❌ S3 connectivity test failed")
    
    print("\n💡 Next steps:")
    if s3_ok:
        print("   1. Build Hare Run V6 container: .\\build-hare-run-v6.ps1")
        print("   2. Deploy to production: .\\deploy-hare-run-v6.ps1")
    else:
        print("   1. Check AWS credentials and permissions")
        print("   2. Verify S3 bucket exists and is accessible")
        print("   3. Ensure model files are uploaded to S3")
