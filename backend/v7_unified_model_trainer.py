#!/usr/bin/env python3
"""
V7 Unified Model Trainer
Real training pipeline with CLI logging and dashboard integration
"""

import os
import json
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tqdm import tqdm

class V7UnifiedModelTrainer:
    """V7 Unified Model Trainer with multi-task learning"""
    
    def __init__(self, dataset_dir="./v7_cleaned_features", output_dir="./v7_unified_model"):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Training configuration
        self.config = {
            'batch_size': 32,
            'epochs': 100,
            'learning_rate': 0.001,
            'validation_split': 0.2,
            'test_split': 0.1,
            'feature_dim': 1296,  # Updated to match cleaned dataset
            'dropout_rate': 0.3,
            'patience': 15
        }
        
        # Model components
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Training data
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = {}
        self.y_val = {}
        self.y_test = {}
        
        # Training history
        self.training_history = {
            'epochs': [],
            'loss': {'train': [], 'val': []},
            'accuracy': {'train': [], 'val': []},
            'skin_condition_accuracy': [],
            'age_accuracy': [],
            'ethnicity_accuracy': [],
            'gender_accuracy': [],
            'learning_rate': [],
            'training_start_time': None,
            'training_end_time': None
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = self.output_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"v7_training_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("V7 Unified Model Trainer initialized")
        self.logger.info(f"Dataset: {self.dataset_dir}")
        self.logger.info(f"Output: {self.output_dir}")
        self.logger.info(f"Log file: {log_file}")
    
    def load_dataset(self):
        """Load the unified V7 dataset"""
        self.logger.info("Loading V7 unified dataset...")
        
        # Load training manifest
        manifest_path = self.dataset_dir / "v7_cleaned_manifest.csv"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Training manifest not found: {manifest_path}")
            
        self.manifest = pd.read_csv(manifest_path)
        self.logger.info(f"Loaded manifest with {len(self.manifest)} samples")
        
        # Load features
        features_dir = self.dataset_dir / "features"
        if not features_dir.exists():
            raise FileNotFoundError(f"Features directory not found: {features_dir}")
            
        # List feature files
        feature_files = list(features_dir.glob("*.json"))
        self.logger.info(f"Found {len(feature_files)} feature files")
        
        if len(feature_files) == 0:
            raise ValueError("❌ No feature files found! Check if the features directory exists and contains feature files.")
        
        # Load features and labels
        features_list = []
        labels_condition = []
        labels_age = []
        labels_gender = []
        labels_ethnicity = []
        
        for _, row in tqdm(self.manifest.iterrows(), desc="Loading features", total=len(self.manifest)):
            try:
                sample_id = row['sample_id']
                
                # In our cleaned dataset, all feature files are named consistently
                feature_file = features_dir / f"{sample_id}_cleaned_features.json"
                
                if not feature_file.exists():
                    self.logger.warning(f"Feature file not found: {feature_file}")
                    continue
                
                # Load features
                with open(feature_file, 'r') as f:
                    feature_data = json.load(f)
                
                # Extract features from cleaned dataset
                if 'features' in feature_data:
                    features = feature_data['features']
                else:
                    self.logger.warning(f"No features found in {feature_file}")
                    continue
                
                # Convert to numpy array and ensure it's 1D
                features = np.array(features).flatten()
                
                # All features should already be the same length (1,296) from our cleaning
                features_list.append(features)
                labels_condition.append(row['condition'])
                labels_age.append(row['age_group'])
                labels_gender.append(row['gender'])
                labels_ethnicity.append(row['ethnicity'])
                
            except Exception as e:
                self.logger.error(f"Error loading features for sample {sample_id}: {e}")
                continue
        
        if len(features_list) == 0:
            raise ValueError("❌ No features loaded successfully!")
        
        # All features should now have the same length after padding
        feature_lengths = [len(f) for f in features_list]
        unique_lengths = set(feature_lengths)
        self.logger.info(f"Feature lengths after padding: {unique_lengths}")
        
        if len(unique_lengths) > 1:
            self.logger.error(f"❌ Still have inconsistent feature lengths after padding: {unique_lengths}")
            raise ValueError(f"❌ Padding failed. Found: {unique_lengths}")
        
        # Convert to numpy arrays
        self.X = np.array(features_list)
        actual_feature_dim = self.X.shape[1]
        self.config['feature_dim'] = actual_feature_dim
        self.logger.info(f"Loaded {len(self.X)} samples with {actual_feature_dim} features each")
        self.logger.info(f"Updated feature dimension to {actual_feature_dim}")
        
        # Prepare labels
        self.prepare_labels(labels_condition, labels_age, labels_gender, labels_ethnicity)
        
        # Split dataset
        self.split_dataset()
        
        self.logger.info("Dataset loading completed successfully!")
        return True
    
    def prepare_labels(self, condition_labels, age_labels, gender_labels, ethnicity_labels):
        """Prepare labels for multi-task learning"""
        self.logger.info("Preparing multi-task labels...")
        
        # Task 1: Skin Condition Classification
        skin_conditions = pd.Series(condition_labels).fillna('unknown')
        unique_conditions = skin_conditions.unique()
        self.logger.info(f"Skin conditions: {len(unique_conditions)} classes")
        
        self.label_encoders['condition'] = LabelEncoder()
        self.y_condition = self.label_encoders['condition'].fit_transform(skin_conditions)
        
        # Task 2: Age Group Classification
        age_groups = pd.Series(age_labels).fillna('unknown')
        unique_ages = age_groups.unique()
        self.logger.info(f"Age groups: {len(unique_ages)} classes")
        
        self.label_encoders['age_group'] = LabelEncoder()
        self.y_age = self.label_encoders['age_group'].fit_transform(age_groups)
        
        # Task 3: Ethnicity Classification
        ethnicities = pd.Series(ethnicity_labels).fillna('unknown')
        unique_ethnicities = ethnicities.unique()
        self.logger.info(f"Ethnicities: {len(unique_ethnicities)} classes")
        
        self.label_encoders['ethnicity'] = LabelEncoder()
        self.y_ethnicity = self.label_encoders['ethnicity'].fit_transform(ethnicities)
        
        # Task 4: Gender Classification
        genders = pd.Series(gender_labels).fillna('unknown')
        unique_genders = genders.unique()
        self.logger.info(f"Genders: {len(unique_genders)} classes")
        
        self.label_encoders['gender'] = LabelEncoder()
        self.y_gender = self.label_encoders['gender'].fit_transform(genders)
        
        # Store number of classes for each task
        self.num_classes = {
            'condition': len(unique_conditions),
            'age_group': len(unique_ages),
            'ethnicity': len(unique_ethnicities),
            'gender': len(unique_genders)
        }
        
        self.logger.info(f"Multi-task setup: {self.num_classes}")
    
    def split_dataset(self):
        """Split dataset into train/validation/test sets"""
        self.logger.info("Splitting dataset...")
        
        # First split: separate test set
        X_temp, self.X_test, y_condition_temp, y_condition_test, y_age_temp, y_age_test, \
        y_ethnicity_temp, y_ethnicity_test, y_gender_temp, y_gender_test = train_test_split(
            self.X, self.y_condition, self.y_age, self.y_ethnicity, self.y_gender,
            test_size=self.config['test_split'], random_state=42, stratify=self.y_condition
        )
        
        # Second split: train/validation
        self.X_train, self.X_val, y_condition_train, y_condition_val, y_age_train, y_age_val, \
        y_ethnicity_train, y_ethnicity_val, y_gender_train, y_gender_val = train_test_split(
            X_temp, y_condition_temp, y_age_temp, y_ethnicity_temp, y_gender_temp,
            test_size=self.config['validation_split'], random_state=42, stratify=y_condition_temp
        )
        
        # Store labels
        self.y_train = {
            'condition': y_condition_train,
            'age_group': y_age_train,
            'ethnicity': y_ethnicity_train,
            'gender': y_gender_train
        }
        
        self.y_val = {
            'condition': y_condition_val,
            'age_group': y_age_val,
            'ethnicity': y_ethnicity_val,
            'gender': y_gender_val
        }
        
        self.y_test = {
            'condition': y_condition_test,
            'age_group': y_age_test,
            'ethnicity': y_ethnicity_test,
            'gender': y_gender_test
        }
        
        self.logger.info(f"Train: {len(self.X_train):,} samples")
        self.logger.info(f"Validation: {len(self.X_val):,} samples")
        self.logger.info(f"Test: {len(self.X_test):,} samples")
        
        # Normalize features
        self.logger.info("Normalizing features...")
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_val = self.scaler.transform(self.X_val)
        self.X_test = self.scaler.transform(self.X_test)
    
    def build_model(self):
        """Build multi-task neural network"""
        self.logger.info("Building V7 unified model architecture...")
        
        # Input layer
        input_layer = Input(shape=(self.X_train.shape[1],), name='features_input')
        
        # Shared layers
        x = Dense(1024, activation='relu', name='shared_dense_1')(input_layer)
        x = BatchNormalization(name='shared_bn_1')(x)
        x = Dropout(self.config['dropout_rate'], name='shared_dropout_1')(x)
        
        x = Dense(512, activation='relu', name='shared_dense_2')(x)
        x = BatchNormalization(name='shared_bn_2')(x)
        x = Dropout(self.config['dropout_rate'], name='shared_dropout_2')(x)
        
        x = Dense(256, activation='relu', name='shared_dense_3')(x)
        x = BatchNormalization(name='shared_bn_3')(x)
        x = Dropout(self.config['dropout_rate'], name='shared_dropout_3')(x)
        
        # Task-specific heads
        # Skin Condition Head
        condition_head = Dense(128, activation='relu', name='condition_dense')(x)
        condition_head = Dropout(0.2, name='condition_dropout')(condition_head)
        condition_output = Dense(self.num_classes['condition'], activation='softmax', name='condition_output')(condition_head)
        
        # Age Group Head
        age_head = Dense(64, activation='relu', name='age_dense')(x)
        age_head = Dropout(0.2, name='age_dropout')(age_head)
        age_output = Dense(self.num_classes['age_group'], activation='softmax', name='age_output')(age_head)
        
        # Ethnicity Head
        ethnicity_head = Dense(64, activation='relu', name='ethnicity_dense')(x)
        ethnicity_head = Dropout(0.2, name='ethnicity_dropout')(ethnicity_head)
        ethnicity_output = Dense(self.num_classes['ethnicity'], activation='softmax', name='ethnicity_output')(ethnicity_head)
        
        # Gender Head
        gender_head = Dense(32, activation='relu', name='gender_dense')(x)
        gender_head = Dropout(0.2, name='gender_dropout')(gender_head)
        gender_output = Dense(self.num_classes['gender'], activation='softmax', name='gender_output')(gender_head)
        
        # Create model
        self.model = Model(
            inputs=input_layer,
            outputs=[condition_output, age_output, ethnicity_output, gender_output],
            name='V7_Unified_Model'
        )
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss={
                'condition_output': 'sparse_categorical_crossentropy',
                'age_output': 'sparse_categorical_crossentropy',
                'ethnicity_output': 'sparse_categorical_crossentropy',
                'gender_output': 'sparse_categorical_crossentropy'
            },
            loss_weights={
                'condition_output': 1.0,  # Primary task
                'age_output': 0.8,
                'ethnicity_output': 0.6,
                'gender_output': 0.7
            },
            metrics=['accuracy']
        )
        
        self.logger.info("✅ Model architecture built successfully")
        self.logger.info(f"Total parameters: {self.model.count_params():,}")
        
        return self.model
    
    def train_model(self):
        """Train the V7 unified model"""
        self.logger.info("Starting V7 unified model training...")
        self.training_history['training_start_time'] = datetime.now()
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=self.config['patience'],
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=str(self.output_dir / 'best_model.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train model
        history = self.model.fit(
            self.X_train,
            {
                'condition_output': self.y_train['condition'],
                'age_output': self.y_train['age_group'],
                'ethnicity_output': self.y_train['ethnicity'],
                'gender_output': self.y_train['gender']
            },
            validation_data=(
                self.X_val,
                {
                    'condition_output': self.y_val['condition'],
                    'age_output': self.y_val['age_group'],
                    'ethnicity_output': self.y_val['ethnicity'],
                    'gender_output': self.y_val['gender']
                }
            ),
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            callbacks=callbacks,
            verbose=1
        )
        
        self.training_history['training_end_time'] = datetime.now()
        
        # Store training history
        for epoch in range(len(history.history['loss'])):
            self.training_history['epochs'].append(epoch + 1)
            self.training_history['loss']['train'].append(history.history['loss'][epoch])
            self.training_history['loss']['val'].append(history.history['val_loss'][epoch])
            
            # Calculate average accuracy across tasks
            train_acc = np.mean([
                history.history['condition_output_accuracy'][epoch],
                history.history['age_output_accuracy'][epoch],
                history.history['ethnicity_output_accuracy'][epoch],
                history.history['gender_output_accuracy'][epoch]
            ])
            val_acc = np.mean([
                history.history['val_condition_output_accuracy'][epoch],
                history.history['val_age_output_accuracy'][epoch],
                history.history['val_ethnicity_output_accuracy'][epoch],
                history.history['val_gender_output_accuracy'][epoch]
            ])
            
            self.training_history['accuracy']['train'].append(train_acc * 100)
            self.training_history['accuracy']['val'].append(val_acc * 100)
            
            # Individual task accuracies
            self.training_history['skin_condition_accuracy'].append(
                history.history['val_condition_output_accuracy'][epoch] * 100
            )
            self.training_history['age_accuracy'].append(
                history.history['val_age_output_accuracy'][epoch] * 100
            )
            self.training_history['ethnicity_accuracy'].append(
                history.history['val_ethnicity_output_accuracy'][epoch] * 100
            )
            self.training_history['gender_accuracy'].append(
                history.history['val_gender_output_accuracy'][epoch] * 100
            )
        
        self.logger.info("✅ Training completed successfully!")
        
        return history
    
    def train_model_with_callback(self, callback_func):
        """Train the V7 unified model with custom callback for real-time updates"""
        self.logger.info("Starting V7 unified model training with callback...")
        self.training_history['training_start_time'] = datetime.now()
        
        # Custom callback for real-time updates
        class RealTimeCallback(tf.keras.callbacks.Callback):
            def __init__(self, callback_func):
                super().__init__()
                self.callback_func = callback_func
            
            def on_epoch_end(self, epoch, logs=None):
                if self.callback_func:
                    self.callback_func(epoch, logs)
        
        # Callbacks
        callbacks = [
            RealTimeCallback(callback_func),
            EarlyStopping(
                monitor='val_loss',
                patience=self.config['patience'],
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=str(self.output_dir / 'best_model.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train model
        history = self.model.fit(
            self.X_train,
            {
                'condition_output': self.y_train['condition'],
                'age_output': self.y_train['age_group'],
                'ethnicity_output': self.y_train['ethnicity'],
                'gender_output': self.y_train['gender']
            },
            validation_data=(
                self.X_val,
                {
                    'condition_output': self.y_val['condition'],
                    'age_output': self.y_val['age_group'],
                    'ethnicity_output': self.y_val['ethnicity'],
                    'gender_output': self.y_val['gender']
                }
            ),
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            callbacks=callbacks,
            verbose=1
        )
        
        self.training_history['training_end_time'] = datetime.now()
        self.logger.info("✅ Training completed successfully!")
        
        return history
    
    def evaluate_model(self):
        """Evaluate model on test set"""
        self.logger.info("Evaluating model on test set...")
        
        # Make predictions
        predictions = self.model.predict(self.X_test)
        
        # Calculate accuracies for each task
        results = {}
        task_names = ['condition', 'age_group', 'ethnicity', 'gender']
        
        for i, task in enumerate(task_names):
            y_pred = np.argmax(predictions[i], axis=1)
            y_true = self.y_test[task]
            
            accuracy = np.mean(y_pred == y_true)
            results[task] = {
                'accuracy': accuracy,
                'predictions': y_pred,
                'true_labels': y_true
            }
            
            self.logger.info(f"{task.title()} Accuracy: {accuracy:.3f}")
        
        # Save evaluation results
        eval_results = {
            'test_accuracies': {task: results[task]['accuracy'] for task in task_names},
            'evaluation_time': datetime.now().isoformat(),
            'test_samples': len(self.X_test)
        }
        
        with open(self.output_dir / 'evaluation_results.json', 'w') as f:
            json.dump(eval_results, f, indent=2)
        
        return results
    
    def save_model_artifacts(self):
        """Save all model artifacts"""
        self.logger.info("Saving model artifacts...")
        
        # Save final model
        self.model.save(self.output_dir / 'final_model.h5')
        
        # Save scaler
        import joblib
        joblib.dump(self.scaler, self.output_dir / 'feature_scaler.pkl')
        
        # Save label encoders
        encoders_path = self.output_dir / 'label_encoders.pkl'
        joblib.dump(self.label_encoders, encoders_path)
        
        # Save training history
        history_path = self.output_dir / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(self.training_history, f, indent=2, default=str)
        
        # Save configuration
        config_path = self.output_dir / 'training_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.logger.info("All artifacts saved successfully!")
    
    def run_complete_training(self):
        """Run the complete training pipeline"""
        try:
            self.logger.info("Starting V7 Unified Model Training Pipeline")
            
            # Load dataset
            self.load_dataset()
            
            # Build model
            self.build_model()
            
            # Train model
            self.train_model()
            
            # Evaluate model
            self.evaluate_model()
            
            # Save artifacts
            self.save_model_artifacts()
            
            training_time = self.training_history['training_end_time'] - self.training_history['training_start_time']
            self.logger.info(f"Training pipeline completed in {training_time}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise e

def main():
    """Main training function"""
    print("V7 Unified Model Trainer")
    print("=" * 50)
    
    # Initialize trainer
    trainer = V7UnifiedModelTrainer()
    
    # Run training
    success = trainer.run_complete_training()
    
    if success:
        print("\nTraining completed successfully!")
        print(f"Results saved to: {trainer.output_dir}")
        print(f"Training history: {trainer.output_dir}/training_history.json")
        print(f"Model: {trainer.output_dir}/final_model.h5")
    else:
        print("\nTraining failed!")

if __name__ == '__main__':
    main()
