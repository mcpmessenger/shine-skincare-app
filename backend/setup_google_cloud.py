#!/usr/bin/env python3
"""
Google Cloud Setup Script for Shine Skincare App
Helps configure Google Cloud credentials and test integration
"""

import os
import json
import logging
from google_cloud_integration import GoogleCloudIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_google_cloud_credentials():
    """Setup Google Cloud credentials"""
    print("🔧 Setting up Google Cloud credentials...")
    
    # Check for existing credentials
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    print(f"Current credentials path: {credentials_path}")
    print(f"Current project ID: {project_id}")
    
    if not credentials_path:
        print("⚠️ No GOOGLE_APPLICATION_CREDENTIALS environment variable found")
        print("To enable Google Cloud features, you need to:")
        print("1. Create a Google Cloud project")
        print("2. Enable Vision API and Vertex AI")
        print("3. Create a service account and download the JSON key")
        print("4. Set GOOGLE_APPLICATION_CREDENTIALS to the path of your JSON key")
        print("5. Set GOOGLE_CLOUD_PROJECT to your project ID")
        return False
    
    if not project_id:
        print("⚠️ No GOOGLE_CLOUD_PROJECT environment variable found")
        print("Set GOOGLE_CLOUD_PROJECT to your Google Cloud project ID")
        return False
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return False
    
    print("✅ Google Cloud credentials configured")
    return True

def test_google_cloud_integration():
    """Test Google Cloud integration"""
    print("\n🧪 Testing Google Cloud integration...")
    
    # Initialize Google Cloud integration
    google_cloud = GoogleCloudIntegration()
    
    # Get status
    status = google_cloud.get_status()
    print(f"Google Cloud Status: {json.dumps(status, indent=2)}")
    
    if google_cloud.is_available():
        print("✅ Google Cloud integration is available!")
        return True
    else:
        print("❌ Google Cloud integration is not available")
        print("This is normal if credentials are not configured")
        return False

def create_sample_environment_file():
    """Create a sample .env file for Google Cloud configuration"""
    env_content = """# Google Cloud Configuration
# Replace these values with your actual Google Cloud project details

# Path to your Google Cloud service account JSON key file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Your Google Cloud project ID
GOOGLE_CLOUD_PROJECT=your-project-id

# Google Cloud location (default: us-central1)
GOOGLE_CLOUD_LOCATION=us-central1

# Enable/disable Google Cloud features
VISION_API_ENABLED=true
VERTEX_AI_ENABLED=true
"""
    
    env_file_path = ".env.google_cloud"
    with open(env_file_path, 'w') as f:
        f.write(env_content)
    
    print(f"📝 Created sample environment file: {env_file_path}")
    print("Edit this file with your actual Google Cloud credentials")

def print_setup_instructions():
    """Print setup instructions"""
    print("\n📋 Google Cloud Setup Instructions:")
    print("=" * 50)
    print("1. Create a Google Cloud Project:")
    print("   - Go to https://console.cloud.google.com")
    print("   - Create a new project or select existing one")
    print("   - Note your project ID")
    print()
    print("2. Enable Required APIs:")
    print("   - Go to APIs & Services > Library")
    print("   - Enable 'Cloud Vision API'")
    print("   - Enable 'Vertex AI API'")
    print()
    print("3. Create Service Account:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'Create Credentials' > 'Service Account'")
    print("   - Give it a name (e.g., 'shine-skincare-app')")
    print("   - Assign roles: 'Cloud Vision API User', 'Vertex AI User'")
    print("   - Create and download the JSON key file")
    print()
    print("4. Configure Environment Variables:")
    print("   - Set GOOGLE_APPLICATION_CREDENTIALS to your JSON key path")
    print("   - Set GOOGLE_CLOUD_PROJECT to your project ID")
    print("   - Or use the sample .env.google_cloud file")
    print()
    print("5. Test Integration:")
    print("   - Run this script again to test")
    print("   - Check the Flask server logs for Google Cloud status")

def main():
    """Main setup function"""
    print("🚀 Google Cloud Setup for Shine Skincare App")
    print("=" * 50)
    
    # Check current setup
    credentials_ok = setup_google_cloud_credentials()
    
    # Test integration
    integration_ok = test_google_cloud_integration()
    
    # Create sample environment file
    create_sample_environment_file()
    
    # Print instructions
    print_setup_instructions()
    
    # Summary
    print("\n📊 Setup Summary:")
    print("=" * 50)
    print(f"Credentials configured: {'✅' if credentials_ok else '❌'}")
    print(f"Integration available: {'✅' if integration_ok else '❌'}")
    
    if integration_ok:
        print("\n🎉 Google Cloud integration is ready!")
        print("The Flask server will now use Google Cloud Vision API and Vertex AI")
    else:
        print("\n⚠️ Google Cloud integration is not available")
        print("The Flask server will use local fallbacks")
        print("Follow the setup instructions above to enable Google Cloud features")

if __name__ == "__main__":
    main() 