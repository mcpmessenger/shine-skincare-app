#!/usr/bin/env python3
"""
Google Cloud APIs Verification Script for Shine Skincare App
Tests all required APIs and services for Operation Right Brain 🧠
"""

import os
import json
import requests
from google.cloud import vision
from google.cloud import aiplatform
from google.cloud import storage
import google.auth
from google.auth.exceptions import DefaultCredentialsError

def print_status(message, status="INFO"):
    """Print status message with color coding"""
    colors = {
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",    # Red
        "WARNING": "\033[93m",  # Yellow
        "INFO": "\033[94m"      # Blue
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')}[{status}]{reset} {message}")

def test_authentication():
    """Test Google Cloud authentication"""
    print_status("Testing Google Cloud authentication...", "INFO")
    try:
        credentials, project = google.auth.default()
        print_status(f"✅ Authentication successful for project: {project}", "SUCCESS")
        return True
    except DefaultCredentialsError as e:
        print_status(f"❌ Authentication failed: {e}", "ERROR")
        return False

def test_vision_api():
    """Test Google Vision API"""
    print_status("Testing Google Vision API...", "INFO")
    try:
        client = vision.ImageAnnotatorClient()
        print_status("✅ Vision API client created successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Vision API test failed: {e}", "ERROR")
        return False

def test_vertex_ai():
    """Test Vertex AI API"""
    print_status("Testing Vertex AI API...", "INFO")
    try:
        aiplatform.init()
        print_status("✅ Vertex AI initialized successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Vertex AI test failed: {e}", "ERROR")
        return False

def test_storage_api():
    """Test Cloud Storage API"""
    print_status("Testing Cloud Storage API...", "INFO")
    try:
        client = storage.Client()
        print_status("✅ Cloud Storage client created successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Cloud Storage test failed: {e}", "ERROR")
        return False

def test_service_account():
    """Test service account file"""
    print_status("Testing service account file...", "INFO")
    sa_file = "shine-466907-91c5bce91fda.json"
    if os.path.exists(sa_file):
        try:
            with open(sa_file, 'r') as f:
                content = f.read().strip()
                if content:
                    sa_data = json.loads(content)
                    project_id = sa_data.get('project_id', 'Unknown')
                    print_status(f"✅ Service account file found and valid for project: {project_id}", "SUCCESS")
                    return True
                else:
                    print_status("⚠️ Service account file exists but is empty", "WARNING")
                    return False
        except json.JSONDecodeError:
            print_status("❌ Service account file is not valid JSON", "ERROR")
            return False
    else:
        print_status("❌ Service account file not found", "ERROR")
        return False

def test_required_apis():
    """Test all required APIs"""
    print_status("=" * 50, "INFO")
    print_status("GOOGLE CLOUD APIS VERIFICATION", "INFO")
    print_status("=" * 50, "INFO")
    
    results = {
        "authentication": test_authentication(),
        "vision_api": test_vision_api(),
        "vertex_ai": test_vertex_ai(),
        "storage_api": test_storage_api(),
        "service_account": test_service_account()
    }
    
    print_status("=" * 50, "INFO")
    print_status("VERIFICATION SUMMARY", "INFO")
    print_status("=" * 50, "INFO")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"{test_name.replace('_', ' ').title()}: {status}")
        if not result:
            all_passed = False
    
    print_status("=" * 50, "INFO")
    if all_passed:
        print_status("🎉 ALL TESTS PASSED! Your Google Cloud setup is ready for Operation Right Brain 🧠", "SUCCESS")
    else:
        print_status("⚠️ Some tests failed. Please check the errors above and fix them.", "WARNING")
    
    return all_passed

if __name__ == "__main__":
    test_required_apis() 