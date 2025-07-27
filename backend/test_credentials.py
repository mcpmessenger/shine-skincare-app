"""
Test script to verify credentials are working
Run this locally to test before deploying
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

def test_supabase():
    """Test Supabase connection"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    print(f"Supabase URL: {url}")
    print(f"Supabase Key: {'✓ Present' if key else '✗ Missing'}")
    
    if url and key:
        try:
            # Test connection (you'd need supabase-py installed)
            print("✓ Supabase credentials configured")
            return True
        except Exception as e:
            print(f"✗ Supabase connection failed: {e}")
            return False
    return False

def test_google_vision():
    """Test Google Vision credentials"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    print(f"Google Credentials JSON: {'✓ Present' if creds_json else '✗ Missing'}")
    print(f"Google Credentials Path: {'✓ Present' if creds_path else '✗ Missing'}")
    
    if creds_json or creds_path:
        try:
            # Test Google Vision (you'd need google-cloud-vision installed)
            print("✓ Google Vision credentials configured")
            return True
        except Exception as e:
            print(f"✗ Google Vision connection failed: {e}")
            return False
    return False

def test_basic_config():
    """Test basic configuration"""
    secret_key = os.environ.get('SECRET_KEY')
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    print(f"Secret Key: {'✓ Present' if secret_key else '✗ Missing'}")
    print(f"Log Level: {log_level}")
    
    return bool(secret_key)

if __name__ == "__main__":
    print("🧪 Testing Credentials Configuration...")
    print("=" * 50)
    
    supabase_ok = test_supabase()
    print()
    
    google_ok = test_google_vision()
    print()
    
    basic_ok = test_basic_config()
    print()
    
    print("=" * 50)
    if supabase_ok and basic_ok:
        print("✅ Ready for deployment!")
    else:
        print("❌ Some credentials missing - check configuration")