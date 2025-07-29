#!/usr/bin/env python3
"""
Python script to create a Linux-compatible zip file for Elastic Beanstalk
This script ensures forward slashes are used in the zip file
"""

import os
import zipfile
import shutil

def create_deployment_zip():
    print("Creating Python deployment zip file...")
    
    # Remove existing zip file
    if os.path.exists("backend-deployment-python.zip"):
        os.remove("backend-deployment-python.zip")
    
    # Create temporary directory
    temp_dir = "temp-python-deploy"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Copy essential files
    print("Copying essential files...")
    
    files_to_copy = [
        "backend/simple_server_basic.py",
        "backend/Procfile",
        "backend/requirements-eb.txt",
        "backend/requirements.txt",
        "backend/.ebignore",
        "backend/README.md"
    ]
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            dest_path = os.path.join(temp_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            print(f"Copied {file_path}")
    
    # Copy .ebextensions directory
    if os.path.exists("backend/.ebextensions"):
        shutil.copytree("backend/.ebextensions", os.path.join(temp_dir, ".ebextensions"))
        print("Copied .ebextensions directory")
    
    # Create zip file with forward slashes
    print("Creating zip file with forward slashes...")
    
    with zipfile.ZipFile("backend-deployment-python.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Convert to forward slashes for the archive
                arcname = os.path.relpath(file_path, temp_dir).replace("\\", "/")
                zipf.write(file_path, arcname)
                print(f"Added to zip: {arcname}")
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Check file size
    if os.path.exists("backend-deployment-python.zip"):
        size = os.path.getsize("backend-deployment-python.zip")
        print(f"SUCCESS: Python deployment zip file created at backend-deployment-python.zip")
        print(f"File size: {size} bytes")
        print("You can now upload this file to Elastic Beanstalk.")
    else:
        print("ERROR: Failed to create zip file.")

if __name__ == "__main__":
    create_deployment_zip() 