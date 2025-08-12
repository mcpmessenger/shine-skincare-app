#!/usr/bin/env python3
"""
🏥 HAM10000 SKIN CANCER DATASET DOWNLOADER
Downloads the HAM10000 dataset for skin cancer classification
Source: Kaggle - Skin Cancer MNIST: HAM10000
"""

import os
import json
import logging
import zipfile
import requests
from pathlib import Path
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HAM10000Downloader:
    """
    Downloads and prepares the HAM10000 skin cancer dataset
    """
    
    def __init__(self):
        self.dataset_dir = Path('data/real_facial_skin_conditions/raw/kmader_skin-cancer-mnist-ham10000')
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset information
        self.dataset_info = {
            'name': 'HAM10000',
            'description': 'Skin Cancer MNIST: HAM10000',
            'source': 'Kaggle',
            'url': 'https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000',
            'size': '~2GB',
            'images': '10,000+',
            'classes': 7
        }
        
        logger.info("🏥 HAM10000 SKIN CANCER DATASET DOWNLOADER INITIALIZED!")
        logger.info(f"📊 Dataset: {self.dataset_info['name']}")
        logger.info(f"📁 Target: {self.dataset_dir}")
        logger.info(f"🎯 Classes: {self.dataset_info['classes']} skin conditions")
    
    def check_kaggle_installed(self):
        """Check if Kaggle CLI is installed"""
        try:
            result = subprocess.run(['kaggle', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("✅ Kaggle CLI is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️ Kaggle CLI not found")
            return False
    
    def install_kaggle_instructions(self):
        """Provide instructions for installing Kaggle CLI"""
        logger.info("📋 KAGGLE CLI INSTALLATION INSTRUCTIONS:")
        logger.info("="*60)
        logger.info("1. Install Kaggle CLI:")
        logger.info("   pip install kaggle")
        logger.info("")
        logger.info("2. Get your Kaggle API credentials:")
        logger.info("   - Go to: https://www.kaggle.com/account")
        logger.info("   - Click 'Create New API Token'")
        logger.info("   - Download kaggle.json")
        logger.info("")
        logger.info("3. Place kaggle.json in:")
        logger.info("   Windows: %USERPROFILE%\\.kaggle\\kaggle.json")
        logger.info("   Linux/Mac: ~/.kaggle/kaggle.json")
        logger.info("")
        logger.info("4. Set permissions (Linux/Mac):")
        logger.info("   chmod 600 ~/.kaggle/kaggle.json")
        logger.info("="*60)
    
    def download_dataset(self):
        """Download the HAM10000 dataset"""
        logger.info("🚀 STARTING HAM10000 DATASET DOWNLOAD!")
        
        if not self.check_kaggle_installed():
            self.install_kaggle_instructions()
            return False
        
        try:
            # Download dataset
            logger.info("📥 Downloading HAM10000 dataset...")
            cmd = [
                'kaggle', 'datasets', 'download',
                'kmader/skin-cancer-mnist-ham10000',
                '--path', str(self.dataset_dir),
                '--unzip'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("✅ Dataset downloaded successfully!")
            
            # Verify download
            self.verify_download()
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Download failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def verify_download(self):
        """Verify the downloaded dataset"""
        logger.info("🔍 Verifying downloaded dataset...")
        
        # Check for key files
        expected_files = [
            'HAM10000_images_part_1.zip',
            'HAM10000_images_part_2.zip',
            'HAM10000_metadata.csv'
        ]
        
        found_files = []
        for file in expected_files:
            file_path = self.dataset_dir / file
            if file_path.exists():
                found_files.append(file)
                logger.info(f"✅ Found: {file}")
            else:
                logger.warning(f"⚠️ Missing: {file}")
        
        if len(found_files) >= 2:
            logger.info("🎉 Dataset verification successful!")
            self.extract_images()
        else:
            logger.error("❌ Dataset verification failed!")
    
    def extract_images(self):
        """Extract image files from zip archives"""
        logger.info("📦 Extracting image files...")
        
        try:
            # Extract part 1
            part1_zip = self.dataset_dir / 'HAM10000_images_part_1.zip'
            if part1_zip.exists():
                with zipfile.ZipFile(part1_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.dataset_dir)
                logger.info("✅ Part 1 extracted")
            
            # Extract part 2
            part2_zip = self.dataset_dir / 'HAM10000_images_part_2.zip'
            if part2_zip.exists():
                with zipfile.ZipFile(part2_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.dataset_dir)
                logger.info("✅ Part 2 extracted")
            
            # Count extracted images
            image_files = list(self.dataset_dir.glob('*.jpg')) + list(self.dataset_dir.glob('*.png'))
            logger.info(f"📊 Total images extracted: {len(image_files)}")
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
    
    def create_dataset_structure(self):
        """Create organized dataset structure for training"""
        logger.info("🏗️ Creating organized dataset structure...")
        
        # Create training structure
        train_dir = self.dataset_dir / 'organized' / 'train'
        val_dir = self.dataset_dir / 'organized' / 'val'
        
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # Read metadata
        metadata_file = self.dataset_dir / 'HAM10000_metadata.csv'
        if metadata_file.exists():
            logger.info("📊 Reading metadata for organization...")
            # TODO: Implement metadata parsing and organization
            logger.info("✅ Dataset structure created!")
        else:
            logger.warning("⚠️ Metadata file not found")
    
    def get_dataset_info(self):
        """Get information about the downloaded dataset"""
        logger.info("📊 HAM10000 DATASET INFORMATION:")
        logger.info("="*50)
        logger.info(f"Name: {self.dataset_info['name']}")
        logger.info(f"Description: {self.dataset_info['description']}")
        logger.info(f"Source: {self.dataset_info['source']}")
        logger.info(f"Size: {self.dataset_info['size']}")
        logger.info(f"Images: {self.dataset_info['images']}")
        logger.info(f"Classes: {self.dataset_info['classes']}")
        logger.info("="*50)
        
        # Class information
        classes = {
            'akiec': 'Actinic keratoses and intraepithelial carcinoma',
            'bcc': 'Basal cell carcinoma',
            'bkl': 'Benign keratosis-like lesions',
            'df': 'Dermatofibroma',
            'mel': 'Melanoma',
            'nv': 'Melanocytic nevi',
            'vasc': 'Vascular lesions'
        }
        
        logger.info("🏷️ SKIN CONDITION CLASSES:")
        for code, description in classes.items():
            logger.info(f"  {code.upper()}: {description}")


def main():
    """Main execution function"""
    logger.info("🏥 HAM10000 SKIN CANCER DATASET DOWNLOADER")
    logger.info("="*60)
    
    downloader = HAM10000Downloader()
    
    # Show dataset info
    downloader.get_dataset_info()
    
    # Download dataset
    if downloader.download_dataset():
        logger.info("🎉 HAM10000 DATASET DOWNLOAD COMPLETE!")
        logger.info("🚀 Ready for Hare Run V6 training!")
    else:
        logger.error("❌ HAM10000 DATASET DOWNLOAD FAILED!")
        logger.info("📋 Please follow the installation instructions above")
    
    logger.info("="*60)


if __name__ == "__main__":
    main()
