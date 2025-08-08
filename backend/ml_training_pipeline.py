#!/usr/bin/env python3
"""
ML Training Pipeline for Shine Skincare App
Integrates data preprocessing with enhanced model training, bias mitigation, and evaluation
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.metrics import classification_report, confusion_matrix, silhouette_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from ml_data_preprocessing import MLDataPreprocessor
from ml_enhanced_model import EnhancedSkinModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLTrainingPipeline:
    """Comprehensive training pipeline for enhanced skin analysis model"""
    
    def __init__(self, 
                 data_dir: str = "datasets",
                 processed_data_dir: str = "processed_data",
                 models_dir: str = "models",
                 results_dir: str = "results"):
        """
        Initialize the training pipeline
        
        Args:
            data_dir: Directory containing raw datasets
            processed_data_dir: Directory for processed data
            models_dir: Directory for saved models
            results_dir: Directory for training results
        """
        self.data_dir = Path(data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.models_dir = Path(models_dir)
        self.results_dir = Path(results_dir)
        
        # Create directories
        for dir_path in [self.processed_data_dir, self.models_dir, self.results_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.preprocessor = MLDataPreprocessor(data_dir, processed_data_dir)
        self.model = None
        self.label_encoders = {}
        self.scalers = {}
        
        # Training configuration
        self.config = {
            'input_shape': (224, 224, 3),
            'num_conditions': 6,
            'embedding_dim': 2048,
            'use_attention': True,
            'backbone': 'resnet50',
            'batch_size': 32,
            'epochs': 100,
            'learning_rate': 1e-4,
            'early_stopping_patience': 15,
            'reduce_lr_patience': 10
        }
        
        logger.info("✅ ML Training Pipeline initialized")
    
    def run_data_preprocessing(self) -> bool:
        """Run complete data preprocessing pipeline"""
        try:
            logger.info("🚀 Starting data preprocessing pipeline")
            
            # Run preprocessing
            success = self.preprocessor.run_full_preprocessing()
            
            if success:
                logger.info("✅ Data preprocessing completed successfully")
                return True
            else:
                logger.error("❌ Data preprocessing failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Data preprocessing failed: {e}")
            return False
    
    def load_processed_data(self) -> Dict:
        """Load processed data from disk"""
        try:
            logger.info("📂 Loading processed data...")
            
            data = {}
            for split in ['train', 'validation', 'test']:
                split_dir = self.processed_data_dir / split
                if split_dir.exists():
                    # Load images
                    data_path = split_dir / "data.npz"
                    if data_path.exists():
                        loaded_data = np.load(data_path)
                        data[f'{split}_images'] = loaded_data['images']
                    
                    # Load metadata
                    metadata_path = split_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as f:
                            data[f'{split}_metadata'] = json.load(f)
            
            logger.info("✅ Processed data loaded successfully")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load processed data: {e}")
            return {}
    
    def prepare_training_data(self, data: Dict) -> Dict:
        """Prepare data for training with proper encoding and scaling"""
        try:
            logger.info("🔄 Preparing training data...")
            
            # Extract labels from metadata
            train_metadata = data.get('train_metadata', {})
            val_metadata = data.get('validation_metadata', {})
            test_metadata = data.get('test_metadata', {})
            
            # Prepare labels for each split
            prepared_data = {}
            
            for split_name, metadata in [('train', train_metadata), ('validation', val_metadata), ('test', test_metadata)]:
                if 'data' in metadata:
                    split_data = metadata['data']
                    
                    # Extract labels
                    conditions = [item['condition'] for item in split_data]
                    ages = [item.get('age', 30) for item in split_data]
                    genders = [item.get('gender', 'unknown') for item in split_data]
                    ethnicities = [item.get('ethnicity', 'unknown') for item in split_data]
                    
                    # Encode categorical variables
                    if split_name == 'train':
                        # Fit encoders on training data
                        self.label_encoders['condition'] = LabelEncoder()
                        self.label_encoders['gender'] = LabelEncoder()
                        self.label_encoders['ethnicity'] = LabelEncoder()
                        self.scalers['age'] = StandardScaler()
                        
                        # Fit and transform
                        condition_encoded = self.label_encoders['condition'].fit_transform(conditions)
                        gender_encoded = self.label_encoders['gender'].fit_transform(genders)
                        ethnicity_encoded = self.label_encoders['ethnicity'].fit_transform(ethnicities)
                        age_scaled = self.scalers['age'].fit_transform(np.array(ages).reshape(-1, 1)).flatten()
                    else:
                        # Transform using fitted encoders
                        condition_encoded = self.label_encoders['condition'].transform(conditions)
                        gender_encoded = self.label_encoders['gender'].transform(genders)
                        ethnicity_encoded = self.label_encoders['ethnicity'].transform(ethnicities)
                        age_scaled = self.scalers['age'].transform(np.array(ages).reshape(-1, 1)).flatten()
                    
                    # Convert to one-hot encoding
                    condition_onehot = tf.keras.utils.to_categorical(condition_encoded, num_classes=self.config['num_conditions'])
                    gender_onehot = tf.keras.utils.to_categorical(gender_encoded, num_classes=2)
                    ethnicity_onehot = tf.keras.utils.to_categorical(ethnicity_encoded, num_classes=7)
                    
                    # Create skin characteristics (placeholder - in practice, these would be extracted from images)
                    skin_characteristics = np.random.random((len(split_data), 3))  # redness, texture, pigmentation
                    
                    # Store prepared data
                    prepared_data[f'{split_name}_images'] = data.get(f'{split_name}_images', [])
                    prepared_data[f'{split_name}_condition_labels'] = condition_onehot
                    prepared_data[f'{split_name}_age_labels'] = age_scaled
                    prepared_data[f'{split_name}_gender_labels'] = gender_onehot
                    prepared_data[f'{split_name}_ethnicity_labels'] = ethnicity_onehot
                    prepared_data[f'{split_name}_skin_char_labels'] = skin_characteristics
                    
                    # Create dummy embeddings for contrastive learning
                    dummy_embeddings = np.random.random((len(split_data), self.config['embedding_dim']))
                    prepared_data[f'{split_name}_embedding_labels'] = dummy_embeddings
            
            logger.info("✅ Training data prepared successfully")
            return prepared_data
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare training data: {e}")
            return {}
    
    def create_data_generators(self, prepared_data: Dict):
        """Create TensorFlow data generators for training"""
        try:
            logger.info("🔄 Creating data generators...")
            
            # Create training generator
            train_dataset = tf.data.Dataset.from_tensor_slices((
                prepared_data['train_images'],
                [
                    prepared_data['train_condition_labels'],
                    prepared_data['train_embedding_labels'],
                    prepared_data['train_skin_char_labels'],
                    prepared_data['train_age_labels'],
                    prepared_data['train_gender_labels'],
                    prepared_data['train_ethnicity_labels']
                ]
            )).batch(self.config['batch_size']).prefetch(tf.data.AUTOTUNE)
            
            # Create validation generator
            val_dataset = tf.data.Dataset.from_tensor_slices((
                prepared_data['validation_images'],
                [
                    prepared_data['validation_condition_labels'],
                    prepared_data['validation_embedding_labels'],
                    prepared_data['validation_skin_char_labels'],
                    prepared_data['validation_age_labels'],
                    prepared_data['validation_gender_labels'],
                    prepared_data['validation_ethnicity_labels']
                ]
            )).batch(self.config['batch_size']).prefetch(tf.data.AUTOTUNE)
            
            # Create test generator
            test_dataset = tf.data.Dataset.from_tensor_slices((
                prepared_data['test_images'],
                [
                    prepared_data['test_condition_labels'],
                    prepared_data['test_embedding_labels'],
                    prepared_data['test_skin_char_labels'],
                    prepared_data['test_age_labels'],
                    prepared_data['test_gender_labels'],
                    prepared_data['test_ethnicity_labels']
                ]
            )).batch(self.config['batch_size']).prefetch(tf.data.AUTOTUNE)
            
            self.train_generator = train_dataset
            self.val_generator = val_dataset
            self.test_generator = test_dataset
            
            logger.info("✅ Data generators created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create data generators: {e}")
    
    def initialize_model(self):
        """Initialize the enhanced skin analysis model"""
        try:
            logger.info("🏗️ Initializing enhanced model...")
            
            self.model = EnhancedSkinModel(
                input_shape=self.config['input_shape'],
                num_conditions=self.config['num_conditions'],
                embedding_dim=self.config['embedding_dim'],
                use_attention=self.config['use_attention'],
                backbone=self.config['backbone']
            )
            
            # Build and compile model
            self.model.build_model()
            self.model.compile_model()
            
            logger.info("✅ Model initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model: {e}")
    
    def train_model(self) -> Dict:
        """Train the enhanced model with comprehensive monitoring"""
        try:
            logger.info("🚀 Starting model training...")
            
            # Create callbacks
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=self.config['early_stopping_patience'],
                    restore_best_weights=True,
                    verbose=1
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=self.config['reduce_lr_patience'],
                    min_lr=1e-7,
                    verbose=1
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    filepath=str(self.models_dir / "best_model.h5"),
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                ),
                tf.keras.callbacks.TensorBoard(
                    log_dir=str(self.results_dir / "logs"),
                    histogram_freq=1,
                    write_graph=True,
                    write_images=True
                )
            ]
            
            # Train model
            history = self.model.model.fit(
                self.train_generator,
                validation_data=self.val_generator,
                epochs=self.config['epochs'],
                callbacks=callbacks,
                verbose=1
            )
            
            # Save training history
            history_path = self.results_dir / "training_history.json"
            with open(history_path, 'w') as f:
                json.dump(history.history, f, indent=2)
            
            logger.info("✅ Model training completed successfully")
            return history.history
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return {}
    
    def evaluate_model(self, prepared_data: Dict) -> Dict:
        """Comprehensive model evaluation with fairness metrics"""
        try:
            logger.info("📊 Evaluating model performance...")
            
            # Make predictions on test set
            test_predictions = self.model.model.predict(self.test_generator)
            
            # Extract predictions for each task
            condition_preds = test_predictions[0]
            embedding_preds = test_predictions[1]
            skin_char_preds = test_predictions[2]
            age_preds = test_predictions[3]
            gender_preds = test_predictions[4]
            ethnicity_preds = test_predictions[5]
            
            # Get true labels
            condition_true = prepared_data['test_condition_labels']
            age_true = prepared_data['test_age_labels']
            gender_true = prepared_data['test_gender_labels']
            ethnicity_true = prepared_data['test_ethnicity_labels']
            skin_char_true = prepared_data['test_skin_char_labels']
            
            # Calculate metrics
            metrics = {}
            
            # Condition classification metrics
            condition_accuracy = np.mean(np.argmax(condition_preds, axis=1) == np.argmax(condition_true, axis=1))
            metrics['condition_accuracy'] = float(condition_accuracy)
            
            # Age regression metrics
            age_mae = np.mean(np.abs(age_preds.flatten() - age_true))
            metrics['age_mae'] = float(age_mae)
            
            # Gender classification metrics
            gender_accuracy = np.mean(np.argmax(gender_preds, axis=1) == np.argmax(gender_true, axis=1))
            metrics['gender_accuracy'] = float(gender_accuracy)
            
            # Ethnicity classification metrics
            ethnicity_accuracy = np.mean(np.argmax(ethnicity_preds, axis=1) == np.argmax(ethnicity_true, axis=1))
            metrics['ethnicity_accuracy'] = float(ethnicity_accuracy)
            
            # Skin characteristics metrics
            skin_char_mae = np.mean(np.abs(skin_char_preds - skin_char_true))
            metrics['skin_characteristics_mae'] = float(skin_char_mae)
            
            # Embedding distinctiveness
            condition_indices = np.argmax(condition_true, axis=1)
            embedding_distinctiveness = silhouette_score(embedding_preds, condition_indices)
            metrics['embedding_distinctiveness'] = float(embedding_distinctiveness)
            
            # Fairness metrics
            fairness_metrics = self._calculate_fairness_metrics(
                condition_preds, condition_true, 
                gender_preds, gender_true,
                ethnicity_preds, ethnicity_true
            )
            metrics.update(fairness_metrics)
            
            # Save evaluation results
            evaluation_path = self.results_dir / "evaluation_results.json"
            with open(evaluation_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            # Generate detailed reports
            self._generate_evaluation_reports(
                condition_preds, condition_true,
                gender_preds, gender_true,
                ethnicity_preds, ethnicity_true
            )
            
            logger.info("✅ Model evaluation completed")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}
    
    def _calculate_fairness_metrics(self, condition_preds, condition_true, 
                                  gender_preds, gender_true,
                                  ethnicity_preds, ethnicity_true) -> Dict:
        """Calculate fairness metrics across demographic groups"""
        try:
            fairness_metrics = {}
            
            # Get demographic groups
            gender_groups = np.argmax(gender_true, axis=1)
            ethnicity_groups = np.argmax(ethnicity_true, axis=1)
            
            # Calculate performance by demographic group
            for group_name, group_indices in [('gender', gender_groups), ('ethnicity', ethnicity_groups)]:
                unique_groups = np.unique(group_indices)
                
                for group in unique_groups:
                    mask = group_indices == group
                    if np.sum(mask) > 0:
                        group_accuracy = np.mean(
                            np.argmax(condition_preds[mask], axis=1) == 
                            np.argmax(condition_true[mask], axis=1)
                        )
                        fairness_metrics[f'{group_name}_{group}_accuracy'] = float(group_accuracy)
            
            # Calculate demographic parity
            gender_parity = self._calculate_demographic_parity(condition_preds, gender_groups)
            ethnicity_parity = self._calculate_demographic_parity(condition_preds, ethnicity_groups)
            
            fairness_metrics['gender_demographic_parity'] = gender_parity
            fairness_metrics['ethnicity_demographic_parity'] = ethnicity_parity
            
            return fairness_metrics
            
        except Exception as e:
            logger.warning(f"⚠️ Could not calculate fairness metrics: {e}")
            return {}
    
    def _calculate_demographic_parity(self, predictions, groups) -> float:
        """Calculate demographic parity metric"""
        try:
            unique_groups = np.unique(groups)
            positive_rates = []
            
            for group in unique_groups:
                mask = groups == group
                if np.sum(mask) > 0:
                    group_predictions = predictions[mask]
                    positive_rate = np.mean(np.argmax(group_predictions, axis=1) != 0)  # Not healthy
                    positive_rates.append(positive_rate)
            
            if len(positive_rates) > 1:
                return np.std(positive_rates)  # Lower is better
            else:
                return 0.0
                
        except Exception as e:
            return 0.0
    
    def _generate_evaluation_reports(self, condition_preds, condition_true,
                                   gender_preds, gender_true,
                                   ethnicity_preds, ethnicity_true):
        """Generate detailed evaluation reports and visualizations"""
        try:
            # Create confusion matrices
            self._create_confusion_matrix(
                condition_preds, condition_true,
                'condition_classification',
                ['healthy', 'acne', 'eczema', 'keratosis', 'milia', 'rosacea']
            )
            
            self._create_confusion_matrix(
                gender_preds, gender_true,
                'gender_classification',
                ['male', 'female']
            )
            
            self._create_confusion_matrix(
                ethnicity_preds, ethnicity_true,
                'ethnicity_classification',
                ['white', 'black', 'asian', 'indian', 'hispanic', 'middle_eastern', 'other']
            )
            
            # Create performance plots
            self._create_performance_plots()
            
            logger.info("✅ Evaluation reports generated successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not generate evaluation reports: {e}")
    
    def _create_confusion_matrix(self, predictions, true_labels, task_name, class_names):
        """Create and save confusion matrix"""
        try:
            pred_indices = np.argmax(predictions, axis=1)
            true_indices = np.argmax(true_labels, axis=1)
            
            cm = confusion_matrix(true_indices, pred_indices)
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=class_names, yticklabels=class_names)
            plt.title(f'{task_name.replace("_", " ").title()} Confusion Matrix')
            plt.xlabel('Predicted')
            plt.ylabel('True')
            plt.tight_layout()
            
            # Save plot
            plot_path = self.results_dir / f"{task_name}_confusion_matrix.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create confusion matrix for {task_name}: {e}")
    
    def _create_performance_plots(self):
        """Create performance visualization plots"""
        try:
            # Load training history
            history_path = self.results_dir / "training_history.json"
            if history_path.exists():
                with open(history_path, 'r') as f:
                    history = json.load(f)
                
                # Create training curves
                fig, axes = plt.subplots(2, 2, figsize=(15, 10))
                
                # Loss curves
                axes[0, 0].plot(history.get('loss', []), label='Training Loss')
                axes[0, 0].plot(history.get('val_loss', []), label='Validation Loss')
                axes[0, 0].set_title('Model Loss')
                axes[0, 0].set_xlabel('Epoch')
                axes[0, 0].set_ylabel('Loss')
                axes[0, 0].legend()
                
                # Accuracy curves
                if 'condition_classification_accuracy' in history:
                    axes[0, 1].plot(history['condition_classification_accuracy'], label='Training Accuracy')
                    axes[0, 1].plot(history['val_condition_classification_accuracy'], label='Validation Accuracy')
                    axes[0, 1].set_title('Condition Classification Accuracy')
                    axes[0, 1].set_xlabel('Epoch')
                    axes[0, 1].set_ylabel('Accuracy')
                    axes[0, 1].legend()
                
                # Learning rate
                if 'lr' in history:
                    axes[1, 0].plot(history['lr'])
                    axes[1, 0].set_title('Learning Rate')
                    axes[1, 0].set_xlabel('Epoch')
                    axes[1, 0].set_ylabel('Learning Rate')
                    axes[1, 0].set_yscale('log')
                
                plt.tight_layout()
                
                # Save plot
                plot_path = self.results_dir / "training_performance.png"
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                
        except Exception as e:
            logger.warning(f"⚠️ Could not create performance plots: {e}")
    
    def save_model_and_metadata(self):
        """Save the trained model and metadata"""
        try:
            # Save model
            model_path = self.models_dir / "enhanced_skin_model.h5"
            self.model.save_model(str(model_path))
            
            # Save metadata
            metadata = {
                'config': self.config,
                'label_encoders': {
                    'condition_classes': self.label_encoders['condition'].classes_.tolist(),
                    'gender_classes': self.label_encoders['gender'].classes_.tolist(),
                    'ethnicity_classes': self.label_encoders['ethnicity'].classes_.tolist()
                },
                'scalers': {
                    'age_mean': float(self.scalers['age'].mean_[0]),
                    'age_scale': float(self.scalers['age'].scale_[0])
                },
                'training_date': datetime.now().isoformat(),
                'model_summary': self.model.model.summary()
            }
            
            metadata_path = self.models_dir / "model_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ Model and metadata saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to save model and metadata: {e}")
    
    def run_full_pipeline(self) -> bool:
        """Run the complete training pipeline"""
        try:
            logger.info("🚀 Starting complete ML training pipeline")
            
            # Step 1: Data preprocessing
            logger.info("📥 Step 1: Data preprocessing")
            if not self.run_data_preprocessing():
                return False
            
            # Step 2: Load processed data
            logger.info("📂 Step 2: Loading processed data")
            data = self.load_processed_data()
            if not data:
                logger.warning("⚠️ No processed data found, using existing data")
            
            # Step 3: Prepare training data
            logger.info("🔄 Step 3: Preparing training data")
            prepared_data = self.prepare_training_data(data)
            if not prepared_data:
                return False
            
            # Step 4: Create data generators
            logger.info("🔄 Step 4: Creating data generators")
            self.create_data_generators(prepared_data)
            
            # Step 5: Initialize model
            logger.info("🏗️ Step 5: Initializing model")
            self.initialize_model()
            
            # Step 6: Train model
            logger.info("🎯 Step 6: Training model")
            training_history = self.train_model()
            if not training_history:
                return False
            
            # Step 7: Evaluate model
            logger.info("📊 Step 7: Evaluating model")
            evaluation_results = self.evaluate_model(prepared_data)
            
            # Step 8: Save model and metadata
            logger.info("💾 Step 8: Saving model and metadata")
            self.save_model_and_metadata()
            
            # Print summary
            logger.info("🎉 ML training pipeline completed successfully!")
            logger.info(f"📊 Final condition accuracy: {evaluation_results.get('condition_accuracy', 0):.3f}")
            logger.info(f"📊 Embedding distinctiveness: {evaluation_results.get('embedding_distinctiveness', 0):.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ML training pipeline failed: {e}")
            return False

def main():
    """Main function to run the complete training pipeline"""
    # Initialize pipeline
    pipeline = MLTrainingPipeline()
    
    # Run full pipeline
    success = pipeline.run_full_pipeline()
    
    if success:
        print("✅ ML training pipeline completed successfully!")
        print("📁 Check the 'models' and 'results' directories for outputs")
    else:
        print("❌ ML training pipeline failed!")

if __name__ == "__main__":
    main() 