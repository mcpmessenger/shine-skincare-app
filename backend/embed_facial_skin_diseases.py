#!/usr/bin/env python3
"""
Facial Skin Diseases Dataset Embedding Script
This script processes and embeds the facial skin diseases dataset for condition-specific analysis.
"""

import os
import sys
import numpy as np
import pandas as pd
import cv2
import logging
from typing import Dict, List, Optional, Tuple
from PIL import Image
import json
from pathlib import Path
from datetime import datetime

# Try to import TensorFlow/Keras for embedding models
try:
    import tensorflow as tf
    from tensorflow.keras.applications import ResNet50
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import GlobalAveragePooling2D
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Install with: pip install tensorflow")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacialSkinDiseasesEmbedder:
    """Embedder for facial skin diseases dataset"""
    
    def __init__(self, data_dir: str = "datasets/facial_skin_diseases/DATA", use_tensorflow: bool = True):
        """
        Initialize facial skin diseases embedder
        
        Args:
            data_dir: Directory containing facial skin diseases dataset
            use_tensorflow: Whether to use TensorFlow for embeddings
        """
        self.data_dir = Path(data_dir)
        self.use_tensorflow = use_tensorflow and TENSORFLOW_AVAILABLE
        
        # Initialize embedding model
        self.embedding_model = None
        if self.use_tensorflow:
            self._initialize_embedding_model()
        
        # Condition mapping
        self.condition_mapping = {
            'Acne': 'acne',
            'Actinic Keratosis': 'actinic_keratosis',
            'Basal Cell Carcinoma': 'basal_cell_carcinoma',
            'Eczemaa': 'eczema',  # Note: dataset has typo
            'Rosacea': 'rosacea',
            'Healthy': 'healthy'
        }
        
        # Embeddings storage
        self.condition_embeddings = {}
        self.condition_metadata = {}
        
        # Try to load existing embeddings
        self._load_existing_embeddings()
        
        logger.info("✅ Facial Skin Diseases Embedder initialized")
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model (ResNet50)"""
        try:
            logger.info("🔄 Loading embedding model (ResNet50)...")
            base_model = ResNet50(
                weights='imagenet', 
                include_top=False, 
                input_shape=(224, 224, 3)
            )
            
            # Add global average pooling to get fixed-size embeddings
            embedding_output = GlobalAveragePooling2D()(base_model.output)
            self.embedding_model = Model(inputs=base_model.input, outputs=embedding_output)
            self.embedding_model.trainable = False  # Freeze weights for feature extraction
            
            logger.info(f"✅ Embedding model loaded. Output shape: {self.embedding_model.output_shape}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
    
    def _load_existing_embeddings(self):
        """Load existing embeddings from saved files"""
        try:
            # Check for embeddings in data directory
            embeddings_file = Path("data/facial_skin_diseases/condition_embeddings.npy")
            metadata_file = Path("data/facial_skin_diseases/condition_metadata.csv")
            
            if embeddings_file.exists() and metadata_file.exists():
                logger.info("🔄 Loading existing facial skin diseases embeddings...")
                
                # Load embeddings
                embeddings_data = np.load(str(embeddings_file))
                
                # Load metadata
                metadata_df = pd.read_csv(str(metadata_file))
                
                # Group by condition
                for condition in metadata_df['condition'].unique():
                    condition_mask = metadata_df['condition'] == condition
                    condition_embeddings = embeddings_data[condition_mask]
                    condition_metadata = metadata_df[condition_mask].to_dict('records')
                    
                    self.condition_embeddings[condition] = condition_embeddings
                    self.condition_metadata[condition] = condition_metadata
                
                logger.info(f"✅ Loaded embeddings for {len(self.condition_embeddings)} conditions")
                for condition, embeddings in self.condition_embeddings.items():
                    logger.info(f"  - {condition}: {len(embeddings)} embeddings")
                
            else:
                logger.warning("No existing embeddings found. Run embed_all_conditions() to generate them.")
                
        except Exception as e:
            logger.error(f"Failed to load existing embeddings: {e}")
            logger.warning("Will need to generate embeddings from scratch")
    
    def preprocess_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224)) -> Optional[np.ndarray]:
        """
        Preprocess image for embedding generation
        
        Args:
            image_path: Path to the image file
            target_size: Target size for resizing
            
        Returns:
            Preprocessed image array or None if failed
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Could not read image: {image_path}")
                return None
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize image
            img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
            
            # Normalize to [0, 1]
            img = img.astype(np.float32) / 255.0
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def process_condition_directory(self, condition_dir: Path, condition_name: str) -> Tuple[List[np.ndarray], List[Dict]]:
        """
        Process all images in a condition directory
        
        Args:
            condition_dir: Directory containing images for a condition
            condition_name: Name of the condition
            
        Returns:
            Tuple of (embeddings list, metadata list)
        """
        embeddings = []
        metadata = []
        
        if not condition_dir.exists():
            logger.warning(f"Condition directory not found: {condition_dir}")
            return embeddings, metadata
        
        # Get all image files
        image_files = list(condition_dir.glob("*.jpg")) + list(condition_dir.glob("*.jpeg")) + list(condition_dir.glob("*.png"))
        
        logger.info(f"🔄 Processing {len(image_files)} images for condition: {condition_name}")
        
        for img_file in image_files:
            try:
                # Preprocess image
                processed_img = self.preprocess_image(str(img_file))
                
                if processed_img is not None:
                    # Generate embedding
                    if self.embedding_model is not None:
                        embedding = self.embedding_model.predict(
                            np.expand_dims(processed_img, axis=0), 
                            verbose=0
                        )[0]
                        
                        embeddings.append(embedding)
                        metadata.append({
                            'filename': img_file.name,
                            'condition': condition_name,
                            'filepath': str(img_file),
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        logger.error("Embedding model not available")
                        break
                else:
                    logger.warning(f"Failed to preprocess {img_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {img_file.name}: {e}")
        
        logger.info(f"✅ Processed {len(embeddings)} images for {condition_name}")
        return embeddings, metadata
    
    def embed_all_conditions(self) -> bool:
        """
        Embed all conditions in the facial skin diseases dataset
        
        Returns:
            True if successful, False otherwise
        """
        if self.embedding_model is None:
            logger.error("Embedding model not available")
            return False
        
        train_dir = self.data_dir / "train"
        test_dir = self.data_dir / "test"
        
        if not train_dir.exists():
            logger.error(f"Train directory not found: {train_dir}")
            return False
        
        all_embeddings = []
        all_metadata = []
        
        # Process each condition
        for condition_folder in train_dir.iterdir():
            if condition_folder.is_dir():
                condition_name = condition_folder.name
                mapped_condition = self.condition_mapping.get(condition_name, condition_name.lower())
                
                logger.info(f"🔄 Processing condition: {condition_name} -> {mapped_condition}")
                
                # Process training data
                train_embeddings, train_metadata = self.process_condition_directory(
                    condition_folder, mapped_condition
                )
                
                # Process test data if available
                test_condition_dir = test_dir / condition_name
                test_embeddings, test_metadata = [], []
                if test_condition_dir.exists():
                    test_embeddings, test_metadata = self.process_condition_directory(
                        test_condition_dir, mapped_condition
                    )
                
                # Combine train and test
                condition_embeddings = train_embeddings + test_embeddings
                condition_metadata = train_metadata + test_metadata
                
                if condition_embeddings:
                    # Store condition-specific data
                    self.condition_embeddings[mapped_condition] = np.array(condition_embeddings)
                    self.condition_metadata[mapped_condition] = condition_metadata
                    
                    # Add to overall data
                    all_embeddings.extend(condition_embeddings)
                    all_metadata.extend(condition_metadata)
                    
                    logger.info(f"✅ {mapped_condition}: {len(condition_embeddings)} embeddings")
                else:
                    logger.warning(f"⚠️ No embeddings generated for {mapped_condition}")
        
        # Save embeddings and metadata
        if all_embeddings:
            self._save_embeddings(all_embeddings, all_metadata)
            logger.info(f"🎉 Successfully embedded {len(all_embeddings)} images across {len(self.condition_embeddings)} conditions")
            return True
        else:
            logger.error("❌ No embeddings generated")
            return False
    
    def _save_embeddings(self, embeddings: List[np.ndarray], metadata: List[Dict]):
        """Save embeddings and metadata to files"""
        try:
            # Create output directory
            output_dir = Path("data/facial_skin_diseases")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save embeddings
            embeddings_array = np.array(embeddings)
            embeddings_path = output_dir / "condition_embeddings.npy"
            np.save(embeddings_path, embeddings_array)
            logger.info(f"✅ Saved embeddings to {embeddings_path}")
            
            # Save metadata
            metadata_df = pd.DataFrame(metadata)
            metadata_path = output_dir / "condition_metadata.csv"
            metadata_df.to_csv(metadata_path, index=False)
            logger.info(f"✅ Saved metadata to {metadata_path}")
            
            # Save condition-specific data
            condition_data = {
                'embeddings': {k: v.tolist() for k, v in self.condition_embeddings.items()},
                'metadata': self.condition_metadata,
                'condition_mapping': self.condition_mapping,
                'total_images': len(embeddings),
                'total_conditions': len(self.condition_embeddings),
                'embedding_dimensions': embeddings_array.shape[1],
                'timestamp': datetime.now().isoformat()
            }
            
            condition_data_path = output_dir / "condition_data.json"
            with open(condition_data_path, 'w') as f:
                json.dump(condition_data, f, indent=2)
            logger.info(f"✅ Saved condition data to {condition_data_path}")
            
            # Print summary
            logger.info("📊 Embedding Summary:")
            for condition, embeddings in self.condition_embeddings.items():
                logger.info(f"  - {condition}: {len(embeddings)} images")
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
    
    def get_condition_analysis(self, user_embedding: np.ndarray) -> Dict:
        """
        Analyze user image against condition embeddings
        
        Args:
            user_embedding: User's image embedding
            
        Returns:
            Analysis results dictionary
        """
        try:
            from scipy.spatial.distance import cosine
            
            results = {}
            
            for condition, condition_embeddings in self.condition_embeddings.items():
                # Calculate similarities to all images in this condition
                similarities = []
                for condition_embedding in condition_embeddings:
                    similarity = 1 - cosine(user_embedding, condition_embedding)
                    similarities.append(similarity)
                
                # Calculate average similarity and confidence
                avg_similarity = np.mean(similarities)
                confidence = np.std(similarities)  # Lower std = higher confidence
                
                results[condition] = {
                    'similarity': float(avg_similarity),
                    'confidence': float(confidence),
                    'sample_count': len(condition_embeddings)
                }
            
            # Find best matching condition
            best_condition = max(results.keys(), key=lambda k: results[k]['similarity'])
            best_similarity = results[best_condition]['similarity']
            
            # Determine assessment
            if best_similarity >= 0.8:
                assessment = f"High similarity to {best_condition}"
            elif best_similarity >= 0.6:
                assessment = f"Moderate similarity to {best_condition}"
            else:
                assessment = "Low similarity to all conditions"
            
            return {
                'status': 'success',
                'best_match': best_condition,
                'best_similarity': best_similarity,
                'assessment': assessment,
                'condition_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in condition analysis: {e}")
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }


def main():
    """Main function for embedding facial skin diseases dataset"""
    print("🔄 Starting Facial Skin Diseases Dataset Embedding...")
    
    # Initialize embedder
    embedder = FacialSkinDiseasesEmbedder()
    
    # Embed all conditions
    success = embedder.embed_all_conditions()
    
    if success:
        print("✅ Facial skin diseases embedding completed successfully!")
        print(f"📊 Total conditions processed: {len(embedder.condition_embeddings)}")
        print("Available conditions:")
        for condition in embedder.condition_embeddings.keys():
            print(f"  - {condition}")
    else:
        print("❌ Facial skin diseases embedding failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 