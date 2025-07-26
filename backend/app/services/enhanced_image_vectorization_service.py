import os
import logging
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image
import torch
import torchvision.transforms as transforms
import timm
from io import BytesIO
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedImageVectorizationService:
    """Enhanced service for image vectorization with SCIN dataset support"""
    
    def __init__(self, 
                 model_name: str = 'resnet50', 
                 device: Optional[str] = None,
                 feature_dimension: int = 2048,
                 cache_dir: str = 'vector_cache'):
        """
        Initialize the enhanced image vectorization service
        
        Args:
            model_name: Name of the pre-trained model to use
            device: Device to run the model on ('cpu' or 'cuda')
            feature_dimension: Expected feature dimension
            cache_dir: Directory to cache vectorized images
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.feature_dimension = feature_dimension
        self.cache_dir = cache_dir
        self.model = None
        self.transform = None
        self._initialize_model()
        self._ensure_cache_dir()
    
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
            
            # Set up image transformations
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            logger.info(f"Model {self.model_name} initialized successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model {self.model_name}: {e}")
            self.model = None
            self.transform = None
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")
    
    def _get_cache_path(self, image_id: str) -> str:
        """Get cache file path for an image"""
        return os.path.join(self.cache_dir, f"{image_id}.pkl")
    
    def _load_from_cache(self, image_id: str) -> Optional[np.ndarray]:
        """Load vector from cache"""
        try:
            cache_path = self._get_cache_path(image_id)
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    # Check if cache is still valid (e.g., based on model version)
                    if cached_data.get('model_name') == self.model_name:
                        return cached_data['vector']
        except Exception as e:
            logger.warning(f"Failed to load from cache for {image_id}: {e}")
        return None
    
    def _save_to_cache(self, image_id: str, vector: np.ndarray):
        """Save vector to cache"""
        try:
            cache_path = self._get_cache_path(image_id)
            cached_data = {
                'vector': vector,
                'model_name': self.model_name,
                'timestamp': datetime.now().isoformat()
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            logger.warning(f"Failed to save to cache for {image_id}: {e}")
    
    def vectorize_image(self, 
                       image_path: str, 
                       image_id: Optional[str] = None,
                       use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Vectorize an image from file path
        
        Args:
            image_path: Path to the image file
            image_id: Optional ID for caching
            use_cache: Whether to use caching
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Try cache first
            if use_cache and image_id:
                cached_vector = self._load_from_cache(image_id)
                if cached_vector is not None:
                    logger.info(f"Loaded vector from cache for {image_id}")
                    return cached_vector
            
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            vector = self._process_image(image)
            
            # Save to cache
            if use_cache and image_id and vector is not None:
                self._save_to_cache(image_id, vector)
            
            return vector
            
        except Exception as e:
            logger.error(f"Error vectorizing image {image_path}: {e}")
            return None
    
    def vectorize_image_from_bytes(self, 
                                  image_bytes: bytes,
                                  image_id: Optional[str] = None,
                                  use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Vectorize an image from bytes
        
        Args:
            image_bytes: Image data as bytes
            image_id: Optional ID for caching
            use_cache: Whether to use caching
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Try cache first
            if use_cache and image_id:
                cached_vector = self._load_from_cache(image_id)
                if cached_vector is not None:
                    logger.info(f"Loaded vector from cache for {image_id}")
                    return cached_vector
            
            # Load and preprocess image
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            vector = self._process_image(image)
            
            # Save to cache
            if use_cache and image_id and vector is not None:
                self._save_to_cache(image_id, vector)
            
            return vector
            
        except Exception as e:
            logger.error(f"Error vectorizing image from bytes: {e}")
            return None
    
    def vectorize_image_from_pil(self, 
                                image: Image.Image,
                                image_id: Optional[str] = None,
                                use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Vectorize a PIL Image object
        
        Args:
            image: PIL Image object
            image_id: Optional ID for caching
            use_cache: Whether to use caching
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Try cache first
            if use_cache and image_id:
                cached_vector = self._load_from_cache(image_id)
                if cached_vector is not None:
                    logger.info(f"Loaded vector from cache for {image_id}")
                    return cached_vector
            
            vector = self._process_image(image)
            
            # Save to cache
            if use_cache and image_id and vector is not None:
                self._save_to_cache(image_id, vector)
            
            return vector
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
            
            # Ensure correct dimension
            if len(feature_vector) != self.feature_dimension:
                logger.warning(f"Feature dimension mismatch: expected {self.feature_dimension}, got {len(feature_vector)}")
                # Resize if necessary (simple truncation or padding)
                if len(feature_vector) > self.feature_dimension:
                    feature_vector = feature_vector[:self.feature_dimension]
                else:
                    feature_vector = np.pad(feature_vector, (0, self.feature_dimension - len(feature_vector)))
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def batch_vectorize(self, 
                       image_paths: List[str],
                       image_ids: Optional[List[str]] = None,
                       batch_size: int = 32,
                       use_cache: bool = True) -> List[Optional[np.ndarray]]:
        """
        Vectorize multiple images in batches
        
        Args:
            image_paths: List of image file paths
            image_ids: Optional list of image IDs for caching
            batch_size: Number of images to process in each batch
            use_cache: Whether to use caching
            
        Returns:
            List of feature vectors (None for failed images)
        """
        results = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_ids = image_ids[i:i + batch_size] if image_ids else None
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(image_paths) + batch_size - 1)//batch_size}")
            
            for j, path in enumerate(batch_paths):
                image_id = batch_ids[j] if batch_ids else None
                vector = self.vectorize_image(path, image_id, use_cache)
                results.append(vector)
        
        return results
    
    def get_feature_dimension(self) -> int:
        """Get the feature dimension of the model"""
        return self.feature_dimension
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.model is not None and self.transform is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'feature_dimension': self.feature_dimension,
            'device': self.device,
            'available': self.is_available(),
            'cache_dir': self.cache_dir
        }
    
    def clear_cache(self):
        """Clear the vector cache"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
            self._ensure_cache_dir()
            logger.info("Vector cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache"""
        try:
            if not os.path.exists(self.cache_dir):
                return {'cached_vectors': 0, 'cache_size_mb': 0}
            
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            cache_size = sum(os.path.getsize(os.path.join(self.cache_dir, f)) for f in cache_files)
            
            return {
                'cached_vectors': len(cache_files),
                'cache_size_mb': round(cache_size / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {'error': str(e)} 