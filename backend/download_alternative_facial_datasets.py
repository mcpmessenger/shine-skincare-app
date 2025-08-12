#!/usr/bin/env python3
"""
🏥 ALTERNATIVE FACIAL SKIN DISEASE DATASET DOWNLOADER
Downloads facial skin disease datasets from alternative sources
Focus: Real facial skin condition images for training
"""

import os
import json
import logging
import requests
import zipfile
from pathlib import Path
import urllib.request
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlternativeFacialDatasetDownloader:
    """
    Downloads facial skin disease datasets from alternative sources
    """
    
    def __init__(self):
        self.output_dir = Path('data/alternative_facial_skin_conditions')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Alternative dataset sources
        self.alternative_sources = {
            'dermatology_faces_github': {
                'name': 'Dermatology Faces (GitHub)',
                'url': 'https://github.com/andrewmvd/dermatology-faces-dataset/archive/refs/heads/main.zip',
                'description': 'Facial skin conditions from GitHub repository',
                'size': '~500MB',
                'classes': ['acne', 'rosacea', 'eczema', 'healthy', 'melanoma', 'psoriasis']
            },
            'facial_skin_diseases_github': {
                'name': 'Facial Skin Diseases (GitHub)',
                'url': 'https://github.com/aryashah2k/facial-skin-diseases-dataset/archive/refs/heads/main.zip',
                'description': 'Comprehensive facial skin conditions',
                'size': '~300MB',
                'classes': ['acne', 'actinic_keratosis', 'basal_cell_carcinoma', 'eczema', 'healthy', 'rosacea']
            },
            'skin_lesion_faces_github': {
                'name': 'Skin Lesion Faces (GitHub)',
                'url': 'https://github.com/aryashah2k/skin-lesion-faces/archive/refs/heads/main.zip',
                'description': 'Facial skin lesions and conditions',
                'size': '~200MB',
                'classes': ['benign', 'malignant', 'healthy']
            }
        }
        
        logger.info("🏥 ALTERNATIVE FACIAL SKIN DISEASE DATASET DOWNLOADER INITIALIZED!")
        logger.info(f"📁 Output: {self.output_dir}")
        logger.info(f"🎯 Sources: {len(self.alternative_sources)} alternative sources")
    
    def download_from_github(self, source_key):
        """Download dataset from GitHub repository"""
        if source_key not in self.alternative_sources:
            logger.error(f"❌ Unknown source: {source_key}")
            return False
        
        source = self.alternative_sources[source_key]
        logger.info(f"🚀 DOWNLOADING: {source['name']}")
        logger.info(f"📊 Description: {source['description']}")
        logger.info(f"🏷️ Classes: {', '.join(source['classes'])}")
        
        try:
            # Create source directory
            source_dir = self.output_dir / source_key
            source_dir.mkdir(exist_ok=True)
            
            # Download URL
            url = source['url']
            filename = urlparse(url).path.split('/')[-1]
            filepath = source_dir / filename
            
            logger.info(f"📥 Downloading from: {url}")
            logger.info(f"📁 Saving to: {filepath}")
            
            # Download file
            urllib.request.urlretrieve(url, filepath)
            logger.info(f"✅ Download completed: {filepath}")
            
            # Extract if it's a zip file
            if filename.endswith('.zip'):
                logger.info("📦 Extracting zip file...")
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(source_dir)
                logger.info("✅ Extraction completed")
                
                # Remove zip file to save space
                filepath.unlink()
                logger.info("🗑️ Zip file removed")
            
            # Verify download
            self.verify_download(source_key)
            return True
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False
    
    def verify_download(self, source_key):
        """Verify the downloaded dataset"""
        logger.info(f"🔍 Verifying {source_key} download...")
        
        source_dir = self.output_dir / source_key
        
        # Look for image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(list(source_dir.rglob(ext)))
        
        logger.info(f"📊 Total images found: {len(image_files)}")
        
        if len(image_files) > 0:
            logger.info("🎉 Dataset verification successful!")
            self.organize_dataset(source_key)
        else:
            logger.warning("⚠️ No images found - may need manual organization")
    
    def organize_dataset(self, source_key):
        """Organize the downloaded dataset"""
        logger.info(f"🏗️ Organizing {source_key} dataset...")
        
        source_dir = self.output_dir / source_key
        organized_dir = source_dir / 'organized'
        
        # Create organized structure
        train_dir = organized_dir / 'train'
        val_dir = organized_dir / 'val'
        
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # Get source info
        source = self.alternative_sources[source_key]
        
        # Create class directories
        for class_name in source['classes']:
            (train_dir / class_name).mkdir(exist_ok=True)
            (val_dir / class_name).mkdir(exist_ok=True)
        
        logger.info(f"✅ Organized structure created for {source_key}")
        logger.info(f"🏷️ Classes: {', '.join(source['classes'])}")
    
    def download_all_alternative_sources(self):
        """Download all available alternative sources"""
        logger.info("🚀 DOWNLOADING ALL ALTERNATIVE FACIAL SKIN DISEASE DATASETS!")
        
        success_count = 0
        total_count = len(self.alternative_sources)
        
        for source_key in self.alternative_sources.keys():
            logger.info(f"\n{'='*60}")
            if self.download_from_github(source_key):
                success_count += 1
            else:
                logger.error(f"❌ Failed to download {source_key}")
        
        logger.info(f"\n🎉 DOWNLOAD SUMMARY:")
        logger.info(f"✅ Successful: {success_count}/{total_count}")
        logger.info(f"❌ Failed: {total_count - success_count}/{total_count}")
        
        if success_count > 0:
            logger.info("🚀 Ready for Hare Run V6 training!")
        else:
            logger.error("❌ No datasets downloaded successfully")
    
    def show_available_sources(self):
        """Show available alternative dataset sources"""
        logger.info("📊 AVAILABLE ALTERNATIVE FACIAL SKIN DISEASE DATASETS:")
        logger.info("="*70)
        
        for key, source in self.alternative_sources.items():
            logger.info(f"🔑 Key: {key}")
            logger.info(f"📛 Name: {source['name']}")
            logger.info(f"📝 Description: {source['description']}")
            logger.info(f"🏷️ Classes: {', '.join(source['classes'])}")
            logger.info(f"📏 Size: {source['size']}")
            logger.info(f"🔗 URL: {source['url']}")
            logger.info("-" * 50)


def main():
    """Main execution function"""
    logger.info("🏥 ALTERNATIVE FACIAL SKIN DISEASE DATASET DOWNLOADER")
    logger.info("🎯 Focus: Real facial skin condition images from alternative sources")
    logger.info("="*70)
    
    downloader = AlternativeFacialDatasetDownloader()
    
    # Show available sources
    downloader.show_available_sources()
    
    # Ask user which source to download
    print("\n🎯 WHICH ALTERNATIVE SOURCE WOULD YOU LIKE TO DOWNLOAD?")
    print("1. dermatology_faces_github - Comprehensive facial conditions")
    print("2. facial_skin_diseases_github - Focused facial skin issues")
    print("3. skin_lesion_faces_github - Facial lesions and conditions")
    print("4. all - Download all alternative sources")
    print("5. exit - Exit without downloading")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        downloader.download_from_github('dermatology_faces_github')
    elif choice == '2':
        downloader.download_from_github('facial_skin_diseases_github')
    elif choice == '3':
        downloader.download_from_github('skin_lesion_faces_github')
    elif choice == '4':
        downloader.download_all_alternative_sources()
    elif choice == '5':
        logger.info("👋 Exiting without download")
    else:
        logger.error("❌ Invalid choice")
    
    logger.info("="*70)


if __name__ == "__main__":
    main()
