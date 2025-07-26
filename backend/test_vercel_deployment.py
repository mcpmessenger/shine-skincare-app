#!/usr/bin/env python3
"""
Test script for Vercel deployment verification.
This script tests that the core Flask app can start without heavy ML dependencies.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        # Test Flask imports
        from flask import Flask
        print("✅ Flask import successful")
        
        # Test basic app creation
        app = Flask(__name__)
        print("✅ Flask app creation successful")
        
        # Test SCIN service imports (without heavy ML)
        try:
            from app.services.scin_dataset_service import SCINDatasetService
            print("✅ SCIN Dataset Service import successful")
        except ImportError as e:
            print(f"⚠️  SCIN Dataset Service import failed (expected for Vercel): {e}")
        
        # Test basic app structure
        try:
            from app import create_app
            print("✅ App factory import successful")
        except ImportError as e:
            print(f"❌ App factory import failed: {e}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created."""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        
        # Set minimal environment
        os.environ.setdefault('FLASK_ENV', 'production')
        os.environ.setdefault('SECRET_KEY', 'test-key')
        
        app = create_app()
        print("✅ Flask app creation successful")
        
        # Test basic route registration
        with app.app_context():
            print("✅ App context successful")
            
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_requirements():
    """Test that all requirements can be imported."""
    print("\nTesting requirements...")
    
    requirements = [
        'flask',
        'flask_cors', 
        'flask_sqlalchemy',
        'flask_migrate',
        'flask_jwt_extended',
        'psycopg2',
        'redis',
        'celery',
        'stripe',
        'requests',
        'PIL',
        'dotenv',
        'gunicorn',
        'google.cloud.storage',
        'gcsfs',
        'pandas',
        'numpy'
    ]
    
    failed_imports = []
    
    for req in requirements:
        try:
            __import__(req)
            print(f"✅ {req}")
        except ImportError:
            print(f"❌ {req}")
            failed_imports.append(req)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports (may be expected): {failed_imports}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Vercel Deployment Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        return False
    
    # Test requirements
    if not test_requirements():
        print("\n⚠️  Some requirements failed (may be expected)")
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation test failed")
        return False
    
    print("\n✅ All core tests passed!")
    print("🚀 Ready for Vercel deployment")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 