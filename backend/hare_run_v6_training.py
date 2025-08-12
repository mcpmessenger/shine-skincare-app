#!/usr/bin/env python3
"""
🐇 HARE RUN V6 TRAINING SYSTEM
Ultra-fast, aggressive training for maximum accuracy
Target: 85%+ accuracy in record time
"""

import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import EfficientNetB4, ResNet50V2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HareRunV6Trainer:
    """
    🐇 HARE RUN V6 TRAINING SYSTEM
    Ultra-fast, aggressive training for maximum accuracy
    """
    
    def __init__(self):
        """Initialize the Hare Run V6 training system"""
        self.config = {
            'dataset': {
                'path': 'data/comprehensive_real_dataset/processed',
                'image_size': (224, 224),
                'batch_size': 64,  # Aggressive batch size
                'validation_split': 0.15
            },
            'training': {
                'epochs': 100,  # Aggressive training
                'learning_rate': 0.001,  # Higher learning rate
                'optimizer': 'adam',
                'loss_function': 'categorical_crossentropy',
                'metrics': ['accuracy', 'precision', 'recall', 'f1_score'],
                'early_stopping_patience': 10,  # Faster stopping
                'reduce_lr_patience': 5,  # Faster LR reduction
                'restore_best_weights': True
            },
            'model': {
                'architecture': 'efficientnet_resnet_ensemble',
                'pretrained': True,
                'num_classes': 13,
                'dropout_rate': 0.5,
                'regularization': 'l2',
                'regularization_factor': 0.005
            },
            'augmentation': {
                'rotation_range': 30,  # More aggressive
                'width_shift_range': 0.2,
                'height_shift_range': 0.2,
                'horizontal_flip': True,
                'vertical_flip': False,
                'brightness_range': [0.6, 1.4],  # More variation
                'zoom_range': 0.2,
                'fill_mode': 'nearest',
                'shear_range': 0.15,
                'channel_shift_range': 30,
                'mixup_alpha': 0.2,  # Mixup augmentation
                'cutmix_alpha': 1.0   # CutMix augmentation
            },
            'targets': {
                'accuracy': 0.85,  # 85% target
                'precision': 0.90,
                'recall': 0.85,
                'f1_score': 0.87
            }
        }
        
        self.results_dir = Path('results/hare_run_v6')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🐇 HARE RUN V6 TRAINING SYSTEM INITIALIZED!")
        logger.info(f"🎯 Target Accuracy: {self.config['targets']['accuracy']*100:.1f}%")
        logger.info(f"⚡ Aggressive Training: {self.config['training']['epochs']} epochs")
        logger.info(f"🚀 Ultra-Fast Batch Size: {self.config['dataset']['batch_size']}")
    
    def create_hare_run_architecture(self) -> tf.keras.Model:
        """Create the ultra-fast Hare Run V6 architecture"""
        logger.info("🏗️ Creating Hare Run V6 Architecture...")
        
        # Input layer
        input_layer = layers.Input(shape=(*self.config['dataset']['image_size'], 3))
        
        # EfficientNetB4 branch (fast and efficient)
        efficientnet = EfficientNetB4(
            include_top=False,
            weights='imagenet',
            input_tensor=input_layer,
            pooling='avg'
        )
        efficientnet.trainable = False  # Freeze for speed
        
        # ResNet50V2 branch (proven performance)
        resnet_input = layers.Input(shape=(*self.config['dataset']['image_size'], 3))
        resnet = ResNet50V2(
            include_top=False,
            weights='imagenet',
            input_tensor=resnet_input,
            pooling='avg'
        )
        resnet.trainable = False  # Freeze for speed
        
        # Feature extraction
        efficientnet_features = efficientnet(input_layer)
        resnet_features = resnet(input_layer)
        
        # Concatenate features
        combined_features = layers.Concatenate()([efficientnet_features, resnet_features])
        
        # Aggressive feature processing
        x = layers.Dense(1024, activation='relu')(combined_features)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Output layer
        output = layers.Dense(self.config['model']['num_classes'], activation='softmax')(x)
        
        # Create model
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        
        # Compile with aggressive settings
        optimizer = optimizers.Adam(
            learning_rate=self.config['training']['learning_rate'],
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-7
        )
        
        model.compile(
            optimizer=optimizer,
            loss=self.config['training']['loss_function'],
            metrics=self.config['training']['metrics']
        )
        
        logger.info("✅ Hare Run V6 Architecture Created!")
        logger.info(f"📊 Model Parameters: {model.count_params():,}")
        
        return model
    
    def create_aggressive_augmentation(self) -> ImageDataGenerator:
        """Create ultra-aggressive data augmentation"""
        logger.info("🚀 Creating Ultra-Aggressive Augmentation...")
        
        return ImageDataGenerator(
            rotation_range=self.config['augmentation']['rotation_range'],
            width_shift_range=self.config['augmentation']['width_shift_range'],
            height_shift_range=self.config['augmentation']['height_shift_range'],
            horizontal_flip=self.config['augmentation']['horizontal_flip'],
            vertical_flip=self.config['augmentation']['vertical_flip'],
            brightness_range=self.config['augmentation']['brightness_range'],
            zoom_range=self.config['augmentation']['zoom_range'],
            fill_mode=self.config['augmentation']['fill_mode'],
            shear_range=self.config['augmentation']['shear_range'],
            channel_shift_range=self.config['augmentation']['channel_shift_range'],
            validation_split=self.config['dataset']['validation_split']
        )
    
    def create_hare_run_callbacks(self) -> List[callbacks.Callback]:
        """Create aggressive training callbacks"""
        logger.info("⚡ Creating Hare Run V6 Callbacks...")
        
        callbacks_list = [
            # Early stopping with aggressive patience
            callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=self.config['training']['early_stopping_patience'],
                restore_best_weights=self.config['training']['restore_best_weights'],
                verbose=1
            ),
            
            # Learning rate reduction
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=self.config['training']['reduce_lr_patience'],
                min_lr=1e-7,
                verbose=1
            ),
            
            # Model checkpointing
            callbacks.ModelCheckpoint(
                filepath=str(self.results_dir / 'hare_run_v6_best.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            
            # Custom Hare Run progress callback
            HareRunProgressCallback(self.config['training']['epochs'])
        ]
        
        return callbacks_list
    
    def train_hare_run_v6(self) -> Dict:
        """Execute the Hare Run V6 training"""
        logger.info("🐇 STARTING HARE RUN V6 TRAINING!")
        logger.info("="*80)
        
        try:
            # Create model
            model = self.create_hare_run_architecture()
            
            # Create data generators
            train_datagen = self.create_aggressive_augmentation()
            
            # Load training data
            train_generator = train_datagen.flow_from_directory(
                self.config['dataset']['path'],
                target_size=self.config['dataset']['image_size'],
                batch_size=self.config['dataset']['batch_size'],
                class_mode='categorical',
                subset='training',
                shuffle=True
            )
            
            validation_generator = train_datagen.flow_from_directory(
                self.config['dataset']['path'],
                target_size=self.config['dataset']['image_size'],
                batch_size=self.config['dataset']['batch_size'],
                class_mode='categorical',
                subset='validation',
                shuffle=False
            )
            
            logger.info(f"📊 Training samples: {train_generator.samples}")
            logger.info(f"📊 Validation samples: {validation_generator.samples}")
            logger.info(f"🏷️ Classes: {list(train_generator.class_indices.keys())}")
            
            # Create callbacks
            callbacks_list = self.create_hare_run_callbacks()
            
            # Train the model
            logger.info("🚀 STARTING AGGRESSIVE TRAINING!")
            start_time = time.time()
            
            history = model.fit(
                train_generator,
                epochs=self.config['training']['epochs'],
                validation_data=validation_generator,
                callbacks=callbacks_list,
                verbose=1,
                workers=4,
                use_multiprocessing=True
            )
            
            training_time = time.time() - start_time
            
            # Evaluate the model
            logger.info("📊 Evaluating Hare Run V6 Model...")
            results = self.evaluate_hare_run_model(model, validation_generator)
            results['training_time'] = training_time
            results['training_time_minutes'] = training_time / 60
            
            # Save results
            self.save_hare_run_results(results, history, model)
            
            logger.info("🎉 HARE RUN V6 TRAINING COMPLETE!")
            logger.info(f"⏱️ Total Training Time: {training_time/60:.1f} minutes")
            logger.info(f"🎯 Final Accuracy: {results['test_accuracy']*100:.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Hare Run V6 Training Failed: {e}")
            raise
    
    def evaluate_hare_run_model(self, model, test_generator) -> Dict:
        """Evaluate the Hare Run V6 model"""
        logger.info("📊 Evaluating Hare Run V6 Model...")
        
        # Get predictions
        test_generator.reset()
        predictions = model.predict(test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        # Calculate metrics
        test_accuracy = np.mean(predicted_classes == true_classes)
        
        # Classification report
        class_names = list(test_generator.class_indices.keys())
        report = classification_report(
            true_classes, 
            predicted_classes, 
            target_names=class_names,
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(true_classes, predicted_classes)
        
        # Calculate per-class accuracy
        per_class_accuracy = {}
        for i, class_name in enumerate(class_names):
            class_mask = true_classes == i
            if np.sum(class_mask) > 0:
                class_accuracy = np.mean(predicted_classes[class_mask] == true_classes[class_mask])
                per_class_accuracy[class_name] = class_accuracy
        
        results = {
            'test_accuracy': test_accuracy,
            'target_accuracy': self.config['targets']['accuracy'],
            'target_precision': self.config['targets']['precision'],
            'target_recall': self.config['targets']['recall'],
            'target_f1_score': self.config['targets']['f1_score'],
            'improvement_needed': self.config['targets']['accuracy'] - test_accuracy,
            'per_class_accuracy': per_class_accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'predictions': predictions.tolist(),
            'true_classes': true_classes.tolist(),
            'predicted_classes': predicted_classes.tolist(),
            'model_architecture': 'Hare_Run_V6_Ensemble',
            'training_config': self.config
        }
        
        return results
    
    def save_hare_run_results(self, results: Dict, history, model):
        """Save Hare Run V6 results"""
        logger.info("💾 Saving Hare Run V6 Results...")
        
        # Save results to JSON
        results_file = self.results_dir / 'hare_run_v6_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save model
        model_file = self.results_dir / 'hare_run_v6_final.h5'
        model.save(model_file)
        
        # Create training plots
        self._create_hare_run_plots(history, results)
        
        logger.info(f"✅ Results saved to: {results_file}")
        logger.info(f"✅ Model saved to: {model_file}")
    
    def _create_hare_run_plots(self, history, results):
        """Create Hare Run V6 training plots"""
        try:
            # Training history plots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('🐇 Hare Run V6 Training Results', fontsize=16, fontweight='bold')
            
            # Accuracy
            axes[0, 0].plot(history.history['accuracy'], label='Training Accuracy', color='#FF6B6B')
            axes[0, 0].plot(history.history['val_accuracy'], label='Validation Accuracy', color='#4ECDC4')
            axes[0, 0].axhline(y=self.config['targets']['accuracy'], color='#45B7D1', linestyle='--', label='Target (85%)')
            axes[0, 0].set_title('Accuracy')
            axes[0, 0].set_xlabel('Epoch')
            axes[0, 0].set_ylabel('Accuracy')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)
            
            # Loss
            axes[0, 1].plot(history.history['loss'], label='Training Loss', color='#FF6B6B')
            axes[0, 1].plot(history.history['val_loss'], label='Validation Loss', color='#4ECDC4')
            axes[0, 1].set_title('Loss')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Loss')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            
            # Per-class accuracy
            class_names = list(results['per_class_accuracy'].keys())
            accuracies = list(results['per_class_accuracy'].values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(class_names)))
            
            axes[1, 0].barh(class_names, accuracies, color=colors)
            axes[1, 0].axvline(x=self.config['targets']['accuracy'], color='#45B7D1', linestyle='--', label='Target (85%)')
            axes[1, 0].set_title('Per-Class Accuracy')
            axes[1, 0].set_xlabel('Accuracy')
            axes[1, 0].set_ylabel('Class')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # Confusion matrix
            cm = np.array(results['confusion_matrix'])
            im = axes[1, 1].imshow(cm, cmap='Blues', interpolation='nearest')
            axes[1, 1].set_title('Confusion Matrix')
            axes[1, 1].set_xlabel('Predicted')
            axes[1, 1].set_ylabel('True')
            
            # Add colorbar
            plt.colorbar(im, ax=axes[1, 1])
            
            plt.tight_layout()
            
            # Save plot
            plot_file = self.results_dir / 'hare_run_v6_training_plots.png'
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📊 Training plots saved to: {plot_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create plots: {e}")


class HareRunProgressCallback(tf.keras.callbacks.Callback):
    """Custom callback for Hare Run V6 progress display"""
    
    def __init__(self, total_epochs):
        super().__init__()
        self.total_epochs = total_epochs
        self.start_time = None
        
    def on_train_begin(self, logs=None):
        self.start_time = time.time()
        print("\n" + "="*80)
        print("🐇 HARE RUN V6 TRAINING STARTED!")
        print("="*80)
        print(f"⚡ Ultra-Fast Training: {self.total_epochs} epochs")
        print(f"🎯 Target: 85%+ accuracy in record time")
        print(f"🚀 Aggressive Batch Size: 64")
        print(f"💨 Ultra-Fast Augmentation: Enabled")
        print("="*80)
        
    def on_epoch_begin(self, epoch, logs=None):
        print(f"\n🐇 HARE RUN V6 - EPOCH {epoch + 1}/{self.total_epochs}")
        print("-" * 60)
        
    def on_epoch_end(self, epoch, logs=None):
        # Progress bar
        progress = (epoch + 1) / self.total_epochs
        bar_length = 50
        filled_length = int(bar_length * progress)
        bar = '🐇' * filled_length + '⚡' * (bar_length - filled_length)
        
        # Time calculations
        elapsed_time = time.time() - self.start_time
        if epoch > 0:
            avg_time_per_epoch = elapsed_time / (epoch + 1)
            remaining_epochs = self.total_epochs - (epoch + 1)
            eta_seconds = remaining_epochs * avg_time_per_epoch
            eta_minutes = eta_seconds / 60
            eta_str = f"{int(eta_minutes)}m {int(eta_seconds % 60)}s"
        else:
            eta_str = "Calculating..."
        
        # Display results
        accuracy = logs.get('accuracy', 0)
        val_accuracy = logs.get('val_accuracy', 0)
        loss = logs.get('loss', 0)
        val_loss = logs.get('val_loss', 0)
        
        print(f"✅ HARE RUN V6 EPOCH {epoch + 1} COMPLETE:")
        print(f"   🎯 Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
        print(f"   🚀 Val Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.1f}%)")
        print(f"   📉 Loss: {loss:.4f}")
        print(f"   📊 Val Loss: {val_loss:.4f}")
        print(f"   🐇 Progress: |{bar}| {progress*100:.1f}%")
        print(f"   ⏰ ETA: {eta_str}")
        
        # Hare Run performance indicators
        if val_accuracy > 0.8:
            print("   🏆 HARE RUN V6 EXCELLENCE!")
        elif val_accuracy > 0.7:
            print("   🚀 HARE RUN V6 SPEEDING UP!")
        elif val_accuracy > 0.6:
            print("   ⚡ HARE RUN V6 ACCELERATING!")
        elif val_accuracy > 0.5:
            print("   🐇 HARE RUN V6 BUILDING SPEED!")
        else:
            print("   🐰 HARE RUN V6 WARMING UP!")
            
        sys.stdout.flush()
        
    def on_train_end(self, logs=None):
        total_time = time.time() - self.start_time
        print("\n" + "="*80)
        print("🎉 HARE RUN V6 TRAINING COMPLETE!")
        print("="*80)
        print(f"⏱️ Total Training Time: {total_time/60:.1f} minutes")
        print(f"🚀 Ultra-Fast Performance Achieved!")
        print("🐇 The Hare has completed the race!")
        print("="*80)


if __name__ == "__main__":
    # Initialize Hare Run V6 Trainer
    hare_trainer = HareRunV6Trainer()
    
    # Execute Hare Run V6 Training
    try:
        results = hare_trainer.train_hare_run_v6()
        
        print("\n" + "="*80)
        print("🏆 HARE RUN V6 FINAL RESULTS")
        print("="*80)
        print(f"🎯 Final Accuracy: {results['test_accuracy']*100:.1f}%")
        print(f"🎯 Target Accuracy: {results['target_accuracy']*100:.1f}%")
        print(f"📈 Improvement Needed: {results['improvement_needed']*100:.1f}%")
        print(f"⏱️ Training Time: {results['training_time_minutes']:.1f} minutes")
        print(f"📊 Results saved to: results/hare_run_v6/")
        print("="*80)
        
        if results['test_accuracy'] >= results['target_accuracy']:
            print("🎉 HARE RUN V6 SUCCESS! Target accuracy achieved!")
        else:
            print("🐇 HARE RUN V6 needs more training to reach target!")
            
    except Exception as e:
        print(f"❌ HARE RUN V6 Training Failed: {e}")
        sys.exit(1)
