#!/usr/bin/env python3
"""
Environment Setup Script for Shine App
Helps configure environment variables for development
"""

import os
import secrets
import subprocess
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def setup_backend_env():
    """Set up backend environment file"""
    print("🔧 Setting up backend environment...")
    
    # Check if .env already exists
    if Path("backend/.env").exists():
        print("⚠️  backend/.env already exists. Skipping...")
        return
    
    # Copy example file
    if Path("backend/env.enhanced.example").exists():
        subprocess.run(["cp", "backend/env.enhanced.example", "backend/.env"])
        print("✅ Copied env.enhanced.example to backend/.env")
    else:
        print("❌ env.enhanced.example not found in backend/")
        return
    
    # Generate secure keys
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    # Update .env with generated keys
    with open("backend/.env", "r") as f:
        content = f.read()
    
    content = content.replace("your-super-secret-flask-key-change-this-in-production", secret_key)
    content = content.replace("your-super-secret-jwt-key-change-this-in-production", jwt_secret)
    
    with open("backend/.env", "w") as f:
        f.write(content)
    
    print("✅ Generated secure keys for backend")

def setup_frontend_env():
    """Set up frontend environment file"""
    print("🔧 Setting up frontend environment...")
    
    # Check if .env.local already exists
    if Path(".env.local").exists():
        print("⚠️  .env.local already exists. Skipping...")
        return
    
    # Copy example file
    if Path("env.frontend.example").exists():
        subprocess.run(["cp", "env.frontend.example", ".env.local"])
        print("✅ Copied env.frontend.example to .env.local")
    else:
        print("❌ env.frontend.example not found")
        return

def main():
    """Main setup function"""
    print("🚀 Shine App Environment Setup")
    print("=" * 40)
    
    setup_backend_env()
    setup_frontend_env()
    
    print("\n✅ Environment setup complete!")
    print("\n📝 Next steps:")
    print("1. Update backend/.env with your actual credentials")
    print("2. Update .env.local with your frontend credentials")
    print("3. Set up Google Cloud Vision AI: python backend/setup_google_vision.py")
    print("4. Test your setup: npm run dev")

if __name__ == "__main__":
    main() 