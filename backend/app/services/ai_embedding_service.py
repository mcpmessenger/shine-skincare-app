"""
AI Embedding Service - Handles image embedding generation using pre-trained CNN models

This service is part of Operation Left Brain and provides the core functionality
for generating high-dimensional feature vectors from skin images for similarity search.
"""

import logging
import io
import numpy as np
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import torch
import torchvision.transforms as transforms

# Try to import timm for pre-trained models
try:
    import timm
    TIMM_AVAILABLE = True
except ImportError:
    TIMM_AVAILABLE = False
    logging.warning("timm not available - using fallback embedding method")

logger = logging.getLogger(__name__)

class AIEmbeddingService:
    """
    Service for generating image embeddings using pre-trained CNN models
    """
    
    def __init__(self, model_name: str = 'resnet50', device: str = 'auto'):
        """
        Initialize the embedding service
        
        Args:
            model_name: Name of the pre-trained model to use
            device: 'cpu', 'cuda', or 'auto' for automatic detection
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.transform = None
        self.embedding_dimension = None
        
        # Initialize the model
        self._initialize_model()
        
    def _get_device(self, device: str) -> str:
        """Get the appropriate device for model inference"""
        if device == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return device
    
    def _initialize_model(self):
        """Initialize the pre-trained model and transforms"""
        try:
            if TIMM_AVAILABLE:
                # Use timm for pre-trained models
                self.model = timm.create_model(
                    self.model_name, 
                    pretrained=True, 
                    num_classes=0  # Remove classification head to get features
                )
                self.model.eval()
                self.model.to(self.device)
                
                # Get embedding dimension
                with torch.no_grad():
                    dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
                    dummy_output = self.model(dummy_input)
                    self.embedding_dimension = dummy_output.shape[1]
                
                logger.info(f"✅ Loaded {self.model_name} model with {self.embedding_dimension}D embeddings")
                
            else:
                # Fallback to a simple feature extractor
                logger.warning("Using fallback embedding method - install timm for better performance")
                self._initialize_fallback_model()
                
            # Initialize transforms
            self._initialize_transforms()
            
        except Exception as e:
            logger.error(f"Failed to initialize model {self.model_name}: {e}")
            raise
    
    def _initialize_fallback_model(self):
        """Initialize a fallback model when timm is not available"""
        # Simple CNN for feature extraction
        self.model = torch.nn.Sequential(
            torch.nn.Conv2d(3, 64, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.Conv2d(64, 128, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),
            torch.nn.AdaptiveAvgPool2d((1, 1)),
            torch.nn.Flatten(),
            torch.nn.Linear(128, 512)
        )
        self.model.eval()
        self.model.to(self.device)
        self.embedding_dimension = 512
        
    def _initialize_transforms(self):
        """Initialize image transforms for the model"""
        if TIMM_AVAILABLE and self.model_name.startswith('resnet'):
            # ImageNet normalization for ResNet models
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], 
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            # Simple normalization for fallback
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
    
    def generate_embedding(self, image_bytes: bytes) -> np.ndarray:
        """
        Generate embedding vector from image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            numpy array representing the image embedding
        """
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.model(image_tensor)
                embedding_np = embedding.cpu().numpy().flatten()
            
            logger.debug(f"Generated {len(embedding_np)}D embedding")
            return embedding_np
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embedding_batch(self, image_bytes_list: list) -> np.ndarray:
        """
        Generate embeddings for multiple images (batch processing)
        
        Args:
            image_bytes_list: List of image bytes
            
        Returns:
            numpy array of embeddings (n_images x embedding_dim)
        """
        embeddings = []
        
        for i, image_bytes in enumerate(image_bytes_list):
            try:
                embedding = self.generate_embedding(image_bytes)
                embeddings.append(embedding)
                logger.debug(f"Processed image {i+1}/{len(image_bytes_list)}")
            except Exception as e:
                logger.error(f"Error processing image {i+1}: {e}")
                # Add zero embedding as fallback
                embeddings.append(np.zeros(self.embedding_dimension))
        
        return np.array(embeddings)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.embedding_dimension
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'embedding_dimension': self.embedding_dimension,
            'timm_available': TIMM_AVAILABLE,
            'cuda_available': torch.cuda.is_available()
        }

# Global instance for reuse
embedding_service = AIEmbeddingService() 