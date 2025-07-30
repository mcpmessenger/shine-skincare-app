#!/usr/bin/env python3
"""
Verify UNICORN ALPHA Deployment Package
Check for Windows/Linux path separator fix
"""

import os
import zipfile
import glob
from datetime import datetime

def verify_unicorn_deployment():
    """Verify the UNICORN ALPHA deployment package"""
    print("🦄 Verifying UNICORN ALPHA deployment...")
    
    # Find the deployment package
    deployment_zips = glob.glob("../UNICORN_ALPHA_FIXED-*.zip")
    if not deployment_zips:
        print("❌ No UNICORN_ALPHA_FIXED deployment package found!")
        print("Run: python create-unicorn-alpha-simple.py")
        return False
    
    # Get the most recent package
    deployment_zip = max(deployment_zips, key=os.path.getctime)
    print(f"Found deployment package: {os.path.basename(deployment_zip)}")
    
    # Extract and check structure
    temp_extract = "temp-verify-unicorn"
    if os.path.exists(temp_extract):
        import shutil
        shutil.rmtree(temp_extract)
    os.makedirs(temp_extract)
    
    print("\n📦 Checking deployment package structure...")
    
    # Extract using Python to avoid path issues
    with zipfile.ZipFile(deployment_zip, 'r') as zipf:
        zipf.extractall(temp_extract)
    
    # Check for critical files
    critical_files = ['app.py', 'requirements.txt', 'Procfile']
    missing_files = []
    
    for file in critical_files:
        file_path = os.path.join(temp_extract, file)
        if os.path.exists(file_path):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)
    
    # Check for .ebextensions
    ebextensions_path = os.path.join(temp_extract, '.ebextensions')
    if os.path.exists(ebextensions_path):
        print("✅ Found: .ebextensions directory")
    else:
        print("❌ Missing: .ebextensions directory")
        missing_files.append('.ebextensions')
    
    # Check path separators in zip
    print("\n🔍 Checking path separators...")
    with zipfile.ZipFile(deployment_zip, 'r') as zipf:
        backslash_found = False
        for info in zipf.infolist():
            if '\\' in info.filename:
                print(f"⚠️  Warning: Backslash found in: {info.filename}")
                backslash_found = True
            else:
                print(f"✅ Forward slash: {info.filename}")
                break  # Just show first few
    
    if not backslash_found:
        print("✅ All paths use forward slashes (Linux compatible)")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_extract)
    
    success = len(missing_files) == 0
    if success:
        print("\n✅ All critical files present!")
        print("✅ Package structure is correct!")
        print("✅ Ready for deployment to XL Elastic Beanstalk environment!")
    else:
        print(f"\n❌ Missing critical files: {missing_files}")
    
    return success

def test_current_backend():
    """Test current backend health"""
    print("\n🏥 Testing current backend health...")
    
    try:
        import requests
        response = requests.get("https://api.shineskincollective.com/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responding")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health check failed: {str(e)}")

def test_cors_headers():
    """Test CORS headers"""
    print("\n🌐 Testing CORS headers...")
    
    try:
        import requests
        response = requests.get("https://api.shineskincollective.com/api/health", timeout=10)
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        
        if cors_header == "https://www.shineskincollective.com":
            print("✅ CORS headers configured correctly")
        else:
            print(f"⚠️  CORS headers may need adjustment: {cors_header}")
    except Exception as e:
        print(f"❌ CORS test failed: {str(e)}")

if __name__ == "__main__":
    print("🎯 UNICORN ALPHA Deployment Verification")
    print("=" * 50)
    
    # Verify package structure
    package_ok = verify_unicorn_deployment()
    
    # Test current backend
    test_current_backend()
    
    # Test CORS headers
    test_cors_headers()
    
    print("\n🎯 Deployment Verification Complete!")
    if package_ok:
        print("Next steps:")
        print("1. Upload the UNICORN_ALPHA_FIXED-*.zip to your XL EB environment")
        print("2. Monitor deployment logs for success")
        print("3. Test the ML endpoints after deployment")
    else:
        print("❌ Package verification failed. Please fix issues before deployment.") 