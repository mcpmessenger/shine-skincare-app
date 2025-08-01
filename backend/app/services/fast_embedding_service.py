"""
Fast Embedding Service - Optimized for <5 minute search times
Uses lightweight algorithms and caching for speed
"""

import time
import numpy as np
from PIL import Image
import io
import hashlib
import json
import os
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class FastEmbeddingService:
    """Fast embedding service optimized for speed (<5 minutes)"""
    
    def __init__(self):
        self.cache_dir = "/tmp/embedding_cache"
        self.ensure_cache_dir()
        self.feature_cache = {}
        self.search_cache = {}
        
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def generate_image_hash(self, image_bytes: bytes) -> str:
        """Generate hash for image caching"""
        return hashlib.md5(image_bytes).hexdigest()
    
    def extract_fast_features(self, image_bytes: bytes) -> np.ndarray:
        """Extract features using fast, lightweight methods"""
        start_time = time.time()
        
        try:
            # Load image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for faster processing
            image = image.resize((224, 224), Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract multiple feature types for better representation
            features = []
            
            # 1. Color features (fast)
            color_features = self._extract_color_features(img_array)
            features.extend(color_features)
            
            # 2. Texture features (fast)
            texture_features = self._extract_texture_features(img_array)
            features.extend(texture_features)
            
            # 3. Edge features (fast)
            edge_features = self._extract_edge_features(img_array)
            features.extend(edge_features)
            
            # 4. Histogram features (fast)
            histogram_features = self._extract_histogram_features(img_array)
            features.extend(histogram_features)
            
            # 5. Statistical features (fast)
            statistical_features = self._extract_statistical_features(img_array)
            features.extend(statistical_features)
            
            # Combine all features
            combined_features = np.array(features, dtype=np.float32)
            
            # Normalize features
            combined_features = self._normalize_features(combined_features)
            
            processing_time = time.time() - start_time
            logger.info(f"Fast feature extraction completed in {processing_time:.2f}s")
            
            return combined_features
            
        except Exception as e:
            logger.error(f"Fast feature extraction failed: {e}")
            # Return default features if extraction fails
            return np.zeros(512, dtype=np.float32)
    
    def _extract_color_features(self, img_array: np.ndarray) -> List[float]:
        """Extract color-based features (fast)"""
        features = []
        
        # Mean RGB values
        mean_rgb = np.mean(img_array, axis=(0, 1))
        features.extend(mean_rgb.tolist())
        
        # Standard deviation RGB values
        std_rgb = np.std(img_array, axis=(0, 1))
        features.extend(std_rgb.tolist())
        
        # Color moments (mean, std, skewness)
        for channel in range(3):
            channel_data = img_array[:, :, channel].flatten()
            features.append(np.mean(channel_data))
            features.append(np.std(channel_data))
            features.append(self._skewness(channel_data))
        
        # Color histogram (simplified)
        for channel in range(3):
            hist, _ = np.histogram(img_array[:, :, channel], bins=16, range=(0, 255))
            features.extend(hist.tolist())
        
        return features
    
    def _extract_texture_features(self, img_array: np.ndarray) -> List[float]:
        """Extract texture features using Local Binary Patterns (fast)"""
        features = []
        
        # Convert to grayscale for texture analysis
        gray = np.mean(img_array, axis=2)
        
        # Local Binary Patterns (simplified)
        lbp_features = self._compute_lbp(gray)
        features.extend(lbp_features)
        
        # Gabor-like features (simplified)
        gabor_features = self._compute_gabor_like(gray)
        features.extend(gabor_features)
        
        return features
    
    def _extract_edge_features(self, img_array: np.ndarray) -> List[float]:
        """Extract edge-based features (fast)"""
        features = []
        
        # Convert to grayscale
        gray = np.mean(img_array, axis=2)
        
        # Sobel edge detection (simplified)
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Apply filters
        grad_x = self._apply_filter(gray, sobel_x)
        grad_y = self._apply_filter(gray, sobel_y)
        
        # Edge magnitude
        edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Edge statistics
        features.append(np.mean(edge_magnitude))
        features.append(np.std(edge_magnitude))
        features.append(np.max(edge_magnitude))
        
        # Edge histogram
        edge_hist, _ = np.histogram(edge_magnitude, bins=16, range=(0, np.max(edge_magnitude)))
        features.extend(edge_hist.tolist())
        
        return features
    
    def _extract_histogram_features(self, img_array: np.ndarray) -> List[float]:
        """Extract histogram features (fast)"""
        features = []
        
        # RGB histograms
        for channel in range(3):
            hist, _ = np.histogram(img_array[:, :, channel], bins=32, range=(0, 255))
            features.extend(hist.tolist())
        
        # HSV histograms (if needed)
        # hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        # for channel in range(3):
        #     hist, _ = np.histogram(hsv[:, :, channel], bins=16)
        #     features.extend(hist.tolist())
        
        return features
    
    def _extract_statistical_features(self, img_array: np.ndarray) -> List[float]:
        """Extract statistical features (fast)"""
        features = []
        
        # Overall statistics
        features.append(np.mean(img_array))
        features.append(np.std(img_array))
        features.append(np.var(img_array))
        features.append(np.max(img_array))
        features.append(np.min(img_array))
        
        # Per-channel statistics
        for channel in range(3):
            channel_data = img_array[:, :, channel]
            features.append(np.mean(channel_data))
            features.append(np.std(channel_data))
            features.append(np.var(channel_data))
            features.append(np.max(channel_data))
            features.append(np.min(channel_data))
        
        return features
    
    def _compute_lbp(self, gray_image: np.ndarray) -> List[float]:
        """Compute Local Binary Patterns (simplified)"""
        features = []
        
        # Simplified LBP computation
        height, width = gray_image.shape
        lbp_image = np.zeros((height-2, width-2), dtype=np.uint8)
        
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = gray_image[i, j]
                code = 0
                
                # 8-neighbor LBP
                neighbors = [
                    gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                    gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                    gray_image[i+1, j-1], gray_image[i, j-1]
                ]
                
                for k, neighbor in enumerate(neighbors):
                    if neighbor >= center:
                        code |= (1 << k)
                
                lbp_image[i-1, j-1] = code
        
        # LBP histogram
        lbp_hist, _ = np.histogram(lbp_image, bins=16, range=(0, 256))
        features.extend(lbp_hist.tolist())
        
        return features
    
    def _compute_gabor_like(self, gray_image: np.ndarray) -> List[float]:
        """Compute Gabor-like features (simplified)"""
        features = []
        
        # Simplified Gabor-like features using simple filters
        filters = [
            np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]]),  # Horizontal
            np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]]),   # Vertical
            np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]]),   # Diagonal
        ]
        
        for filter_kernel in filters:
            filtered = self._apply_filter(gray_image, filter_kernel)
            features.append(np.mean(filtered))
            features.append(np.std(filtered))
            features.append(np.max(filtered))
        
        return features
    
    def _apply_filter(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Apply 2D filter to image (simplified)"""
        height, width = image.shape
        kernel_height, kernel_width = kernel.shape
        
        # Pad image
        pad_height = kernel_height // 2
        pad_width = kernel_width // 2
        padded = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width)), mode='edge')
        
        # Apply filter
        filtered = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                filtered[i, j] = np.sum(padded[i:i+kernel_height, j:j+kernel_width] * kernel)
        
        return filtered
    
    def _skewness(self, data: np.ndarray) -> float:
        """Compute skewness of data"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to [0, 1] range"""
        min_val = np.min(features)
        max_val = np.max(features)
        if max_val - min_val == 0:
            return features
        return (features - min_val) / (max_val - min_val)
    
    def compute_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Compute cosine similarity between feature vectors"""
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def fast_search(self, query_image_bytes: bytes, database_features: List[Dict], top_k: int = 5) -> List[Dict]:
        """Fast similarity search (<5 minutes)"""
        start_time = time.time()
        
        try:
            # Extract features from query image
            query_features = self.extract_fast_features(query_image_bytes)
            
            # Compute similarities with database
            similarities = []
            for i, db_item in enumerate(database_features):
                similarity = self.compute_similarity(query_features, db_item['features'])
                similarities.append({
                    'index': i,
                    'similarity': similarity,
                    'item': db_item
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top-k results
            results = similarities[:top_k]
            
            search_time = time.time() - start_time
            logger.info(f"Fast search completed in {search_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Fast search failed: {e}")
            return []
    
    def create_mock_database(self, size: int = 1000) -> List[Dict]:
        """Create mock database for testing"""
        database = []
        
        conditions = ['Acne', 'Dry Skin', 'Oily Skin', 'Sensitive Skin', 'Aging Skin']
        treatments = [
            'Gentle cleanser and spot treatment',
            'Hydrating moisturizer',
            'Oil-control products',
            'Fragrance-free products',
            'Anti-aging serum'
        ]
        
        for i in range(size):
            # Generate random features
            features = np.random.rand(512).astype(np.float32)
            features = self._normalize_features(features)
            
            condition_idx = i % len(conditions)
            treatment_idx = i % len(treatments)
            
            database.append({
                'id': f'mock_{i}',
                'features': features,
                'condition': conditions[condition_idx],
                'treatment': treatments[treatment_idx],
                'confidence': 0.7 + (i % 3) * 0.1
            })
        
        return database

# Global instance for caching
fast_embedding_service = FastEmbeddingService() 