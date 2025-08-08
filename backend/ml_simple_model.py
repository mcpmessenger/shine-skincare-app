#!/usr/bin/env python3
"""
Simple ML Model for Shine Skincare App
Simplified model focusing on condition classification only
"""

import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, optimizers, callbacks
from tensorflow.keras.applications import ResNet50
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSkinModel:
    """Simple skin condition classification model"""
    
    def __init__(self, 
                 input_shape: Tuple[int, int, int] = (224, 224, 3),
                 num_conditions: int = 6):
        """
        Initialize the simple skin model
        
        Args:
            input_shape: Input image shape (height, width, channels)
            num_conditions: Number of skin conditions to classify
        """
        self.input_shape = input_shape
        self.num_conditions = num_conditions
        self.model = None
        
        # Training parameters
        self.learning_rate = 1e-4
        self.batch_size = 16
        self.epochs = 20
        
        logger.info("✅ Simple Skin Model initialized")
    
    def build_model(self) -> keras.Model:
        """Build the simple classification model"""
        # Input layer
        input_layer = layers.Input(shape=self.input_shape, name='input_image')
        
        # Pre-trained ResNet50 backbone
        backbone = ResNet50(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        # Freeze early layers for transfer learning
        for layer in backbone.layers[:-20]:
            layer.trainable = False
        
        # Add classification head
        x = backbone(input_layer)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation='relu')(x)
        output = layers.Dense(self.num_conditions, activation='softmax', name='condition_classification')(x)
        
        # Create model
        self.model = keras.Model(inputs=input_layer, outputs=output, name='simple_skin_model')
        
        logger.info("✅ Simple skin model built successfully")
        return self.model
    
    def compile_model(self):
        """Compile the model"""
        # Optimizer
        optimizer = optimizers.Adam(learning_rate=self.learning_rate)
        
        # Compile model
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        logger.info("✅ Model compiled successfully")
    
    def train_model(self, train_data: np.ndarray, train_labels: np.ndarray,
                   val_data: np.ndarray, val_labels: np.ndarray,
                   model_save_path: str = "models"):
        """Train the simple model"""
        try:
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
                    filepath=f"{model_save_path}/simple_skin_model.h5",
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train model
            logger.info("🚀 Starting model training...")
            history = self.model.fit(
                train_data,
                train_labels,
                validation_data=(val_data, val_labels),
                epochs=self.epochs,
                batch_size=self.batch_size,
                callbacks=callbacks_list,
                verbose=1
            )
            
            logger.info("✅ Model training completed successfully")
            return history
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return None
    
    def evaluate_model(self, test_data: np.ndarray, test_labels: np.ndarray) -> Dict:
        """Evaluate the trained model"""
        try:
            logger.info("📊 Evaluating model performance...")
            
            # Make predictions
            predictions = self.model.predict(test_data)
            
            # Calculate accuracy
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(test_labels, axis=1))
            
            # Calculate per-condition accuracy
            condition_names = ['healthy', 'acne', 'eczema', 'keratosis', 'basal_cell_carcinoma', 'rosacea']
            per_condition_accuracy = {}
            
            for i, condition in enumerate(condition_names):
                condition_mask = np.argmax(test_labels, axis=1) == i
                if np.sum(condition_mask) > 0:
                    condition_acc = np.mean(
                        np.argmax(predictions[condition_mask], axis=1) == i
                    )
                    per_condition_accuracy[condition] = condition_acc
            
            metrics = {
                'overall_accuracy': float(accuracy),
                'per_condition_accuracy': per_condition_accuracy,
                'test_samples': len(test_data)
            }
            
            logger.info(f"✅ Model evaluation completed:")
            logger.info(f"   Overall accuracy: {accuracy:.3f}")
            for condition, acc in per_condition_accuracy.items():
                logger.info(f"   {condition}: {acc:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}
    
    def predict(self, test_data: np.ndarray) -> np.ndarray:
        """Make predictions on test data"""
        try:
            return self.model.predict(test_data)
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return None
    
    def predict_single_image(self, image_path: str) -> Dict:
        """Predict on a single image"""
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            image = cv2.resize(image, (self.input_shape[0], self.input_shape[1]))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = image.astype(np.float32) / 255.0
            image = np.expand_dims(image, axis=0)
            
            # Make prediction
            prediction = self.model.predict(image)
            
            # Decode prediction
            condition_names = ['healthy', 'acne', 'eczema', 'keratosis', 'basal_cell_carcinoma', 'rosacea']
            condition_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][condition_idx])
            
            result = {
                'condition': condition_names[condition_idx],
                'confidence': confidence,
                'all_probabilities': prediction[0].tolist()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return {}
    
    def save_model(self, model_path: str = "models/simple_skin_model.h5"):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            self.model.save(model_path)
            logger.info(f"✅ Model saved to {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False
    
    def load_model(self, model_path: str = "models/simple_skin_model.h5"):
        """Load a trained model"""
        try:
            self.model = keras.models.load_model(model_path)
            logger.info(f"✅ Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

def main():
    """Main function to demonstrate simple model usage"""
    # Initialize model
    model = SimpleSkinModel(
        input_shape=(224, 224, 3),
        num_conditions=6
    )
    
    # Build and compile model
    model.build_model()
    model.compile_model()
    
    # Print model summary
    model.model.summary()
    
    print("✅ Simple ML model created successfully!")

if __name__ == "__main__":
    main() 