#!/usr/bin/env python3
"""
Script to analyze the quality of the facial skin diseases dataset
"""

import cv2
import numpy as np
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_dataset_quality():
    """Analyze the quality of the dataset"""
    datasets_dir = Path("datasets")
    facial_diseases_path = datasets_dir / "facial_skin_diseases" / "DATA" / "train"
    
    logger.info("🔍 Analyzing dataset quality...")
    
    condition_mapping = {
        'Acne': 'acne',
        'Actinic Keratosis': 'keratosis',
        'Basal Cell Carcinoma': 'basal_cell_carcinoma',
        'Eczemaa': 'eczema',
        'Healthy': 'healthy',
        'Rosacea': 'rosacea'
    }
    
    total_images = 0
    successful_loads = 0
    failed_loads = 0
    
    for condition_name, mapped_condition in condition_mapping.items():
        condition_dir = facial_diseases_path / condition_name
        if condition_dir.exists():
            image_files = list(condition_dir.glob("*.jpg")) + list(condition_dir.glob("*.png"))
            
            logger.info(f"📁 Analyzing {condition_name}: {len(image_files)} files")
            
            condition_successful = 0
            condition_failed = 0
            
            for img_path in image_files:
                try:
                    # Load image
                    image = cv2.imread(str(img_path))
                    if image is not None:
                        # Check image properties
                        height, width, channels = image.shape
                        if height > 0 and width > 0 and channels == 3:
                            condition_successful += 1
                            successful_loads += 1
                        else:
                            condition_failed += 1
                            failed_loads += 1
                            logger.warning(f"⚠️ Invalid image dimensions: {img_path}")
                    else:
                        condition_failed += 1
                        failed_loads += 1
                        logger.warning(f"⚠️ Failed to load image: {img_path}")
                
                except Exception as e:
                    condition_failed += 1
                    failed_loads += 1
                    logger.warning(f"⚠️ Exception loading {img_path}: {e}")
            
            logger.info(f"✅ {condition_name}: {condition_successful} successful, {condition_failed} failed")
            total_images += len(image_files)
    
    logger.info(f"\n📊 Dataset Quality Summary:")
    logger.info(f"   Total files: {total_images}")
    logger.info(f"   Successful loads: {successful_loads}")
    logger.info(f"   Failed loads: {failed_loads}")
    logger.info(f"   Success rate: {(successful_loads/total_images)*100:.1f}%")

if __name__ == "__main__":
    analyze_dataset_quality() 