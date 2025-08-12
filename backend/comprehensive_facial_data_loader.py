#!/usr/bin/env python3
"""
🐇 COMPREHENSIVE FACIAL DATA LOADER
Combines all facial datasets for robust Hare Run V6 training
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import cv2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveFacialDataLoader:
    """
    🐇 Comprehensive Facial Data Loader
    Combines all available facial datasets for robust training
    """
    
    def __init__(self):
        """Initialize the comprehensive data loader"""
        self.config = {
            'datasets': {
                'utkface': {
                    'path': 'data/utkface/utkface_aligned_cropped/crop_part1',
                    'type': 'healthy',
                    'target_count': 1000  # Limit for healthy faces
                },
                'skin_disease': {
                    'path': 'data/skin_disease_classification',
                    'csv_file': 'skin_defects.csv',
                    'type': 'skin_conditions',
                    'target_count': 1000  # All available
                },
                'facial_skin_conditions': {
                    'path': 'data/facial_skin_conditions',
                    'csv_file': 'Facial Skin Condition Dataset.csv',
                    'type': 'facial_conditions',
                    'target_count': 1000  # All available
                },
                'facial_skin_diseases': {
                    'path': 'data/facial_skin_diseases',
                    'metadata_file': 'condition_metadata.csv',
                    'type': 'disease_conditions',
                    'target_count': 1000  # All available
                }
            },
            'image_size': (224, 224),
            'class_mapping': {
                'healthy': 0,
                'acne': 1,
                'bags': 2,
                'redness': 3,
                'rosacea': 4,
                'eczema': 5,
                'hyperpigmentation': 6,
                'other': 7
            }
        }
        
        self.class_names = list(self.config['class_mapping'].keys())
        logger.info("🐇 Comprehensive Facial Data Loader Initialized!")
        logger.info(f"🎯 Target Classes: {', '.join(self.class_names)}")
    
    def load_utkface_healthy_faces(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load healthy faces from UTKFace dataset"""
        logger.info("📊 Loading UTKFace Healthy Faces...")
        
        utkface_path = Path(self.config['datasets']['utkface']['path'])
        images = []
        labels = []
        
        # Get list of image files
        image_files = list(utkface_path.glob('*.jpg')) + list(utkface_path.glob('*.png'))
        target_count = min(self.config['datasets']['utkface']['target_count'], len(image_files))
        
        logger.info(f"Found {len(image_files)} UTKFace images, loading {target_count}")
        
        for i, img_path in enumerate(image_files[:target_count]):
            try:
                # Load and preprocess image
                img = cv2.imread(str(img_path))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, self.config['image_size'])
                    img = img.astype(np.float32) / 255.0
                    
                    images.append(img)
                    labels.append(self.config['class_mapping']['healthy'])
                    
            except Exception as e:
                logger.warning(f"Error loading UTKFace image {img_path}: {e}")
        
        logger.info(f"✅ Loaded {len(images)} healthy faces from UTKFace")
        return np.array(images), np.array(labels)
    
    def load_skin_disease_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load skin disease classification dataset"""
        logger.info("📊 Loading Skin Disease Classification Dataset...")
        
        dataset_path = Path(self.config['datasets']['skin_disease']['path'])
        csv_path = dataset_path / self.config['datasets']['skin_disease']['csv_file']
        
        if not csv_path.exists():
            logger.warning("Skin disease CSV not found")
            return np.array([]), np.array([])
        
        df = pd.read_csv(csv_path)
        images = []
        labels = []
        
        for _, row in df.iterrows():
            try:
                # Load front image
                front_path = dataset_path / 'files' / row['front'].lstrip('/')
                if front_path.exists():
                    img = cv2.imread(str(front_path))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.config['image_size'])
                        img = img.astype(np.float32) / 255.0
                        
                        images.append(img)
                        
                        # Map condition to class
                        condition = row['type']
                        if condition == 'acne':
                            labels.append(self.config['class_mapping']['acne'])
                        elif condition == 'bags':
                            labels.append(self.config['class_mapping']['bags'])
                        elif condition == 'redness':
                            labels.append(self.config['class_mapping']['redness'])
                        else:
                            labels.append(self.config['class_mapping']['other'])
                            
            except Exception as e:
                logger.warning(f"Error loading skin disease image: {e}")
        
        logger.info(f"✅ Loaded {len(images)} skin disease images")
        return np.array(images), np.array(labels)
    
    def load_facial_skin_conditions(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load facial skin conditions dataset"""
        logger.info("📊 Loading Facial Skin Conditions Dataset...")
        
        dataset_path = Path(self.config['datasets']['facial_skin_conditions']['path'])
        csv_path = dataset_path / self.config['datasets']['facial_skin_conditions']['csv_file']
        
        if not csv_path.exists():
            logger.warning("Facial skin conditions CSV not found")
            return np.array([]), np.array([])
        
        df = pd.read_csv(csv_path)
        images = []
        labels = []
        
        for _, row in df.iterrows():
            try:
                # Load front image - try both .png and .jpg extensions
                base_path = row['image front'].lstrip('/')
                front_path_png = dataset_path / base_path
                front_path_jpg = dataset_path / base_path.replace('.png', '.jpg')
                
                front_path = None
                if front_path_png.exists():
                    front_path = front_path_png
                elif front_path_jpg.exists():
                    front_path = front_path_jpg
                
                if front_path is not None:
                    img = cv2.imread(str(front_path))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.config['image_size'])
                        img = img.astype(np.float32) / 255.0
                        
                        images.append(img)
                        labels.append(self.config['class_mapping']['other'])  # Generic condition
                        
            except Exception as e:
                logger.warning(f"Error loading facial condition image: {e}")
        
        logger.info(f"✅ Loaded {len(images)} facial condition images")
        return np.array(images), np.array(labels)
    
    def load_facial_skin_diseases(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load facial skin diseases dataset"""
        logger.info("📊 Loading Facial Skin Diseases Dataset...")
        
        dataset_path = Path(self.config['datasets']['facial_skin_diseases']['path'])
        metadata_path = dataset_path / self.config['datasets']['facial_skin_diseases']['metadata_file']
        
        if not metadata_path.exists():
            logger.warning("Facial skin diseases metadata not found")
            return np.array([]), np.array([])
        
        df = pd.read_csv(metadata_path)
        images = []
        labels = []
        
        # This dataset has condition labels, let's load the images
        logger.info(f"Facial skin diseases metadata shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        for _, row in df.iterrows():
            try:
                # Load image from filepath
                image_path = dataset_path / row['filepath']
                if image_path.exists():
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.config['image_size'])
                        img = img.astype(np.float32) / 255.0
                        
                        images.append(img)
                        
                        # Map condition to class
                        condition = row['condition'].lower()
                        if 'acne' in condition:
                            labels.append(self.config['class_mapping']['acne'])
                        elif 'rosacea' in condition:
                            labels.append(self.config['class_mapping']['rosacea'])
                        elif 'eczema' in condition:
                            labels.append(self.config['class_mapping']['eczema'])
                        elif 'hyperpigmentation' in condition:
                            labels.append(self.config['class_mapping']['hyperpigmentation'])
                        else:
                            labels.append(self.config['class_mapping']['other'])
                            
            except Exception as e:
                logger.warning(f"Error loading facial disease image: {e}")
        
        logger.info(f"✅ Loaded {len(images)} facial disease images")
        return np.array(images), np.array(labels)
    
    def combine_all_datasets(self) -> Tuple[np.ndarray, np.ndarray]:
        """Combine all available datasets"""
        logger.info("🔄 Combining All Facial Datasets...")
        
        all_images = []
        all_labels = []
        
        # Load UTKFace healthy faces
        utkface_images, utkface_labels = self.load_utkface_healthy_faces()
        if len(utkface_images) > 0:
            all_images.append(utkface_images)
            all_labels.append(utkface_labels)
            logger.info(f"Added {len(utkface_images)} healthy faces")
        
        # Load skin disease dataset
        skin_images, skin_labels = self.load_skin_disease_dataset()
        if len(skin_images) > 0:
            all_images.append(skin_images)
            all_labels.append(skin_labels)
            logger.info(f"Added {len(skin_images)} skin disease images")
        
        # Load facial skin conditions
        facial_images, facial_labels = self.load_facial_skin_conditions()
        if len(facial_images) > 0:
            all_images.append(facial_images)
            all_labels.append(facial_labels)
            logger.info(f"Added {len(facial_images)} facial condition images")
        
        # Load facial skin diseases
        disease_images, disease_labels = self.load_facial_skin_diseases()
        if len(disease_images) > 0:
            all_images.append(disease_images)
            all_labels.append(disease_labels)
            logger.info(f"Added {len(disease_images)} facial disease images")
        
        # Combine all datasets
        if all_images:
            combined_images = np.concatenate(all_images, axis=0)
            combined_labels = np.concatenate(all_labels, axis=0)
            
            # Convert to categorical
            combined_labels = tf.keras.utils.to_categorical(
                combined_labels, num_classes=len(self.class_names)
            )
            
            logger.info(f"🎉 Combined Dataset: {len(combined_images)} total images")
            logger.info(f"📊 Class distribution: {np.sum(combined_labels, axis=0)}")
            
            return combined_images, combined_labels
        else:
            logger.error("❌ No datasets could be loaded!")
            return np.array([]), np.array([])
    
    def get_dataset_summary(self) -> Dict:
        """Get summary of all available datasets"""
        summary = {
            'total_datasets': len(self.config['datasets']),
            'available_datasets': [],
            'total_images': 0,
            'class_distribution': {}
        }
        
        for dataset_name, dataset_config in self.config['datasets'].items():
            dataset_path = Path(dataset_config['path'])
            if dataset_path.exists():
                summary['available_datasets'].append(dataset_name)
                
                # Count images in directory
                if dataset_name == 'utkface':
                    image_count = len(list(dataset_path.glob('*.jpg'))) + len(list(dataset_path.glob('*.png')))
                else:
                    image_count = len(list(dataset_path.rglob('*.jpg'))) + len(list(dataset_path.rglob('*.png')))
                
                summary['total_images'] += image_count
                summary['class_distribution'][dataset_name] = image_count
        
        return summary

def main():
    """Test the comprehensive data loader"""
    print("🐇 Testing Comprehensive Facial Data Loader...")
    
    loader = ComprehensiveFacialDataLoader()
    
    # Get dataset summary
    summary = loader.get_dataset_summary()
    print(f"📊 Dataset Summary:")
    print(f"   Available datasets: {', '.join(summary['available_datasets'])}")
    print(f"   Total images found: {summary['total_images']}")
    print(f"   Class distribution: {summary['class_distribution']}")
    
    # Load combined dataset
    print("\n🔄 Loading combined dataset...")
    images, labels = loader.combine_all_datasets()
    
    if len(images) > 0:
        print(f"✅ Successfully loaded {len(images)} total images")
        print(f"📊 Final class distribution: {np.sum(labels, axis=0)}")
        print(f"🎯 Ready for Hare Run V6 training!")
    else:
        print("❌ Failed to load any images")

if __name__ == "__main__":
    main()
