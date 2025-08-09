#!/usr/bin/env python3
"""
Fix Zero Accuracy Issues for Shine Skincare App
Addresses 0% accuracy for acne and actinic_keratosis with improved training
"""

import os
import json
import logging
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZeroAccuracyFixer:
    def __init__(self):
        self.data_dir = Path("data/all_available_data")
        self.splits_dir = self.data_dir / "processed" / "splits"
        
        # Model parameters
        self.img_size = (224, 224)
        self.batch_size = 16  # Smaller batch size for better generalization
        self.epochs = 150
        self.learning_rate = 0.0005  # Lower learning rate
        
        # Create output directories
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    def create_focal_loss(self, alpha=1, gamma=2):
        """Create focal loss to handle class imbalance"""
        def focal_loss(y_true, y_pred):
            # Clip predictions to prevent log(0)
            y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0)
            
            # Calculate cross entropy
            cross_entropy = -y_true * tf.math.log(y_pred)
            
            # Calculate focal loss
            focal_loss = alpha * tf.pow(1 - y_pred, gamma) * cross_entropy
            
            return tf.reduce_mean(focal_loss)
        
        return focal_loss
    
    def create_data_generators(self):
        """Create data generators with better augmentation"""
        logger.info("Creating improved data generators...")
        
        # Enhanced data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.15,
            height_shift_range=0.15,
            shear_range=0.15,
            zoom_range=0.15,
            horizontal_flip=True,
            vertical_flip=False,
            brightness_range=[0.8, 1.2],
            fill_mode='nearest'
        )
        
        # Only rescaling for validation and test
        val_datagen = ImageDataGenerator(rescale=1./255)
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            self.splits_dir / "train",
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=True
        )
        
        val_generator = val_datagen.flow_from_directory(
            self.splits_dir / "val",
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        test_generator = test_datagen.flow_from_directory(
            self.splits_dir / "test",
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        logger.info(f"Training samples: {train_generator.samples}")
        logger.info(f"Validation samples: {val_generator.samples}")
        logger.info(f"Test samples: {test_generator.samples}")
        logger.info(f"Class indices: {train_generator.class_indices}")
        
        return train_generator, val_generator, test_generator
    
    def compute_class_weights(self, train_generator):
        """Compute class weights to handle imbalance"""
        logger.info("Computing class weights...")
        
        # Get class distribution
        class_counts = train_generator.classes
        unique_classes = np.unique(class_counts)
        
        # Compute class weights
        class_weights = compute_class_weight(
            'balanced',
            classes=unique_classes,
            y=class_counts
        )
        
        # Create weight dictionary
        weight_dict = {}
        for i, weight in enumerate(class_weights):
            weight_dict[i] = weight
        
        logger.info(f"Class weights: {weight_dict}")
        return weight_dict
    
    def create_simplified_model(self, num_classes):
        """Create a simpler model to avoid overfitting"""
        logger.info(f"Creating simplified model with {num_classes} classes...")
        
        # Use a simpler base model
        base_model = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=(*self.img_size, 3)
        )
        
        # Freeze more layers initially
        base_model.trainable = False
        
        # Create simpler architecture
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),  # More dropout
            layers.Dense(512, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
            layers.Dropout(0.2),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile with focal loss
        focal_loss = self.create_focal_loss(alpha=1, gamma=2)
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.learning_rate),
            loss=focal_loss,
            metrics=['accuracy']
        )
        
        logger.info("Simplified model architecture:")
        model.summary()
        
        return model
    
    def create_callbacks(self):
        """Create improved callbacks"""
        callbacks_list = [
            # Early stopping with more patience
            callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=30,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Learning rate reduction
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=15,
                min_lr=1e-8,
                verbose=1
            ),
            
            # Model checkpoint
            callbacks.ModelCheckpoint(
                filepath=self.models_dir / 'fixed_model_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            ),
            
            # TensorBoard logging
            callbacks.TensorBoard(
                log_dir=self.results_dir / 'logs_fixed',
                histogram_freq=1,
                write_graph=True,
                write_images=True
            )
        ]
        
        return callbacks_list
    
    def train_model_with_weights(self, model, train_generator, val_generator, class_weights):
        """Train model with class weights"""
        logger.info("Training model with class weights...")
        
        callbacks_list = self.create_callbacks()
        
        # Train with class weights
        history = model.fit(
            train_generator,
            epochs=self.epochs,
            validation_data=val_generator,
            callbacks=callbacks_list,
            class_weight=class_weights,
            verbose=1
        )
        
        return history
    
    def fine_tune_with_weights(self, model, train_generator, val_generator, class_weights):
        """Fine-tune model with class weights"""
        logger.info("Fine-tuning model with class weights...")
        
        # Unfreeze base model layers gradually
        base_model = model.layers[0]
        base_model.trainable = True
        
        # Freeze early layers, unfreeze later layers
        for layer in base_model.layers[:-30]:  # Unfreeze fewer layers
            layer.trainable = False
        
        # Recompile with lower learning rate
        focal_loss = self.create_focal_loss(alpha=1, gamma=2)
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.learning_rate * 0.1),
            loss=focal_loss,
            metrics=['accuracy']
        )
        
        # Fine-tune with class weights
        fine_tune_history = model.fit(
            train_generator,
            epochs=50,
            validation_data=val_generator,
            callbacks=self.create_callbacks(),
            class_weight=class_weights,
            verbose=1
        )
        
        return fine_tune_history
    
    def evaluate_fixed_model(self, model, test_generator):
        """Evaluate the fixed model"""
        logger.info("Evaluating fixed model...")
        
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
            'per_class_accuracy': per_class_accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'predictions': predictions.tolist(),
            'true_classes': true_classes.tolist(),
            'predicted_classes': predicted_classes.tolist()
        }
        
        return results
    
    def save_fixed_results(self, results, history, model):
        """Save fixed results"""
        logger.info("Saving fixed results...")
        
        # Save results to JSON
        results_file = self.results_dir / 'fixed_training_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create plots
        self._create_fixed_plots(history, results)
        
        # Save model
        model_file = self.models_dir / 'fixed_model_final.h5'
        model.save(model_file)
        
        logger.info(f"Fixed results saved to {results_file}")
        logger.info(f"Fixed model saved to {model_file}")
    
    def _create_fixed_plots(self, history, results):
        """Create plots for fixed model"""
        # Training history plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy plot
        axes[0, 0].plot(history.history['accuracy'], label='Training Accuracy')
        axes[0, 0].plot(history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 0].set_title('Fixed Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss plot
        axes[0, 1].plot(history.history['loss'], label='Training Loss')
        axes[0, 1].plot(history.history['val_loss'], label='Validation Loss')
        axes[0, 1].set_title('Fixed Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Per-class accuracy
        class_names = list(results['per_class_accuracy'].keys())
        accuracies = list(results['per_class_accuracy'].values())
        colors = ['red' if acc == 0 else 'green' for acc in accuracies]
        
        bars = axes[1, 0].bar(range(len(class_names)), accuracies, color=colors)
        axes[1, 0].set_title('Fixed Model Per-Class Accuracy')
        axes[1, 0].set_xlabel('Class')
        axes[1, 0].set_ylabel('Accuracy')
        axes[1, 0].set_xticks(range(len(class_names)))
        axes[1, 0].set_xticklabels(class_names, rotation=45, ha='right')
        axes[1, 0].grid(True)
        
        # Add value labels on bars
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width()/2., height,
                           f'{acc:.1%}', ha='center', va='bottom')
        
        # Confusion matrix
        cm = np.array(results['confusion_matrix'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1, 1])
        axes[1, 1].set_title('Fixed Model Confusion Matrix')
        axes[1, 1].set_xlabel('Predicted')
        axes[1, 1].set_ylabel('True')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'fixed_training_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_fix_pipeline(self):
        """Run the complete fix pipeline"""
        logger.info("Starting zero accuracy fix pipeline...")
        
        try:
            # Step 1: Create data generators
            train_generator, val_generator, test_generator = self.create_data_generators()
            
            # Step 2: Compute class weights
            class_weights = self.compute_class_weights(train_generator)
            
            # Step 3: Create simplified model
            num_classes = len(train_generator.class_indices)
            model = self.create_simplified_model(num_classes)
            
            # Step 4: Train with class weights
            history = self.train_model_with_weights(model, train_generator, val_generator, class_weights)
            
            # Step 5: Fine-tune with class weights
            fine_tune_history = self.fine_tune_with_weights(model, train_generator, val_generator, class_weights)
            
            # Step 6: Evaluate fixed model
            results = self.evaluate_fixed_model(model, test_generator)
            
            # Step 7: Save results
            self.save_fixed_results(results, history, model)
            
            # Step 8: Print summary
            self._print_fix_summary(results)
            
            return True
            
        except Exception as e:
            logger.error(f"Fix pipeline failed: {e}")
            return False
    
    def _print_fix_summary(self, results):
        """Print fix summary"""
        print("\n" + "="*70)
        print("ZERO ACCURACY FIX RESULTS")
        print("="*70)
        
        print(f"🎯 Test Accuracy: {results['test_accuracy']:.4f} ({results['test_accuracy']*100:.2f}%)")
        
        print("\n📊 Per-Class Accuracy (Fixed):")
        for class_name, accuracy in results['per_class_accuracy'].items():
            status = "✅ FIXED" if accuracy > 0 else "❌ STILL ZERO"
            print(f"  - {class_name}: {accuracy:.4f} ({accuracy*100:.2f}%) {status}")
        
        print("\n🔧 Fixes Applied:")
        print("  ✅ Class weights to handle imbalance")
        print("  ✅ Focal loss for better class handling")
        print("  ✅ Simplified model architecture")
        print("  ✅ Enhanced data augmentation")
        print("  ✅ Lower learning rate")
        print("  ✅ More dropout for regularization")
        
        print("\n✅ Zero accuracy fix completed!")
        print(f"📁 Fixed model saved to: models/fixed_model_final.h5")
        print(f"📊 Results saved to: results/fixed_training_results.json")
        print(f"📈 Plots saved to: results/fixed_training_plots.png")

def main():
    """Main function"""
    print("="*70)
    print("Shine Skincare App - Fix Zero Accuracy Issues")
    print("="*70)
    print("This fixes the 0% accuracy for acne and actinic_keratosis")
    print("using class weights, focal loss, and improved training.")
    print("="*70)
    
    # Create fixer
    fixer = ZeroAccuracyFixer()
    
    # Run fix pipeline
    success = fixer.run_fix_pipeline()
    
    if success:
        print("\n🚀 Zero accuracy fix completed successfully!")
        print("🎯 Acne and actinic_keratosis should now have >0% accuracy!")
    else:
        print("\n❌ Zero accuracy fix failed. Check logs for details.")

if __name__ == "__main__":
    main()
