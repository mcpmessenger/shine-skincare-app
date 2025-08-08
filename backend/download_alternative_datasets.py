#!/usr/bin/env python3
"""
Alternative Dataset Downloader for Shine Skincare App
Downloads and prepares publicly available facial skin condition datasets
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import requests
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlternativeDatasetDownloader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.dataset_dir = self.data_dir / "alternative_facial_skin_conditions"
        self.raw_dir = self.dataset_dir / "raw"
        self.processed_dir = self.dataset_dir / "processed"
        
        # Create directories
        self.dataset_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Available datasets
        self.available_datasets = {
            "dermatology_faces": {
                "name": "Dermatology Faces Dataset",
                "url": "https://www.kaggle.com/datasets/andrewmvd/dermatology-faces-dataset",
                "description": "Dermatology faces dataset with various skin conditions",
                "type": "kaggle"
            },
            "skin_lesion": {
                "name": "Skin Lesion Analysis Towards Melanoma Detection",
                "url": "https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000",
                "description": "HAM10000 dataset with skin lesion images",
                "type": "kaggle"
            },
            "facial_dermatology": {
                "name": "Facial Dermatology Dataset",
                "url": "https://www.kaggle.com/datasets/andrewmvd/facial-dermatology-dataset",
                "description": "Facial dermatology images with conditions",
                "type": "kaggle"
            }
        }
        
        self.expected_conditions = [
            "acne", "rosacea", "melasma", "eczema", "psoriasis", 
            "vitiligo", "dermatitis", "hyperpigmentation", "hypopigmentation",
            "melanoma", "benign", "malignant"
        ]
    
    def download_sample_dataset(self) -> bool:
        """
        Download a sample dataset for testing and development
        """
        logger.info("Downloading sample dataset for development...")
        
        try:
            # Create a sample dataset structure
            self._create_sample_dataset()
            logger.info("Sample dataset created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sample dataset: {e}")
            return False
    
    def _create_sample_dataset(self):
        """Create a sample dataset for development purposes"""
        logger.info("Creating sample dataset structure...")
        
        # Create condition directories
        for condition in self.expected_conditions:
            condition_dir = self.processed_dir / condition
            condition_dir.mkdir(exist_ok=True)
        
        # Create sample metadata
        sample_metadata = {
            "dataset_name": "Sample Facial Skin Conditions Dataset",
            "description": "Sample dataset for development and testing",
            "total_conditions": len(self.expected_conditions),
            "conditions": self.expected_conditions,
            "statistics": {},
            "notes": [
                "This is a sample dataset for development purposes",
                "Replace with actual dataset when available",
                "Each condition directory is ready for image placement"
            ]
        }
        
        # Count directories created
        for condition in self.expected_conditions:
            condition_dir = self.processed_dir / condition
            if condition_dir.exists():
                sample_metadata["statistics"][condition] = 0  # Placeholder
        
        # Save metadata
        metadata_file = self.processed_dir / "sample_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(sample_metadata, f, indent=2)
        
        logger.info(f"Sample metadata saved to {metadata_file}")
    
    def download_from_kaggle(self, dataset_name: str) -> bool:
        """
        Download dataset from Kaggle (requires kaggle CLI)
        """
        try:
            import subprocess
            
            logger.info(f"Downloading dataset from Kaggle: {dataset_name}")
            
            # Check if kaggle CLI is installed
            try:
                subprocess.run(["kaggle", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.error("Kaggle CLI not found. Please install it first:")
                logger.error("pip install kaggle")
                logger.error("Then configure with: kaggle config set-credentials")
                return False
            
            # Download dataset
            subprocess.run([
                "kaggle", "datasets", "download", 
                f"--dataset={dataset_name}",
                f"--path={self.raw_dir}",
                "--unzip"
            ], check=True)
            
            logger.info("Dataset downloaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            return False
    
    def download_public_images(self) -> bool:
        """
        Download publicly available skin condition images
        """
        logger.info("Downloading publicly available skin condition images...")
        
        # Sample image URLs for different conditions
        sample_images = {
            "acne": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Acne_vulgaris_on_cheek.jpg/800px-Acne_vulgaris_on_cheek.jpg"
            ],
            "rosacea": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Rosacea.jpg/800px-Rosacea.jpg"
            ],
            "melasma": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Melasma.jpg/800px-Melasma.jpg"
            ]
        }
        
        try:
            for condition, urls in sample_images.items():
                condition_dir = self.processed_dir / condition
                condition_dir.mkdir(exist_ok=True)
                
                for i, url in enumerate(urls):
                    try:
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        
                        filename = f"{condition}_sample_{i+1}.jpg"
                        filepath = condition_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        logger.info(f"Downloaded {filename}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to download {url}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download public images: {e}")
            return False
    
    def create_dataset_structure(self) -> bool:
        """
        Create the proper dataset structure for training
        """
        logger.info("Creating dataset structure...")
        
        try:
            # Create splits
            splits_dir = self.processed_dir / "splits"
            splits_dir.mkdir(exist_ok=True)
            
            for split in ['train', 'val', 'test']:
                split_dir = splits_dir / split
                split_dir.mkdir(exist_ok=True)
                
                for condition in self.expected_conditions:
                    condition_dir = split_dir / condition
                    condition_dir.mkdir(exist_ok=True)
            
            # Create annotations directory
            annotations_dir = self.processed_dir / "annotations"
            annotations_dir.mkdir(exist_ok=True)
            
            # Create sample annotation file
            sample_annotations = {
                "dataset_info": {
                    "name": "Facial Skin Conditions Dataset",
                    "version": "1.0",
                    "description": "Dataset for facial skin condition detection"
                },
                "conditions": self.expected_conditions,
                "image_count": 0,
                "annotations": []
            }
            
            annotation_file = annotations_dir / "sample_annotations.json"
            with open(annotation_file, 'w') as f:
                json.dump(sample_annotations, f, indent=2)
            
            logger.info("Dataset structure created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dataset structure: {e}")
            return False
    
    def generate_training_config(self) -> bool:
        """
        Generate training configuration for the dataset
        """
        logger.info("Generating training configuration...")
        
        config = {
            "dataset": {
                "name": "Facial Skin Conditions",
                "path": str(self.processed_dir),
                "conditions": self.expected_conditions,
                "splits": ["train", "val", "test"]
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "image_size": [224, 224],
                "augmentation": {
                    "rotation": 15,
                    "horizontal_flip": True,
                    "brightness": 0.2,
                    "contrast": 0.2
                }
            },
            "model": {
                "architecture": "resnet50",
                "pretrained": True,
                "num_classes": len(self.expected_conditions)
            }
        }
        
        config_file = self.dataset_dir / "training_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Training configuration saved to {config_file}")
        return True
    
    def run_alternative_pipeline(self):
        """
        Run the alternative dataset pipeline
        """
        logger.info("Starting alternative dataset pipeline...")
        
        # Step 1: Create sample dataset structure
        if not self.create_dataset_structure():
            logger.error("Failed to create dataset structure. Exiting.")
            return False
        
        # Step 2: Download sample dataset
        if not self.download_sample_dataset():
            logger.error("Failed to create sample dataset. Exiting.")
            return False
        
        # Step 3: Try to download public images
        self.download_public_images()
        
        # Step 4: Generate training config
        if not self.generate_training_config():
            logger.error("Failed to generate training config. Exiting.")
            return False
        
        logger.info("Alternative dataset pipeline completed successfully!")
        return True

def main():
    """Main function to run the alternative dataset downloader"""
    downloader = AlternativeDatasetDownloader()
    
    print("=" * 60)
    print("Shine Skincare App - Alternative Dataset Downloader")
    print("=" * 60)
    print("Available datasets:")
    for key, dataset in downloader.available_datasets.items():
        print(f"  - {dataset['name']}: {dataset['description']}")
    print("=" * 60)
    
    success = downloader.run_alternative_pipeline()
    
    if success:
        print("\n✅ Alternative dataset pipeline completed successfully!")
        print(f"📁 Dataset structure available at: {downloader.processed_dir}")
        print(f"📋 Sample metadata available at: {downloader.processed_dir}/sample_metadata.json")
        print(f"⚙️ Training config available at: {downloader.dataset_dir}/training_config.json")
        print("\n📝 Next steps:")
        print("  1. Add actual skin condition images to the condition directories")
        print("  2. Update annotations with proper labels")
        print("  3. Run the training pipeline with the new dataset")
    else:
        print("\n❌ Alternative dataset processing failed. Check logs for details.")

if __name__ == "__main__":
    main()
