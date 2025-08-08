#!/usr/bin/env python3
"""
Simplified ML Training for Shine Skincare App
Uses existing datasets to train the enhanced ML model
"""

import os
import json
import logging
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers, callbacks
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# Import our enhanced model
from ml_enhanced_model import EnhancedSkinModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedMLTrainer:
    """Simplified ML trainer using existing datasets"""
    
    def __init__(self):
        """Initialize the simplified trainer"""
        self.datasets_dir = Path("datasets")
        self.models_dir = Path("models")
        self.results_dir = Path("results")
        
        # Create directories
        for dir_path in [self.models_dir, self.results_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Training configuration
        self.config = {
            'input_shape': (224, 224, 3),
            'num_conditions': 6,
            'batch_size': 16,  # Smaller batch size for memory
            'epochs': 20,       # Fewer epochs for quick training
            'learning_rate': 1e-4
        }
        
        logger.info("✅ Simplified ML Trainer initialized")
    
    def load_existing_datasets(self) -> Dict:
        """Load data from existing datasets"""
        try:
            logger.info("📂 Loading existing datasets...")
            
            data = {
                'images': [],
                'conditions': [],
                'ages': [],
                'genders': [],
                'ethnicities': []
            }
            
            # Load from facial skin diseases dataset
            facial_diseases_path = self.datasets_dir / "facial_skin_diseases" / "DATA" / "train"
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
                        
                        for img_path in image_files[:50]:  # Limit to 50 images per condition for quick training
                            try:
                                # Load and preprocess image
                                image = cv2.imread(str(img_path))
                                if image is not None:
                                    # Resize to target size
                                    image = cv2.resize(image, self.config['input_shape'][:2])
                                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                    image = image.astype(np.float32) / 255.0
                                    
                                    data['images'].append(image)
                                    data['conditions'].append(mapped_condition)
                                    
                                    # Add placeholder demographics
                                    data['ages'].append(30)  # Placeholder age
                                    data['genders'].append('unknown')
                                    data['ethnicities'].append('unknown')
                            
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to process {img_path}: {e}")
                                continue
            
            logger.info(f"✅ Loaded {len(data['images'])} images from existing datasets")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load datasets: {e}")
            return {'images': [], 'conditions': [], 'ages': [], 'genders': [], 'ethnicities': []}
    
    def prepare_training_data(self, data: Dict) -> Dict:
        """Prepare data for training"""
        try:
            logger.info("🔄 Preparing training data...")
            
            if len(data['images']) == 0:
                logger.error("❌ No images loaded")
                return {}
            
            # Convert to numpy arrays
            images = np.array(data['images'])
            conditions = np.array(data['conditions'])
            ages = np.array(data['ages'])
            genders = np.array(data['genders'])
            ethnicities = np.array(data['ethnicities'])
            
            # Encode categorical variables
            condition_encoder = LabelEncoder()
            gender_encoder = LabelEncoder()
            ethnicity_encoder = LabelEncoder()
            
            conditions_encoded = condition_encoder.fit_transform(conditions)
            genders_encoded = gender_encoder.fit_transform(genders)
            ethnicities_encoded = ethnicity_encoder.fit_transform(ethnicities)
            
            # Convert to one-hot encoding
            conditions_onehot = tf.keras.utils.to_categorical(conditions_encoded, num_classes=self.config['num_conditions'])
            genders_onehot = tf.keras.utils.to_categorical(genders_encoded, num_classes=2)
            ethnicities_onehot = tf.keras.utils.to_categorical(ethnicities_encoded, num_classes=7)
            
            # Create skin characteristics (placeholder)
            skin_characteristics = np.random.random((len(images), 3))
            
            # Create dummy embeddings for contrastive learning
            dummy_embeddings = np.random.random((len(images), 2048))
            
            # Split data
            train_indices, test_indices = train_test_split(
                range(len(images)), test_size=0.2, random_state=42, stratify=conditions_encoded
            )
            
            train_indices, val_indices = train_test_split(
                train_indices, test_size=0.2, random_state=42, stratify=conditions_encoded[train_indices]
            )
            
            # Create splits
            splits = {
                'train': {
                    'images': images[train_indices],
                    'conditions': conditions_onehot[train_indices],
                    'ages': ages[train_indices],
                    'genders': genders_onehot[train_indices],
                    'ethnicities': ethnicities_onehot[train_indices],
                    'skin_characteristics': skin_characteristics[train_indices],
                    'embeddings': dummy_embeddings[train_indices]
                },
                'validation': {
                    'images': images[val_indices],
                    'conditions': conditions_onehot[val_indices],
                    'ages': ages[val_indices],
                    'genders': genders_onehot[val_indices],
                    'ethnicities': ethnicities_onehot[val_indices],
                    'skin_characteristics': skin_characteristics[val_indices],
                    'embeddings': dummy_embeddings[val_indices]
                },
                'test': {
                    'images': images[test_indices],
                    'conditions': conditions_onehot[test_indices],
                    'ages': ages[test_indices],
                    'genders': genders_onehot[test_indices],
                    'ethnicities': ethnicities_onehot[test_indices],
                    'skin_characteristics': skin_characteristics[test_indices],
                    'embeddings': dummy_embeddings[test_indices]
                }
            }
            
            # Save encoders
            encoders = {
                'condition_encoder': condition_encoder,
                'gender_encoder': gender_encoder,
                'ethnicity_encoder': ethnicity_encoder
            }
            
            logger.info(f"✅ Prepared training data:")
            logger.info(f"   Train: {len(splits['train']['images'])} samples")
            logger.info(f"   Validation: {len(splits['validation']['images'])} samples")
            logger.info(f"   Test: {len(splits['test']['images'])} samples")
            
            return {'splits': splits, 'encoders': encoders}
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare training data: {e}")
            return {}
    
    def create_data_generators(self, splits: Dict):
        """Create TensorFlow data generators"""
        try:
            logger.info("🔄 Creating data generators...")
            
            # Ensure all arrays have the same shape
            train_images = splits['train']['images']
            val_images = splits['validation']['images']
            
            # Create training generator
            train_dataset = tf.data.Dataset.from_tensor_slices((
                train_images,
                [
                    splits['train']['conditions'],
                    splits['train']['embeddings'],
                    splits['train']['skin_characteristics'],
                    splits['train']['ages'],
                    splits['train']['genders'],
                    splits['train']['ethnicities']
                ]
            )).batch(self.config['batch_size']).prefetch(tf.data.AUTOTUNE)
            
            # Create validation generator
            val_dataset = tf.data.Dataset.from_tensor_slices((
                val_images,
                [
                    splits['validation']['conditions'],
                    splits['validation']['embeddings'],
                    splits['validation']['skin_characteristics'],
                    splits['validation']['ages'],
                    splits['validation']['genders'],
                    splits['validation']['ethnicities']
                ]
            )).batch(self.config['batch_size']).prefetch(tf.data.AUTOTUNE)
            
            self.train_generator = train_dataset
            self.val_generator = val_dataset
            self.test_data = splits['test']
            
            logger.info("✅ Data generators created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create data generators: {e}")
            # Create simple fallback generators
            try:
                logger.info("🔄 Creating fallback data generators...")
                
                # Create simple numpy arrays for training
                train_images = splits['train']['images']
                train_conditions = splits['train']['conditions']
                
                # Create simple dataset
                train_dataset = tf.data.Dataset.from_tensor_slices((
                    train_images,
                    train_conditions
                )).batch(self.config['batch_size'])
                
                val_images = splits['validation']['images']
                val_conditions = splits['validation']['conditions']
                
                val_dataset = tf.data.Dataset.from_tensor_slices((
                    val_images,
                    val_conditions
                )).batch(self.config['batch_size'])
                
                self.train_generator = train_dataset
                self.val_generator = val_dataset
                self.test_data = splits['test']
                
                logger.info("✅ Fallback data generators created successfully")
                
            except Exception as e2:
                logger.error(f"❌ Failed to create fallback generators: {e2}")
                raise e2
    
    def train_model(self):
        """Train the enhanced model"""
        try:
            logger.info("🎯 Training enhanced model...")
            
            # Initialize model
            self.model = EnhancedSkinModel(
                input_shape=self.config['input_shape'],
                num_conditions=self.config['num_conditions'],
                embedding_dim=2048,
                use_attention=True,
                backbone='resnet50'
            )
            
            # Build and compile model
            self.model.build_model()
            self.model.compile_model()
            
            # Create callbacks
            callbacks_list = [
                callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True,
                    verbose=1
                ),
                callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=3,
                    min_lr=1e-7,
                    verbose=1
                ),
                callbacks.ModelCheckpoint(
                    filepath=str(self.models_dir / "enhanced_skin_model.h5"),
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train model
            history = self.model.model.fit(
                self.train_generator,
                validation_data=self.val_generator,
                epochs=self.config['epochs'],
                callbacks=callbacks_list,
                verbose=1
            )
            
            # Save training history
            history_path = self.results_dir / "training_history.json"
            with open(history_path, 'w') as f:
                json.dump(history.history, f, indent=2)
            
            logger.info("✅ Model training completed successfully")
            return history
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return None
    
    def evaluate_model(self):
        """Evaluate the trained model"""
        try:
            logger.info("📊 Evaluating model performance...")
            
            if not hasattr(self, 'model') or self.model is None:
                logger.error("❌ No trained model available")
                return {}
            
            # Make predictions
            predictions = self.model.model.predict(self.test_data['images'])
            
            # Extract predictions
            condition_preds = predictions[0]
            condition_true = self.test_data['conditions']
            
            # Calculate accuracy
            condition_accuracy = np.mean(np.argmax(condition_preds, axis=1) == np.argmax(condition_true, axis=1))
            
            # Calculate per-condition accuracy
            condition_names = ['healthy', 'acne', 'eczema', 'keratosis', 'basal_cell_carcinoma', 'rosacea']
            per_condition_accuracy = {}
            
            for i, condition in enumerate(condition_names):
                condition_mask = np.argmax(condition_true, axis=1) == i
                if np.sum(condition_mask) > 0:
                    condition_acc = np.mean(
                        np.argmax(condition_preds[condition_mask], axis=1) == i
                    )
                    per_condition_accuracy[condition] = condition_acc
            
            metrics = {
                'overall_accuracy': float(condition_accuracy),
                'per_condition_accuracy': per_condition_accuracy,
                'test_samples': len(self.test_data['images'])
            }
            
            # Save metrics
            metrics_path = self.results_dir / "evaluation_metrics.json"
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"✅ Model evaluation completed:")
            logger.info(f"   Overall accuracy: {condition_accuracy:.3f}")
            for condition, acc in per_condition_accuracy.items():
                logger.info(f"   {condition}: {acc:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}
    
    def run_training_pipeline(self) -> bool:
        """Run the complete simplified training pipeline"""
        try:
            logger.info("🚀 Starting simplified ML training pipeline")
            
            # Step 1: Load existing datasets
            logger.info("📂 Step 1: Loading existing datasets")
            data = self.load_existing_datasets()
            
            if len(data['images']) == 0:
                logger.error("❌ No data loaded, cannot proceed")
                return False
            
            # Step 2: Prepare training data
            logger.info("🔄 Step 2: Preparing training data")
            prepared_data = self.prepare_training_data(data)
            
            if not prepared_data:
                logger.error("❌ Failed to prepare training data")
                return False
            
            # Step 3: Create data generators
            logger.info("🔄 Step 3: Creating data generators")
            self.create_data_generators(prepared_data['splits'])
            
            # Step 4: Train model
            logger.info("🎯 Step 4: Training model")
            history = self.train_model()
            
            if history is None:
                logger.error("❌ Model training failed")
                return False
            
            # Step 5: Evaluate model
            logger.info("📊 Step 5: Evaluating model")
            metrics = self.evaluate_model()
            
            if metrics:
                logger.info("✅ Simplified ML training pipeline completed successfully!")
                return True
            else:
                logger.error("❌ Model evaluation failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Simplified training pipeline failed: {e}")
            return False

def main():
    """Main function to run simplified training"""
    print("🚀 Shine Skincare App - Simplified ML Training")
    print("="*50)
    
    # Initialize trainer
    trainer = SimplifiedMLTrainer()
    
    # Run training pipeline
    success = trainer.run_training_pipeline()
    
    if success:
        print("\n✅ Simplified ML training completed successfully!")
        print("📁 Check the 'models' and 'results' directories for outputs")
    else:
        print("\n❌ Simplified ML training failed!")
        print("📋 Check the logs for error details")

if __name__ == "__main__":
    main() 