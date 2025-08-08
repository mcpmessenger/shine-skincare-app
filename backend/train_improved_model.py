#!/usr/bin/env python3
"""
Improved Simple Model Training for Shine Skincare App
"""

import os
import sys
import json
import logging
import numpy as np
import tensorflow as tf
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_simple_model import SimpleSkinModel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_dataset():
    """Load and preprocess the dataset with better error handling"""
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
                    for img_path in image_files:
                        try:
                            # Load and preprocess image
                            image = cv2.imread(str(img_path))
                            if image is not None:
                                # Check image dimensions
                                height, width, channels = image.shape
                                if height > 0 and width > 0 and channels == 3:
                                    # Resize to target size
                                    image = cv2.resize(image, (224, 224))
                                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                    image = image.astype(np.float32) / 255.0
                                    
                                    images.append(image)
                                    conditions.append(mapped_condition)
                                    processed_count += 1
                                else:
                                    logger.warning(f"⚠️ Invalid image dimensions for {img_path}")
                            else:
                                logger.warning(f"⚠️ Failed to load {img_path}")
                        
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                            continue
                    
                    logger.info(f"✅ Successfully processed {processed_count} images for {condition_name}")
        
        logger.info(f"✅ Loaded {len(images)} images from existing datasets")
        
        # Print class distribution
        unique_conditions, counts = np.unique(conditions, return_counts=True)
        logger.info("📊 Class distribution:")
        for condition, count in zip(unique_conditions, counts):
            logger.info(f"   {condition}: {count} images")
        
        return np.array(images), np.array(conditions)
        
    except Exception as e:
        logger.error(f"❌ Failed to load datasets: {e}")
        return np.array([]), np.array([])

def prepare_data(images, conditions):
    """Prepare data for training with stratified sampling"""
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
        
        # Split data with simple random sampling to avoid stratification issues
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
    """Train the improved model"""
    try:
        logger.info("🎯 Training improved model...")
        
        # Initialize model
        model = SimpleSkinModel(
            input_shape=(224, 224, 3),
            num_conditions=6
        )
        
        # Build and compile model
        model.build_model()
        model.compile_model()
        
        # Train model
        history = model.train_model(train_images, train_labels, val_images, val_labels)
        
        return model, history
        
    except Exception as e:
        logger.error(f"❌ Failed to train model: {e}")
        return None, None

def evaluate_model_detailed(model, test_images, test_labels, encoder):
    """Detailed model evaluation"""
    try:
        logger.info("📊 Detailed model evaluation...")
        
        # Make predictions
        predictions = model.predict(test_images)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = np.argmax(test_labels, axis=1)
        
        # Get class names
        class_names = encoder.classes_
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        overall_accuracy = accuracy_score(true_classes, predicted_classes)
        precision, recall, f1, support = precision_recall_fscore_support(true_classes, predicted_classes, average=None)
        
        logger.info(f"📊 Overall accuracy: {overall_accuracy:.3f}")
        logger.info("📊 Per-class metrics:")
        
        for i, class_name in enumerate(class_names):
            logger.info(f"   {class_name}:")
            logger.info(f"     Precision: {precision[i]:.3f}")
            logger.info(f"     Recall: {recall[i]:.3f}")
            logger.info(f"     F1-Score: {f1[i]:.3f}")
            logger.info(f"     Support: {support[i]}")
        
        # Confusion matrix
        cm = confusion_matrix(true_classes, predicted_classes)
        logger.info("📊 Confusion Matrix:")
        logger.info(cm)
        
        # Classification report
        report = classification_report(true_classes, predicted_classes, target_names=class_names)
        logger.info("📊 Classification Report:")
        logger.info(report)
        
        return {
            'overall_accuracy': overall_accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': support,
            'confusion_matrix': cm,
            'class_names': class_names
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to evaluate model: {e}")
        return None

def main():
    """Main training pipeline"""
    print("🚀 Shine Skincare App - Improved Model Training")
    print("=" * 50)
    
    try:
        # Step 1: Load dataset
        logger.info("📂 Step 1: Loading dataset")
        images, conditions = load_dataset()
        
        if len(images) == 0:
            logger.error("❌ No images loaded. Exiting.")
            return
        
        # Step 2: Prepare data
        logger.info("🔄 Step 2: Preparing data")
        train_images, val_images, train_labels, val_labels, test_images, test_labels = prepare_data(images, conditions)
        
        if train_images is None:
            logger.error("❌ Failed to prepare data. Exiting.")
            return
        
        # Step 3: Train model
        logger.info("🎯 Step 3: Training model")
        model, history = train_model(train_images, val_images, train_labels, val_labels)
        
        if model is None:
            logger.error("❌ Failed to train model. Exiting.")
            return
        
        # Step 4: Evaluate model
        logger.info("📊 Step 4: Evaluating model")
        encoder = LabelEncoder()
        encoder.fit(conditions)
        
        evaluation_results = evaluate_model_detailed(model, test_images, test_labels, encoder)
        
        if evaluation_results:
            logger.info("✅ Model evaluation completed successfully")
        else:
            logger.error("❌ Failed to evaluate model")
        
        print("\n✅ Improved model training completed successfully!")
        print(f"📊 Overall accuracy: {evaluation_results['overall_accuracy']:.3f}")
        print("📁 Check the 'models' directory for the trained model")
        
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}")
        return

if __name__ == "__main__":
    main() 