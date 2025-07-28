#!/usr/bin/env python3
"""
Dependency validation script for Shine ML backend
Checks if all required packages are installed and working
"""

import sys
import importlib
import subprocess
from typing import Dict, List, Tuple

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError as e:
        return False, str(e)

def get_package_info() -> Dict[str, Tuple[str, str]]:
    """Get information about required packages"""
    packages = {
        # Core dependencies
        'flask': ('flask', 'Flask'),
        'gunicorn': ('gunicorn', 'gunicorn'),
        'numpy': ('numpy', 'numpy'),
        
        # ML dependencies
        'faiss-cpu': ('faiss', 'faiss'),
        'opencv-python-headless': ('cv2', 'opencv-python'),
        'pillow': ('PIL', 'Pillow'),
        'scikit-learn': ('sklearn', 'scikit-learn'),
        'scipy': ('scipy', 'scipy'),
        
        # Google Cloud
        'google-cloud-vision': ('google.cloud.vision', 'google-cloud-vision'),
        'google-auth': ('google.auth', 'google-auth'),
        
        # Database
        'psycopg2-binary': ('psycopg2', 'psycopg2'),
        'supabase': ('supabase', 'supabase'),
        
        # Utilities
        'requests': ('requests', 'requests'),
        'structlog': ('structlog', 'structlog'),
        'psutil': ('psutil', 'psutil'),
    }
    
    results = {}
    for package_name, (import_name, display_name) in packages.items():
        success, info = check_package(import_name)
        results[display_name] = (success, info)
    
    return results

def check_system_requirements():
    """Check system-level requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python {python_version.major}.{python_version.minor}.{python_version.micro} (3.11+ recommended)")
    
    # Check pip version
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("⚠️ pip not available")
    except Exception:
        print("⚠️ Could not check pip version")

def main():
    print("🧪 Validating Shine ML Backend Dependencies")
    print("=" * 50)
    
    # Check system requirements
    check_system_requirements()
    print()
    
    # Check package dependencies
    print("📦 Checking package dependencies...")
    packages = get_package_info()
    
    success_count = 0
    total_count = len(packages)
    
    for package_name, (success, info) in packages.items():
        if success:
            print(f"✅ {package_name}: {info}")
            success_count += 1
        else:
            print(f"❌ {package_name}: {info}")
    
    print()
    print("📊 Summary:")
    print(f"Successful: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All dependencies are installed and working!")
        return 0
    elif success_count >= total_count * 0.8:  # 80% success rate
        print("⚠️ Most dependencies are working. Some optional packages may be missing.")
        return 0
    else:
        print("❌ Critical dependencies are missing. Check installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())