#!/usr/bin/env python3
"""
Google Vision AI Setup Script
Automates the setup and testing of Google Cloud Vision AI integration
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables
project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")
    print("-" * 40)

def check_file_exists(file_path):
    """Check if a file exists"""
    return Path(file_path).exists()

def check_env_var(var_name):
    """Check if environment variable is set"""
    return os.environ.get(var_name) is not None

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def test_google_vision_service():
    """Test the Google Vision service"""
    print_step("Testing", "Google Vision Service")
    
    try:
        # Import the service
        sys.path.append('.')
        from app.services.google_vision_service import GoogleVisionService
        
        # Initialize service
        service = GoogleVisionService()
        
        # Check if available
        if service.is_available():
            print("✅ Google Vision service is available")
            
            # Test with a sample image (if available)
            test_image_path = "test_image.jpg"
            if check_file_exists(test_image_path):
                print("Testing with sample image...")
                with open(test_image_path, 'rb') as f:
                    image_bytes = f.read()
                
                result = service.analyze_image_from_bytes(image_bytes)
                if result.get('status') == 'success':
                    print("✅ Image analysis successful")
                    print(f"Results: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Image analysis failed: {result.get('error')}")
            else:
                print("ℹ️  No test image found. Service is ready for use.")
            
            return True
        else:
            print("❌ Google Vision service is not available")
            print("Please check your credentials and configuration")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the backend directory and dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def main():
    """Main setup function"""
    print_header("Google Vision AI Setup")
    
    # Check if we're in the right directory
    if not check_file_exists("requirements.txt"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Step 1: Check environment
    print_step("1", "Checking Environment")
    
    env_file = ".env"
    if not check_file_exists(env_file):
        print("❌ .env file not found")
        print("Please copy env.enhanced.example to .env and configure it")
        return False
    
    # Check Google Cloud configuration
    # project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    # credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not set")
        print("Please set this in your .env file")
        return False
    
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("Please set this in your .env file")
        return False
    
    if not check_file_exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please download your service account key and place it in the correct location")
        return False
    
    print("✅ Environment configuration looks good")
    
    # Step 2: Check dependencies
    print_step("2", "Checking Dependencies")
    
    required_packages = [
        'google-cloud-vision',
        'PIL',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'google-cloud-vision':
                import google.cloud.vision
            elif package == 'numpy':
                import numpy
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        if not run_command("pip install -r requirements.txt", "Install dependencies"):
            return False
    
    # Step 3: Test Google Vision service
    print_step("3", "Testing Google Vision Service")
    
    if not test_google_vision_service():
        print("\n❌ Google Vision service test failed")
        print("Please check the setup guide for troubleshooting steps")
        return False
    
    # Step 4: Test API endpoint
    print_step("4", "Testing API Endpoint")
    
    # Check if Flask app can start
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False
    
    print_header("Setup Complete!")
    print("🎉 Google Vision AI is ready to use!")
    print("\nNext steps:")
    print("1. Start your Flask backend: python run.py")
    print("2. Start your Next.js frontend: npm run dev")
    print("3. Visit: http://localhost:3000/skin-analysis-mvp")
    print("4. Test with a real selfie!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 