#!/usr/bin/env python3
"""
Check for Hare Run V6 models in S3
"""

import boto3
import os

def check_v6_models():
    """Check for Hare Run V6 models in S3"""
    print("🔍 Checking for Hare Run V6 models in S3...")
    
    s3_bucket = 'shine-skincare-models'
    
    try:
        s3_client = boto3.client('s3')
        
        # Check for hare_run_v6 models
        v6_prefixes = [
            "hare_run_v6/",
            "v6/",
            "hare-run-v6/",
            "ml-models/production/hare_run_v6/",
            "ml-models/production/v6/"
        ]
        
        print("📋 Checking for V6 models in these paths:")
        for prefix in v6_prefixes:
            print(f"   🔍 {prefix}")
            
            try:
                response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prefix, MaxKeys=10)
                if 'Contents' in response:
                    print(f"      ✅ Found {len(response['Contents'])} objects:")
                    for obj in response['Contents']:
                        size_mb = obj['Size'] / (1024 * 1024)
                        print(f"         📁 {obj['Key']} ({size_mb:.1f} MB)")
                else:
                    print(f"      ⚠️  No objects found")
            except Exception as e:
                print(f"      ❌ Error checking {prefix}: {e}")
        
        # Also check for any files with "v6" in the name
        print("\n🔍 Searching for any files with 'v6' in the name...")
        response = s3_client.list_objects_v2(Bucket=s3_bucket, MaxKeys=100)
        if 'Contents' in response:
            v6_files = [obj for obj in response['Contents'] if 'v6' in obj['Key'].lower()]
            if v6_files:
                print(f"✅ Found {len(v6_files)} files with 'v6' in name:")
                for obj in v6_files:
                    size_mb = obj['Size'] / (1024 * 1024)
                    print(f"   📁 {obj['Key']} ({size_mb:.1f} MB)")
            else:
                print("⚠️  No files with 'v6' found")
        
        # Check current production models
        print("\n📋 Current production models:")
        prod_prefix = "ml-models/production/"
        response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=prod_prefix, MaxKeys=20)
        if 'Contents' in response:
            for obj in response['Contents']:
                size_mb = obj['Size'] / (1024 * 1024)
                print(f"   📁 {obj['Key']} ({size_mb:.1f} MB)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_v6_models()
