#!/usr/bin/env python3
"""
🐇 HARE RUN V6 FACIAL SKIN CONDITION TRAINING
Ultra-fast, aggressive training for facial skin condition classification
Target: 85%+ accuracy with demographic awareness
"""

import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import EfficientNetB0, ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HareRunV6FacialTrainer:
    """
    🐇 HARE RUN V6 FACIAL SKIN CONDITION TRAINING SYSTEM
    Ultra-fast, aggressive training for facial skin condition classification
    """
    
    def __init__(self):
        """Initialize the Hare Run V6 facial training system"""
        self.config = {
            'dataset': {
                'path': 'data/skin_disease_classification',
                'csv_file': 'skin_defects.csv',
                'image_size': (224, 224),
                'batch_size': 16,  # Optimized for facial images
                'validation_split': 0.2,
                'test_split': 0.2
            },
            'training': {
                'epochs': 100,  # Aggressive training
                'learning_rate': 0.001,
                'optimizer': 'adam',
                'loss_function': 'categorical_crossentropy',
                'metrics': ['accuracy'],
                'early_stopping_patience': 15,
                'reduce_lr_patience': 8,
                'restore_best_weights': True
            },
            'model': {
                'architecture': 'efficientnet_resnet_ensemble',
                'pretrained': True,
                'num_classes': 8,  # Healthy, Acne, Bags, Redness, Rosacea, Eczema, Hyperpigmentation, Other
                'dropout_rate': 0.4,
                'regularization': 'l2',
                'regularization_factor': 0.001
            },
            'augmentation': {
                'rotation_range': 20,
                'width_shift_range': 0.15,
                'height_shift_range': 0.15,
                'horizontal_flip': True,
                'vertical_flip': False,
                'brightness_range': [0.8, 1.2],
                'zoom_range': 0.15,
                'fill_mode': 'nearest',
                'shear_range': 0.1,
                'channel_shift_range': 20
            },
            'targets': {
                'accuracy': 0.85,  # 85% target
                'precision': 0.80,
                'recall': 0.80,
                'f1_score': 0.80
            }
        }
        
        self.results_dir = Path('results/hare_run_v6_facial')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Class mapping - updated for comprehensive dataset
        self.class_names = ['healthy', 'acne', 'bags', 'redness', 'rosacea', 'eczema', 'hyperpigmentation', 'other']
        self.class_mapping = {name: idx for idx, name in enumerate(self.class_names)}
        
        logger.info("🐇 HARE RUN V6 FACIAL TRAINING SYSTEM INITIALIZED!")
        logger.info(f"🎯 Target Accuracy: {self.config['targets']['accuracy']*100:.1f}%")
        logger.info(f"⚡ Aggressive Training: {self.config['training']['epochs']} epochs")
        logger.info(f"🚀 Facial Conditions: {', '.join(self.class_names)}")
    
    def load_facial_dataset(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Load the comprehensive facial dataset using our new loader"""
        logger.info("📊 Loading Comprehensive Facial Dataset...")
        
        # Import and use our comprehensive data loader
        from comprehensive_facial_data_loader import ComprehensiveFacialDataLoader
        
        loader = ComprehensiveFacialDataLoader()
        images, labels = loader.combine_all_datasets()
        
        if len(images) == 0:
            raise ValueError("Failed to load any images from comprehensive data loader")
        
        logger.info(f"✅ Loaded {len(images)} comprehensive facial images")
        logger.info(f"📊 Class distribution: {np.sum(labels, axis=0)}")
        
        return images, labels
    
    def create_facial_architecture(self) -> tf.keras.Model:
        """Create the facial skin condition classification architecture"""
        logger.info("🏗️ Creating Facial Skin Condition Architecture...")
        
        # Input layer
        input_layer = layers.Input(shape=(*self.config['dataset']['image_size'], 3))
        
        # EfficientNetB0 branch
        efficientnet = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_tensor=input_layer
        )
        efficientnet.trainable = False  # Freeze for transfer learning
        
        # ResNet50 branch
        resnet = ResNet50(
            weights='imagenet',
            include_top=False,
            input_tensor=input_layer
        )
        resnet.trainable = False  # Freeze for transfer learning
        
        # Global average pooling
        efficientnet_pool = layers.GlobalAveragePooling2D()(efficientnet.output)
        resnet_pool = layers.GlobalAveragePooling2D()(resnet.output)
        
        # Concatenate features
        combined = layers.Concatenate()([efficientnet_pool, resnet_pool])
        
        # Dense layers
        x = layers.Dense(512, activation='relu')(combined)
        x = layers.Dropout(self.config['model']['dropout_rate'])(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(self.config['model']['dropout_rate'])(x)
        
        # Output layer
        output = layers.Dense(len(self.class_names), activation='softmax')(x)
        
        # Create model
        model = models.Model(inputs=input_layer, outputs=output)
        
        logger.info("✅ Facial Architecture Created Successfully!")
        return model
    
    def prepare_data_generators(self, images: np.ndarray, labels: np.ndarray):
        """Prepare data generators with augmentation"""
        logger.info("🔄 Preparing Data Generators...")
        
        # Split data
        total_samples = len(images)
        val_size = int(total_samples * self.config['dataset']['validation_split'])
        test_size = int(total_samples * self.config['dataset']['test_split'])
        train_size = total_samples - val_size - test_size
        
        # Shuffle indices
        indices = np.random.permutation(total_samples)
        
        # Split indices
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        # Split data
        train_images = images[train_indices]
        train_labels = labels[train_indices]
        val_images = images[val_indices]
        val_labels = labels[val_indices]
        test_images = images[test_indices]
        test_labels = labels[test_indices]
        
        logger.info(f"📊 Data Split - Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rotation_range=self.config['augmentation']['rotation_range'],
            width_shift_range=self.config['augmentation']['width_shift_range'],
            height_shift_range=self.config['augmentation']['height_shift_range'],
            horizontal_flip=self.config['augmentation']['horizontal_flip'],
            brightness_range=self.config['augmentation']['brightness_range'],
            zoom_range=self.config['augmentation']['zoom_range'],
            shear_range=self.config['augmentation']['shear_range'],
            channel_shift_range=self.config['augmentation']['channel_shift_range'],
            fill_mode=self.config['augmentation']['fill_mode']
        )
        
        # No augmentation for validation/test
        val_datagen = ImageDataGenerator()
        test_datagen = ImageDataGenerator()
        
        return (train_images, train_labels, val_images, val_labels, test_images, test_labels,
                train_datagen, val_datagen, test_datagen)
    
    def train_facial_model(self, model: tf.keras.Model, train_data: Tuple, val_data: Tuple):
        """Train the facial skin condition model"""
        logger.info("🚀 Starting Facial Model Training...")
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.config['training']['learning_rate']),
            loss=self.config['training']['loss_function'],
            metrics=self.config['training']['metrics']
        )
        
        # Callbacks
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config['training']['early_stopping_patience'],
                restore_best_weights=self.config['training']['restore_best_weights']
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.config['training']['reduce_lr_patience'],
                min_lr=1e-7
            ),
            callbacks.ModelCheckpoint(
                filepath=str(self.results_dir / 'best_facial_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max'
            ),
            callbacks.TensorBoard(
                log_dir=str(self.results_dir / 'logs'),
                histogram_freq=1
            )
        ]
        
        # Train model
        history = model.fit(
            train_data[0], train_data[1],
            validation_data=(val_data[0], val_data[1]),
            epochs=self.config['training']['epochs'],
            batch_size=self.config['dataset']['batch_size'],
            callbacks=callbacks_list,
            verbose=1
        )
        
        logger.info("✅ Facial Model Training Completed!")
        return history
    
    def evaluate_facial_model(self, model: tf.keras.Model, test_images: np.ndarray, test_labels: np.ndarray):
        """Evaluate the trained facial model"""
        logger.info("📊 Evaluating Facial Model...")
        
        # Predictions
        predictions = model.predict(test_images)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = np.argmax(test_labels, axis=1)
        
        # Metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        accuracy = accuracy_score(true_classes, predicted_classes)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_classes, predicted_classes, average='weighted'
        )
        
        logger.info(f"🎯 Final Results:")
        logger.info(f"   Accuracy: {accuracy:.4f}")
        logger.info(f"   Precision: {precision:.4f}")
        logger.info(f"   Recall: {recall:.4f}")
        logger.info(f"   F1-Score: {f1:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(true_classes, predicted_classes)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=self.class_names,
                   yticklabels=self.class_names)
        plt.title('Facial Skin Condition Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.savefig(str(self.results_dir / 'confusion_matrix.png'))
        plt.close()
        
        # Classification report - use actual detected classes
        unique_classes = np.unique(np.concatenate([true_classes, predicted_classes]))
        actual_class_names = [self.class_names[i] for i in unique_classes if i < len(self.class_names)]
        
        report = classification_report(true_classes, predicted_classes, 
                                    target_names=actual_class_names, output_dict=True)
        
        # Save results
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'class_names': self.class_names,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(str(self.results_dir / 'facial_results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("✅ Evaluation Completed and Results Saved!")
        return results
    
    def run_facial_training(self):
        """Run the complete facial skin condition training pipeline"""
        logger.info("🐇 STARTING HARE RUN V6 FACIAL TRAINING!")
        logger.info("=" * 60)
        
        try:
            # Load dataset
            images, labels = self.load_facial_dataset()
            
            # Prepare data generators
            (train_images, train_labels, val_images, val_labels, test_images, test_labels,
             train_datagen, val_datagen, test_datagen) = self.prepare_data_generators(images, labels)
            
            # Create model
            model = self.create_facial_architecture()
            
            # Train model
            history = self.train_facial_model(model, (train_images, train_labels), (val_images, val_labels))
            
            # Evaluate model
            results = self.evaluate_facial_model(model, test_images, test_labels)
            
            # Save final model
            model.save(str(self.results_dir / 'final_facial_model.h5'))
            
            logger.info("🎉 HARE RUN V6 FACIAL TRAINING COMPLETED SUCCESSFULLY!")
            logger.info(f"🏆 Final Accuracy: {results['accuracy']*100:.2f}%")
            
            return model, results
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise

if __name__ == "__main__":
    # Initialize trainer
    trainer = HareRunV6FacialTrainer()
    
    # Run training
    model, results = trainer.run_facial_training()
    
    print(f"\n🎉 HARE RUN V6 FACIAL TRAINING COMPLETED!")
    print(f"🏆 Final Accuracy: {results['accuracy']*100:.2f}%")
    print(f"📊 Results saved to: {trainer.results_dir}")
