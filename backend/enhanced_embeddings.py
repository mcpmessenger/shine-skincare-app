#!/usr/bin/env python3
"""
Enhanced Embedding System for Shine Skincare App
Provides embedding functionality for skin condition analysis
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from datetime import datetime
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedEmbeddingSystem:
    """
    Enhanced embedding system for skin condition analysis
    Integrates with existing 103 demographic baselines and condition embeddings
    """

    def __init__(self):
        """Initialize the enhanced embedding system"""
        self.embedding_dimensions = 2048  # Match demographic baseline dimensions
        self.condition_embeddings = self._load_condition_embeddings()
        self.demographic_baselines = self._load_demographic_baselines()
        
        logger.info("✅ Enhanced embedding system initialized")

    def _load_condition_embeddings(self) -> Dict:
        """Load existing condition embeddings"""
        try:
            embeddings_path = Path(__file__).parent / "data" / "condition_embeddings.npy"
            if embeddings_path.exists():
                embeddings = np.load(str(embeddings_path), allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(embeddings)} condition embeddings")
                return embeddings
            else:
                logger.warning("⚠️ Condition embeddings file not found, using empty dict")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load condition embeddings: {e}")
            return {}

    def _load_demographic_baselines(self) -> Dict:
        """Load existing demographic baselines"""
        try:
            baselines_path = Path("data/utkface/demographic_baselines.npy")
            if baselines_path.exists():
                baselines = np.load(str(baselines_path), allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(baselines)} demographic baselines")
                return baselines
            else:
                logger.warning("⚠️ Demographic baselines file not found, using empty dict")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load demographic baselines: {e}")
            return {}

    def get_embedding_for_condition(self, condition: str) -> Optional[np.ndarray]:
        """Get embedding for a specific condition"""
        return self.condition_embeddings.get(condition)

    def get_baseline_for_demographics(self, demographics: Dict) -> Optional[np.ndarray]:
        """Get baseline for specific demographics"""
        # Create a key from demographics
        key = self._create_demographic_key(demographics)
        return self.demographic_baselines.get(key)

    def _create_demographic_key(self, demographics: Dict) -> str:
        """Create a key from demographic information"""
        age = demographics.get('age', 30)
        gender = demographics.get('gender', 0)
        ethnicity = demographics.get('ethnicity', 0)
        
        # Convert age to age range format used in baselines
        if age < 10:
            age_range = "0-9"
        elif age < 20:
            age_range = "10-19"
        elif age < 30:
            age_range = "20-29"
        elif age < 40:
            age_range = "30-39"
        elif age < 50:
            age_range = "40-49"
        elif age < 60:
            age_range = "50-59"
        elif age < 70:
            age_range = "60-69"
        elif age < 80:
            age_range = "70-79"
        else:
            age_range = "80+"
        
        return f"{age_range}_{gender}_{ethnicity}"

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Failed to calculate similarity: {e}")
            return 0.0

    def generate_enhanced_embeddings(self, image_data: bytes) -> Dict:
        """
        Generate enhanced embeddings for skin condition analysis
        """
        try:
            import traceback
            
            logger.info(f"🔍 Starting embedding generation with {len(image_data)} bytes")
            
            # Convert image bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            logger.info(f"🔍 Converted to numpy array with shape: {nparr.shape}")
            
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("❌ cv2.imdecode returned None")
                return {'error': 'Failed to decode image'}
            
            logger.info(f"🔍 Successfully decoded image with shape: {img.shape}")
            
            # Resize image for consistent processing
            img = cv2.resize(img, (224, 224))
            logger.info(f"🔍 Resized image to: {img.shape}")
            
            # Convert to grayscale for texture analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            logger.info(f"🔍 Converted to grayscale: {gray.shape}")
            
            # Extract features based on image characteristics
            features = []
            
            # 1. Color statistics (RGB channels)
            b, g, r = cv2.split(img)
            features.extend([
                np.mean(b), np.std(b), np.mean(g), np.std(g), np.mean(r), np.std(r)
            ])
            logger.info(f"🔍 Added color statistics: {len(features)} features")
            
            # 2. Texture features (GLCM-like)
            features.extend([
                np.mean(gray), np.std(gray), np.var(gray),
                np.percentile(gray, 25), np.percentile(gray, 75)
            ])
            logger.info(f"🔍 Added texture features: {len(features)} features")
            
            # 3. Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            logger.info(f"🔍 Added edge density: {len(features)} features")
            
            # 4. Local Binary Pattern-like features
            lbp_features = self._extract_lbp_features(gray)
            features.extend(lbp_features)
            logger.info(f"🔍 Added LBP features: {len(features)} features")
            
            # 5. Histogram features
            hist_features = self._extract_histogram_features(gray)
            features.extend(hist_features)
            logger.info(f"🔍 Added histogram features: {len(features)} features")
            
            # 6. Fill the rest with derived features to reach 2048 dimensions
            base_features = np.array(features)
            enhanced_embedding = np.zeros(2048, dtype=np.float32)
            
            # Add some randomization based on image characteristics
            np.random.seed(int(np.sum(base_features) * 1000) % 2**32)
            
            # Use the base features to seed the embedding with more image-specific characteristics
            for i in range(2048):
                if i < len(base_features):
                    enhanced_embedding[i] = base_features[i]
                else:
                    # Create derived features based on the base features with image-specific patterns
                    seed = i % len(base_features)
                    
                    # Add image-specific characteristics based on color and texture
                    color_factor = np.mean(base_features[:6]) if len(base_features) >= 6 else 0.5  # Color statistics
                    texture_factor = np.mean(base_features[6:17]) if len(base_features) >= 17 else 0.5  # Texture features
                    edge_factor = base_features[17] if len(base_features) > 17 else 0.5  # Edge density
                    
                    # Create more varied patterns based on image characteristics
                    pattern_factor = (color_factor * 0.4 + texture_factor * 0.4 + edge_factor * 0.2)
                    random_factor = np.random.uniform(0.7, 1.3)
                    
                    enhanced_embedding[i] = base_features[seed] * pattern_factor * random_factor
            
            # Normalize the embedding
            norm = np.linalg.norm(enhanced_embedding)
            if norm > 0:
                enhanced_embedding = enhanced_embedding / norm
            
            logger.info(f"✅ Generated embedding with {len(features)} base features, {len(enhanced_embedding)} total dimensions")
            
            return {
                'enhanced': enhanced_embedding.tolist(),
                'combined': enhanced_embedding.tolist(),
                'dimensions': len(enhanced_embedding),
                'normalized': True,
                'base_features_count': len(features)
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced embedding generation failed: {e}")
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}
    
    def _extract_lbp_features(self, gray_img: np.ndarray) -> List[float]:
        """Extract Local Binary Pattern-like features"""
        features = []
        
        # Simple texture analysis
        for radius in [1, 2, 3]:
            for x in range(0, gray_img.shape[0] - radius, radius):
                for y in range(0, gray_img.shape[1] - radius, radius):
                    if x + radius < gray_img.shape[0] and y + radius < gray_img.shape[1]:
                        patch = gray_img[x:x+radius, y:y+radius]
                        features.append(np.mean(patch))
                        features.append(np.std(patch))
                        if len(features) >= 50:  # Limit to prevent too many features
                            break
                if len(features) >= 50:
                    break
            if len(features) >= 50:
                break
        
        return features[:50]  # Return max 50 features
    
    def _extract_histogram_features(self, gray_img: np.ndarray) -> List[float]:
        """Extract histogram-based features"""
        features = []
        
        # Calculate histogram
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Extract histogram features
        features.extend([
            np.mean(hist),
            np.std(hist),
            np.percentile(hist, 25),
            np.percentile(hist, 50),
            np.percentile(hist, 75),
            np.max(hist),
            np.min(hist)
        ])
        
        # Add histogram bins (sampled)
        for i in range(0, 256, 16):  # Sample every 16th bin
            features.append(hist[i])
        
        return features

    def get_system_status(self) -> Dict:
        """Get system status"""
        return {
            'status': 'operational',
            'condition_embeddings_loaded': len(self.condition_embeddings),
            'demographic_baselines_loaded': len(self.demographic_baselines),
            'embedding_dimensions': self.embedding_dimensions,
            'available_conditions': list(self.condition_embeddings.keys()),
            'timestamp': datetime.now().isoformat()
        } 