#!/usr/bin/env python3
"""
UTKFace Dataset Download Script using Kaggle API
This script downloads the UTKFace dataset from Kaggle using the provided API credentials.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def check_kaggle_installed():
    """Check if kaggle CLI is installed"""
    try:
        subprocess.run(["kaggle", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_kaggle():
    """Install kaggle CLI if not already installed"""
    print("📦 Installing Kaggle CLI...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "kaggle"], check=True)
        print("✅ Kaggle CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Kaggle CLI: {e}")
        return False

def setup_kaggle_credentials():
    """Setup Kaggle credentials from the kaggle.json file"""
    print("🔑 Setting up Kaggle credentials...")
    
    # Path to kaggle.json (assuming it's in the project root)
    kaggle_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kaggle.json")
    
    if not os.path.exists(kaggle_json_path):
        print(f"❌ Kaggle credentials file not found at: {kaggle_json_path}")
        return False
    
    # Read the kaggle.json file
    try:
        with open(kaggle_json_path, 'r') as f:
            credentials = json.load(f)
        
        # Create .kaggle directory in user's home
        kaggle_dir = os.path.expanduser("~/.kaggle")
        os.makedirs(kaggle_dir, exist_ok=True)
        
        # Copy kaggle.json to .kaggle directory
        kaggle_credentials_path = os.path.join(kaggle_dir, "kaggle.json")
        shutil.copy2(kaggle_json_path, kaggle_credentials_path)
        
        # Set proper permissions (important for security)
        os.chmod(kaggle_credentials_path, 0o600)
        
        print("✅ Kaggle credentials configured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Kaggle credentials: {e}")
        return False

def download_utkface_dataset():
    """Download UTKFace dataset from Kaggle"""
    print("📥 Downloading UTKFace dataset from Kaggle...")
    
    try:
        # Create data directory
        data_dir = "data/utkface"
        raw_images_dir = os.path.join(data_dir, "raw_images")
        os.makedirs(raw_images_dir, exist_ok=True)
        
        # Download the dataset
        # Updated dataset names based on what's actually available on Kaggle
        dataset_name = "jangedoo/utkface-new"  # This one has the most downloads
        
        print(f"🔍 Attempting to download dataset: {dataset_name}")
        
        # Try to download the dataset
        result = subprocess.run([
            "kaggle", "datasets", "download", 
            "--dataset", dataset_name,
            "--path", data_dir,
            "--unzip"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dataset downloaded successfully!")
            
            # Move files to raw_images directory if needed
            downloaded_files = os.listdir(data_dir)
            for file in downloaded_files:
                if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                    src = os.path.join(data_dir, file)
                    dst = os.path.join(raw_images_dir, file)
                    if os.path.isfile(src):
                        shutil.move(src, dst)
            
            # Also check for subdirectories that might contain the images
            for subdir in os.listdir(data_dir):
                subdir_path = os.path.join(data_dir, subdir)
                if os.path.isdir(subdir_path):
                    print(f"📁 Checking subdirectory: {subdir}")
                    subdir_files = os.listdir(subdir_path)
                    for file in subdir_files:
                        if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                            src = os.path.join(subdir_path, file)
                            dst = os.path.join(raw_images_dir, file)
                            if os.path.isfile(src):
                                shutil.move(src, dst)
                                print(f"  📄 Moved: {file}")
            
            print(f"📁 Files moved to: {raw_images_dir}")
            return True
        else:
            print(f"❌ Failed to download dataset: {result.stderr}")
            
            # Try alternative dataset names (updated with actual available datasets)
            alternative_datasets = [
                "moritzm00/utkface-cropped",
                "chiragsaipanuganti/utkface",
                "samuelagyemang/utkface",
                "aibloy/utkface"
            ]
            
            for alt_dataset in alternative_datasets:
                print(f"🔄 Trying alternative dataset: {alt_dataset}")
                result = subprocess.run([
                    "kaggle", "datasets", "download", 
                    "--dataset", alt_dataset,
                    "--path", data_dir,
                    "--unzip"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Dataset downloaded successfully from: {alt_dataset}")
                    return True
            
            print("❌ Could not download UTKFace dataset from any available source")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return False

def verify_dataset():
    """Verify that the dataset was downloaded correctly"""
    print("🔍 Verifying dataset...")
    
    raw_images_dir = "data/utkface/raw_images"
    
    if not os.path.exists(raw_images_dir):
        print("❌ Raw images directory not found")
        return False
    
    # Count image files
    image_files = [f for f in os.listdir(raw_images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_files) == 0:
        print("❌ No image files found in raw_images directory")
        return False
    
    print(f"✅ Found {len(image_files)} image files")
    
    # Check for UTKFace naming convention (age_gender_ethnicity_*.jpg)
    utkface_files = [f for f in image_files if '_' in f and f.split('_')[0].isdigit()]
    
    if len(utkface_files) > 0:
        print(f"✅ Found {len(utkface_files)} files with UTKFace naming convention")
        return True
    else:
        print("⚠️  No files found with UTKFace naming convention, but proceeding anyway")
        return True

def main():
    """Main function to download UTKFace dataset"""
    print("🧠 UTKFace Dataset Download Script")
    print("==================================")
    
    # Step 1: Check if kaggle CLI is installed
    if not check_kaggle_installed():
        print("📦 Kaggle CLI not found, installing...")
        if not install_kaggle():
            print("❌ Failed to install Kaggle CLI")
            return False
    
    # Step 2: Setup Kaggle credentials
    if not setup_kaggle_credentials():
        print("❌ Failed to setup Kaggle credentials")
        return False
    
    # Step 3: Download dataset
    if not download_utkface_dataset():
        print("❌ Failed to download dataset")
        return False
    
    # Step 4: Verify dataset
    if not verify_dataset():
        print("❌ Dataset verification failed")
        return False
    
    print("")
    print("🎉 UTKFace dataset download completed successfully!")
    print("📁 Dataset location: data/utkface/raw_images/")
    print("")
    print("Next steps:")
    print("1. Run: python setup_utkface_setup.py")
    print("2. Run: python setup_utkface_test.py")
    print("3. Start the backend: python enhanced_app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 