#!/usr/bin/env python3
"""
Smart dependency installer for Shine ML backend
Tries optimized requirements first, falls back to minimal if needed
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, timeout=600):
    """Run a command with timeout and return success status"""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_available_memory():
    """Check if we have enough memory for ML packages"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        print(f"Available memory: {available_gb:.1f} GB")
        return available_gb > 2.0  # Need at least 2GB for ML packages
    except:
        print("Could not check memory, assuming sufficient")
        return True

def install_requirements(requirements_file):
    """Install requirements from a specific file"""
    if not Path(requirements_file).exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print(f"📦 Installing from {requirements_file}...")
    
    # Upgrade pip first
    if not run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']):
        print("⚠️ Could not upgrade pip, continuing anyway...")
    
    # Install requirements
    cmd = [
        sys.executable, '-m', 'pip', 'install', 
        '-r', requirements_file,
        '--no-cache-dir',
        '--timeout', '300'
    ]
    
    return run_command(cmd, timeout=1200)  # 20 minutes for ML packages

def main():
    print("🚀 Smart Dependency Installer for Shine ML Backend")
    print("=" * 55)
    
    # Check system resources
    has_memory = check_available_memory()
    
    # Try installation strategies in order
    strategies = [
        ("requirements-optimized.txt", "Optimized ML dependencies"),
        ("requirements-aws.txt", "AWS-specific dependencies"),
        ("requirements-minimal.txt", "Minimal fallback dependencies")
    ]
    
    for requirements_file, description in strategies:
        print(f"\n🔄 Attempting: {description}")
        
        if not has_memory and "optimized" in requirements_file:
            print("⚠️ Low memory detected, skipping heavy ML packages")
            continue
        
        if install_requirements(requirements_file):
            print(f"✅ Successfully installed {description}")
            
            # Set environment variable based on what was installed
            if "minimal" in requirements_file:
                os.environ['USE_MOCK_SERVICES'] = 'true'
                print("🔧 Configured to use mock services for missing ML packages")
            else:
                os.environ['USE_MOCK_SERVICES'] = 'false'
                print("🔧 Configured to use production ML services")
            
            # Validate installation
            print("\n🧪 Validating installation...")
            if run_command([sys.executable, 'validate-dependencies.py']):
                print("🎉 Installation completed successfully!")
                return 0
            else:
                print("⚠️ Some packages may not be working correctly")
                return 0
        else:
            print(f"❌ Failed to install {description}")
    
    print("❌ All installation strategies failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())