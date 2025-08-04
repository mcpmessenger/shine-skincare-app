#!/usr/bin/env python3
"""
UTKFace Integration for Demographically-Normalized Healthy Image Embeddings
Implements the technical guide for integrating UTKFace dataset into Shine Skincare App
"""

import os
import numpy as np
import pandas as pd
import cv2
import logging
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image
import json
from pathlib import Path
import requests
from scipy.spatial.distance import cosine
from datetime import datetime

# Try to import TensorFlow/Keras for embedding models
try:
    import tensorflow as tf
    from tensorflow.keras.applications import ResNet50, MobileNetV2
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import GlobalAveragePooling2D
    from tensorflow.keras.preprocessing import image
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Install with: pip install tensorflow")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UTKFaceIntegration:
    """UTKFace integration for demographically-normalized healthy image embeddings"""
    
    def __init__(self, data_dir: str = "data/utkface", use_tensorflow: bool = True):
        """
        Initialize UTKFace integration system
        
        Args:
            data_dir: Directory containing UTKFace dataset
            use_tensorflow: Whether to use TensorFlow for embeddings
        """
        self.data_dir = Path(data_dir)
        self.raw_images_dir = self.data_dir / "raw_images"
        self.use_tensorflow = use_tensorflow and TENSORFLOW_AVAILABLE
        
        # Initialize embedding model
        self.embedding_model = None
        if self.use_tensorflow:
            self._initialize_embedding_model()
        
        # Demographic baselines storage
        self.demographic_baselines = {}
        self.metadata_df = None
        
        # Age binning configuration
        self.age_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120]
        self.age_labels = [f'{i}-{i+9}' for i in range(0, 100, 10)] + ['100+']
        
        # Ethnicity mapping
        self.ethnicity_mapping = {
            0: "White",
            1: "Black", 
            2: "Asian",
            3: "Indian",
            4: "Others"
        }
        
        # Gender mapping
        self.gender_mapping = {
            0: "Male",
            1: "Female"
        }
        
        logger.info("✅ UTKFace integration system initialized")
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model (ResNet50 by default)"""
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
    
    def verify_images(self, image_dir: str) -> List[str]:
        """
        Verify image integrity in the dataset
        
        Args:
            image_dir: Directory containing images to verify
            
        Returns:
            List of corrupted file paths
        """
        corrupted_files = []
        image_dir_path = Path(image_dir)
        
        if not image_dir_path.exists():
            logger.error(f"Image directory does not exist: {image_dir}")
            return corrupted_files
        
        logger.info(f"🔍 Verifying images in {image_dir}...")
        
        for filename in image_dir_path.iterdir():
            if filename.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                try:
                    with Image.open(filename) as img:
                        img.verify()  # Verify file integrity
                    img.close()
                except Exception as e:
                    logger.warning(f"Corrupted file detected: {filename} - {e}")
                    corrupted_files.append(str(filename))
        
        logger.info(f"✅ Image verification complete. Found {len(corrupted_files)} corrupted files.")
        return corrupted_files
    
    def extract_utkface_metadata(self, image_dir: str) -> pd.DataFrame:
        """
        Extract metadata from UTKFace filenames
        
        Args:
            image_dir: Directory containing UTKFace images
            
        Returns:
            DataFrame with extracted metadata
        """
        data = []
        image_dir_path = Path(image_dir)
        
        if not image_dir_path.exists():
            logger.error(f"Image directory does not exist: {image_dir}")
            return pd.DataFrame()
        
        logger.info(f"🔍 Extracting metadata from {image_dir}...")
        
        for filename in image_dir_path.iterdir():
            if filename.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                # Parse filename: [age]_[gender]_[ethnicity]_[date&time].jpg
                parts = filename.stem.split('_')
                
                if len(parts) >= 4:
                    try:
                        age = int(parts[0])
                        gender = int(parts[1])
                        ethnicity = int(parts[2])
                        
                        data.append({
                            'filename': filename.name,
                            'age': age,
                            'gender': gender,
                            'ethnicity': ethnicity,
                            'filepath': str(filename)
                        })
                    except ValueError as e:
                        logger.warning(f"Skipping malformed filename: {filename.name} - {e}")
                else:
                    logger.warning(f"Skipping filename with insufficient parts: {filename.name}")
        
        df = pd.DataFrame(data)
        logger.info(f"✅ Metadata extraction complete. Found {len(df)} valid images.")
        return df
    
    def preprocess_face_image(self, image_path: str, target_size: Tuple[int, int] = (224, 224), 
                             normalize_mean_std: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """
        Preprocess face image for embedding generation
        
        Args:
            image_path: Path to the image file
            target_size: Target size for resizing
            normalize_mean_std: Optional mean/std for normalization
            
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
            
            # Apply additional normalization if specified (e.g., ImageNet normalization)
            if normalize_mean_std:
                mean, std = normalize_mean_std
                img = (img - mean) / std
            
            return img
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return None
    
    def generate_embeddings(self, metadata_df: pd.DataFrame, image_dir: str, 
                           batch_size: int = 16) -> Tuple[np.ndarray, List[Dict]]:
        """
        Generate embeddings for a set of images
        
        Args:
            metadata_df: DataFrame with image metadata
            image_dir: Directory containing images
            batch_size: Batch size for processing
            
        Returns:
            Tuple of (embeddings array, labels list)
        """
        if self.embedding_model is None:
            logger.error("Embedding model not available")
            return np.array([]), []
        
        embeddings = []
        labels = []
        total_images = len(metadata_df)
        processed_count = 0
        failed_count = 0
        
        logger.info(f"🔄 Generating embeddings for {total_images} images...")
        logger.info(f"📊 Processing in batches of {batch_size} images")
        
        # Process images in batches
        for i in range(0, total_images, batch_size):
            batch_start = i + 1
            batch_end = min(i + batch_size, total_images)
            batch_df = metadata_df.iloc[i:i+batch_size]
            
            logger.info(f"📦 Processing batch {batch_start}-{batch_end} of {total_images} ({(batch_end/total_images)*100:.1f}%)")
            
            batch_images = []
            batch_labels = []
            batch_failed = 0
            
            for idx, (_, row) in enumerate(batch_df.iterrows()):
                image_path = os.path.join(image_dir, row['filename'])
                processed_img = self.preprocess_face_image(image_path)
                
                if processed_img is not None:
                    batch_images.append(processed_img)
                    batch_labels.append(row.to_dict())
                else:
                    batch_failed += 1
                    logger.warning(f"❌ Could not preprocess {row['filename']}")
            
            if batch_images:
                try:
                    # Convert to numpy array and predict embeddings
                    batch_array = np.array(batch_images)
                    logger.info(f"🧠 Generating embeddings for {len(batch_images)} images...")
                    batch_embeddings = self.embedding_model.predict(batch_array, verbose=0)
                    
                    embeddings.extend(batch_embeddings)
                    labels.extend(batch_labels)
                    processed_count += len(batch_images)
                    failed_count += batch_failed
                    
                    logger.info(f"✅ Batch {batch_start}-{batch_end} complete: {len(batch_images)} embeddings generated")
                    logger.info(f"📈 Progress: {processed_count}/{total_images} images processed ({processed_count/total_images*100:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing batch {batch_start}-{batch_end}: {e}")
                    failed_count += len(batch_images)
            else:
                logger.warning(f"⚠️ No valid images in batch {batch_start}-{batch_end}")
                failed_count += len(batch_df)
        
        logger.info(f"🎉 Embedding generation complete!")
        logger.info(f"✅ Successfully processed: {processed_count} images")
        logger.info(f"❌ Failed to process: {failed_count} images")
        logger.info(f"📊 Success rate: {(processed_count/total_images)*100:.1f}%")
        
        return np.array(embeddings), labels
    
    def create_demographic_baselines(self, embeddings: np.ndarray, labels_df: pd.DataFrame) -> Dict:
        """
        Create demographically-stratified healthy baselines
        
        Args:
            embeddings: Array of embeddings
            labels_df: DataFrame with demographic labels
            
        Returns:
            Dictionary mapping demographic keys to baseline embeddings
        """
        # Create age bins
        labels_df['age_bin'] = pd.cut(
            labels_df['age'], 
            bins=self.age_bins, 
            right=False, 
            labels=self.age_labels
        )
        
        # Create demographic key
        labels_df['demographic_key'] = (
            labels_df['age_bin'].astype(str) + '_' +
            labels_df['gender'].astype(str) + '_' +
            labels_df['ethnicity'].astype(str)
        )
        
        demographic_baselines = {}
        
        logger.info("🔄 Creating demographic baselines...")
        
        total_groups = len(labels_df.groupby('demographic_key'))
        processed_groups = 0
        
        for key, group_df in labels_df.groupby('demographic_key'):
            indices = group_df.index.tolist()
            if indices and len(indices) > 0:
                group_embeddings = embeddings[indices]
                demographic_baselines[key] = np.mean(group_embeddings, axis=0)
                processed_groups += 1
                logger.info(f"📊 Created baseline for {key}: {len(indices)} samples ({processed_groups}/{total_groups} groups)")
        
        logger.info(f"✅ Created {len(demographic_baselines)} demographic baselines")
        logger.info(f"📈 Successfully processed {processed_groups}/{total_groups} demographic groups")
        return demographic_baselines
    
    def load_demographic_baselines(self, baselines_path: str) -> bool:
        """
        Load pre-computed demographic baselines
        
        Args:
            baselines_path: Path to the baselines file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(baselines_path):
                self.demographic_baselines = np.load(baselines_path, allow_pickle=True).item()
                logger.info(f"✅ Loaded {len(self.demographic_baselines)} demographic baselines")
                return True
            else:
                logger.warning(f"Baselines file not found: {baselines_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading baselines: {e}")
            return False
    
    def save_demographic_baselines(self, baselines: Dict, output_path: str) -> bool:
        """
        Save demographic baselines to file
        
        Args:
            baselines: Dictionary of demographic baselines
            output_path: Path to save the baselines
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            np.save(output_path, baselines)
            logger.info(f"✅ Saved {len(baselines)} demographic baselines to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving baselines: {e}")
            return False
    
    def get_demographic_key(self, age: int, gender: int, ethnicity: int) -> str:
        """
        Generate demographic key for given attributes
        
        Args:
            age: Age of the person
            gender: Gender (0=male, 1=female)
            ethnicity: Ethnicity (0-4 as per UTKFace mapping)
            
        Returns:
            Demographic key string
        """
        # Map age to bin
        age_bin = pd.cut([age], bins=self.age_bins, right=False, labels=self.age_labels)[0]
        return f"{age_bin}_{gender}_{ethnicity}"
    
    def get_relevant_baseline(self, age: int, gender: int, ethnicity: int) -> Optional[np.ndarray]:
        """
        Get the most relevant demographic baseline for given attributes
        
        Args:
            age: Age of the person
            gender: Gender (0=male, 1=female)
            ethnicity: Ethnicity (0-4 as per UTKFace mapping)
            
        Returns:
            Relevant baseline embedding or None if not found
        """
        demographic_key = self.get_demographic_key(age, gender, ethnicity)
        
        if demographic_key in self.demographic_baselines:
            return self.demographic_baselines[demographic_key]
        else:
            logger.warning(f"No baseline found for demographic key: {demographic_key}")
            # Return overall mean baseline as fallback
            if self.demographic_baselines:
                return np.mean(list(self.demographic_baselines.values()), axis=0)
            return None
    
    def calculate_health_score(self, user_embedding: np.ndarray, baseline_embedding: np.ndarray) -> float:
        """
        Calculate health score based on similarity to healthy baseline
        
        Args:
            user_embedding: User's image embedding
            baseline_embedding: Healthy baseline embedding
            
        Returns:
            Health score (0-100)
        """
        try:
            # Calculate cosine similarity
            similarity = 1 - cosine(user_embedding, baseline_embedding)
            
            # Scale to 0-100 range
            health_score = max(0, min(100, similarity * 100))
            
            return health_score
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50.0  # Default fallback score
    
    def analyze_skin_demographic(self, image_data: bytes, age: int, gender: int, 
                                ethnicity: int) -> Dict:
        """
        Analyze skin image with demographic normalization
        
        Args:
            image_data: Image data as bytes
            age: Age of the person
            gender: Gender (0=male, 1=female)
            ethnicity: Ethnicity (0-4 as per UTKFace mapping)
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {
                    'status': 'error',
                    'message': 'Could not decode image data'
                }
            
            # Preprocess image
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (224, 224))
            img_normalized = img_resized.astype(np.float32) / 255.0
            
            # Generate embedding
            if self.embedding_model is None:
                return {
                    'status': 'error',
                    'message': 'Embedding model not available'
                }
            
            user_embedding = self.embedding_model.predict(
                np.expand_dims(img_normalized, axis=0), 
                verbose=0
            )[0]
            
            # Get relevant baseline
            baseline_embedding = self.get_relevant_baseline(age, gender, ethnicity)
            
            if baseline_embedding is None:
                return {
                    'status': 'error',
                    'message': 'No suitable demographic baseline found'
                }
            
            # Calculate health score
            health_score = self.calculate_health_score(user_embedding, baseline_embedding)
            
            # Determine assessment
            if health_score >= 85:
                assessment = "Healthy"
            elif health_score >= 70:
                assessment = "Good"
            elif health_score >= 50:
                assessment = "Needs attention"
            else:
                assessment = "Consult professional"
            
            demographic_key = self.get_demographic_key(age, gender, ethnicity)
            
            return {
                'status': 'success',
                'health_score': round(health_score, 2),
                'assessment': assessment,
                'demographic_baseline_used': demographic_key,
                'age': age,
                'gender': self.gender_mapping.get(gender, "Unknown"),
                'ethnicity': self.ethnicity_mapping.get(ethnicity, "Unknown"),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in demographic analysis: {e}")
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }
    
    def download_utkface_dataset(self, output_dir: str = None) -> bool:
        """
        Download UTKFace dataset (placeholder for actual implementation)
        
        Args:
            output_dir: Directory to save the dataset
            
        Returns:
            True if successful, False otherwise
        """
        if output_dir is None:
            output_dir = str(self.data_dir)
        
        logger.info("⚠️ Dataset download not implemented. Please download UTKFace manually.")
        logger.info("Download from: https://susanqq.github.io/UTKFace/")
        logger.info(f"Extract to: {output_dir}/raw_images/")
        
        return False
    
    def setup_demographic_baselines(self, force_rebuild: bool = False) -> bool:
        """
        Set up demographic baselines from UTKFace dataset
        
        Args:
            force_rebuild: Whether to rebuild baselines even if they exist
            
        Returns:
            True if successful, False otherwise
        """
        baselines_path = self.data_dir / "demographic_baselines.npy"
        metadata_path = self.data_dir / "utkface_metadata.csv"
        
        # Check if baselines already exist
        if not force_rebuild and baselines_path.exists() and metadata_path.exists():
            logger.info("📁 Found existing baselines, loading...")
            self.metadata_df = pd.read_csv(metadata_path)
            return self.load_demographic_baselines(str(baselines_path))
        
        # Check if raw images exist
        if not self.raw_images_dir.exists():
            logger.error(f"Raw images directory not found: {self.raw_images_dir}")
            logger.info("Please download UTKFace dataset and extract to the raw_images directory")
            return False
        
        # Verify images
        corrupted_files = self.verify_images(str(self.raw_images_dir))
        if corrupted_files:
            logger.warning(f"Found {len(corrupted_files)} corrupted files")
        
        # Extract metadata
        self.metadata_df = self.extract_utkface_metadata(str(self.raw_images_dir))
        if self.metadata_df.empty:
            logger.error("No valid metadata extracted")
            return False
        
        # Save metadata
        self.metadata_df.to_csv(metadata_path, index=False)
        logger.info(f"✅ Saved metadata to {metadata_path}")
        
        # Generate embeddings
        if self.embedding_model is None:
            logger.error("Embedding model not available")
            return False
        
        embeddings, labels = self.generate_embeddings(
            self.metadata_df, 
            str(self.raw_images_dir)
        )
        
        if len(embeddings) == 0:
            logger.error("No embeddings generated")
            return False
        
        # Create demographic baselines
        self.demographic_baselines = self.create_demographic_baselines(
            embeddings, 
            pd.DataFrame(labels)
        )
        
        # Save baselines
        success = self.save_demographic_baselines(
            self.demographic_baselines, 
            str(baselines_path)
        )
        
        if success:
            logger.info("✅ Demographic baselines setup complete")
            return True
        else:
            logger.error("❌ Failed to save demographic baselines")
            return False


def main():
    """Main function for testing UTKFace integration"""
    # Initialize UTKFace integration
    utkface = UTKFaceIntegration()
    
    # Set up demographic baselines
    success = utkface.setup_demographic_baselines()
    
    if success:
        print("✅ UTKFace integration setup complete")
        print(f"📊 Available demographic baselines: {len(utkface.demographic_baselines)}")
        
        # Print some example baselines
        for key in list(utkface.demographic_baselines.keys())[:5]:
            print(f"  - {key}")
    else:
        print("❌ UTKFace integration setup failed")


if __name__ == "__main__":
    main() 