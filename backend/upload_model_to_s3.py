#!/usr/bin/env python3
"""
Helper script to upload ML model files to S3
Run this script to upload your model files to S3 for Elastic Beanstalk deployment
"""

import boto3
import os
import sys
from botocore.exceptions import ClientError

def upload_model_to_s3(bucket_name, model_file_path, s3_key=None):
    """Upload model file to S3 bucket"""
    
    if not os.path.exists(model_file_path):
        print(f"❌ Error: Model file not found at {model_file_path}")
        return False
    
    if s3_key is None:
        s3_key = os.path.basename(model_file_path)
    
    try:
        # Create S3 client with minimal configuration
        s3_client = boto3.client('s3')
        
        # Check if bucket exists, create if it doesn't
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"🔄 Creating bucket '{bucket_name}'...")
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created successfully")
            else:
                raise e
        
        # Upload the file
        print(f"🔄 Uploading {model_file_path} to s3://{bucket_name}/{s3_key}...")
        s3_client.upload_file(model_file_path, bucket_name, s3_key)
        
        # Verify upload
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        print(f"✅ Model uploaded successfully to s3://{bucket_name}/{s3_key}")
        
        # Get file size
        file_size = os.path.getsize(model_file_path)
        file_size_mb = file_size / (1024 * 1024)
        print(f"📊 File size: {file_size_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading model: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Shine Skincare App - ML Model S3 Upload")
    print("=" * 50)
    
    # Configuration
    bucket_name = "shine-ml-models-2025"
    model_file = "models/fixed_model_best.h5"
    
    print(f"📦 S3 Bucket: {bucket_name}")
    print(f"📁 Model File: {model_file}")
    print()
    
    # Check if model file exists
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        print("Please make sure you're running this script from the backend directory")
        sys.exit(1)
    
    # Upload model
    success = upload_model_to_s3(bucket_name, model_file)
    
    if success:
        print()
        print("🎉 Model upload completed successfully!")
        print()
        print("Next steps:")
        print("1. Deploy your application: eb deploy")
        print("2. The app will automatically download the model from S3")
        print("3. Test the /ready endpoint to verify model availability")
    else:
        print()
        print("❌ Model upload failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
