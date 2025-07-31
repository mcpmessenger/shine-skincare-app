import os
import logging
import gcsfs
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from PIL import Image
import io
from datetime import datetime
import json
from tqdm import tqdm

logger = logging.getLogger(__name__)

class SCINDatasetService:
    """Service for managing SCIN dataset integration"""
    
    def __init__(self, bucket_path: str = 'gs://dx-scin-public-data/dataset/'):
        """
        Initialize the SCIN dataset service
        
        Args:
            bucket_path: GCS bucket path containing the SCIN dataset
        """
        self.bucket_path = bucket_path
        self.fs = None
        self.cases_df = None
        self.labels_df = None
        self.merged_df = None
        self._initialize_gcs()
    
    def _initialize_gcs(self):
        """Initialize Google Cloud Storage filesystem"""
        try:
            self.fs = gcsfs.GCSFileSystem()
            logger.info("GCS filesystem initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS filesystem: {e}")
            self.fs = None
    
    def load_metadata(self) -> bool:
        """
        Load SCIN dataset metadata from CSV files
        
        Returns:
            True if successful, False otherwise
        """
        if not self.fs:
            logger.error("GCS filesystem not initialized")
            return False
        
        try:
            # Load scin_cases.csv
            logger.info("Loading scin_cases.csv...")
            with self.fs.open(f"{self.bucket_path}scin_cases.csv") as f:
                self.cases_df = pd.read_csv(f)
            logger.info(f"Loaded {len(self.cases_df)} cases")
            
            # Load scin_labels.csv
            logger.info("Loading scin_labels.csv...")
            with self.fs.open(f"{self.bucket_path}scin_labels.csv") as f:
                self.labels_df = pd.read_csv(f)
            logger.info(f"Loaded {len(self.labels_df)} labels")
            
            # Merge datasets
            logger.info("Merging datasets...")
            self.merged_df = pd.merge(
                self.cases_df, 
                self.labels_df, 
                on='case_id', 
                how='left'
            )
            logger.info(f"Merged dataset contains {len(self.merged_df)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return False
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """Get information about the loaded dataset"""
        if self.merged_df is None:
            return {"error": "Dataset not loaded"}
        
        info = {
            "total_records": len(self.merged_df),
            "columns": list(self.merged_df.columns),
            "missing_values": self.merged_df.isnull().sum().to_dict(),
            "condition_distribution": self.merged_df['dermatologist_skin_condition_on_label_name'].value_counts().to_dict() if 'dermatologist_skin_condition_on_label_name' in self.merged_df.columns else {},
            "skin_type_distribution": self.merged_df['dermatologist_fitzpatrick_skin_type_label_1'].value_counts().to_dict() if 'dermatologist_fitzpatrick_skin_type_label_1' in self.merged_df.columns else {},
            "skin_tone_distribution": self.merged_df['monk_skin_tone_label_us'].value_counts().to_dict() if 'monk_skin_tone_label_us' in self.merged_df.columns else {}
        }
        
        return info
    
    def filter_dataset(self, 
                      conditions: Optional[List[str]] = None,
                      skin_types: Optional[List[str]] = None,
                      skin_tones: Optional[List[str]] = None,
                      limit: Optional[int] = None) -> pd.DataFrame:
        """
        Filter the dataset based on criteria
        
        Args:
            conditions: List of dermatologist condition labels to include
            skin_types: List of Fitzpatrick skin types to include
            skin_tones: List of Monk skin tones to include
            limit: Maximum number of records to return
            
        Returns:
            Filtered DataFrame
        """
        if self.merged_df is None:
            logger.error("Dataset not loaded")
            return pd.DataFrame()
        
        filtered_df = self.merged_df.copy()
        
        if conditions:
            filtered_df = filtered_df[
                filtered_df['dermatologist_skin_condition_on_label_name'].isin(conditions)
            ]
        
        if skin_types:
            filtered_df = filtered_df[
                filtered_df['dermatologist_fitzpatrick_skin_type_label_1'].isin(skin_types)
            ]
        
        if skin_tones:
            filtered_df = filtered_df[
                filtered_df['monk_skin_tone_label_us'].isin(skin_tones)
            ]
        
        if limit:
            filtered_df = filtered_df.head(limit)
        
        logger.info(f"Filtered dataset contains {len(filtered_df)} records")
        return filtered_df
    
    def load_image_from_gcs(self, image_filename: str) -> Optional[Image.Image]:
        """
        Load an image from GCS
        
        Args:
            image_filename: Name of the image file
            
        Returns:
            PIL Image object or None if failed
        """
        if not self.fs:
            logger.error("GCS filesystem not initialized")
            return None
        
        try:
            image_path = f"{self.bucket_path}images/{image_filename}"
            with self.fs.open(image_path, 'rb') as f:
                img_bytes = f.read()
            img = Image.open(io.BytesIO(img_bytes))
            return img
        except Exception as e:
            logger.error(f"Failed to load image {image_filename}: {e}")
            return None
    
    def get_image_path(self, image_filename: str) -> str:
        """Get the full GCS path for an image"""
        return f"{self.bucket_path}images/{image_filename}"
    
    def get_sample_images(self, n: int = 5, 
                         conditions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get a sample of images with metadata
        
        Args:
            n: Number of sample images to return
            conditions: Optional list of conditions to filter by
            
        Returns:
            List of dictionaries containing image info and metadata
        """
        if self.merged_df is None:
            logger.error("Dataset not loaded")
            return []
        
        # Filter if conditions specified
        if conditions:
            sample_df = self.merged_df[
                self.merged_df['dermatologist_skin_condition_on_label_name'].isin(conditions)
            ].sample(min(n, len(self.merged_df)))
        else:
            sample_df = self.merged_df.sample(min(n, len(self.merged_df)))
        
        samples = []
        for _, row in sample_df.iterrows():
            # Get image path from image_1_path column
            image_path = row.get('image_1_path', '')
            if image_path:
                # Extract filename from path
                image_filename = image_path.split('/')[-1]
            else:
                image_filename = f"{row['case_id']}.jpg"
            
            sample = {
                'case_id': row['case_id'],
                'image_filename': image_filename,
                'condition': row.get('dermatologist_skin_condition_on_label_name'),
                'skin_type': row.get('dermatologist_fitzpatrick_skin_type_label_1'),
                'skin_tone': row.get('monk_skin_tone_label_us'),
                'age': row.get('age_group'),
                'gender': row.get('sex_at_birth'),
                'image_path': image_path or self.get_image_path(image_filename)
            }
            samples.append(sample)
        
        return samples
    
    def get_condition_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about conditions in the dataset"""
        if self.merged_df is None:
            return {"error": "Dataset not loaded"}
        
        stats = {
            "total_conditions": self.merged_df['dermatologist_skin_condition_on_label_name'].nunique() if 'dermatologist_skin_condition_on_label_name' in self.merged_df.columns else 0,
            "condition_counts": self.merged_df['dermatologist_skin_condition_on_label_name'].value_counts().to_dict() if 'dermatologist_skin_condition_on_label_name' in self.merged_df.columns else {},
            "skin_type_by_condition": self.merged_df.groupby('dermatologist_skin_condition_on_label_name')['dermatologist_fitzpatrick_skin_type_label_1'].value_counts().to_dict() if 'dermatologist_skin_condition_on_label_name' in self.merged_df.columns and 'dermatologist_fitzpatrick_skin_type_label_1' in self.merged_df.columns else {},
            "skin_tone_by_condition": self.merged_df.groupby('dermatologist_skin_condition_on_label_name')['monk_skin_tone_label_us'].value_counts().to_dict() if 'dermatologist_skin_condition_on_label_name' in self.merged_df.columns and 'monk_skin_tone_label_us' in self.merged_df.columns else {}
        }
        
        return stats
    
    def export_filtered_dataset(self, 
                               output_path: str,
                               conditions: Optional[List[str]] = None,
                               skin_types: Optional[List[str]] = None,
                               skin_tones: Optional[List[str]] = None) -> bool:
        """
        Export a filtered subset of the dataset to a CSV file
        
        Args:
            output_path: Path to save the CSV file
            conditions: List of conditions to include
            skin_types: List of skin types to include
            skin_tones: List of skin tones to include
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filtered_df = self.filter_dataset(conditions, skin_types, skin_tones)
            filtered_df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(filtered_df)} records to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export dataset: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.fs is not None and self.merged_df is not None 