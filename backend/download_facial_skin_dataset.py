#!/usr/bin/env python3
"""
🏥 FACIAL SKIN CONDITION DATASET DOWNLOADER
Downloads facial skin condition datasets for face-focused analysis
Focus: Facial skin conditions, not body lesions
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

class FacialSkinDatasetDownloader:
    """
    Downloads facial skin condition datasets for face-focused analysis
    """
    
    def __init__(self):
        self.dataset_dir = Path('data/real_facial_skin_conditions/raw/facial_skin_conditions')
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Facial skin condition datasets
        self.facial_datasets = {
            'dermatology_faces': {
                'name': 'Dermatology Faces Dataset',
                'source': 'Kaggle',
                'url': 'https://www.kaggle.com/datasets/andrewmvd/dermatology-faces-dataset',
                'description': 'Facial skin conditions and healthy faces',
                'classes': ['acne', 'rosacea', 'eczema', 'healthy', 'melanoma', 'psoriasis'],
                'size': '~500MB'
            },
            'facial_skin_diseases': {
                'name': 'Facial Skin Diseases Dataset',
                'source': 'Kaggle',
                'url': 'https://www.kaggle.com/datasets/aryashah2k/facial-skin-diseases-dataset',
                'description': 'Comprehensive facial skin condition images',
                'classes': ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'eczema', 'healthy', 'rosacea'],
                'size': '~300MB'
            },
            'skin_lesion_faces': {
                'name': 'Skin Lesion Faces',
                'source': 'Kaggle',
                'url': 'https://www.kaggle.com/datasets/aryashah2k/skin-lesion-faces',
                'description': 'Facial skin lesions and conditions',
                'classes': ['benign', 'malignant', 'healthy'],
                'size': '~200MB'
            }
        }
        
        logger.info("🏥 FACIAL SKIN CONDITION DATASET DOWNLOADER INITIALIZED!")
        logger.info("🎯 Focus: Facial skin conditions (NOT body lesions)")
        logger.info(f"📁 Target: {self.dataset_dir}")
    
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
    
    def download_facial_dataset(self, dataset_key):
        """Download a specific facial skin condition dataset"""
        if dataset_key not in self.facial_datasets:
            logger.error(f"❌ Unknown dataset: {dataset_key}")
            return False
        
        dataset = self.facial_datasets[dataset_key]
        logger.info(f"🚀 DOWNLOADING: {dataset['name']}")
        logger.info(f"📊 Description: {dataset['description']}")
        logger.info(f"🏷️ Classes: {', '.join(dataset['classes'])}")
        
        if not self.check_kaggle_installed():
            self.install_kaggle_instructions()
            return False
        
        try:
            # Extract dataset ID from URL
            dataset_id = dataset['url'].split('/')[-1]
            
            # Download dataset
            logger.info(f"📥 Downloading {dataset['name']}...")
            cmd = [
                'kaggle', 'datasets', 'download',
                dataset_id,
                '--path', str(self.dataset_dir),
                '--unzip'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"✅ {dataset['name']} downloaded successfully!")
            
            # Verify download
            self.verify_facial_download(dataset_key)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Download failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def verify_facial_download(self, dataset_key):
        """Verify the downloaded facial dataset"""
        logger.info(f"🔍 Verifying {dataset_key} download...")
        
        # Check for image files
        image_files = list(self.dataset_dir.glob('*.jpg')) + list(self.dataset_dir.glob('*.png'))
        logger.info(f"📊 Total images found: {len(image_files)}")
        
        if len(image_files) > 0:
            logger.info("🎉 Facial dataset verification successful!")
            self.organize_facial_dataset(dataset_key)
        else:
            logger.error("❌ No facial images found!")
    
    def organize_facial_dataset(self, dataset_key):
        """Organize facial dataset for training"""
        logger.info(f"🏗️ Organizing {dataset_key} for training...")
        
        dataset = self.facial_datasets[dataset_key]
        
        # Create organized structure
        organized_dir = self.dataset_dir / 'organized'
        train_dir = organized_dir / 'train'
        val_dir = organized_dir / 'val'
        
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # Create class directories
        for class_name in dataset['classes']:
            (train_dir / class_name).mkdir(exist_ok=True)
            (val_dir / class_name).mkdir(exist_ok=True)
        
        logger.info(f"✅ Organized structure created for {dataset_key}")
        logger.info(f"🏷️ Classes: {', '.join(dataset['classes'])}")
    
    def show_available_datasets(self):
        """Show available facial skin condition datasets"""
        logger.info("📊 AVAILABLE FACIAL SKIN CONDITION DATASETS:")
        logger.info("="*70)
        
        for key, dataset in self.facial_datasets.items():
            logger.info(f"🔑 Key: {key}")
            logger.info(f"📛 Name: {dataset['name']}")
            logger.info(f"📝 Description: {dataset['description']}")
            logger.info(f"🏷️ Classes: {', '.join(dataset['classes'])}")
            logger.info(f"📏 Size: {dataset['size']}")
            logger.info(f"🔗 URL: {dataset['url']}")
            logger.info("-" * 50)
    
    def download_all_facial_datasets(self):
        """Download all available facial skin condition datasets"""
        logger.info("🚀 DOWNLOADING ALL FACIAL SKIN CONDITION DATASETS!")
        
        success_count = 0
        total_count = len(self.facial_datasets)
        
        for dataset_key in self.facial_datasets.keys():
            logger.info(f"\n{'='*60}")
            if self.download_facial_dataset(dataset_key):
                success_count += 1
            else:
                logger.error(f"❌ Failed to download {dataset_key}")
        
        logger.info(f"\n🎉 DOWNLOAD SUMMARY:")
        logger.info(f"✅ Successful: {success_count}/{total_count}")
        logger.info(f"❌ Failed: {total_count - success_count}/{total_count}")
        
        if success_count > 0:
            logger.info("🚀 Ready for Hare Run V6 facial training!")
        else:
            logger.error("❌ No datasets downloaded successfully")


def main():
    """Main execution function"""
    logger.info("🏥 FACIAL SKIN CONDITION DATASET DOWNLOADER")
    logger.info("🎯 Focus: Facial skin conditions (NOT body lesions)")
    logger.info("="*70)
    
    downloader = FacialSkinDatasetDownloader()
    
    # Show available datasets
    downloader.show_available_datasets()
    
    # Ask user which dataset to download
    print("\n🎯 WHICH DATASET WOULD YOU LIKE TO DOWNLOAD?")
    print("1. dermatology_faces - Comprehensive facial conditions")
    print("2. facial_skin_diseases - Focused facial skin issues")
    print("3. skin_lesion_faces - Facial lesions and conditions")
    print("4. all - Download all datasets")
    print("5. exit - Exit without downloading")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        downloader.download_facial_dataset('dermatology_faces')
    elif choice == '2':
        downloader.download_facial_dataset('facial_skin_diseases')
    elif choice == '3':
        downloader.download_facial_dataset('skin_lesion_faces')
    elif choice == '4':
        downloader.download_all_facial_datasets()
    elif choice == '5':
        logger.info("👋 Exiting without download")
    else:
        logger.error("❌ Invalid choice")
    
    logger.info("="*70)


if __name__ == "__main__":
    main()
