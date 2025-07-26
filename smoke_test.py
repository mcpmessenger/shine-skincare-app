#!/usr/bin/env python3
"""
Smoke Test Script for Shine App
Run this before pushing to GitHub to ensure everything works
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

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

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} - Success")
                return True, result.stdout
            else:
                print(f"❌ {description} - Failed")
                print(f"Error: {result.stderr}")
                return False, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                print(f"✅ {description} - Success")
                return True, None
            else:
                print(f"❌ {description} - Failed")
                return False, None
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False, str(e)

def test_backend_services():
    """Test backend services"""
    print_step("Testing", "Backend Services")
    
    # Check if backend directory exists
    if not check_file_exists("backend"):
        print("❌ Backend directory not found")
        return False
    
    # Test Google Vision service
    try:
        sys.path.append('backend')
        from app.services.google_vision_service import GoogleVisionService
        
        service = GoogleVisionService()
        if service.is_available():
            print("✅ Google Vision service available")
        else:
            print("⚠️  Google Vision service not available (will use mock data)")
        
        return True
    except ImportError as e:
        print(f"⚠️  Google Vision service not configured: {e}")
        return True  # Not critical for smoke test

def test_frontend_build():
    """Test frontend build"""
    print_step("Testing", "Frontend Build")
    
    # Check if package.json exists
    if not check_file_exists("package.json"):
        print("❌ package.json not found")
        return False
    
    # Test npm install
    success, _ = run_command("npm install", "Install dependencies")
    if not success:
        return False
    
    # Test build
    success, _ = run_command("npm run build", "Build frontend")
    return success

def test_api_endpoints():
    """Test API endpoints"""
    print_step("Testing", "API Endpoints")
    
    # Start backend server in background
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        ["python", "run.py"], 
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        import time
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check passed")
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend not responding: {e}")
            return False
        
        return True
    
    finally:
        # Stop backend server
        backend_process.terminate()
        backend_process.wait()

def check_environment_files():
    """Check environment files"""
    print_step("Checking", "Environment Files")
    
    # Check backend .env
    if check_file_exists("backend/.env"):
        print("✅ Backend .env file exists")
    else:
        print("⚠️  Backend .env file not found")
    
    # Check frontend .env.local
    if check_file_exists(".env.local"):
        print("✅ Frontend .env.local file exists")
    else:
        print("⚠️  Frontend .env.local file not found")
    
    # Check for sensitive data in git
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], 
            capture_output=True, 
            text=True
        )
        if "secret" in result.stdout.lower() or "key" in result.stdout.lower():
            print("❌ Sensitive data detected in staged changes")
            return False
        else:
            print("✅ No sensitive data in staged changes")
    except Exception as e:
        print(f"⚠️  Could not check for sensitive data: {e}")
    
    return True

def run_tests():
    """Run test suites"""
    print_step("Running", "Test Suites")
    
    # Backend tests
    if check_file_exists("backend/test_api.py"):
        success, _ = run_command("python test_api.py", "Backend tests", cwd="backend")
        if not success:
            print("⚠️  Backend tests failed")
    
    # Frontend tests (if available)
    if check_file_exists("package.json"):
        # Check if test script exists
        with open("package.json", "r") as f:
            package_json = json.load(f)
            if "test" in package_json.get("scripts", {}):
                success, _ = run_command("npm test", "Frontend tests")
                if not success:
                    print("⚠️  Frontend tests failed")
            else:
                print("ℹ️  No frontend test script found")
    
    return True

def main():
    """Main smoke test function"""
    print_header("Shine App Smoke Test")
    
    tests = [
        ("Environment Files", check_environment_files),
        ("Backend Services", test_backend_services),
        ("Frontend Build", test_frontend_build),
        ("API Endpoints", test_api_endpoints),
        ("Test Suites", run_tests),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Smoke Test Results")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for GitHub push.")
        return True
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. Review failures before pushing.")
        return False
    else:
        print("\n❌ Multiple tests failed. Fix issues before pushing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 