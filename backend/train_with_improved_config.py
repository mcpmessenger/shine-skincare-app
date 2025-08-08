#!/usr/bin/env python3
"""
Training Script for Shine Skincare App with Improved Configuration
Uses the comprehensive real dataset and improved training configuration
to address ML-2.md issues and target >80% accuracy
"""

import os
import json
import argparse
import logging
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedModelTrainer:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.model_dir = Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Set up GPU if available
        self._setup_gpu()
        
    def _load_config(self) -> dict:
        """Load training configuration"""
        logger.info(f"Loading configuration from {self.config_path}")
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded: {config['dataset']['name']}")
        return config
    
    def _setup_gpu(self):
        """Setup GPU if available"""
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"Found {len(gpus)} GPU(s): {gpus}")
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info("GPU memory growth enabled")
            except RuntimeError as e:
                logger.warning(f"GPU setup error: {e}")
        else:
            logger.info("No GPU found, using CPU")
    
    def create_data_generators(self):
        """Create data generators with augmentation"""
        logger.info("Creating data generators...")
        
        config = self.config['training']
        dataset_path = Path(self.config['dataset']['path'])
        
        # Training data generator with augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=config['augmentation']['rotation_range'],
            width_shift_range=config['augmentation']['width_shift_range'],
            height_shift_range=config['augmentation']['height_shift_range'],
            horizontal_flip=config['augmentation']['horizontal_flip'],
            vertical_flip=config['augmentation']['vertical_flip'],
            brightness_range=config['augmentation']['brightness_range'],
            zoom_range=config['augmentation']['zoom_range'],
            fill_mode=config['augmentation']['fill_mode'],
            shear_range=config['augmentation'].get('shear_range', 0.1),
            channel_shift_range=config['augmentation'].get('channel_shift_range', 20)
        )
        
        # Validation data generator (no augmentation)
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Test data generator (no augmentation)
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            dataset_path / 'splits' / 'train',
            target_size=tuple(self.config['dataset']['image_size']),
            batch_size=config['batch_size'],
            class_mode='categorical',
            shuffle=True
        )
        
        val_generator = val_datagen.flow_from_directory(
            dataset_path / 'splits' / 'val',
            target_size=tuple(self.config['dataset']['image_size']),
            batch_size=config['batch_size'],
            class_mode='categorical',
            shuffle=False
        )
        
        test_generator = test_datagen.flow_from_directory(
            dataset_path / 'splits' / 'test',
            target_size=tuple(self.config['dataset']['image_size']),
            batch_size=config['batch_size'],
            class_mode='categorical',
            shuffle=False
        )
        
        logger.info(f"Training samples: {train_generator.samples}")
        logger.info(f"Validation samples: {val_generator.samples}")
        logger.info(f"Test samples: {test_generator.samples}")
        logger.info(f"Classes: {train_generator.class_indices}")
        
        return train_generator, val_generator, test_generator
    
    def create_improved_model(self):
        """Create improved ResNet50 model"""
        logger.info("Creating improved ResNet50 model...")
        
        config = self.config['model']
        num_classes = config['num_classes']
        image_size = tuple(self.config['dataset']['image_size'])
        
        # Base ResNet50 model
        base_model = ResNet50(
            weights='imagenet' if config['pretrained'] else None,
            include_top=False,
            input_shape=(*image_size, 3)
        )
        
        # Freeze base model layers initially
        base_model.trainable = False
        
        # Create model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(config['dropout_rate']),
            layers.Dense(512, activation='relu', 
                        kernel_regularizer=tf.keras.regularizers.l2(config['regularization_factor'])),
            layers.Dropout(config['dropout_rate']),
            layers.Dense(256, activation='relu',
                        kernel_regularizer=tf.keras.regularizers.l2(config['regularization_factor'])),
            layers.Dropout(config['dropout_rate']),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.config['training']['learning_rate']),
            loss=self.config['training']['loss_function'],
            metrics=self.config['training']['metrics']
        )
        
        logger.info(f"Model created with {model.count_params():,} parameters")
        return model, base_model
    
    def create_callbacks(self):
        """Create training callbacks"""
        logger.info("Creating training callbacks...")
        
        config = self.config['training']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks_list = [
            # Early stopping
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=config['early_stopping_patience'],
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate on plateau
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=config['reduce_lr_patience'],
                min_lr=1e-7,
                verbose=1
            ),
            
            # Model checkpoint
            callbacks.ModelCheckpoint(
                filepath=self.model_dir / f"improved_model_{timestamp}.h5",
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            
            # TensorBoard logging
            callbacks.TensorBoard(
                log_dir=self.model_dir / 'logs' / timestamp,
                histogram_freq=1
            )
        ]
        
        return callbacks_list
    
    def train_model(self, model, train_generator, val_generator):
        """Train the model"""
        logger.info("Starting model training...")
        
        config = self.config['training']
        
        # Train the model
        history = model.fit(
            train_generator,
            epochs=config['epochs'],
            validation_data=val_generator,
            callbacks=self.create_callbacks(),
            verbose=1
        )
        
        logger.info("Training completed!")
        return history
    
    def fine_tune_model(self, model, base_model, train_generator, val_generator):
        """Fine-tune the model by unfreezing base layers"""
        logger.info("Fine-tuning model...")
        
        # Unfreeze base model layers
        base_model.trainable = True
        
        # Freeze first 100 layers, unfreeze the rest
        for layer in base_model.layers[:100]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        model.compile(
            optimizer=optimizers.Adam(learning_rate=1e-5),
            loss=self.config['training']['loss_function'],
            metrics=self.config['training']['metrics']
        )
        
        # Fine-tune for a few epochs
        fine_tune_history = model.fit(
            train_generator,
            epochs=20,
            validation_data=val_generator,
            callbacks=self.create_callbacks(),
            verbose=1
        )
        
        logger.info("Fine-tuning completed!")
        return fine_tune_history
    
    def evaluate_model(self, model, test_generator):
        """Evaluate the model"""
        logger.info("Evaluating model...")
        
        # Predict on test set
        predictions = model.predict(test_generator)
        y_pred = np.argmax(predictions, axis=1)
        y_true = test_generator.classes
        
        # Calculate metrics
        test_loss, test_accuracy = model.evaluate(test_generator, verbose=0)
        
        # Classification report
        class_names = list(test_generator.class_indices.keys())
        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        logger.info(f"Test Accuracy: {test_accuracy:.4f}")
        logger.info(f"Test Loss: {test_loss:.4f}")
        
        # Save evaluation results
        evaluation_results = {
            'test_accuracy': test_accuracy,
            'test_loss': test_loss,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'target_accuracy': self.config['evaluation']['target_accuracy'],
            'ml2_baseline': 0.602,  # 60.2% baseline from ML-2.md
            'improvement': test_accuracy - 0.602
        }
        
        # Save results
        results_file = self.model_dir / 'evaluation_results.json'
        with open(results_file, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        
        logger.info(f"Evaluation results saved to {results_file}")
        
        # Print detailed results
        self._print_evaluation_results(evaluation_results, class_names)
        
        return evaluation_results
    
    def _print_evaluation_results(self, results, class_names):
        """Print detailed evaluation results"""
        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)
        
        print(f"Test Accuracy: {results['test_accuracy']:.4f} ({results['test_accuracy']*100:.2f}%)")
        print(f"ML-2.md Baseline: {results['ml2_baseline']:.4f} ({results['ml2_baseline']*100:.2f}%)")
        print(f"Improvement: {results['improvement']:.4f} ({results['improvement']*100:.2f}%)")
        print(f"Target Accuracy: {results['target_accuracy']:.4f} ({results['target_accuracy']*100:.2f}%)")
        
        if results['test_accuracy'] >= results['target_accuracy']:
            print("✅ TARGET ACHIEVED! Model accuracy exceeds target.")
        else:
            print("⚠️ Target not yet achieved. Consider additional training or data.")
        
        print("\nPer-Class Performance:")
        report = results['classification_report']
        for class_name in class_names:
            if class_name in report:
                precision = report[class_name]['precision']
                recall = report[class_name]['recall']
                f1 = report[class_name]['f1-score']
                print(f"  {class_name}: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
        
        print("\n" + "="*60)
    
    def save_model_summary(self, model):
        """Save model summary"""
        logger.info("Saving model summary...")
        
        summary_file = self.model_dir / 'model_summary.txt'
        with open(summary_file, 'w') as f:
            model.summary(print_fn=lambda x: f.write(x + '\n'))
        
        logger.info(f"Model summary saved to {summary_file}")
    
    def run_training_pipeline(self):
        """Run the complete training pipeline"""
        logger.info("Starting improved training pipeline...")
        
        try:
            # Step 1: Create data generators
            train_generator, val_generator, test_generator = self.create_data_generators()
            
            # Step 2: Create model
            model, base_model = self.create_improved_model()
            
            # Step 3: Save model summary
            self.save_model_summary(model)
            
            # Step 4: Train model
            history = self.train_model(model, train_generator, val_generator)
            
            # Step 5: Fine-tune model
            fine_tune_history = self.fine_tune_model(model, base_model, train_generator, val_generator)
            
            # Step 6: Evaluate model
            evaluation_results = self.evaluate_model(model, test_generator)
            
            # Step 7: Save final model
            final_model_path = self.model_dir / 'final_improved_model.h5'
            model.save(final_model_path)
            logger.info(f"Final model saved to {final_model_path}")
            
            logger.info("Training pipeline completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {e}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Train improved model for Shine Skincare App')
    parser.add_argument('--config', type=str, 
                       default='data/comprehensive_real_dataset/improved_training_config.json',
                       help='Path to training configuration file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Shine Skincare App - Improved Model Training")
    print("="*70)
    print("This will train a ResNet50 model with improved configuration")
    print("to address the issues identified in ML-2.md analysis.")
    print("="*70)
    
    # Create trainer
    trainer = ImprovedModelTrainer(args.config)
    
    # Run training pipeline
    success = trainer.run_training_pipeline()
    
    if success:
        print("\n✅ Training pipeline completed successfully!")
        print("📁 Model saved to: models/final_improved_model.h5")
        print("📊 Evaluation results: models/evaluation_results.json")
        print("📋 Model summary: models/model_summary.txt")
        print("\n🎯 ML-2.md Issues Addressed:")
        print("  ✅ Upgraded from simple CNN to ResNet50")
        print("  ✅ Enhanced training configuration")
        print("  ✅ Added missing melasma condition")
        print("  ✅ Balanced dataset across conditions")
        print("  ✅ Target: >80% accuracy (from 60.2% baseline)")
    else:
        print("\n❌ Training pipeline failed. Check logs for details.")

if __name__ == "__main__":
    main()
