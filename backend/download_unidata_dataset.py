#!/usr/bin/env python3
"""
Dataset Downloader for Shine Skincare App
Downloads and prepares the UniDataPro/facial-skin-condition-dataset from Hugging Face
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
import requests
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatasetDownloader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.dataset_dir = self.data_dir / "unidata_facial_skin_conditions"
        self.raw_dir = self.dataset_dir / "raw"
        self.processed_dir = self.dataset_dir / "processed"
        
        # Create directories
        self.dataset_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Dataset info
        self.dataset_name = "UniDataPro/facial-skin-condition-dataset"
        self.expected_conditions = [
            "acne", "rosacea", "melasma", "eczema", "psoriasis", 
            "vitiligo", "dermatitis", "hyperpigmentation", "hypopigmentation"
        ]
    
    def download_from_huggingface(self) -> bool:
        """
        Download dataset from Hugging Face using huggingface_hub
        """
        try:
            from huggingface_hub import snapshot_download
            
            logger.info(f"Downloading dataset: {self.dataset_name}")
            
            # Download the dataset
            snapshot_download(
                repo_id=self.dataset_name,
                local_dir=self.raw_dir,
                local_dir_use_symlinks=False
            )
            
            logger.info("Dataset downloaded successfully!")
            return True
            
        except ImportError:
            logger.error("huggingface_hub not installed. Installing...")
            self._install_huggingface_hub()
            return self.download_from_huggingface()
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            return False
    
    def _install_huggingface_hub(self):
        """Install huggingface_hub if not available"""
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "huggingface_hub"])
            logger.info("huggingface_hub installed successfully")
        except Exception as e:
            logger.error(f"Failed to install huggingface_hub: {e}")
            raise
    
    def analyze_dataset_structure(self) -> Dict:
        """
        Analyze the downloaded dataset structure
        """
        logger.info("Analyzing dataset structure...")
        
        structure = {
            "total_files": 0,
            "image_files": 0,
            "annotation_files": 0,
            "conditions_found": [],
            "file_types": {},
            "directory_structure": {}
        }
        
        for root, dirs, files in os.walk(self.raw_dir):
            relative_path = os.path.relpath(root, self.raw_dir)
            
            for file in files:
                structure["total_files"] += 1
                file_path = os.path.join(root, file)
                file_ext = Path(file).suffix.lower()
                
                # Count file types
                if file_ext not in structure["file_types"]:
                    structure["file_types"][file_ext] = 0
                structure["file_types"][file_ext] += 1
                
                # Count image files
                if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    structure["image_files"] += 1
                
                # Count annotation files
                if file_ext in ['.json', '.csv', '.txt', '.xml']:
                    structure["annotation_files"] += 1
        
        # Save analysis
        analysis_file = self.dataset_dir / "dataset_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(structure, f, indent=2)
        
        logger.info(f"Dataset analysis saved to {analysis_file}")
        return structure
    
    def process_dataset(self) -> bool:
        """
        Process the downloaded dataset for use in training
        """
        logger.info("Processing dataset...")
        
        try:
            # Create organized structure
            self._organize_images()
            self._extract_annotations()
            self._create_training_splits()
            self._generate_metadata()
            
            logger.info("Dataset processing completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process dataset: {e}")
            return False
    
    def _organize_images(self):
        """Organize images by condition"""
        logger.info("Organizing images by condition...")
        
        # Create condition directories
        for condition in self.expected_conditions:
            condition_dir = self.processed_dir / condition
            condition_dir.mkdir(exist_ok=True)
        
        # Find and organize images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for root, dirs, files in os.walk(self.raw_dir):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    # Try to determine condition from filename or path
                    condition = self._extract_condition_from_path(root, file)
                    if condition:
                        src_path = Path(root) / file
                        dst_path = self.processed_dir / condition / file
                        shutil.copy2(src_path, dst_path)
    
    def _extract_condition_from_path(self, root: str, filename: str) -> Optional[str]:
        """
        Extract skin condition from file path or filename
        """
        path_lower = (root + "/" + filename).lower()
        
        # Map common terms to our condition categories
        condition_mapping = {
            'acne': ['acne', 'pimple', 'zit', 'breakout'],
            'rosacea': ['rosacea', 'rosacea'],
            'melasma': ['melasma', 'chloasma', 'hyperpigmentation'],
            'eczema': ['eczema', 'atopic', 'dermatitis'],
            'psoriasis': ['psoriasis', 'psoriatic'],
            'vitiligo': ['vitiligo', 'depigmentation'],
            'dermatitis': ['dermatitis', 'contact'],
            'hyperpigmentation': ['hyperpigmentation', 'dark', 'spot'],
            'hypopigmentation': ['hypopigmentation', 'light', 'white']
        }
        
        for condition, keywords in condition_mapping.items():
            if any(keyword in path_lower for keyword in keywords):
                return condition
        
        return None
    
    def _extract_annotations(self):
        """Extract and organize annotation files"""
        logger.info("Extracting annotations...")
        
        annotation_dir = self.processed_dir / "annotations"
        annotation_dir.mkdir(exist_ok=True)
        
        # Find annotation files
        annotation_extensions = {'.json', '.csv', '.txt', '.xml'}
        
        for root, dirs, files in os.walk(self.raw_dir):
            for file in files:
                if Path(file).suffix.lower() in annotation_extensions:
                    src_path = Path(root) / file
                    dst_path = annotation_dir / file
                    shutil.copy2(src_path, dst_path)
    
    def _create_training_splits(self):
        """Create train/validation/test splits"""
        logger.info("Creating training splits...")
        
        splits_dir = self.processed_dir / "splits"
        splits_dir.mkdir(exist_ok=True)
        
        # Create split directories
        for split in ['train', 'val', 'test']:
            split_dir = splits_dir / split
            split_dir.mkdir(exist_ok=True)
            
            for condition in self.expected_conditions:
                condition_dir = split_dir / condition
                condition_dir.mkdir(exist_ok=True)
    
    def _generate_metadata(self):
        """Generate metadata about the processed dataset"""
        logger.info("Generating metadata...")
        
        metadata = {
            "dataset_name": "UniDataPro Facial Skin Conditions",
            "processed_date": str(Path().cwd()),
            "total_conditions": len(self.expected_conditions),
            "conditions": self.expected_conditions,
            "statistics": {}
        }
        
        # Count images per condition
        for condition in self.expected_conditions:
            condition_dir = self.processed_dir / condition
            if condition_dir.exists():
                image_count = len(list(condition_dir.glob("*.jpg")) + 
                               list(condition_dir.glob("*.jpeg")) + 
                               list(condition_dir.glob("*.png")))
                metadata["statistics"][condition] = image_count
        
        # Save metadata
        metadata_file = self.processed_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {metadata_file}")
    
    def create_requirements_file(self):
        """Create requirements file for dataset processing"""
        requirements = [
            "huggingface_hub>=0.19.0",
            "tqdm>=4.64.0",
            "requests>=2.28.0",
            "Pillow>=9.0.0",
            "numpy>=1.21.0"
        ]
        
        req_file = self.dataset_dir / "requirements_dataset.txt"
        with open(req_file, 'w') as f:
            for req in requirements:
                f.write(f"{req}\n")
        
        logger.info(f"Requirements file created: {req_file}")
    
    def run_full_pipeline(self):
        """Run the complete dataset download and processing pipeline"""
        logger.info("Starting dataset download and processing pipeline...")
        
        # Step 1: Download dataset
        if not self.download_from_huggingface():
            logger.error("Failed to download dataset. Exiting.")
            return False
        
        # Step 2: Analyze structure
        structure = self.analyze_dataset_structure()
        logger.info(f"Dataset structure: {structure}")
        
        # Step 3: Process dataset
        if not self.process_dataset():
            logger.error("Failed to process dataset. Exiting.")
            return False
        
        # Step 4: Create requirements
        self.create_requirements_file()
        
        logger.info("Dataset pipeline completed successfully!")
        return True

def main():
    """Main function to run the dataset downloader"""
    downloader = DatasetDownloader()
    
    print("=" * 60)
    print("Shine Skincare App - Dataset Downloader")
    print("=" * 60)
    print(f"Dataset: UniDataPro/facial-skin-condition-dataset")
    print(f"Target directory: {downloader.dataset_dir}")
    print("=" * 60)
    
    success = downloader.run_full_pipeline()
    
    if success:
        print("\n✅ Dataset download and processing completed successfully!")
        print(f"📁 Processed dataset available at: {downloader.processed_dir}")
        print(f"📊 Analysis available at: {downloader.dataset_dir}/dataset_analysis.json")
        print(f"📋 Metadata available at: {downloader.processed_dir}/metadata.json")
    else:
        print("\n❌ Dataset processing failed. Check logs for details.")

if __name__ == "__main__":
    main()
