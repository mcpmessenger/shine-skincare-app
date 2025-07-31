import os
import logging
import numpy as np
import io
from typing import Dict, Any, Optional, Union
from datetime import datetime
from PIL import Image
import cv2

# Try to import deep learning libraries
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50, ResNet50_Weights
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("PyTorch not available, using fallback vectorization")
    TORCH_AVAILABLE = False
    torch = None
    transforms = None

logger = logging.getLogger(__name__)

class EnhancedImageVectorizationService:
    """
    Enhanced image vectorization service for converting facial images to high-dimensional vectors
    Uses pre-trained deep learning models for feature extraction
    """
    
    def __init__(self, model_name: str = 'resnet50', dimension: int = 2048):
        """
        Initialize the enhanced image vectorization service
        
        Args:
            model_name: Name of the model to use for feature extraction
            dimension: Dimension of the output feature vector
        """
        self.model_name = model_name
        self.dimension = dimension
        self.model = None
        self.transform = None
        self.device = 'cpu'
        
        self._initialize_model()
        logger.info(f"Enhanced Image Vectorization Service initialized with {model_name}")
    
    def _initialize_model(self):
        """Initialize the deep learning model for feature extraction"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available, using fallback vectorization")
            return
        
        try:
            # Load pre-trained ResNet50 model
            if self.model_name == 'resnet50':
                self.model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
                # Remove the final classification layer to get feature vectors
                self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
                self.model.eval()
                
                # Define image transformations
                self.transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    )
                ])
                
                logger.info("ResNet50 model loaded successfully")
            else:
                logger.warning(f"Model {self.model_name} not supported, using fallback")
                
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self.model = None
            self.transform = None
    
    def vectorize_image_from_bytes(self, image_data: bytes) -> Optional[np.ndarray]:
        """
        Vectorize an image from bytes using deep learning model
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Feature vector as numpy array or None if failed
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            if self.model is not None and self.transform is not None:
                # Use deep learning model
                return self._vectorize_with_model(image)
            else:
                # Fallback to traditional feature extraction
                return self._vectorize_fallback(image)
                
        except Exception as e:
            logger.error(f"Error vectorizing image: {e}")
            return None
    
    def _vectorize_with_model(self, image: Image.Image) -> np.ndarray:
        """Vectorize image using deep learning model"""
        try:
            # Apply transformations
            input_tensor = self.transform(image).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
                # Flatten the features
                feature_vector = features.squeeze().numpy()
            
            # Normalize the feature vector
            feature_norm = np.linalg.norm(feature_vector)
            if feature_norm > 0:
                feature_vector = feature_vector / feature_norm
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error in model-based vectorization: {e}")
            return self._vectorize_fallback(image)
    
    def _vectorize_fallback(self, image: Image.Image) -> np.ndarray:
        """Fallback vectorization using traditional computer vision features"""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Resize to standard size
            cv_image = cv2.resize(cv_image, (224, 224))
            
            # Extract multiple feature types
            features = []
            
            # 1. Color histogram features
            color_hist = cv2.calcHist([cv_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            color_hist = cv2.normalize(color_hist, color_hist).flatten()
            features.extend(color_hist)
            
            # 2. Texture features (GLCM-like)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Sobel gradients
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            gradient_features = [
                np.mean(gradient_magnitude),
                np.std(gradient_magnitude),
                np.max(gradient_magnitude)
            ]
            features.extend(gradient_features)
            
            # 3. Edge density
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # 4. Local Binary Pattern (simplified)
            lbp_features = self._extract_lbp_features(gray)
            features.extend(lbp_features)
            
            # 5. Fill remaining dimensions with zeros if needed
            while len(features) < self.dimension:
                features.append(0.0)
            
            # Truncate if too long
            features = features[:self.dimension]
            
            # Convert to numpy array and normalize
            feature_vector = np.array(features, dtype=np.float32)
            feature_norm = np.linalg.norm(feature_vector)
            if feature_norm > 0:
                feature_vector = feature_vector / feature_norm
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error in fallback vectorization: {e}")
            # Return zero vector as last resort
            return np.zeros(self.dimension, dtype=np.float32)
    
    def _extract_lbp_features(self, gray_image: np.ndarray) -> list:
        """Extract Local Binary Pattern features"""
        try:
            # Simplified LBP implementation
            height, width = gray_image.shape
            lbp_features = []
            
            # Sample points for LBP calculation
            sample_points = min(100, height * width // 100)
            for _ in range(sample_points):
                y = np.random.randint(1, height - 1)
                x = np.random.randint(1, width - 1)
                
                center = gray_image[y, x]
                lbp_code = 0
                
                # 8-neighbor LBP
                neighbors = [
                    gray_image[y-1, x-1], gray_image[y-1, x], gray_image[y-1, x+1],
                    gray_image[y, x+1], gray_image[y+1, x+1], gray_image[y+1, x],
                    gray_image[y+1, x-1], gray_image[y, x-1]
                ]
                
                for i, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        lbp_code += 2**i
                
                lbp_features.append(lbp_code)
            
            # Calculate histogram of LBP codes
            lbp_hist, _ = np.histogram(lbp_features, bins=16, range=(0, 256))
            lbp_hist = lbp_hist.astype(np.float32)
            
            # Normalize
            if np.sum(lbp_hist) > 0:
                lbp_hist = lbp_hist / np.sum(lbp_hist)
            
            return lbp_hist.tolist()
            
        except Exception as e:
            logger.error(f"Error extracting LBP features: {e}")
            return [0.0] * 16
    
    def vectorize_cropped_face(self, cropped_image_data: bytes) -> Optional[np.ndarray]:
        """
        Vectorize a cropped face image specifically for skin analysis
        
        Args:
            cropped_image_data: Cropped face image data as bytes
            
        Returns:
            Feature vector optimized for skin analysis
        """
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(cropped_image_data)).convert('RGB')
            
            # For skin analysis, we might want to focus on specific regions
            # This is a simplified version - in production, you'd want more sophisticated
            # skin region detection and analysis
            
            return self.vectorize_image_from_bytes(cropped_image_data)
            
        except Exception as e:
            logger.error(f"Error vectorizing cropped face: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'model_available': self.model is not None,
            'torch_available': TORCH_AVAILABLE,
            'device': self.device,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.model is not None or True  # Always available due to fallback
    
    def update_model(self, model_name: str) -> bool:
        """
        Update the model being used for vectorization
        
        Args:
            model_name: Name of the new model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.model_name = model_name
            self._initialize_model()
            return True
        except Exception as e:
            logger.error(f"Failed to update model: {e}")
            return False 