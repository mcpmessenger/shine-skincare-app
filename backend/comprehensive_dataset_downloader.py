#!/usr/bin/env python3
"""
Comprehensive Dataset Downloader for Shine Skincare App
Downloads and prepares multiple publicly available facial skin condition datasets
"""

import os
import json
import shutil
import zipfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from tqdm import tqdm
import logging
import random
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDatasetDownloader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.dataset_dir = self.data_dir / "comprehensive_facial_skin_conditions"
        self.raw_dir = self.dataset_dir / "raw"
        self.processed_dir = self.dataset_dir / "processed"
        
        # Create directories
        self.dataset_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Dataset sources
        self.dataset_sources = {
            "dermnet": {
                "name": "DermNet NZ",
                "base_url": "https://www.dermnetnz.org",
                "conditions": ["acne", "rosacea", "melasma", "eczema", "psoriasis"],
                "type": "web_scrape"
            },
            "isic": {
                "name": "ISIC Archive",
                "base_url": "https://isic-archive.com",
                "conditions": ["melanoma", "benign", "malignant"],
                "type": "api"
            },
            "dermatology_atlas": {
                "name": "Dermatology Atlas",
                "base_url": "https://www.dermatlas.net",
                "conditions": ["acne", "rosacea", "melasma", "eczema", "psoriasis"],
                "type": "web_scrape"
            }
        }
        
        self.expected_conditions = [
            "acne", "rosacea", "melasma", "eczema", "psoriasis", 
            "vitiligo", "dermatitis", "hyperpigmentation", "hypopigmentation",
            "melanoma", "benign", "malignant"
        ]
        
        # User agent for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def create_synthetic_dataset(self) -> bool:
        """
        Create a synthetic dataset for development and testing
        """
        logger.info("Creating synthetic dataset for development...")
        
        try:
            # Create condition directories
            for condition in self.expected_conditions:
                condition_dir = self.processed_dir / condition
                condition_dir.mkdir(exist_ok=True)
            
            # Generate synthetic images for each condition
            for condition in self.expected_conditions:
                self._generate_synthetic_images(condition, num_images=10)
            
            # Create comprehensive metadata
            self._create_comprehensive_metadata()
            
            logger.info("Synthetic dataset created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create synthetic dataset: {e}")
            return False
    
    def _generate_synthetic_images(self, condition: str, num_images: int = 10):
        """
        Generate synthetic images for a given condition
        """
        condition_dir = self.processed_dir / condition
        condition_dir.mkdir(exist_ok=True)
        
        # Define color patterns for different conditions
        condition_patterns = {
            "acne": {"colors": [(255, 0, 0), (200, 50, 50)], "pattern": "spots"},
            "rosacea": {"colors": [(255, 100, 100), (200, 150, 150)], "pattern": "diffuse"},
            "melasma": {"colors": [(150, 100, 50), (100, 80, 60)], "pattern": "patches"},
            "eczema": {"colors": [(255, 200, 150), (200, 150, 100)], "pattern": "scaly"},
            "psoriasis": {"colors": [(255, 220, 180), (200, 180, 150)], "pattern": "scaly"},
            "vitiligo": {"colors": [(255, 255, 255), (240, 240, 240)], "pattern": "patches"},
            "dermatitis": {"colors": [(255, 180, 120), (200, 150, 100)], "pattern": "irritated"},
            "hyperpigmentation": {"colors": [(100, 80, 60), (80, 60, 40)], "pattern": "dark"},
            "hypopigmentation": {"colors": [(240, 240, 240), (220, 220, 220)], "pattern": "light"},
            "melanoma": {"colors": [(50, 30, 20), (80, 60, 40)], "pattern": "irregular"},
            "benign": {"colors": [(150, 120, 100), (120, 100, 80)], "pattern": "regular"},
            "malignant": {"colors": [(80, 60, 40), (60, 40, 20)], "pattern": "irregular"}
        }
        
        pattern = condition_patterns.get(condition, {"colors": [(200, 200, 200), (180, 180, 180)], "pattern": "normal"})
        
        for i in range(num_images):
            # Create synthetic image
            img = self._create_synthetic_image(pattern, size=(224, 224))
            
            # Save image
            filename = f"{condition}_synthetic_{i+1:03d}.jpg"
            filepath = condition_dir / filename
            img.save(filepath, "JPEG", quality=85)
            
            logger.info(f"Generated {filename}")
    
    def _create_synthetic_image(self, pattern: Dict, size: Tuple[int, int] = (224, 224)) -> Image.Image:
        """
        Create a synthetic skin condition image
        """
        # Create base skin tone
        base_color = (220, 200, 180)  # Light skin tone
        img_array = np.full((size[0], size[1], 3), base_color, dtype=np.uint8)
        
        # Add condition-specific patterns
        if pattern["pattern"] == "spots":
            # Add random spots
            for _ in range(random.randint(5, 15)):
                x = random.randint(20, size[0]-20)
                y = random.randint(20, size[1]-20)
                radius = random.randint(3, 8)
                color = random.choice(pattern["colors"])
                self._draw_circle(img_array, x, y, radius, color)
        
        elif pattern["pattern"] == "diffuse":
            # Add diffuse redness
            for x in range(0, size[0], 2):
                for y in range(0, size[1], 2):
                    if random.random() < 0.3:
                        color = random.choice(pattern["colors"])
                        img_array[x, y] = color
        
        elif pattern["pattern"] == "patches":
            # Add irregular patches
            for _ in range(random.randint(2, 5)):
                center_x = random.randint(30, size[0]-30)
                center_y = random.randint(30, size[1]-30)
                color = random.choice(pattern["colors"])
                self._draw_irregular_patch(img_array, center_x, center_y, color)
        
        elif pattern["pattern"] == "scaly":
            # Add scaly texture
            for x in range(0, size[0], 4):
                for y in range(0, size[1], 4):
                    if random.random() < 0.4:
                        color = random.choice(pattern["colors"])
                        img_array[x:x+2, y:y+2] = color
        
        elif pattern["pattern"] == "irregular":
            # Add irregular patterns
            for _ in range(random.randint(3, 8)):
                x = random.randint(20, size[0]-20)
                y = random.randint(20, size[1]-20)
                color = random.choice(pattern["colors"])
                self._draw_irregular_shape(img_array, x, y, color)
        
        # Add some noise for realism
        noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
        img_array = np.clip(img_array + noise, 0, 255)
        
        return Image.fromarray(img_array)
    
    def _draw_circle(self, img_array: np.ndarray, x: int, y: int, radius: int, color: Tuple[int, int, int]):
        """Draw a circle on the image array"""
        for i in range(max(0, x-radius), min(img_array.shape[0], x+radius)):
            for j in range(max(0, y-radius), min(img_array.shape[1], y+radius)):
                if (i-x)**2 + (j-y)**2 <= radius**2:
                    img_array[i, j] = color
    
    def _draw_irregular_patch(self, img_array: np.ndarray, x: int, y: int, color: Tuple[int, int, int]):
        """Draw an irregular patch on the image array"""
        points = []
        for angle in range(0, 360, 30):
            radius = random.randint(10, 20)
            px = x + int(radius * np.cos(np.radians(angle)))
            py = y + int(radius * np.sin(np.radians(angle)))
            points.append((px, py))
        
        # Fill the irregular shape
        for i in range(max(0, x-25), min(img_array.shape[0], x+25)):
            for j in range(max(0, y-25), min(img_array.shape[1], y+25)):
                if self._point_in_polygon(i, j, points):
                    img_array[i, j] = color
    
    def _draw_irregular_shape(self, img_array: np.ndarray, x: int, y: int, color: Tuple[int, int, int]):
        """Draw an irregular shape on the image array"""
        points = []
        for angle in range(0, 360, 45):
            radius = random.randint(5, 15)
            px = x + int(radius * np.cos(np.radians(angle)))
            py = y + int(radius * np.sin(np.radians(angle)))
            points.append((px, py))
        
        # Fill the shape
        for i in range(max(0, x-20), min(img_array.shape[0], x+20)):
            for j in range(max(0, y-20), min(img_array.shape[1], y+20)):
                if self._point_in_polygon(i, j, points):
                    img_array[i, j] = color
    
    def _point_in_polygon(self, x: int, y: int, polygon: List[Tuple[int, int]]) -> bool:
        """Check if a point is inside a polygon"""
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _create_comprehensive_metadata(self):
        """Create comprehensive metadata for the dataset"""
        logger.info("Creating comprehensive metadata...")
        
        metadata = {
            "dataset_name": "Comprehensive Facial Skin Conditions Dataset",
            "description": "Synthetic dataset for facial skin condition detection",
            "version": "1.0",
            "created_date": str(Path().cwd()),
            "total_conditions": len(self.expected_conditions),
            "conditions": self.expected_conditions,
            "statistics": {},
            "dataset_info": {
                "total_images": 0,
                "images_per_condition": 10,
                "image_size": [224, 224],
                "format": "JPEG",
                "quality": 85
            },
            "synthetic_info": {
                "generation_method": "procedural",
                "patterns": ["spots", "diffuse", "patches", "scaly", "irregular"],
                "realism_level": "development"
            },
            "usage_notes": [
                "This is a synthetic dataset for development and testing",
                "Replace with real data for production use",
                "Images are procedurally generated based on condition patterns",
                "Use for model architecture testing and pipeline validation"
            ]
        }
        
        # Count images per condition
        for condition in self.expected_conditions:
            condition_dir = self.processed_dir / condition
            if condition_dir.exists():
                image_count = len(list(condition_dir.glob("*.jpg")))
                metadata["statistics"][condition] = image_count
                metadata["dataset_info"]["total_images"] += image_count
        
        # Save metadata
        metadata_file = self.processed_dir / "comprehensive_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Comprehensive metadata saved to {metadata_file}")
    
    def create_training_splits(self) -> bool:
        """
        Create train/validation/test splits from the processed dataset
        """
        logger.info("Creating training splits...")
        
        try:
            splits_dir = self.processed_dir / "splits"
            splits_dir.mkdir(exist_ok=True)
            
            # Split ratios
            train_ratio = 0.7
            val_ratio = 0.2
            test_ratio = 0.1
            
            for condition in self.expected_conditions:
                condition_dir = self.processed_dir / condition
                if not condition_dir.exists():
                    continue
                
                # Get all images for this condition
                images = list(condition_dir.glob("*.jpg"))
                random.shuffle(images)
                
                # Calculate split indices
                n_images = len(images)
                train_end = int(n_images * train_ratio)
                val_end = int(n_images * (train_ratio + val_ratio))
                
                # Split images
                train_images = images[:train_end]
                val_images = images[train_end:val_end]
                test_images = images[val_end:]
                
                # Copy to split directories
                splits = {
                    'train': train_images,
                    'val': val_images,
                    'test': test_images
                }
                
                for split_name, split_images in splits.items():
                    split_dir = splits_dir / split_name / condition
                    split_dir.mkdir(parents=True, exist_ok=True)
                    
                    for img_path in split_images:
                        dst_path = split_dir / img_path.name
                        shutil.copy2(img_path, dst_path)
                
                logger.info(f"Split {condition}: {len(train_images)} train, {len(val_images)} val, {len(test_images)} test")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create training splits: {e}")
            return False
    
    def generate_advanced_training_config(self) -> bool:
        """
        Generate advanced training configuration
        """
        logger.info("Generating advanced training configuration...")
        
        config = {
            "dataset": {
                "name": "Comprehensive Facial Skin Conditions",
                "path": str(self.processed_dir),
                "conditions": self.expected_conditions,
                "splits": ["train", "val", "test"],
                "image_size": [224, 224],
                "num_channels": 3
            },
            "training": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss_function": "categorical_crossentropy",
                "metrics": ["accuracy", "precision", "recall", "f1_score"],
                "early_stopping_patience": 10,
                "reduce_lr_patience": 5,
                "augmentation": {
                    "rotation_range": 15,
                    "width_shift_range": 0.1,
                    "height_shift_range": 0.1,
                    "horizontal_flip": True,
                    "vertical_flip": False,
                    "brightness_range": [0.8, 1.2],
                    "zoom_range": 0.1,
                    "fill_mode": "nearest"
                }
            },
            "model": {
                "architecture": "resnet50",
                "pretrained": True,
                "num_classes": len(self.expected_conditions),
                "dropout_rate": 0.5,
                "regularization": "l2",
                "regularization_factor": 0.01
            },
            "evaluation": {
                "confusion_matrix": True,
                "classification_report": True,
                "roc_curves": True,
                "precision_recall_curves": True
            }
        }
        
        config_file = self.dataset_dir / "advanced_training_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Advanced training configuration saved to {config_file}")
        return True
    
    def run_comprehensive_pipeline(self):
        """
        Run the comprehensive dataset pipeline
        """
        logger.info("Starting comprehensive dataset pipeline...")
        
        # Step 1: Create synthetic dataset
        if not self.create_synthetic_dataset():
            logger.error("Failed to create synthetic dataset. Exiting.")
            return False
        
        # Step 2: Create training splits
        if not self.create_training_splits():
            logger.error("Failed to create training splits. Exiting.")
            return False
        
        # Step 3: Generate advanced training config
        if not self.generate_advanced_training_config():
            logger.error("Failed to generate training config. Exiting.")
            return False
        
        logger.info("Comprehensive dataset pipeline completed successfully!")
        return True

def main():
    """Main function to run the comprehensive dataset downloader"""
    downloader = ComprehensiveDatasetDownloader()
    
    print("=" * 70)
    print("Shine Skincare App - Comprehensive Dataset Downloader")
    print("=" * 70)
    print("This will create a synthetic dataset for development and testing.")
    print("The dataset includes procedurally generated images for all conditions.")
    print("=" * 70)
    
    success = downloader.run_comprehensive_pipeline()
    
    if success:
        print("\n✅ Comprehensive dataset pipeline completed successfully!")
        print(f"📁 Dataset available at: {downloader.processed_dir}")
        print(f"📋 Metadata available at: {downloader.processed_dir}/comprehensive_metadata.json")
        print(f"⚙️ Training config available at: {downloader.dataset_dir}/advanced_training_config.json")
        print(f"📊 Training splits available at: {downloader.processed_dir}/splits/")
        print("\n📝 Dataset Statistics:")
        
        # Display statistics
        metadata_file = downloader.processed_dir / "comprehensive_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                for condition, count in metadata["statistics"].items():
                    print(f"  - {condition}: {count} images")
        
        print("\n🚀 Ready for training! Use the advanced_training_config.json for model training.")
    else:
        print("\n❌ Comprehensive dataset processing failed. Check logs for details.")

if __name__ == "__main__":
    main()
