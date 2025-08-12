#!/usr/bin/env python3
"""
🐇 HARE RUN V6 UTKFACE SIMPLE TRAINING SYSTEM
Ultra-fast, aggressive training for maximum accuracy
Using UTKFace dataset for system validation
Target: 85%+ accuracy in record time
"""

import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use('Agg')  # AWS-compatible backend
import matplotlib.pyplot as plt
from datetime import datetime
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HareRunV6UTKFaceTrainer:
    """
    🐇 HARE RUN V6 UTKFACE SIMPLE TRAINING SYSTEM
    Ultra-fast, aggressive training for maximum accuracy
    Using UTKFace dataset for validation
    """
    
    def __init__(self):
        """Initialize the UTKFace Hare Run V6 training system"""
        self.config = {
            'dataset': {
                'utkface_path': 'data/utkface/utkface_aligned_cropped/crop_part1',
                'image_size': (224, 224),
                'batch_size': 32,  # AWS-optimized batch size
                'validation_split': 0.15
            },
            'training': {
                'epochs': 50,  # Reduced for testing
                'learning_rate': 0.001,  # Higher learning rate
                'optimizer': 'adam',
                'loss_function': 'categorical_crossentropy',
                'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
                'early_stopping_patience': 10,
                'reduce_lr_patience': 5,
                'restore_best_weights': True
            },
            'model': {
                'architecture': 'efficientnet_simple',
                'pretrained': True,
                'num_classes': 2,  # Healthy vs Other
                'dropout_rate': 0.5,
                'regularization': 'l2',
                'regularization_factor': 0.005
            },
            'augmentation': {
                'rotation_range': 30,
                'width_shift_range': 0.2,
                'height_shift_range': 0.2,
                'horizontal_flip': True,
                'vertical_flip': False,
                'brightness_range': [0.6, 1.4],
                'zoom_range': 0.2,
                'fill_mode': 'nearest',
                'shear_range': 0.15,
                'channel_shift_range': 30
            },
            'targets': {
                'accuracy': 0.85,  # 85% target
                'precision': 0.90,
                'recall': 0.85,
                'f1_score': 0.87
            }
        }
        
        self.results_dir = Path('results/hare_run_v6_utkface')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🐇 HARE RUN V6 UTKFACE SIMPLE TRAINING SYSTEM INITIALIZED!")
        logger.info(f"🎯 Target Accuracy: {self.config['targets']['accuracy']*100:.1f}%")
        logger.info(f"⚡ Aggressive Training: {self.config['training']['epochs']} epochs")
        logger.info(f"🚀 AWS-Optimized Batch Size: {self.config['dataset']['batch_size']}")
        logger.info(f"🏷️ Classes: {self.config['model']['num_classes']} (Healthy vs Other)")
    
    def create_simple_architecture(self) -> tf.keras.Model:
        """Create a simple EfficientNetB0 architecture for UTKFace"""
        logger.info("🏗️ Creating Simple Hare Run V6 Architecture...")
        
        # Input layer
        input_layer = layers.Input(shape=(*self.config['dataset']['image_size'], 3))
        
        # EfficientNetB0 base (AWS-optimized)
        base_model = EfficientNetB0(
            include_top=False,
            weights='imagenet',
            input_tensor=input_layer,
            pooling='avg'
        )
        base_model.trainable = False  # Freeze for speed
        
        # Simple classification head
        x = base_model(input_layer)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer (2 classes: Healthy vs Other)
        output = layers.Dense(self.config['model']['num_classes'], activation='softmax')(x)
        
        # Create model
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        
        # Compile
        optimizer = optimizers.Adam(learning_rate=self.config['training']['learning_rate'])
        model.compile(
            optimizer=optimizer,
            loss=self.config['training']['loss_function'],
            metrics=self.config['training']['metrics']
        )
        
        logger.info("✅ Simple Hare Run V6 Architecture Created!")
        logger.info(f"📊 Model Parameters: {model.count_params():,}")
        
        return model
    
    def create_data_generators(self):
        """Create data generators for UTKFace dataset"""
        logger.info("🚀 Creating UTKFace Data Generators...")
        
        # Create augmentation
        datagen = ImageDataGenerator(
            rotation_range=self.config['augmentation']['rotation_range'],
            width_shift_range=self.config['augmentation']['width_shift_range'],
            height_shift_range=self.config['augmentation']['height_shift_range'],
            horizontal_flip=self.config['augmentation']['horizontal_flip'],
            brightness_range=self.config['augmentation']['brightness_range'],
            zoom_range=self.config['augmentation']['zoom_range'],
            fill_mode=self.config['augmentation']['fill_mode'],
            validation_split=self.config['dataset']['validation_split']
        )
        
        # Create generators
        train_generator = datagen.flow_from_directory(
            self.config['dataset']['utkface_path'],
            target_size=self.config['dataset']['image_size'],
            batch_size=self.config['dataset']['batch_size'],
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        validation_generator = datagen.flow_from_directory(
            self.config['dataset']['utkface_path'],
            target_size=self.config['dataset']['image_size'],
            batch_size=self.config['dataset']['batch_size'],
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        logger.info(f"📊 Training samples: {train_generator.samples}")
        logger.info(f"📊 Validation samples: {validation_generator.samples}")
        logger.info(f"🏷️ Classes: {list(train_generator.class_indices.keys())}")
        
        return train_generator, validation_generator
    
    def create_callbacks(self) -> List[callbacks.Callback]:
        """Create training callbacks"""
        logger.info("⚡ Creating Hare Run V6 Callbacks...")
        
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=self.config['training']['early_stopping_patience'],
                restore_best_weights=True,
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.config['training']['reduce_lr_patience'],
                min_lr=1e-7,
                verbose=1
            ),
            callbacks.ModelCheckpoint(
                filepath=str(self.results_dir / 'hare_run_v6_utkface_best.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            HareRunUTKFaceProgressCallback(self.config['training']['epochs'])
        ]
        
        return callbacks_list
    
    def train_hare_run_v6(self) -> Dict:
        """Execute the Hare Run V6 training"""
        logger.info("🐇 STARTING HARE RUN V6 UTKFACE TRAINING!")
        logger.info("="*80)
        
        try:
            # Create model
            model = self.create_simple_architecture()
            
            # Create data generators
            train_generator, validation_generator = self.create_data_generators()
            
            # Create callbacks
            callbacks_list = self.create_callbacks()
            
            # Train the model
            logger.info("🚀 STARTING AGGRESSIVE TRAINING!")
            start_time = time.time()
            
            history = model.fit(
                train_generator,
                epochs=self.config['training']['epochs'],
                validation_data=validation_generator,
                callbacks=callbacks_list,
                verbose=1,
                workers=2,
                use_multiprocessing=False
            )
            
            training_time = time.time() - start_time
            
            # Evaluate
            results = self.evaluate_model(model, validation_generator)
            results['training_time'] = training_time
            results['training_time_minutes'] = training_time / 60
            
            # Save results
            self.save_results(results, history, model)
            
            logger.info("🎉 HARE RUN V6 UTKFACE TRAINING COMPLETE!")
            logger.info(f"⏱️ Total Training Time: {training_time/60:.1f} minutes")
            logger.info(f"🎯 Final Accuracy: {results['test_accuracy']*100:.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Hare Run V6 Training Failed: {e}")
            raise
    
    def evaluate_model(self, model, test_generator) -> Dict:
        """Evaluate the model"""
        logger.info("📊 Evaluating Hare Run V6 Model...")
        
        test_generator.reset()
        predictions = model.predict(test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        test_accuracy = np.mean(predicted_classes == true_classes)
        
        results = {
            'test_accuracy': test_accuracy,
            'target_accuracy': self.config['targets']['accuracy'],
            'improvement_needed': self.config['targets']['accuracy'] - test_accuracy,
            'model_architecture': 'Hare_Run_V6_UTKFace_Simple',
            'training_config': self.config
        }
        
        return results
    
    def save_results(self, results: Dict, history, model):
        """Save training results"""
        logger.info("💾 Saving Hare Run V6 Results...")
        
        # Save results
        results_file = self.results_dir / 'hare_run_v6_utkface_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save model
        model_file = self.results_dir / 'hare_run_v6_utkface_final.h5'
        model.save(model_file)
        
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Model saved to: {model_file}")


class HareRunUTKFaceProgressCallback(tf.keras.callbacks.Callback):
    """Custom callback for Hare Run V6 progress display"""
    
    def __init__(self, total_epochs):
        super().__init__()
        self.total_epochs = total_epochs
        self.start_time = None
        
    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        print("\n" + "="*80)
        print("🐇 HARE RUN V6 UTKFACE TRAINING STARTED!")
        print("="*80)
        print(f"⚡ Ultra-Fast Training: {self.total_epochs} epochs")
        print(f"🎯 Target: 85%+ accuracy in record time")
        print(f"🚀 AWS-Optimized Batch Size: 32")
        print(f"💨 Ultra-Fast Augmentation: Enabled")
        print("="*80)
        
    def on_epoch_end(self, epoch, logs=None):
        progress = (epoch + 1) / self.total_epochs
        bar_length = 50
        filled_length = int(bar_length * progress)
        bar = '🐇' * filled_length + '⚡' * (bar_length - filled_length)
        
        accuracy = logs.get('accuracy', 0)
        val_accuracy = logs.get('val_accuracy', 0)
        
        print(f"✅ HARE RUN V6 EPOCH {epoch + 1} COMPLETE:")
        print(f"   🎯 Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
        print(f"   🚀 Val Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.1f}%)")
        print(f"   🐇 Progress: |{bar}| {progress*100:.1f}%")
        
        if val_accuracy > 0.8:
            print("   🏆 HARE RUN V6 EXCELLENCE!")
        elif val_accuracy > 0.7:
            print("   🚀 HARE RUN V6 SPEEDING UP!")
        elif val_accuracy > 0.6:
            print("   ⚡ HARE RUN V6 ACCELERATING!")
        else:
            print("   🐇 HARE RUN V6 BUILDING SPEED!")
            
        sys.stdout.flush()
        
    def on_train_end(self, logs=None):
        total_time = time.time() - self.start_time
        print("\n" + "="*80)
        print("🎉 HARE RUN V6 UTKFACE TRAINING COMPLETE!")
        print("="*80)
        print(f"⏱️ Total Training Time: {total_time/60:.1f} minutes")
        print("🐇 The Hare has completed the UTKFace race!")
        print("="*80)


if __name__ == "__main__":
    # Initialize Hare Run V6 UTKFace Trainer
    hare_trainer = HareRunV6UTKFaceTrainer()
    
    # Execute training
    try:
        results = hare_trainer.train_hare_run_v6()
        
        print("\n" + "="*80)
        print("🏆 HARE RUN V6 UTKFACE FINAL RESULTS")
        print("="*80)
        print(f"🎯 Final Accuracy: {results['test_accuracy']*100:.1f}%")
        print(f"🎯 Target Accuracy: {results['target_accuracy']*100:.1f}%")
        print(f"📈 Improvement Needed: {results['improvement_needed']*100:.1f}%")
        print(f"⏱️ Training Time: {results['training_time_minutes']:.1f} minutes")
        print("="*80)
        
        if results['test_accuracy'] >= results['target_accuracy']:
            print("🎉 HARE RUN V6 UTKFACE SUCCESS! Target accuracy achieved!")
        else:
            print("🐇 HARE RUN V6 UTKFACE needs more training to reach target!")
            
    except Exception as e:
        print(f"❌ Hare Run V6 UTKFace Training Failed: {e}")
        sys.exit(1)
