#!/usr/bin/env python3
"""
Setup script for enhanced Shine app features
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if pip is available
    if not shutil.which('pip'):
        print("❌ pip not found. Please install pip first.")
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_env_file():
    """Create .env file from template"""
    print("⚙️ Setting up environment configuration...")
    
    env_template = "env.enhanced.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️ {env_file} already exists, skipping creation")
        return True
    
    if not os.path.exists(env_template):
        print(f"❌ Template file {env_template} not found")
        return False
    
    try:
        shutil.copy(env_template, env_file)
        print(f"✅ Created {env_file} from template")
        print("📝 Please edit .env file with your service credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False

def test_imports():
    """Test if all services can be imported"""
    print("🧪 Testing service imports...")
    
    try:
        # Test basic imports
        from app.services import (
            GoogleVisionService, 
            ImageVectorizationService, 
            FAISSService, 
            SupabaseService
        )
        print("✅ All services imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "uploads",
        "logs",
        "faiss_index"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create {directory}: {e}")
                return False
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Enhanced Shine App Features Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create environment file
    if not create_env_file():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your service credentials")
    print("2. Set up Google Cloud Vision AI (see env.enhanced.example)")
    print("3. Set up Supabase (see env.enhanced.example)")
    print("4. Run database migrations")
    print("5. Start the server: python run.py")
    print("6. Test the services: python test_enhanced_services.py")
    
    print("\n📚 Documentation:")
    print("- See ENHANCED_FEATURES_README.md for detailed instructions")
    print("- See env.enhanced.example for environment setup")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 