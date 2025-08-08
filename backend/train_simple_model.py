#!/usr/bin/env python3
"""
Simple Model Training for Shine Skincare App
Trains a simple condition classification model on existing datasets
"""

import os
import json
import logging
import numpy as np
import cv2
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# Import our simple model
from ml_simple_model import SimpleSkinModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_dataset():
    """Load data from existing datasets"""
    try:
        logger.info("📂 Loading existing datasets...")
        
        images = []
        conditions = []
        
        # Load from facial skin diseases dataset
        datasets_dir = Path("datasets")
        facial_diseases_path = datasets_dir / "facial_skin_diseases" / "DATA" / "train"
        
        if facial_diseases_path.exists():
            logger.info("🔄 Loading facial skin diseases dataset")
            
            condition_mapping = {
                'Acne': 'acne',
                'Actinic Keratosis': 'keratosis',
                'Basal Cell Carcinoma': 'basal_cell_carcinoma',
                'Eczemaa': 'eczema',
                'Healthy': 'healthy',
                'Rosacea': 'rosacea'
            }
            
            for condition_name, mapped_condition in condition_mapping.items():
                condition_dir = facial_diseases_path / condition_name
                if condition_dir.exists():
                    image_files = list(condition_dir.glob("*.jpg")) + list(condition_dir.glob("*.png"))
                    
                    logger.info(f"📁 Processing {len(image_files)} images for {condition_name}")
                    
                    processed_count = 0
                    for img_path in image_files:  # Use all available images per condition
                        try:
                            # Load and preprocess image
                            image = cv2.imread(str(img_path))
                            if image is not None:
                                # Resize to target size
                                image = cv2.resize(image, (224, 224))
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                image = image.astype(np.float32) / 255.0
                                
                                images.append(image)
                                conditions.append(mapped_condition)
                                processed_count += 1
                        
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                            continue
                    
                    logger.info(f"✅ Successfully processed {processed_count} images for {condition_name}")
        
        logger.info(f"✅ Loaded {len(images)} images from existing datasets")
        return np.array(images), np.array(conditions)
        
    except Exception as e:
        logger.error(f"❌ Failed to load datasets: {e}")
        return np.array([]), np.array([])

def prepare_data(images, conditions):
    """Prepare data for training"""
    try:
        logger.info("🔄 Preparing training data...")
        
        if len(images) == 0:
            logger.error("❌ No images loaded")
            return None, None, None, None, None, None
        
        # Encode conditions
        encoder = LabelEncoder()
        conditions_encoded = encoder.fit_transform(conditions)
        
        # Convert to one-hot encoding
        conditions_onehot = tf.keras.utils.to_categorical(conditions_encoded, num_classes=6)
        
        # Split data (without stratification to avoid issues)
        train_images, test_images, train_labels, test_labels = train_test_split(
            images, conditions_onehot, test_size=0.2, random_state=42
        )
        
        train_images, val_images, train_labels, val_labels = train_test_split(
            train_images, train_labels, test_size=0.2, random_state=42
        )
        
        logger.info(f"✅ Prepared training data:")
        logger.info(f"   Train: {len(train_images)} samples")
        logger.info(f"   Validation: {len(val_images)} samples")
        logger.info(f"   Test: {len(test_images)} samples")
        
        return train_images, val_images, train_labels, val_labels, test_images, test_labels
        
    except Exception as e:
        logger.error(f"❌ Failed to prepare training data: {e}")
        return None, None, None, None, None, None

def train_model(train_images, val_images, train_labels, val_labels):
    """Train the simple model"""
    try:
        logger.info("🎯 Training simple model...")
        
        # Initialize model
        model = SimpleSkinModel(
            input_shape=(224, 224, 3),
            num_conditions=6
        )
        
        # Build and compile model
        model.build_model()
        model.compile_model()
        
        # Train model
        history = model.train_model(
            train_images, train_labels,
            val_images, val_labels,
            model_save_path="models"
        )
        
        if history:
            logger.info("✅ Model training completed successfully")
            return model
        else:
            logger.error("❌ Model training failed")
            return None
        
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}")
        return None

def evaluate_model(model, test_images, test_labels):
    """Evaluate the trained model"""
    try:
        logger.info("📊 Evaluating model performance...")
        
        if model is None:
            logger.error("❌ No trained model available")
            return {}
        
        # Evaluate model
        metrics = model.evaluate_model(test_images, test_labels)
        
        if metrics:
            logger.info("✅ Model evaluation completed")
            return metrics
        else:
            logger.error("❌ Model evaluation failed")
            return {}
        
    except Exception as e:
        logger.error(f"❌ Model evaluation failed: {e}")
        return {}

def main():
    """Main function to run simple model training"""
    print("🚀 Shine Skincare App - Simple Model Training")
    print("="*50)
    
    # Step 1: Load dataset
    logger.info("📂 Step 1: Loading dataset")
    images, conditions = load_dataset()
    
    if len(images) == 0:
        print("❌ No data loaded, cannot proceed")
        return
    
    # Step 2: Prepare data
    logger.info("🔄 Step 2: Preparing data")
    train_images, val_images, train_labels, val_labels, test_images, test_labels = prepare_data(images, conditions)
    
    if train_images is None:
        print("❌ Failed to prepare data")
        return
    
    # Step 3: Train model
    logger.info("🎯 Step 3: Training model")
    model = train_model(train_images, val_images, train_labels, val_labels)
    
    if model is None:
        print("❌ Model training failed")
        return
    
    # Step 4: Evaluate model
    logger.info("📊 Step 4: Evaluating model")
    metrics = evaluate_model(model, test_images, test_labels)
    
    if metrics:
        print("\n✅ Simple model training completed successfully!")
        print(f"📊 Overall accuracy: {metrics.get('overall_accuracy', 0):.3f}")
        print("📁 Check the 'models' directory for the trained model")
    else:
        print("\n❌ Model evaluation failed")

if __name__ == "__main__":
    main() 