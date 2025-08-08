#!/usr/bin/env python3
"""
ML Data Preprocessing Pipeline for Shine Skincare App
Implements unified data structure and preprocessing for enhanced ML model
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import albumentations as A
from PIL import Image
import requests
import zipfile
import tarfile
from tqdm import tqdm
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLDataPreprocessor:
    """Comprehensive data preprocessing pipeline for ML model upgrades"""
    
    def __init__(self, data_dir: str = "datasets", output_dir: str = "processed_data"):
        """
        Initialize the data preprocessor
        
        Args:
            data_dir: Directory containing raw datasets
            output_dir: Directory for processed data
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Target image dimensions
        self.target_size = (224, 224)
        
        # Condition mapping for consistency
        self.condition_mapping = {
            'healthy': 'healthy',
            'acne': 'acne',
            'eczema': 'eczema',
            'keratosis': 'keratosis',
            'milia': 'milia',
            'rosacea': 'rosacea',
            'melanoma': 'melanoma',
            'basal_cell_carcinoma': 'basal_cell_carcinoma',
            'squamous_cell_carcinoma': 'squamous_cell_carcinoma',
            'benign_keratosis': 'keratosis',
            'dermatofibroma': 'dermatofibroma',
            'vascular_lesion': 'vascular_lesion',
            'pigmented_benign': 'pigmented_benign'
        }
        
        # Demographic mapping
        self.demographic_mapping = {
            'age_groups': {
                '0-18': 'young',
                '19-35': 'young_adult',
                '36-50': 'adult',
                '51-65': 'middle_aged',
                '65+': 'senior'
            },
            'gender': {
                'male': 'male',
                'female': 'female',
                'm': 'male',
                'f': 'female'
            },
            'ethnicity': {
                'white': 'white',
                'black': 'black',
                'asian': 'asian',
                'indian': 'indian',
                'other': 'other',
                'hispanic': 'hispanic',
                'middle_eastern': 'middle_eastern'
            }
        }
        
        # Data augmentation pipeline
        self.augmentation_pipeline = self._create_augmentation_pipeline()
        
        logger.info("✅ ML Data Preprocessor initialized")
    
    def _create_augmentation_pipeline(self) -> A.Compose:
        """Create comprehensive data augmentation pipeline"""
        return A.Compose([
            # Geometric transformations
            A.RandomRotate90(p=0.5),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Transpose(p=0.5),
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
                A.GaussNoise(),
            ], p=0.2),
            A.OneOf([
                A.MotionBlur(blur_limit=3, p=0.2),
                A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=3, p=0.1),
            ], p=0.2),
            A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.2),
            A.OneOf([
                A.OpticalDistortion(distort_limit=1, shift_limit=0.5, p=0.3),
                A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.1),
                A.ElasticTransform(alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03, p=0.3),
            ], p=0.2),
            
            # Color transformations
            A.OneOf([
                A.CLAHE(clip_limit=2, p=0.5),
                A.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1.0), p=0.5),
                A.Emboss(alpha=(0.2, 0.5), strength=(0.2, 0.7), p=0.5),
                A.RandomBrightnessContrast(p=0.5),
            ], p=0.3),
            A.HueSaturationValue(p=0.3),
            
            # Occlusion simulation
            A.OneOf([
                A.CoarseDropout(max_holes=8, max_height=8, max_width=8, fill_value=0, p=0.5),
                A.GridDropout(ratio=0.5, p=0.5),
            ], p=0.2),
        ])
    
    def download_utkface_dataset(self) -> bool:
        """Download UTKFace dataset for healthy face corpus"""
        try:
            utkface_dir = self.data_dir / "utkface"
            utkface_dir.mkdir(exist_ok=True)
            
            # UTKFace dataset URLs (parts)
            urls = [
                "https://susanqq.github.io/UTKFace/part1.tar.gz",
                "https://susanqq.github.io/UTKFace/part2.tar.gz",
                "https://susanqq.github.io/UTKFace/part3.tar.gz"
            ]
            
            for i, url in enumerate(urls, 1):
                logger.info(f"📥 Downloading UTKFace part {i}/{len(urls)}")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                file_path = utkface_dir / f"part{i}.tar.gz"
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract
                logger.info(f"📦 Extracting UTKFace part {i}")
                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(utkface_dir)
                
                # Clean up
                file_path.unlink()
            
            logger.info("✅ UTKFace dataset downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download UTKFace dataset: {e}")
            return False
    
    def download_ascid_dataset(self) -> bool:
        """Download ASCID dataset for skin conditions"""
        try:
            ascid_dir = self.data_dir / "ascid"
            ascid_dir.mkdir(exist_ok=True)
            
            # ASCID dataset URL
            url = "https://github.com/openmedlab/Awesome-Medical-Dataset/raw/main/resources/ASCID.zip"
            
            logger.info("📥 Downloading ASCID dataset")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_path = ascid_dir / "ascid.zip"
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            logger.info("📦 Extracting ASCID dataset")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(ascid_dir)
            
            # Clean up
            file_path.unlink()
            
            logger.info("✅ ASCID dataset downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download ASCID dataset: {e}")
            return False
    
    def download_ddi_dataset(self) -> bool:
        """Download DDI dataset for demographic diversity"""
        try:
            ddi_dir = self.data_dir / "ddi"
            ddi_dir.mkdir(exist_ok=True)
            
            # DDI dataset URL
            url = "https://ddi-dataset.github.io/ddi.zip"
            
            logger.info("📥 Downloading DDI dataset")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_path = ddi_dir / "ddi.zip"
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            logger.info("📦 Extracting DDI dataset")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(ddi_dir)
            
            # Clean up
            file_path.unlink()
            
            logger.info("✅ DDI dataset downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download DDI dataset: {e}")
            return False
    
    def preprocess_utkface_data(self) -> Dict:
        """Preprocess UTKFace dataset for healthy face corpus"""
        try:
            utkface_dir = self.data_dir / "utkface"
            if not utkface_dir.exists():
                logger.warning("⚠️ UTKFace dataset not found")
                return {}
            
            processed_data = []
            image_files = list(utkface_dir.glob("*.jpg")) + list(utkface_dir.glob("*.png"))
            
            logger.info(f"🔄 Processing {len(image_files)} UTKFace images")
            
            for img_path in tqdm(image_files, desc="Processing UTKFace"):
                try:
                    # Parse filename for demographics (format: [age]_[gender]_[race]_[date&time].jpg)
                    filename = img_path.stem
                    parts = filename.split('_')
                    
                    if len(parts) >= 3:
                        age = int(parts[0])
                        gender = int(parts[1])
                        race = int(parts[2])
                        
                        # Map to our demographic categories
                        age_group = self._map_age_to_group(age)
                        gender_label = 'male' if gender == 0 else 'female'
                        ethnicity = self._map_race_to_ethnicity(race)
                        
                        # Load and preprocess image
                        image = cv2.imread(str(img_path))
                        if image is not None:
                            processed_image = self._preprocess_image(image)
                            
                            processed_data.append({
                                'image_path': str(img_path),
                                'condition': 'healthy',
                                'age': age,
                                'age_group': age_group,
                                'gender': gender_label,
                                'ethnicity': ethnicity,
                                'processed_image': processed_image,
                                'source': 'utkface'
                            })
                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                    continue
            
            logger.info(f"✅ Processed {len(processed_data)} UTKFace images")
            return {'utkface': processed_data}
            
        except Exception as e:
            logger.error(f"❌ Failed to preprocess UTKFace data: {e}")
            return {}
    
    def preprocess_ascid_data(self) -> Dict:
        """Preprocess ASCID dataset for skin conditions"""
        try:
            ascid_dir = self.data_dir / "ascid"
            if not ascid_dir.exists():
                logger.warning("⚠️ ASCID dataset not found")
                return {}
            
            processed_data = []
            conditions = ['acne', 'cancer', 'eczema', 'keratosis', 'milia', 'rosacea']
            
            logger.info(f"🔄 Processing ASCID dataset with {len(conditions)} conditions")
            
            for condition in conditions:
                condition_dir = ascid_dir / condition
                if condition_dir.exists():
                    image_files = list(condition_dir.glob("*.jpg")) + list(condition_dir.glob("*.png"))
                    
                    logger.info(f"📁 Processing {len(image_files)} images for condition: {condition}")
                    
                    for img_path in tqdm(image_files, desc=f"Processing {condition}"):
                        try:
                            # Load and preprocess image
                            image = cv2.imread(str(img_path))
                            if image is not None:
                                processed_image = self._preprocess_image(image)
                                
                                processed_data.append({
                                    'image_path': str(img_path),
                                    'condition': condition,
                                    'processed_image': processed_image,
                                    'source': 'ascid'
                                })
                        
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                            continue
            
            logger.info(f"✅ Processed {len(processed_data)} ASCID images")
            return {'ascid': processed_data}
            
        except Exception as e:
            logger.error(f"❌ Failed to preprocess ASCID data: {e}")
            return {}
    
    def preprocess_ddi_data(self) -> Dict:
        """Preprocess DDI dataset for demographic diversity"""
        try:
            ddi_dir = self.data_dir / "ddi"
            if not ddi_dir.exists():
                logger.warning("⚠️ DDI dataset not found")
                return {}
            
            processed_data = []
            
            # Load metadata
            metadata_path = ddi_dir / "metadata.csv"
            if metadata_path.exists():
                metadata = pd.read_csv(metadata_path)
                
                logger.info(f"🔄 Processing DDI dataset with {len(metadata)} entries")
                
                for _, row in tqdm(metadata.iterrows(), desc="Processing DDI", total=len(metadata)):
                    try:
                        img_path = ddi_dir / row['image_path']
                        if img_path.exists():
                            # Load and preprocess image
                            image = cv2.imread(str(img_path))
                            if image is not None:
                                processed_image = self._preprocess_image(image)
                                
                                processed_data.append({
                                    'image_path': str(img_path),
                                    'condition': row.get('condition', 'unknown'),
                                    'age': row.get('age', None),
                                    'age_group': self._map_age_to_group(row.get('age', 30)),
                                    'gender': row.get('gender', 'unknown'),
                                    'ethnicity': row.get('ethnicity', 'unknown'),
                                    'processed_image': processed_image,
                                    'source': 'ddi'
                                })
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process DDI entry: {e}")
                        continue
            
            logger.info(f"✅ Processed {len(processed_data)} DDI images")
            return {'ddi': processed_data}
            
        except Exception as e:
            logger.error(f"❌ Failed to preprocess DDI data: {e}")
            return {}
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess single image to target format"""
        # Resize to target size
        image = cv2.resize(image, self.target_size)
        
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Normalize to 0-1 range
        image = image.astype(np.float32) / 255.0
        
        return image
    
    def _map_age_to_group(self, age: int) -> str:
        """Map age to age group"""
        if age <= 18:
            return 'young'
        elif age <= 35:
            return 'young_adult'
        elif age <= 50:
            return 'adult'
        elif age <= 65:
            return 'middle_aged'
        else:
            return 'senior'
    
    def _map_race_to_ethnicity(self, race: int) -> str:
        """Map race code to ethnicity"""
        race_mapping = {
            0: 'white',
            1: 'black',
            2: 'asian',
            3: 'indian',
            4: 'other'
        }
        return race_mapping.get(race, 'other')
    
    def create_unified_dataset(self, datasets: Dict) -> Dict:
        """Create unified dataset from multiple sources"""
        try:
            unified_data = []
            
            # Combine all datasets
            for source, data in datasets.items():
                logger.info(f"🔄 Adding {len(data)} samples from {source}")
                unified_data.extend(data)
            
            # Create metadata
            metadata = {
                'total_samples': len(unified_data),
                'conditions': list(set([item['condition'] for item in unified_data])),
                'sources': list(set([item['source'] for item in unified_data])),
                'demographics': {
                    'age_groups': list(set([item.get('age_group', 'unknown') for item in unified_data])),
                    'genders': list(set([item.get('gender', 'unknown') for item in unified_data])),
                    'ethnicities': list(set([item.get('ethnicity', 'unknown') for item in unified_data]))
                }
            }
            
            logger.info(f"✅ Created unified dataset with {len(unified_data)} samples")
            logger.info(f"📊 Conditions: {metadata['conditions']}")
            logger.info(f"📊 Sources: {metadata['sources']}")
            
            return {
                'data': unified_data,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create unified dataset: {e}")
            return {}
    
    def split_dataset(self, unified_data: Dict, test_size: float = 0.15, val_size: float = 0.15) -> Dict:
        """Split dataset into train/validation/test sets with stratification"""
        try:
            data = unified_data['data']
            metadata = unified_data['metadata']
            
            # Prepare stratification labels
            conditions = [item['condition'] for item in data]
            age_groups = [item.get('age_group', 'unknown') for item in data]
            genders = [item.get('gender', 'unknown') for item in data]
            
            # Create stratification groups
            stratify_labels = []
            for i in range(len(data)):
                stratify_labels.append(f"{conditions[i]}_{age_groups[i]}_{genders[i]}")
            
            # Split into train and temp
            train_data, temp_data, train_labels, temp_labels = train_test_split(
                data, stratify_labels, test_size=test_size + val_size, 
                random_state=42, stratify=stratify_labels
            )
            
            # Split temp into validation and test
            val_ratio = val_size / (test_size + val_size)
            val_data, test_data, val_labels, test_labels = train_test_split(
                temp_data, temp_labels, test_size=1-val_ratio,
                random_state=42, stratify=temp_labels
            )
            
            # Create split metadata
            splits = {
                'train': {
                    'data': train_data,
                    'size': len(train_data),
                    'conditions': list(set([item['condition'] for item in train_data]))
                },
                'validation': {
                    'data': val_data,
                    'size': len(val_data),
                    'conditions': list(set([item['condition'] for item in val_data]))
                },
                'test': {
                    'data': test_data,
                    'size': len(test_data),
                    'conditions': list(set([item['condition'] for item in test_data]))
                }
            }
            
            logger.info(f"✅ Dataset split completed:")
            logger.info(f"📊 Train: {splits['train']['size']} samples")
            logger.info(f"📊 Validation: {splits['validation']['size']} samples")
            logger.info(f"📊 Test: {splits['test']['size']} samples")
            
            return splits
            
        except Exception as e:
            logger.error(f"❌ Failed to split dataset: {e}")
            return {}
    
    def save_processed_data(self, splits: Dict, metadata: Dict) -> bool:
        """Save processed data to disk"""
        try:
            # Save splits
            for split_name, split_data in splits.items():
                split_dir = self.output_dir / split_name
                split_dir.mkdir(exist_ok=True)
                
                # Save data
                data_path = split_dir / "data.npz"
                images = np.array([item['processed_image'] for item in split_data['data']])
                np.savez_compressed(data_path, images=images)
                
                # Save metadata
                metadata_path = split_dir / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(split_data, f, indent=2)
                
                logger.info(f"💾 Saved {split_name} split: {len(split_data['data'])} samples")
            
            # Save overall metadata
            overall_metadata_path = self.output_dir / "dataset_metadata.json"
            with open(overall_metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ Processed data saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save processed data: {e}")
            return False
    
    def run_full_preprocessing(self) -> bool:
        """Run complete preprocessing pipeline"""
        try:
            logger.info("🚀 Starting ML data preprocessing pipeline")
            
            # Step 1: Download datasets
            logger.info("📥 Step 1: Downloading datasets")
            self.download_utkface_dataset()
            self.download_ascid_dataset()
            self.download_ddi_dataset()
            
            # Step 2: Preprocess datasets
            logger.info("🔄 Step 2: Preprocessing datasets")
            utkface_data = self.preprocess_utkface_data()
            ascid_data = self.preprocess_ascid_data()
            ddi_data = self.preprocess_ddi_data()
            
            # Step 3: Create unified dataset
            logger.info("🔗 Step 3: Creating unified dataset")
            all_datasets = {**utkface_data, **ascid_data, **ddi_data}
            unified_data = self.create_unified_dataset(all_datasets)
            
            # Step 4: Split dataset
            logger.info("✂️ Step 4: Splitting dataset")
            splits = self.split_dataset(unified_data)
            
            # Step 5: Save processed data
            logger.info("💾 Step 5: Saving processed data")
            success = self.save_processed_data(splits, unified_data['metadata'])
            
            if success:
                logger.info("✅ ML data preprocessing pipeline completed successfully")
                return True
            else:
                logger.error("❌ Failed to save processed data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to run preprocessing pipeline: {e}")
            return False

def main():
    """Main function to run preprocessing pipeline"""
    preprocessor = MLDataPreprocessor()
    success = preprocessor.run_full_preprocessing()
    
    if success:
        print("✅ ML data preprocessing completed successfully!")
    else:
        print("❌ ML data preprocessing failed!")

if __name__ == "__main__":
    main() 