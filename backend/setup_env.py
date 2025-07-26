#!/usr/bin/env python3
"""
Environment Setup Script for SCIN Integration

This script helps set up the required environment variables for SCIN integration.
"""

import os
import sys

def setup_environment():
    """Set up environment variables for SCIN integration"""
    
    print("=" * 60)
    print("SCIN Integration Environment Setup")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found!")
        print("Please copy env.enhanced.example to .env first:")
        print("copy env.enhanced.example .env")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Define required variables with defaults
    required_vars = {
        'FAISS_INDEX_PATH': 'faiss_index',
        'FAISS_DIMENSION': '2048',
        'SCIN_BUCKET_PATH': 'gs://dx-scin-public-data/dataset/',
        'SCIN_CACHE_DIR': 'scin_cache',
        'SCIN_VECTOR_CACHE_DIR': 'vector_cache',
        'SCIN_BATCH_SIZE': '100',
        'SCIN_MAX_IMAGES': '1000',
        'SCIN_FEATURE_DIMENSION': '2048',
        'SCIN_VECTORIZATION_MODEL': 'resnet50',
        'SCIN_VECTORIZATION_DEVICE': 'cpu'
    }
    
    # Check which variables are missing
    missing_vars = []
    for var, default_value in required_vars.items():
        if f'{var}=' not in content:
            missing_vars.append((var, default_value))
    
    if not missing_vars:
        print("✅ All required environment variables are already set!")
        return True
    
    print(f"Found {len(missing_vars)} missing environment variables.")
    print("\nAdding missing variables to .env file...")
    
    # Add missing variables to .env file
    with open(env_file, 'a') as f:
        f.write("\n# SCIN Integration Configuration (Auto-added)\n")
        for var, default_value in missing_vars:
            f.write(f"{var}={default_value}\n")
            print(f"  ✅ Added {var}={default_value}")
    
    print(f"\n✅ Environment setup completed!")
    print(f"Updated {env_file} with {len(missing_vars)} variables.")
    
    return True

def test_environment():
    """Test if environment variables are properly set"""
    print("\n" + "=" * 60)
    print("Testing Environment Configuration")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'FAISS_INDEX_PATH',
        'FAISS_DIMENSION',
        'SCIN_BUCKET_PATH',
        'SCIN_CACHE_DIR',
        'SCIN_VECTOR_CACHE_DIR',
        'SCIN_BATCH_SIZE',
        'SCIN_MAX_IMAGES',
        'SCIN_FEATURE_DIMENSION',
        'SCIN_VECTORIZATION_MODEL',
        'SCIN_VECTORIZATION_DEVICE'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}={value}")
        else:
            print(f"❌ {var} not set")
            all_set = False
    
    if all_set:
        print("\n🎉 All environment variables are properly configured!")
        return True
    else:
        print("\n❌ Some environment variables are missing.")
        return False

def main():
    """Main function"""
    try:
        # Set up environment
        if not setup_environment():
            return 1
        
        # Test environment
        if not test_environment():
            return 1
        
        print("\n" + "=" * 60)
        print("Environment Setup Completed Successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python setup_scin_integration.py")
        print("2. Run: python test_scin_integration.py")
        print("3. Start your Flask application")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Environment setup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 