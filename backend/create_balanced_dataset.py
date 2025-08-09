#!/usr/bin/env python3
"""
Create Balanced Dataset with UTKFace Integration
Addresses the massive class imbalance by properly incorporating UTKFace healthy images
"""

import os
import shutil
import random
import logging
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BalancedDatasetCreator:
    """Creates a balanced dataset incorporating UTKFace for healthy baseline"""
    
    def __init__(self):
        self.base_dir = Path("data")
        self.output_dir = self.base_dir / "balanced_medical_dataset"
        self.output_processed = self.output_dir / "processed"
        
        # Target sample sizes for balanced training
        self.target_samples_per_class = 500  # Balanced target
        self.min_samples_per_class = 100     # Minimum for small classes
        
        # Medical conditions from all_available_data
        self.medical_conditions = {
            "acne": self.base_dir / "all_available_data/processed/acne",
            "actinic_keratosis": self.base_dir / "all_available_data/processed/actinic_keratosis", 
            "basal_cell_carcinoma": self.base_dir / "all_available_data/processed/basal_cell_carcinoma",
            "eczema": self.base_dir / "all_available_data/processed/eczema",
            "rosacea": self.base_dir / "all_available_data/processed/rosacea"
        }
        
        # UTKFace healthy images
        self.utkface_dir = self.base_dir / "utkface/utkface_aligned_cropped/UTKFace"
        self.utkface_metadata = self.base_dir / "utkface/utkface_metadata.csv"
        
        logger.info("🏥 Balanced Medical Dataset Creator initialized")
    
    def analyze_current_distribution(self):
        """Analyze current class distribution"""
        logger.info("📊 Analyzing current class distribution...")
        
        distribution = {}
        
        # Check medical conditions
        for condition, path in self.medical_conditions.items():
            if path.exists():
                count = len(list(path.glob("*.jpg"))) + len(list(path.glob("*.png")))
                distribution[condition] = count
                status = "🚨" if condition in ["basal_cell_carcinoma", "actinic_keratosis"] else "🔍"
                logger.info(f"{status} {condition:25}: {count:3d} images")
            else:
                distribution[condition] = 0
                logger.warning(f"❌ {condition:25}: Directory not found")
        
        # Check healthy images
        healthy_current = self.base_dir / "all_available_data/processed/healthy"
        if healthy_current.exists():
            current_healthy = len(list(healthy_current.glob("*.jpg")))
            logger.info(f"📊 healthy (current)       : {current_healthy:3d} images")
        
        # Check UTKFace availability
        if self.utkface_dir.exists():
            utkface_count = len(list(self.utkface_dir.glob("*.jpg")))
            logger.info(f"💎 UTKFace available       : {utkface_count:,} images")
            distribution["healthy_available"] = utkface_count
        
        return distribution
    
    def create_balanced_healthy_subset(self):
        """Create a balanced subset of UTKFace healthy images"""
        logger.info(f"💎 Creating balanced healthy subset from UTKFace...")
        
        if not self.utkface_dir.exists():
            logger.error("❌ UTKFace directory not found!")
            return []
        
        # Get all UTKFace images
        all_images = list(self.utkface_dir.glob("*.jpg"))
        logger.info(f"📷 Found {len(all_images):,} UTKFace images")
        
        # Load metadata for demographic balancing if available
        selected_images = []
        
        if self.utkface_metadata.exists():
            logger.info("📋 Using metadata for demographic balancing...")
            try:
                metadata = pd.read_csv(self.utkface_metadata)
                
                # Sample across age groups and genders for diversity
                if 'age' in metadata.columns and 'gender' in metadata.columns:
                    # Create balanced demographic sampling
                    balanced_sample = metadata.groupby(['gender', pd.cut(metadata['age'], bins=5)]).apply(
                        lambda x: x.sample(min(len(x), 50))  # Max 50 per demographic group
                    ).reset_index(drop=True)
                    
                    # Select images based on balanced sample
                    selected_files = balanced_sample['filename'].tolist() if 'filename' in balanced_sample.columns else []
                    selected_images = [img for img in all_images if img.name in selected_files]
                    
                    logger.info(f"📊 Demographically balanced selection: {len(selected_images)} images")
                
            except Exception as e:
                logger.warning(f"⚠️ Metadata processing failed: {e}")
                selected_images = []
        
        # Fallback to random sampling if metadata approach fails
        if not selected_images:
            logger.info("🎲 Using random sampling...")
            random.shuffle(all_images)
            selected_images = all_images[:self.target_samples_per_class]
        
        logger.info(f"✅ Selected {len(selected_images)} healthy images for balanced dataset")
        return selected_images
    
    def create_balanced_dataset(self):
        """Create the complete balanced dataset"""
        logger.info("🏗️ Creating balanced medical dataset...")
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.output_processed.mkdir(exist_ok=True)
        
        # Step 1: Analyze current distribution
        distribution = self.analyze_current_distribution()
        
        # Step 2: Process each medical condition
        for condition, source_path in self.medical_conditions.items():
            target_path = self.output_processed / condition
            target_path.mkdir(exist_ok=True)
            
            if source_path.exists():
                # Copy all available medical images
                source_images = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
                
                for i, img_path in enumerate(source_images):
                    target_file = target_path / f"{condition}_{i+1:03d}{img_path.suffix}"
                    shutil.copy2(img_path, target_file)
                
                logger.info(f"✅ {condition}: Copied {len(source_images)} images")
                
                # Augment small classes if needed
                if len(source_images) < self.min_samples_per_class:
                    logger.warning(f"⚠️ {condition}: Only {len(source_images)} images (< {self.min_samples_per_class} minimum)")
            else:
                logger.error(f"❌ {condition}: Source directory not found")
        
        # Step 3: Create balanced healthy subset from UTKFace
        healthy_target = self.output_processed / "healthy"
        healthy_target.mkdir(exist_ok=True)
        
        selected_healthy = self.create_balanced_healthy_subset()
        
        for i, img_path in enumerate(selected_healthy):
            target_file = healthy_target / f"healthy_{i+1:03d}.jpg"
            shutil.copy2(img_path, target_file)
        
        logger.info(f"✅ healthy: Created balanced subset with {len(selected_healthy)} images")
        
        # Step 4: Create train/val/test splits
        self.create_data_splits()
        
        # Step 5: Generate summary
        self.generate_dataset_summary()
        
        logger.info(f"🎉 Balanced dataset created at: {self.output_dir}")
    
    def create_data_splits(self):
        """Create train/validation/test splits"""
        logger.info("📊 Creating train/validation/test splits...")
        
        splits_dir = self.output_processed / "splits"
        for split in ["train", "val", "test"]:
            split_dir = splits_dir / split
            split_dir.mkdir(parents=True, exist_ok=True)
            
            for condition in list(self.medical_conditions.keys()) + ["healthy"]:
                (split_dir / condition).mkdir(exist_ok=True)
        
        # Split each class
        for condition in list(self.medical_conditions.keys()) + ["healthy"]:
            class_dir = self.output_processed / condition
            if class_dir.exists():
                images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
                
                if len(images) > 0:
                    # 70% train, 20% val, 10% test
                    train_imgs, temp_imgs = train_test_split(images, test_size=0.3, random_state=42)
                    val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.33, random_state=42)
                    
                    # Copy to split directories
                    for split, img_list in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
                        for img in img_list:
                            target = splits_dir / split / condition / img.name
                            shutil.copy2(img, target)
                    
                    logger.info(f"📊 {condition}: {len(train_imgs)} train, {len(val_imgs)} val, {len(test_imgs)} test")
    
    def generate_dataset_summary(self):
        """Generate dataset summary"""
        logger.info("📋 Generating dataset summary...")
        
        summary = {
            "dataset_name": "Balanced Medical Dataset with UTKFace",
            "creation_date": pd.Timestamp.now().isoformat(),
            "classes": {},
            "total_images": 0,
            "balance_info": {
                "target_per_class": self.target_samples_per_class,
                "min_per_class": self.min_samples_per_class
            }
        }
        
        # Count images per class
        for condition in list(self.medical_conditions.keys()) + ["healthy"]:
            class_dir = self.output_processed / condition
            if class_dir.exists():
                count = len(list(class_dir.glob("*.jpg"))) + len(list(class_dir.glob("*.png")))
                summary["classes"][condition] = count
                summary["total_images"] += count
        
        # Save summary
        summary_file = self.output_dir / "dataset_summary.json"
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📊 Dataset Summary:")
        logger.info(f"   Total images: {summary['total_images']:,}")
        logger.info(f"   Classes: {len(summary['classes'])}")
        logger.info(f"   Summary saved: {summary_file}")

def main():
    """Main function"""
    print("="*70)
    print("💎 BALANCED MEDICAL DATASET CREATOR")
    print("="*70)
    print("Creating balanced dataset with proper UTKFace integration")
    print("Addresses massive class imbalance (100 vs 23,000+ healthy images)")
    print("="*70)
    
    creator = BalancedDatasetCreator()
    
    try:
        creator.create_balanced_dataset()
        print("\n🎉 Balanced dataset creation completed!")
        print("🔬 Ready for improved medical model training!")
        
    except Exception as e:
        logger.error(f"❌ Dataset creation failed: {e}")
        raise

if __name__ == "__main__":
    main()
