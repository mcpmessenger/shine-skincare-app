#!/usr/bin/env python3
"""
Enhanced ML Model Architecture for Shine Skincare App
Implements multi-task learning with CNN backbone, attention mechanisms, and specialized heads
"""

import os
import json
import logging
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, losses, metrics
from tensorflow.keras.applications import ResNet50, EfficientNetB4
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SqueezeExcitationBlock(layers.Layer):
    """Squeeze-and-Excitation block for channel attention"""
    
    def __init__(self, ratio=16, **kwargs):
        super(SqueezeExcitationBlock, self).__init__(**kwargs)
        self.ratio = ratio
    
    def build(self, input_shape):
        self.channels = input_shape[-1]
        self.squeeze = layers.GlobalAveragePooling2D()
        self.excitation = keras.Sequential([
            layers.Dense(self.channels // self.ratio, activation='relu'),
            layers.Dense(self.channels, activation='sigmoid')
        ])
    
    def call(self, inputs):
        x = self.squeeze(inputs)
        x = self.excitation(x)
        x = tf.expand_dims(tf.expand_dims(x, 1), 1)
        return inputs * x

class ConvolutionalBlockAttentionModule(layers.Layer):
    """Convolutional Block Attention Module (CBAM)"""
    
    def __init__(self, reduction_ratio=16, **kwargs):
        super(ConvolutionalBlockAttentionModule, self).__init__(**kwargs)
        self.reduction_ratio = reduction_ratio
    
    def build(self, input_shape):
        self.channels = input_shape[-1]
        
        # Channel attention
        self.channel_avg_pool = layers.GlobalAveragePooling2D()
        self.channel_max_pool = layers.GlobalMaxPooling2D()
        self.channel_fc = keras.Sequential([
            layers.Dense(self.channels // self.reduction_ratio, activation='relu'),
            layers.Dense(self.channels, activation='sigmoid')
        ])
        
        # Spatial attention
        self.spatial_conv = layers.Conv2D(1, kernel_size=7, padding='same', activation='sigmoid')
    
    def call(self, inputs):
        # Channel attention
        avg_pool = self.channel_avg_pool(inputs)
        max_pool = self.channel_max_pool(inputs)
        
        avg_out = self.channel_fc(avg_pool)
        max_out = self.channel_fc(max_pool)
        
        channel_out = avg_out + max_out
        channel_out = tf.expand_dims(tf.expand_dims(channel_out, 1), 1)
        
        # Apply channel attention
        x = inputs * channel_out
        
        # Spatial attention
        avg_pool = tf.reduce_mean(x, axis=-1, keepdims=True)
        max_pool = tf.reduce_max(x, axis=-1, keepdims=True)
        spatial_input = tf.concat([avg_pool, max_pool], axis=-1)
        spatial_out = self.spatial_conv(spatial_input)
        
        return x * spatial_out

class EnhancedSkinModel:
    """Enhanced multi-task learning model for skin analysis"""
    
    def __init__(self, 
                 input_shape: Tuple[int, int, int] = (224, 224, 3),
                 num_conditions: int = 6,
                 embedding_dim: int = 2048,
                 use_attention: bool = True,
                 backbone: str = 'resnet50'):
        """
        Initialize the enhanced skin analysis model
        
        Args:
            input_shape: Input image shape (height, width, channels)
            num_conditions: Number of skin conditions to classify
            embedding_dim: Dimension of the embedding vector
            use_attention: Whether to use attention mechanisms
            backbone: CNN backbone ('resnet50' or 'efficientnet')
        """
        self.input_shape = input_shape
        self.num_conditions = num_conditions
        self.embedding_dim = embedding_dim
        self.use_attention = use_attention
        self.backbone_name = backbone
        
        # Model components
        self.backbone = None
        self.model = None
        self.condition_encoder = None
        self.demographic_encoder = None
        
        # Training parameters
        self.learning_rate = 1e-4
        self.batch_size = 32
        self.epochs = 100
        
        # Loss weights for multi-task learning
        self.loss_weights = {
            'condition_classification': 1.0,
            'age_regression': 0.5,
            'gender_classification': 0.3,
            'ethnicity_classification': 0.3,
            'skin_characteristics': 0.4,
            'embedding_generation': 0.6
        }
        
        logger.info("✅ Enhanced Skin Model initialized")
    
    def _create_backbone(self) -> keras.Model:
        """Create CNN backbone with transfer learning"""
        if self.backbone_name == 'resnet50':
            backbone = ResNet50(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )
        elif self.backbone_name == 'efficientnet':
            backbone = EfficientNetB4(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )
        else:
            raise ValueError(f"Unsupported backbone: {self.backbone_name}")
        
        # Freeze early layers for transfer learning
        for layer in backbone.layers[:-20]:
            layer.trainable = False
        
        return backbone
    
    def _create_attention_layers(self, x: tf.Tensor) -> tf.Tensor:
        """Add attention mechanisms to the feature maps"""
        if not self.use_attention:
            return x
        
        # Add Squeeze-and-Excitation blocks
        x = SqueezeExcitationBlock(ratio=16)(x)
        
        # Add CBAM
        x = ConvolutionalBlockAttentionModule(reduction_ratio=16)(x)
        
        return x
    
    def _create_condition_classification_head(self, x: tf.Tensor) -> keras.Model:
        """Create skin condition classification head"""
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation='relu')(x)
        output = layers.Dense(self.num_conditions, activation='softmax', name='condition_classification')(x)
        
        return output
    
    def _create_demographic_prediction_head(self, x: tf.Tensor) -> Dict[str, layers.Layer]:
        """Create demographic attribute prediction heads"""
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Age regression
        age_output = layers.Dense(1, activation='linear', name='age_regression')(x)
        
        # Gender classification
        gender_output = layers.Dense(2, activation='softmax', name='gender_classification')(x)
        
        # Ethnicity classification
        ethnicity_output = layers.Dense(7, activation='softmax', name='ethnicity_classification')(x)
        
        return {
            'age': age_output,
            'gender': gender_output,
            'ethnicity': ethnicity_output
        }
    
    def _create_skin_characteristics_head(self, x: tf.Tensor) -> layers.Layer:
        """Create skin characteristics regression head"""
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        
        # Predict redness, texture, pigmentation scores
        output = layers.Dense(3, activation='sigmoid', name='skin_characteristics')(x)
        
        return output
    
    def _create_embedding_generation_head(self, x: tf.Tensor) -> layers.Layer:
        """Create embedding generation head with contrastive learning"""
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation='relu')(x)
        
        # L2 normalization for cosine similarity
        output = layers.Lambda(lambda x: tf.math.l2_normalize(x, axis=1), name='embedding_generation')(x)
        
        return output
    
    def build_model(self) -> keras.Model:
        """Build the complete multi-task learning model"""
        # Input layer
        input_layer = layers.Input(shape=self.input_shape, name='input_image')
        
        # Backbone
        backbone = self._create_backbone()
        x = backbone(input_layer)
        
        # Attention mechanisms
        x = self._create_attention_layers(x)
        
        # Multi-task heads
        condition_output = self._create_condition_classification_head(x)
        demographic_outputs = self._create_demographic_prediction_head(x)
        skin_characteristics_output = self._create_skin_characteristics_head(x)
        embedding_output = self._create_embedding_generation_head(x)
        
        # Combine all outputs
        outputs = [condition_output, embedding_output, skin_characteristics_output]
        outputs.extend(demographic_outputs.values())
        
        # Create model
        self.model = keras.Model(inputs=input_layer, outputs=outputs, name='enhanced_skin_model')
        
        logger.info("✅ Enhanced skin model built successfully")
        return self.model
    
    def compile_model(self):
        """Compile the model with appropriate losses and metrics"""
        # Define losses for each task
        losses = {
            'condition_classification': 'categorical_crossentropy',
            'age_regression': 'mse',
            'gender_classification': 'categorical_crossentropy',
            'ethnicity_classification': 'categorical_crossentropy',
            'skin_characteristics': 'mse',
            'embedding_generation': self._contrastive_loss
        }
        
        # Define metrics for each task
        metrics = {
            'condition_classification': ['accuracy', 'top_3_accuracy'],
            'age_regression': ['mae'],
            'gender_classification': ['accuracy'],
            'ethnicity_classification': ['accuracy'],
            'skin_characteristics': ['mae'],
            'embedding_generation': ['cosine_similarity']
        }
        
        # Optimizer with learning rate scheduling
        optimizer = optimizers.Adam(learning_rate=self.learning_rate)
        
        # Compile model
        self.model.compile(
            optimizer=optimizer,
            loss=losses,
            loss_weights=list(self.loss_weights.values()),
            metrics=metrics
        )
        
        logger.info("✅ Model compiled successfully")
    
    def _contrastive_loss(self, y_true, y_pred):
        """Contrastive loss for embedding generation"""
        # This is a simplified contrastive loss
        # In practice, you'd implement triplet loss or arcface loss
        return tf.reduce_mean(tf.square(y_true - y_pred))
    
    def create_data_generators(self, train_data: Dict, val_data: Dict, test_data: Dict):
        """Create data generators for training"""
        self.train_generator = self._create_generator(train_data)
        self.val_generator = self._create_generator(val_data)
        self.test_generator = self._create_generator(test_data)
        
        logger.info("✅ Data generators created successfully")
    
    def _create_generator(self, data: Dict):
        """Create data generator for a dataset split"""
        # This is a simplified generator
        # In practice, you'd implement a proper generator with augmentation
        return data
    
    def train_model(self, train_data: Dict, val_data: Dict, model_save_path: str = "models"):
        """Train the enhanced model"""
        try:
            # Create data generators
            self.create_data_generators(train_data, val_data, {})
            
            # Create callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True,
                    verbose=1
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7,
                    verbose=1
                ),
                ModelCheckpoint(
                    filepath=f"{model_save_path}/best_model.h5",
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # Train model
            logger.info("🚀 Starting model training...")
            history = self.model.fit(
                self.train_generator,
                validation_data=self.val_generator,
                epochs=self.epochs,
                batch_size=self.batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            logger.info("✅ Model training completed successfully")
            return history
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return None
    
    def evaluate_model(self, test_data: Dict) -> Dict:
        """Evaluate the trained model"""
        try:
            logger.info("📊 Evaluating model performance...")
            
            # Make predictions
            predictions = self.model.predict(test_data)
            
            # Extract predictions for each task
            condition_preds = predictions[0]
            embedding_preds = predictions[1]
            skin_char_preds = predictions[2]
            age_preds = predictions[3]
            gender_preds = predictions[4]
            ethnicity_preds = predictions[5]
            
            # Calculate metrics
            metrics = {}
            
            # Condition classification metrics
            condition_accuracy = np.mean(np.argmax(condition_preds, axis=1) == np.argmax(test_data['condition_labels'], axis=1))
            metrics['condition_accuracy'] = condition_accuracy
            
            # Age regression metrics
            age_mae = np.mean(np.abs(age_preds.flatten() - test_data['age_labels']))
            metrics['age_mae'] = age_mae
            
            # Gender classification metrics
            gender_accuracy = np.mean(np.argmax(gender_preds, axis=1) == np.argmax(test_data['gender_labels'], axis=1))
            metrics['gender_accuracy'] = gender_accuracy
            
            # Ethnicity classification metrics
            ethnicity_accuracy = np.mean(np.argmax(ethnicity_preds, axis=1) == np.argmax(test_data['ethnicity_labels'], axis=1))
            metrics['ethnicity_accuracy'] = ethnicity_accuracy
            
            # Skin characteristics metrics
            skin_char_mae = np.mean(np.abs(skin_char_preds - test_data['skin_char_labels']))
            metrics['skin_characteristics_mae'] = skin_char_mae
            
            # Embedding distinctiveness metrics
            embedding_distinctiveness = self._calculate_embedding_distinctiveness(embedding_preds, test_data['condition_labels'])
            metrics['embedding_distinctiveness'] = embedding_distinctiveness
            
            logger.info("✅ Model evaluation completed")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}
    
    def _calculate_embedding_distinctiveness(self, embeddings: np.ndarray, labels: np.ndarray) -> float:
        """Calculate embedding distinctiveness using silhouette score"""
        from sklearn.metrics import silhouette_score
        
        try:
            # Convert one-hot labels to class indices
            class_indices = np.argmax(labels, axis=1)
            
            # Calculate silhouette score
            silhouette_avg = silhouette_score(embeddings, class_indices)
            
            return silhouette_avg
        except Exception as e:
            logger.warning(f"⚠️ Could not calculate embedding distinctiveness: {e}")
            return 0.0
    
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
            predictions = self.model.predict(image)
            
            # Process predictions
            result = {
                'condition': self._decode_condition_prediction(predictions[0]),
                'age': float(predictions[3][0]),
                'gender': self._decode_gender_prediction(predictions[4]),
                'ethnicity': self._decode_ethnicity_prediction(predictions[5]),
                'skin_characteristics': {
                    'redness': float(predictions[2][0][0]),
                    'texture': float(predictions[2][0][1]),
                    'pigmentation': float(predictions[2][0][2])
                },
                'embedding': predictions[1][0].tolist()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            return {}
    
    def _decode_condition_prediction(self, pred: np.ndarray) -> Dict:
        """Decode condition classification prediction"""
        conditions = ['healthy', 'acne', 'eczema', 'keratosis', 'milia', 'rosacea']
        condition_idx = np.argmax(pred)
        confidence = float(pred[condition_idx])
        
        return {
            'condition': conditions[condition_idx],
            'confidence': confidence,
            'all_probabilities': pred.tolist()
        }
    
    def _decode_gender_prediction(self, pred: np.ndarray) -> Dict:
        """Decode gender classification prediction"""
        genders = ['male', 'female']
        gender_idx = np.argmax(pred)
        confidence = float(pred[gender_idx])
        
        return {
            'gender': genders[gender_idx],
            'confidence': confidence
        }
    
    def _decode_ethnicity_prediction(self, pred: np.ndarray) -> Dict:
        """Decode ethnicity classification prediction"""
        ethnicities = ['white', 'black', 'asian', 'indian', 'hispanic', 'middle_eastern', 'other']
        ethnicity_idx = np.argmax(pred)
        confidence = float(pred[ethnicity_idx])
        
        return {
            'ethnicity': ethnicities[ethnicity_idx],
            'confidence': confidence
        }
    
    def save_model(self, model_path: str = "models/enhanced_skin_model.h5"):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            self.model.save(model_path)
            logger.info(f"✅ Model saved to {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return False
    
    def load_model(self, model_path: str = "models/enhanced_skin_model.h5"):
        """Load a trained model"""
        try:
            self.model = keras.models.load_model(model_path, custom_objects={
                'SqueezeExcitationBlock': SqueezeExcitationBlock,
                'ConvolutionalBlockAttentionModule': ConvolutionalBlockAttentionModule,
                '_contrastive_loss': self._contrastive_loss
            })
            logger.info(f"✅ Model loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

def main():
    """Main function to demonstrate model usage"""
    # Initialize model
    model = EnhancedSkinModel(
        input_shape=(224, 224, 3),
        num_conditions=6,
        embedding_dim=2048,
        use_attention=True,
        backbone='resnet50'
    )
    
    # Build and compile model
    model.build_model()
    model.compile_model()
    
    # Print model summary
    model.model.summary()
    
    print("✅ Enhanced ML model created successfully!")

if __name__ == "__main__":
    main() 