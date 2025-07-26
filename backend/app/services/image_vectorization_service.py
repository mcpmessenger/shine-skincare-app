import os
import logging
import numpy as np
from typing import List, Optional, Tuple
from PIL import Image
import torch
import torchvision.transforms as transforms
import timm
from io import BytesIO

logger = logging.getLogger(__name__)

class ImageVectorizationService:
    """Service for image vectorization using pre-trained CNN models"""
    
    def __init__(self, model_name: str = 'resnet50', device: Optional[str] = None):
        """
        Initialize the image vectorization service
        
        Args:
            model_name: Name of the pre-trained model to use
            device: Device to run the model on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = None
        self.feature_dimension = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the pre-trained model"""
        try:
            # Load pre-trained model
            self.model = timm.create_model(
                self.model_name, 
                pretrained=True, 
                num_classes=0  # Remove classification head to get features
            )
            self.model.to(self.device)
            self.model.eval()
            
            # Get feature dimension
            with torch.no_grad():
                dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
                features = self.model(dummy_input)
                self.feature_dimension = features.shape[1]
            
            # Set up image transformations
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info(f"Model {self.model_name} initialized successfully. Feature dimension: {self.feature_dimension}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model {self.model_name}: {e}")
            self.model = None
            self.transform = None
            self.feature_dimension = None
    
    def vectorize_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Vectorize an image from file path
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            return self._process_image(image)
            
        except Exception as e:
            logger.error(f"Error vectorizing image {image_path}: {e}")
            return None
    
    def vectorize_image_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Vectorize an image from bytes
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Load and preprocess image
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            return self._process_image(image)
            
        except Exception as e:
            logger.error(f"Error vectorizing image from bytes: {e}")
            return None
    
    def vectorize_image_from_pil(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        Vectorize a PIL Image object
        
        Args:
            image: PIL Image object
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            return self._process_image(image)
        except Exception as e:
            logger.error(f"Error vectorizing PIL image: {e}")
            return None
    
    def _process_image(self, image: Image.Image) -> Optional[np.ndarray]:
        """Process image and extract features"""
        if not self.model or not self.transform:
            logger.error("Model not initialized")
            return None
        
        try:
            # Apply transformations
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
                feature_vector = features.cpu().numpy().flatten()
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def get_feature_dimension(self) -> Optional[int]:
        """Get the feature dimension of the model"""
        return self.feature_dimension
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.model is not None and self.transform is not None
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'feature_dimension': self.feature_dimension,
            'device': self.device,
            'available': self.is_available()
        } 