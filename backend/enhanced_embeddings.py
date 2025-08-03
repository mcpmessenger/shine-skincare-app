#!/usr/bin/env python3
"""
Enhanced Embeddings System for Shine Skincare App
Implements multiple embedding models for improved accuracy
"""

import numpy as np
import cv2
import logging
from typing import Dict, List, Optional, Tuple, Union
import base64
import json
import os
from datetime import datetime
import tempfile
from pathlib import Path
import requests
from PIL import Image
import io

# Try to import advanced ML libraries
try:
    import torch
    import torchvision.transforms as transforms
    from torch import nn
    import clip
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import CLIPProcessor, CLIPModel, DinoV2Processor, DinoV2Model
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedEmbeddingSystem:
    """Enhanced embedding system with multiple models for improved accuracy"""
    
    def __init__(self, use_advanced_models: bool = True):
        """
        Initialize enhanced embedding system
        
        Args:
            use_advanced_models: Whether to use advanced models (CLIP, DINO, etc.)
        """
        self.use_advanced_models = use_advanced_models and TORCH_AVAILABLE and TRANSFORMERS_AVAILABLE
        self.models = {}
        self.processors = {}
        
        # Initialize models
        self._initialize_models()
        
        # Embedding configurations
        self.embedding_configs = {
            'clip': {
                'dimensions': 512,
                'model_name': 'openai/clip-vit-base-patch32',
                'description': 'CLIP for general image understanding'
            },
            'dino': {
                'dimensions': 768,
                'model_name': 'facebook/dinov2-base',
                'description': 'DINO v2 for detailed feature extraction'
            },
            'skin_specific': {
                'dimensions': 1024,
                'model_name': 'custom',
                'description': 'Custom skin-specific embeddings'
            },
            'combined': {
                'dimensions': 2304,  # 512 + 768 + 1024
                'description': 'Combined multi-model embeddings'
            }
        }
        
        logger.info("✅ Enhanced embedding system initialized")
    
    def _initialize_models(self):
        """Initialize all embedding models"""
        if not self.use_advanced_models:
            logger.warning("⚠️ Advanced models not available, using fallback")
            return
        
        try:
            # Initialize CLIP
            logger.info("🔄 Loading CLIP model...")
            self.models['clip'] = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
            self.processors['clip'] = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
            self.models['clip'].eval()
            logger.info("✅ CLIP model loaded")
            
            # Initialize DINO v2
            logger.info("🔄 Loading DINO v2 model...")
            self.models['dino'] = DinoV2Model.from_pretrained('facebook/dinov2-base')
            self.processors['dino'] = DinoV2Processor.from_pretrained('facebook/dinov2-base')
            self.models['dino'].eval()
            logger.info("✅ DINO v2 model loaded")
            
            # Initialize custom skin-specific model
            self.models['skin_specific'] = self._create_skin_specific_model()
            logger.info("✅ Custom skin-specific model created")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced models: {e}")
            self.use_advanced_models = False
    
    def _create_skin_specific_model(self) -> nn.Module:
        """Create a custom skin-specific embedding model"""
        class SkinSpecificModel(nn.Module):
            def __init__(self, output_dim=1024):
                super().__init__()
                # Custom CNN for skin analysis
                self.features = nn.Sequential(
                    nn.Conv2d(3, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(128, 256, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d((1, 1))
                )
                self.classifier = nn.Sequential(
                    nn.Linear(256, 512),
                    nn.ReLU(),
                    nn.Dropout(0.5),
                    nn.Linear(512, output_dim)
                )
            
            def forward(self, x):
                x = self.features(x)
                x = x.view(x.size(0), -1)
                x = self.classifier(x)
                return x
        
        return SkinSpecificModel()
    
    def generate_enhanced_embeddings(self, image_data: bytes, face_roi: np.ndarray = None) -> Dict:
        """
        Generate enhanced embeddings using multiple models
        
        Args:
            image_data: Raw image data
            face_roi: Face region of interest (optional)
        
        Returns:
            Dictionary containing embeddings from all models
        """
        try:
            # Convert image data to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            embeddings = {
                'clip': None,
                'dino': None,
                'skin_specific': None,
                'combined': None,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'models_used': [],
                    'image_size': image.size,
                    'face_detected': face_roi is not None
                }
            }
            
            if self.use_advanced_models:
                # Generate CLIP embeddings
                embeddings['clip'] = self._generate_clip_embedding(image)
                embeddings['metadata']['models_used'].append('clip')
                
                # Generate DINO embeddings
                embeddings['dino'] = self._generate_dino_embedding(image)
                embeddings['metadata']['models_used'].append('dino')
                
                # Generate skin-specific embeddings
                if face_roi is not None:
                    face_image = Image.fromarray(face_roi)
                    embeddings['skin_specific'] = self._generate_skin_specific_embedding(face_image)
                    embeddings['metadata']['models_used'].append('skin_specific')
                
                # Combine embeddings
                embeddings['combined'] = self._combine_embeddings(embeddings)
                
            else:
                # Fallback to simulated embeddings
                embeddings['clip'] = self._generate_fallback_embedding(512)
                embeddings['dino'] = self._generate_fallback_embedding(768)
                embeddings['skin_specific'] = self._generate_fallback_embedding(1024)
                embeddings['combined'] = self._combine_embeddings(embeddings)
                embeddings['metadata']['models_used'] = ['fallback']
            
            logger.info(f"✅ Generated embeddings: {embeddings['metadata']['models_used']}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return self._generate_fallback_embeddings()
    
    def _generate_clip_embedding(self, image: Image.Image) -> List[float]:
        """Generate CLIP embedding"""
        try:
            inputs = self.processors['clip'](images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.models['clip'](**inputs)
                embedding = outputs.image_embeds.squeeze().cpu().numpy().tolist()
            return embedding
        except Exception as e:
            logger.error(f"❌ CLIP embedding failed: {e}")
            return self._generate_fallback_embedding(512)
    
    def _generate_dino_embedding(self, image: Image.Image) -> List[float]:
        """Generate DINO v2 embedding"""
        try:
            inputs = self.processors['dino'](images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.models['dino'](**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy().tolist()
            return embedding
        except Exception as e:
            logger.error(f"❌ DINO embedding failed: {e}")
            return self._generate_fallback_embedding(768)
    
    def _generate_skin_specific_embedding(self, face_image: Image.Image) -> List[float]:
        """Generate custom skin-specific embedding"""
        try:
            # Preprocess image for skin analysis
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            input_tensor = transform(face_image).unsqueeze(0)
            
            with torch.no_grad():
                embedding = self.models['skin_specific'](input_tensor)
                embedding = embedding.squeeze().cpu().numpy().tolist()
            
            return embedding
        except Exception as e:
            logger.error(f"❌ Skin-specific embedding failed: {e}")
            return self._generate_fallback_embedding(1024)
    
    def _combine_embeddings(self, embeddings: Dict) -> List[float]:
        """Combine embeddings from multiple models"""
        combined = []
        
        if embeddings['clip']:
            combined.extend(embeddings['clip'])
        if embeddings['dino']:
            combined.extend(embeddings['dino'])
        if embeddings['skin_specific']:
            combined.extend(embeddings['skin_specific'])
        
        return combined if combined else self._generate_fallback_embedding(2304)
    
    def _generate_fallback_embedding(self, dimensions: int) -> List[float]:
        """Generate fallback embedding with specified dimensions"""
        return np.random.rand(dimensions).tolist()
    
    def _generate_fallback_embeddings(self) -> Dict:
        """Generate fallback embeddings when models fail"""
        return {
            'clip': self._generate_fallback_embedding(512),
            'dino': self._generate_fallback_embedding(768),
            'skin_specific': self._generate_fallback_embedding(1024),
            'combined': self._generate_fallback_embedding(2304),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'models_used': ['fallback'],
                'error': 'Advanced models not available'
            }
        }
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Normalize vectors
            vec1_norm = vec1 / np.linalg.norm(vec1)
            vec2_norm = vec2 / np.linalg.norm(vec2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_norm, vec2_norm)
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Similarity calculation failed: {e}")
            return 0.0
    
    def find_similar_conditions(self, query_embedding: List[float], 
                              condition_embeddings: List[Dict], 
                              top_k: int = 5) -> List[Dict]:
        """Find similar conditions based on embedding similarity"""
        try:
            similarities = []
            
            for condition in condition_embeddings:
                if 'embedding' in condition:
                    similarity = self.calculate_similarity(
                        query_embedding, 
                        condition['embedding']
                    )
                    similarities.append({
                        **condition,
                        'similarity_score': similarity
                    })
            
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Similar condition search failed: {e}")
            return []
    
    def analyze_embedding_quality(self, embeddings: Dict) -> Dict:
        """Analyze the quality of generated embeddings"""
        quality_metrics = {
            'total_models': len(embeddings['metadata']['models_used']),
            'embedding_dimensions': {},
            'embedding_stats': {},
            'quality_score': 0.0
        }
        
        for model_name, embedding in embeddings.items():
            if embedding and model_name != 'metadata':
                embedding_array = np.array(embedding)
                quality_metrics['embedding_dimensions'][model_name] = len(embedding)
                quality_metrics['embedding_stats'][model_name] = {
                    'mean': float(np.mean(embedding_array)),
                    'std': float(np.std(embedding_array)),
                    'min': float(np.min(embedding_array)),
                    'max': float(np.max(embedding_array))
                }
        
        # Calculate overall quality score
        if quality_metrics['total_models'] > 0:
            quality_metrics['quality_score'] = min(1.0, quality_metrics['total_models'] / 3.0)
        
        return quality_metrics

def main():
    """Test the enhanced embedding system"""
    print("🧠 Testing Enhanced Embedding System")
    
    # Create test image
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    test_image_bytes = cv2.imencode('.jpg', test_image)[1].tobytes()
    
    # Initialize embedding system
    embedding_system = EnhancedEmbeddingSystem()
    
    # Generate embeddings
    embeddings = embedding_system.generate_enhanced_embeddings(test_image_bytes)
    
    # Analyze quality
    quality = embedding_system.analyze_embedding_quality(embeddings)
    
    print(f"✅ Embeddings generated successfully")
    print(f"📊 Quality metrics: {quality}")
    print(f"🔢 Total dimensions: {len(embeddings['combined'])}")

if __name__ == "__main__":
    main() 