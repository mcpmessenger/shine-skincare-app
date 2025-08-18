#!/usr/bin/env python3
"""
Embed Kris Directory Faces into UTKFace Dataset
Create a hybrid system that combines existing UTKFace embeddings with Kris-specific faces
"""

import os
import cv2
import numpy as np
from pathlib import Path
import pickle
import json
import logging
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrisFaceEmbedder:
    """Embed Kris directory faces and integrate with UTKFace dataset"""
    
    def __init__(self):
        self.kris_dir = Path("../Kris")
        self.utkface_embeddings_path = None
        self.utkface_metadata_path = None
        self.utkface_embeddings = None
        self.utkface_metadata = None
        self.kris_embeddings = []
        self.kris_metadata = []
        
    def find_utkface_files(self):
        """Find existing UTKFace embeddings and metadata"""
        possible_paths = [
            Path('./swan-embeddings/utkface_cnn_embeddings.pkl.gz'),
            Path('../swan-embeddings/utkface_cnn_embeddings.pkl.gz'),
            Path('./backend/swan-embeddings/utkface_cnn_embeddings.pkl.gz'),
            Path('swan-embeddings/utkface_cnn_embeddings.pkl.gz')
        ]
        
        for path in possible_paths:
            if path.exists():
                self.utkface_embeddings_path = path
                logger.info(f"✅ Found UTKFace embeddings at: {path.absolute()}")
                break
        
        if not self.utkface_embeddings_path:
            logger.error("❌ UTKFace embeddings not found")
            return False
        
        # Find metadata
        metadata_path = self.utkface_embeddings_path.parent / "utkface_metadata.json"
        if metadata_path.exists():
            self.utkface_metadata_path = metadata_path
            logger.info(f"✅ Found UTKFace metadata at: {metadata_path.absolute()}")
        else:
            logger.warning("⚠️ UTKFace metadata not found, will create new")
        
        return True
    
    def load_utkface_data(self):
        """Load existing UTKFace embeddings and metadata"""
        try:
            import gzip
            
            # Load embeddings
            with gzip.open(self.utkface_embeddings_path, 'rb') as f:
                self.utkface_embeddings = pickle.load(f)
            
            # Load metadata
            if self.utkface_metadata_path and self.utkface_metadata_path.exists():
                with open(self.utkface_metadata_path, 'r') as f:
                    raw_metadata = json.load(f)
                    
                    # Handle different metadata formats
                    if isinstance(raw_metadata, dict):
                        self.utkface_metadata = raw_metadata
                    elif isinstance(raw_metadata, list):
                        # Convert list to dictionary format
                        self.utkface_metadata = {
                            'dataset_info': {
                                'name': 'UTKFace Original',
                                'description': 'Original UTKFace dataset',
                                'total_samples': len(raw_metadata),
                                'feature_dimensions': self.utkface_embeddings.shape[1] if self.utkface_embeddings is not None else 0
                            },
                            'samples': raw_metadata
                        }
                    else:
                        # Unknown format, create default
                        self.utkface_metadata = {
                            'dataset_info': {
                                'name': 'UTKFace Unknown Format',
                                'description': 'UTKFace dataset with unknown metadata format',
                                'total_samples': len(self.utkface_embeddings),
                                'feature_dimensions': self.utkface_embeddings.shape[1] if self.utkface_embeddings is not None else 0
                            },
                            'samples': []
                        }
            else:
                # Create default metadata structure
                self.utkface_metadata = {
                    'dataset_info': {
                        'name': 'UTKFace + Kris Hybrid',
                        'description': 'Combined UTKFace dataset with Kris-specific faces',
                        'total_samples': len(self.utkface_embeddings),
                        'feature_dimensions': self.utkface_embeddings.shape[1] if self.utkface_embeddings is not None else 0
                    },
                    'samples': []
                }
            
            logger.info(f"✅ Loaded UTKFace data:")
            logger.info(f"   Embeddings shape: {self.utkface_embeddings.shape if self.utkface_embeddings is not None else 'None'}")
            logger.info(f"   Metadata samples: {len(self.utkface_metadata.get('samples', []))}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load UTKFace data: {e}")
            return False
    
    def extract_condition_from_filename(self, filename: str) -> str:
        """Extract skin condition from filename"""
        filename_lower = filename.lower()
        
        if "no_conditions" in filename_lower or "no_acne" in filename_lower:
            return "healthy"
        elif "dark_spots" in filename_lower:
            return "dark_spots"
        elif "acne" in filename_lower:
            return "acne"
        elif "no_pigmentation" in filename_lower:
            return "healthy"
        else:
            # Manual labeling for images without clear condition in filename
            if "Snapchat" in filename:
                return "healthy"  # Assume Snapchat selfies are generally healthy
            elif "4dca20db" in filename:  # The long filename image
                return "acne"  # Based on feedback.md, this shows acne
            else:
                return "unknown"
    
    def generate_cnn_style_embedding(self, image_path: Path) -> np.ndarray:
        """Generate CNN-style embedding for Kris face (same format as UTKFace)"""
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Resize to standard size (if needed)
            if image.shape[:2] != (224, 224):
                image = cv2.resize(image, (224, 224))
            
            # Convert to HSV for skin analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract comprehensive features (512 dimensions to match UTKFace)
            features = []
            
            # 1. Color features (HSV channels)
            h_mean, h_std = np.mean(hsv[:, :, 0]), np.std(hsv[:, :, 0])
            s_mean, s_std = np.mean(hsv[:, :, 1]), np.std(hsv[:, :, 1])
            v_mean, v_std = np.mean(hsv[:, :, 2]), np.std(hsv[:, :, 2])
            features.extend([h_mean, h_std, s_mean, s_std, v_mean, v_std])
            
            # 2. Brightness and contrast
            brightness_mean, brightness_std = np.mean(gray), np.std(gray)
            contrast = np.std(gray)
            features.extend([brightness_mean, brightness_std, contrast])
            
            # 3. Redness detection (acne indicator)
            lower_red = np.array([0, 50, 50])
            upper_red = np.array([10, 255, 255])
            red_mask = cv2.inRange(hsv, lower_red, upper_red)
            redness_coverage = np.sum(red_mask > 0) / (image.shape[0] * image.shape[1])
            features.append(redness_coverage)
            
            # 4. Edge analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (image.shape[0] * image.shape[1])
            edge_mean = np.mean(edges)
            edge_std = np.std(edges)
            features.extend([edge_density, edge_mean, edge_std])
            
            # 5. Texture analysis (Gabor filters)
            for angle in [0, 45, 90, 135]:
                for freq in [0.1, 0.3, 0.5]:
                    kernel = cv2.getGaborKernel((21, 21), 8, angle, 2*np.pi*freq, 0.5, 0, ktype=cv2.CV_32F)
                    filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
                    features.extend([np.mean(filtered), np.std(filtered)])
            
            # 6. Local Binary Pattern (simplified)
            lbp_features = self._compute_lbp_features(gray)
            features.extend(lbp_features)
            
            # 7. Histogram features
            hist_features = self._compute_histogram_features(gray, hsv)
            features.extend(hist_features)
            
            # 8. Statistical moments
            moments = cv2.moments(gray)
            moment_features = [moments['m00'], moments['m10'], moments['m01'], 
                             moments['m20'], moments['m11'], moments['m02']]
            features.extend(moment_features)
            
            # 9. Fill remaining dimensions with zeros to reach 512
            current_features = len(features)
            if current_features < 512:
                features.extend([0.0] * (512 - current_features))
            elif current_features > 512:
                features = features[:512]
            
            return np.array(features, dtype=np.float64)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding for {image_path}: {e}")
            return None
    
    def _compute_lbp_features(self, gray_image: np.ndarray) -> list:
        """Compute Local Binary Pattern features"""
        try:
            # Simplified LBP computation
            height, width = gray_image.shape
            lbp = np.zeros((height, width), dtype=np.uint8)
            
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
                    
                    lbp[i, j] = code
            
            # Compute histogram
            hist = np.histogram(lbp, bins=16, range=(0, 256))[0]
            hist = hist / np.sum(hist)  # Normalize
            
            return hist.tolist()
            
        except Exception as e:
            logger.error(f"❌ LBP computation failed: {e}")
            return [0.0] * 16
    
    def _compute_histogram_features(self, gray_image: np.ndarray, hsv_image: np.ndarray) -> list:
        """Compute histogram features"""
        try:
            features = []
            
            # Gray histogram
            gray_hist = np.histogram(gray_image, bins=32, range=(0, 256))[0]
            gray_hist = gray_hist / np.sum(gray_hist)
            features.extend(gray_hist.tolist())
            
            # HSV histograms (simplified)
            h_hist = np.histogram(hsv_image[:, :, 0], bins=16, range=(0, 180))[0]
            s_hist = np.histogram(hsv_image[:, :, 1], bins=16, range=(0, 256))[0]
            v_hist = np.histogram(hsv_image[:, :, 2], bins=16, range=(0, 256))[0]
            
            # Normalize
            h_hist = h_hist / np.sum(h_hist)
            s_hist = s_hist / np.sum(s_hist)
            v_hist = v_hist / np.sum(v_hist)
            
            features.extend(h_hist.tolist())
            features.extend(s_hist.tolist())
            features.extend(v_hist.tolist())
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Histogram computation failed: {e}")
            return [0.0] * 80  # 32 + 16 + 16 + 16
    
    def process_kris_faces(self):
        """Process all Kris directory faces and generate embeddings"""
        logger.info("🔄 Processing Kris directory faces...")
        
        if not self.kris_dir.exists():
            logger.error(f"❌ Kris directory not found: {self.kris_dir}")
            return False
        
        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        image_files = []
        
        # Main directory
        for ext in image_extensions:
            image_files.extend(self.kris_dir.glob(f"*{ext}"))
        
        # Test images subdirectory
        test_images_dir = self.kris_dir / "test-images" / "selected_images"
        if test_images_dir.exists():
            for ext in image_extensions:
                image_files.extend(test_images_dir.glob(f"*{ext}"))
        
        logger.info(f"📁 Found {len(image_files)} Kris images to process")
        
        for image_file in image_files:
            try:
                # Extract condition from filename
                condition = self.extract_condition_from_filename(image_file.name)
                logger.info(f"📖 Processing {image_file.name} → {condition}")
                
                # Generate embedding
                embedding = self.generate_cnn_style_embedding(image_file)
                if embedding is not None:
                    self.kris_embeddings.append(embedding)
                    
                    # Create metadata entry
                    metadata_entry = {
                        'filename': image_file.name,
                        'condition': condition,
                        'source': 'kris_directory',
                        'file_path': str(image_file.relative_to(self.kris_dir)),
                        'embedding_index': len(self.kris_embeddings) - 1
                    }
                    self.kris_metadata.append(metadata_entry)
                    
            except Exception as e:
                logger.error(f"❌ Failed to process {image_file}: {e}")
        
        logger.info(f"✅ Processed {len(self.kris_embeddings)} Kris faces")
        return len(self.kris_embeddings) > 0
    
    def create_hybrid_dataset(self):
        """Combine UTKFace and Kris embeddings into hybrid dataset"""
        logger.info("🔄 Creating hybrid dataset...")
        
        try:
            if self.utkface_embeddings is None:
                logger.error("❌ UTKFace embeddings not loaded")
                return False
            
            # Convert to numpy arrays
            utkface_array = np.array(self.utkface_embeddings)
            kris_array = np.array(self.kris_embeddings)
            
            # Combine embeddings
            hybrid_embeddings = np.vstack([utkface_array, kris_array])
            
            # Update metadata
            hybrid_metadata = self.utkface_metadata.copy()
            
            # Add Kris samples to metadata
            for kris_sample in self.kris_metadata:
                hybrid_metadata['samples'].append(kris_sample)
            
            # Update dataset info
            hybrid_metadata['dataset_info']['name'] = 'UTKFace + Kris Hybrid'
            hybrid_metadata['dataset_info']['description'] = f'Combined dataset: {len(utkface_array)} UTKFace + {len(kris_array)} Kris faces'
            hybrid_metadata['dataset_info']['total_samples'] = len(hybrid_embeddings)
            hybrid_metadata['dataset_info']['kris_samples'] = len(kris_array)
            hybrid_metadata['dataset_info']['utkface_samples'] = len(utkface_array)
            
            logger.info(f"✅ Hybrid dataset created:")
            logger.info(f"   Total samples: {len(hybrid_embeddings)}")
            logger.info(f"   UTKFace samples: {len(utkface_array)}")
            logger.info(f"   Kris samples: {len(kris_array)}")
            logger.info(f"   Feature dimensions: {hybrid_embeddings.shape[1]}")
            
            return hybrid_embeddings, hybrid_metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to create hybrid dataset: {e}")
            return None, None
    
    def save_hybrid_dataset(self, hybrid_embeddings, hybrid_metadata):
        """Save the hybrid dataset"""
        try:
            import gzip
            
            # Create output directory
            output_dir = Path("swan-embeddings")
            output_dir.mkdir(exist_ok=True)
            
            # Save embeddings
            embeddings_path = output_dir / "utkface_kris_hybrid_embeddings.pkl.gz"
            with gzip.open(embeddings_path, 'wb') as f:
                pickle.dump(hybrid_embeddings, f)
            
            # Save metadata
            metadata_path = output_dir / "utkface_kris_hybrid_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(hybrid_metadata, f, indent=2)
            
            logger.info(f"💾 Hybrid dataset saved:")
            logger.info(f"   Embeddings: {embeddings_path}")
            logger.info(f"   Metadata: {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save hybrid dataset: {e}")
            return False
    
    def run_embedding_pipeline(self):
        """Run complete embedding pipeline"""
        logger.info("🚀 Starting Kris Face Embedding Pipeline")
        logger.info("=" * 60)
        
        # Find UTKFace files
        if not self.find_utkface_files():
            return False
        
        # Load UTKFace data
        if not self.load_utkface_data():
            return False
        
        # Process Kris faces
        if not self.process_kris_faces():
            return False
        
        # Create hybrid dataset
        hybrid_embeddings, hybrid_metadata = self.create_hybrid_dataset()
        if hybrid_embeddings is None:
            return False
        
        # Save hybrid dataset
        if not self.save_hybrid_dataset(hybrid_embeddings, hybrid_metadata):
            return False
        
        logger.info("🎉 Kris face embedding pipeline completed successfully!")
        logger.info("💡 Next: Update EnhancedSkinAnalyzer to use hybrid dataset")
        return True

def main():
    """Main embedding function"""
    embedder = KrisFaceEmbedder()
    success = embedder.run_embedding_pipeline()
    
    if success:
        print("\n🎉 Kris faces embedded successfully!")
        print("📁 Hybrid dataset saved in swan-embeddings/")
        print("💡 Update EnhancedSkinAnalyzer to use the new hybrid dataset")
    else:
        print("\n❌ Embedding pipeline failed. Check the logs above.")

if __name__ == "__main__":
    main()
