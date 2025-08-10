"""
Shine Skincare App - ML Integration Module

Handles TensorFlow model loading, preprocessing, and inference
for skin analysis. Optimized for production deployment.
"""

import tensorflow as tf
import numpy as np
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class SkinAnalysisModel:
    """
    TensorFlow-based skin analysis model wrapper.
    Handles model loading, preprocessing, and inference.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the skin analysis model.
        
        Args:
            model_path: Path to the TensorFlow model file (.h5)
        """
        self.model_path = Path(model_path)
        self.model = None
        self.model_metadata = None
        self.class_names = []
        self.input_shape = None
        self.is_initialized = False
        
        # Load the model
        self._load_model()
    
    def _load_model(self):
        """Load the TensorFlow model and metadata"""
        try:
            logger.info(f"🔄 Loading TensorFlow model from: {self.model_path}")
            
            # Check if model file exists
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Define custom loss function (same as training)
            def focal_loss(gamma=2., alpha=.25):
                def focal_loss_fixed(y_true, y_pred):
                    pt_1 = tf.where(tf.equal(y_true, 1), y_pred, tf.ones_like(y_pred))
                    pt_0 = tf.where(tf.equal(y_true, 0), y_pred, tf.zeros_like(y_pred))
                    return -tf.reduce_mean(alpha * tf.pow(1. - pt_1, gamma) * tf.math.log(pt_1 + 1e-7)) - \
                           tf.reduce_mean((1 - alpha) * tf.pow(pt_0, gamma) * tf.math.log(1. - pt_0 + 1e-7))
                return focal_loss_fixed
            
            # Load the model with custom objects
            self.model = tf.keras.models.load_model(
                str(self.model_path),
                custom_objects={'focal_loss': focal_loss},
                compile=False
            )
            
            # Get model information
            self.input_shape = self.model.input_shape[1:]  # Remove batch dimension
            self.output_shape = self.model.output_shape[1:]
            
            # Load class names and metadata
            self._load_metadata()
            
            # Compile the model for inference
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            self.is_initialized = True
            logger.info(f"✅ Model loaded successfully")
            logger.info(f"   Input shape: {self.input_shape}")
            logger.info(f"   Output shape: {self.output_shape}")
            logger.info(f"   Classes: {len(self.class_names)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            self.is_initialized = False
            raise
    
    def _load_metadata(self):
        """Load model metadata and class names"""
        try:
            # Try to load from metadata file
            metadata_path = self.model_path.parent / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                    self.class_names = self.model_metadata.get('class_names', [])
                    logger.info(f"✅ Loaded metadata from: {metadata_path}")
            else:
                # Fallback to default class names based on our dataset
                self.class_names = [
                    'acne', 'actinic_keratosis', 'basal_cell_carcinoma',
                    'dermatitis', 'eczema', 'healthy', 'hyperpigmentation',
                    'hypopigmentation', 'malignant', 'melanoma', 'melasma',
                    'psoriasis', 'rosacea', 'vitiligo'
                ]
                logger.info("⚠️ Using default class names (no metadata file found)")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load metadata: {e}")
            # Use default class names
            self.class_names = [
                'acne', 'actinic_keratosis', 'basal_cell_carcinoma',
                'dermatitis', 'eczema', 'healthy', 'hyperpigmentation',
                'hypopigmentation', 'malignant', 'melanoma', 'melasma',
                'psoriasis', 'rosacea', 'vitiligo'
            ]
    
    def is_ready(self) -> bool:
        """Check if the model is ready for inference"""
        return (
            self.is_initialized and 
            self.model is not None and 
            len(self.class_names) > 0
        )
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input.
        
        Args:
            image: Input image array (H, W, C) or (B, H, W, C)
            
        Returns:
            Preprocessed image array
        """
        try:
            # Ensure correct shape
            if len(image.shape) == 3:
                # Single image (H, W, C) -> (1, H, W, C)
                image = np.expand_dims(image, axis=0)
            
            # Ensure correct dimensions
            if len(image.shape) != 4:
                raise ValueError(f"Expected 4D input, got {len(image.shape)}D")
            
            # Resize if necessary (should already be 224x224 from Flask app)
            if image.shape[1:3] != self.input_shape[:2]:
                logger.warning(f"Resizing image from {image.shape[1:3]} to {self.input_shape[:2]}")
                # This would require additional preprocessing logic
                pass
            
            # Ensure correct data type
            if image.dtype != np.float32:
                image = image.astype(np.float32)
            
            # Normalize if not already normalized (0-1 range)
            if image.max() > 1.0:
                image = image / 255.0
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            raise
    
    def predict(self, image: np.ndarray) -> np.ndarray:
        """
        Make prediction on preprocessed image.
        
        Args:
            image: Preprocessed image array (B, H, W, C)
            
        Returns:
            Prediction probabilities array (B, num_classes)
        """
        if not self.is_ready():
            raise RuntimeError("Model not ready for inference")
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            raise
    
    def analyze_skin(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze skin image and return detailed results.
        
        Args:
            image: Input image array (B, H, W, C)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Make prediction
            predictions = self.predict(image)
            
            # Get top predictions
            top_indices = np.argsort(predictions[0])[::-1][:3]
            top_probabilities = predictions[0][top_indices]
            top_classes = [self.class_names[i] for i in top_indices]
            
            # Format results
            result = {
                'predictions': [],
                'top_prediction': {
                    'class': top_classes[0],
                    'confidence': float(top_probabilities[0]),
                    'probability': float(top_probabilities[0])
                },
                'all_probabilities': {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.class_names, predictions[0])
                },
                'model_info': {
                    'input_shape': self.input_shape,
                    'output_shape': self.output_shape,
                    'num_classes': len(self.class_names),
                    'model_path': str(self.model_path)
                }
            }
            
            # Add top 3 predictions
            for i, (class_name, prob) in enumerate(zip(top_classes, top_probabilities)):
                result['predictions'].append({
                    'rank': i + 1,
                    'class': class_name,
                    'confidence': float(prob),
                    'probability': float(prob)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Skin analysis failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        return {
            'model_path': str(self.model_path),
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'num_classes': len(self.class_names),
            'class_names': self.class_names,
            'is_initialized': self.is_initialized,
            'model_metadata': self.model_metadata
        }
    
    def get_class_names(self) -> list:
        """Get list of class names"""
        return self.class_names.copy()
    
    def get_input_shape(self) -> Tuple[int, ...]:
        """Get model input shape"""
        return self.input_shape
    
    def get_output_shape(self) -> Tuple[int, ...]:
        """Get model output shape"""
        return self.output_shape
