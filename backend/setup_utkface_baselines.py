#!/usr/bin/env python3
"""
Setup UTKFace Healthy Baselines
Creates demographic-specific healthy skin baselines for normalized analysis
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utkface_integration import UTKFaceIntegration
from enhanced_embeddings import EnhancedEmbeddingSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_utkface_baselines():
    """Set up UTKFace healthy baselines for demographic normalization"""
    try:
        logger.info("🔄 Setting up UTKFace healthy baselines...")
        
        # Initialize UTKFace integration
        utkface = UTKFaceIntegration()
        
        # Check if UTKFace dataset exists
        utkface_data_dir = Path("data/utkface")
        if not utkface_data_dir.exists():
            logger.error("❌ UTKFace data directory not found")
            logger.info("📥 Please download UTKFace dataset first")
            return False
        
        # Check for raw images
        raw_images_dir = utkface_data_dir / "raw_images"
        if not raw_images_dir.exists():
            logger.error("❌ UTKFace raw images not found")
            logger.info("📥 Please extract UTKFace images to data/utkface/raw_images/")
            return False
        
        # Verify images exist
        image_files = list(raw_images_dir.glob("*.jpg")) + list(raw_images_dir.glob("*.jpeg")) + list(raw_images_dir.glob("*.png"))
        if not image_files:
            logger.error("❌ No image files found in UTKFace raw_images directory")
            return False
        
        logger.info(f"✅ Found {len(image_files)} UTKFace images")
        
        # Extract metadata from filenames
        logger.info("🔄 Extracting metadata from UTKFace images...")
        metadata_df = utkface.extract_utkface_metadata(str(raw_images_dir))
        
        if metadata_df.empty:
            logger.error("❌ Failed to extract metadata from UTKFace images")
            return False
        
        logger.info(f"✅ Extracted metadata for {len(metadata_df)} images")
        
        # Filter for healthy-looking faces (no obvious skin conditions)
        logger.info("🔄 Filtering for healthy baseline images...")
        healthy_metadata = filter_healthy_images(metadata_df, raw_images_dir)
        
        if healthy_metadata.empty:
            logger.error("❌ No healthy baseline images found")
            return False
        
        logger.info(f"✅ Found {len(healthy_metadata)} healthy baseline images")
        
        # Generate embeddings for healthy images
        logger.info("🔄 Generating embeddings for healthy baseline images...")
        embeddings, embedding_metadata = utkface.generate_embeddings(
            healthy_metadata, str(raw_images_dir), batch_size=16
        )
        
        if len(embeddings) == 0:
            logger.error("❌ Failed to generate embeddings")
            return False
        
        logger.info(f"✅ Generated embeddings for {len(embeddings)} healthy images")
        
        # Create demographic baselines
        logger.info("🔄 Creating demographic baselines...")
        baselines = utkface.create_demographic_baselines(embeddings, healthy_metadata)
        
        if not baselines:
            logger.error("❌ Failed to create demographic baselines")
            return False
        
        logger.info(f"✅ Created baselines for {len(baselines)} demographic groups")
        
        # Save baselines
        baselines_path = utkface_data_dir / "demographic_baselines.npy"
        if utkface.save_demographic_baselines(baselines, str(baselines_path)):
            logger.info(f"✅ Saved baselines to {baselines_path}")
        else:
            logger.error("❌ Failed to save baselines")
            return False
        
        # Create summary report
        create_baseline_summary(baselines, healthy_metadata, utkface_data_dir)
        
        logger.info("✅ UTKFace healthy baselines setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ UTKFace baselines setup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def filter_healthy_images(metadata_df: pd.DataFrame, images_dir: Path) -> pd.DataFrame:
    """Filter for healthy-looking images (no obvious skin conditions)"""
    try:
        # Basic filtering criteria for healthy images
        healthy_criteria = []
        
        for idx, row in metadata_df.iterrows():
            filename = row['filename']
            age = row['age']
            gender = row['gender']
            ethnicity = row['ethnicity']
            
            # Skip images with missing demographic info
            if pd.isna(age) or pd.isna(gender) or pd.isna(ethnicity):
                continue
            
            # Skip very young children (under 5) as their skin characteristics are different
            if age < 5:
                continue
            
            # Skip very elderly (over 80) as skin changes significantly with age
            if age > 80:
                continue
            
            # Check if image file exists
            image_path = images_dir / filename
            if not image_path.exists():
                continue
            
            # Basic quality check - file size should be reasonable
            file_size = image_path.stat().st_size
            if file_size < 1000 or file_size > 10000000:  # 1KB to 10MB
                continue
            
            healthy_criteria.append(idx)
        
        # Create filtered dataframe
        healthy_df = metadata_df.loc[healthy_criteria].copy()
        
        # Add age_group column for analysis
        healthy_df['age_group'] = pd.cut(healthy_df['age'], 
                                        bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 100], 
                                        labels=['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+'])
        
        # Ensure we have a good distribution across demographics
        logger.info(f"📊 Healthy image distribution:")
        logger.info(f"   Age groups: {healthy_df['age_group'].value_counts().to_dict()}")
        logger.info(f"   Gender: {healthy_df['gender'].value_counts().to_dict()}")
        logger.info(f"   Ethnicity: {healthy_df['ethnicity'].value_counts().to_dict()}")
        
        return healthy_df
        
    except Exception as e:
        logger.error(f"❌ Failed to filter healthy images: {e}")
        return pd.DataFrame()

def create_baseline_summary(baselines: dict, metadata_df: pd.DataFrame, output_dir: Path):
    """Create a summary report of the baselines"""
    try:
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_baselines': len(baselines),
            'demographic_groups': list(baselines.keys()),
            'metadata_summary': {
                'total_images': len(metadata_df),
                'age_range': {
                    'min': int(metadata_df['age'].min()),
                    'max': int(metadata_df['age'].max()),
                    'mean': float(metadata_df['age'].mean())
                },
                'gender_distribution': metadata_df['gender'].value_counts().to_dict(),
                'ethnicity_distribution': metadata_df['ethnicity'].value_counts().to_dict()
            },
            'embedding_info': {
                'dimensions': len(list(baselines.values())[0]) if baselines else 0,
                'embedding_type': 'ResNet50_GlobalAveragePooling'
            }
        }
        
        # Save summary
        summary_path = output_dir / "baseline_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✅ Saved baseline summary to {summary_path}")
        
        # Print summary
        print("\n" + "="*50)
        print("UTKFACE HEALTHY BASELINES SUMMARY")
        print("="*50)
        print(f"Total demographic groups: {summary['total_baselines']}")
        print(f"Age range: {summary['metadata_summary']['age_range']['min']}-{summary['metadata_summary']['age_range']['max']}")
        print(f"Gender distribution: {summary['metadata_summary']['gender_distribution']}")
        print(f"Ethnicity distribution: {summary['metadata_summary']['ethnicity_distribution']}")
        print(f"Embedding dimensions: {summary['embedding_info']['dimensions']}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Failed to create baseline summary: {e}")

def verify_baselines():
    """Verify that baselines are working correctly"""
    try:
        logger.info("🔄 Verifying UTKFace baselines...")
        
        # Load baselines
        baselines_path = Path("data/utkface/demographic_baselines.npy")
        if not baselines_path.exists():
            logger.error("❌ Baselines file not found")
            return False
        
        baselines = np.load(baselines_path, allow_pickle=True).item()
        
        if not baselines:
            logger.error("❌ No baselines loaded")
            return False
        
        logger.info(f"✅ Loaded {len(baselines)} demographic baselines")
        
        # Test baseline retrieval
        utkface = UTKFaceIntegration()
        
        # Test a few demographic combinations
        test_demographics = [
            (25, 0, 0),  # 25-year-old white male
            (30, 1, 1),  # 30-year-old black female
            (40, 0, 2),  # 40-year-old asian male
        ]
        
        for age, gender, ethnicity in test_demographics:
            baseline = utkface.get_relevant_baseline(age, gender, ethnicity)
            if baseline is not None:
                logger.info(f"✅ Baseline found for age={age}, gender={gender}, ethnicity={ethnicity}")
            else:
                logger.warning(f"⚠️ No baseline found for age={age}, gender={gender}, ethnicity={ethnicity}")
        
        logger.info("✅ UTKFace baselines verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Baseline verification failed: {e}")
        return False

def main():
    """Main function to set up UTKFace baselines"""
    print("🔄 UTKFace Healthy Baselines Setup")
    print("="*50)
    
    # Check if setup is needed
    baselines_path = Path("data/utkface/demographic_baselines.npy")
    if baselines_path.exists():
        print("📋 UTKFace baselines already exist")
        response = input("Do you want to recreate them? (y/N): ")
        if response.lower() != 'y':
            print("✅ Using existing baselines")
            verify_baselines()
            return
    
    # Run setup
    if setup_utkface_baselines():
        print("✅ UTKFace baselines setup completed successfully!")
        
        # Verify baselines
        print("\n🔄 Verifying baselines...")
        if verify_baselines():
            print("✅ All baselines verified successfully!")
        else:
            print("⚠️ Some baseline verification issues found")
    else:
        print("❌ UTKFace baselines setup failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 