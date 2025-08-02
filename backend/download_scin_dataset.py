"""
Download and prepare the real SCIN dataset for Operation Right Brain
"""

import os
import requests
import zipfile
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SCINDatasetDownloader:
    """Download and prepare SCIN dataset for Google Cloud processing"""
    
    def __init__(self):
        self.dataset_dir = "scin_dataset"
        self.raw_dir = f"{self.dataset_dir}/raw"
        self.processed_dir = f"{self.dataset_dir}/processed"
        
    def create_directories(self):
        """Create necessary directories"""
        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        logger.info("✅ Created SCIN dataset directories")
    
    def download_scin_dataset(self):
        """Download SCIN dataset from public sources"""
        try:
            # SCIN dataset sources (these are examples - you'll need the actual URLs)
            scin_sources = [
                {
                    'name': 'SCIN_2023',
                    'url': 'https://huggingface.co/datasets/SCIN-2023/SCIN-2023/resolve/main/data/train-00000-of-00001.parquet',
                    'description': 'SCIN 2023 Challenge Dataset'
                }
            ]
            
            logger.info("🔍 Attempting to download SCIN dataset...")
            
            # For now, we'll create a script to help you download manually
            # since the actual SCIN dataset requires proper access
            self.create_download_instructions()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download SCIN dataset: {e}")
            return False
    
    def create_download_instructions(self):
        """Create instructions for manual SCIN dataset download"""
        instructions = """
# SCIN Dataset Download Instructions

## Option 1: Hugging Face Dataset
```bash
# Install datasets library
pip install datasets

# Download SCIN dataset
python -c "
from datasets import load_dataset
dataset = load_dataset('SCIN-2023/SCIN-2023')
dataset.save_to_disk('./scin_dataset/raw')
"
```

## Option 2: Manual Download
1. Visit: https://huggingface.co/datasets/SCIN-2023/SCIN-2023
2. Download the dataset files
3. Extract to: ./scin_dataset/raw/

## Option 3: Use Google Cloud Storage (if you have access)
```bash
# Create bucket for SCIN dataset
gsutil mb gs://shine-scin-dataset

# Upload your SCIN dataset files
gsutil cp -r ./scin_dataset/raw/* gs://shine-scin-dataset/scin_dataset/
```
"""
        
        with open("SCIN_DOWNLOAD_INSTRUCTIONS.md", "w") as f:
            f.write(instructions)
        
        logger.info("📝 Created SCIN_DOWNLOAD_INSTRUCTIONS.md")
    
    def prepare_for_google_cloud(self):
        """Prepare dataset for Google Cloud processing"""
        try:
            # Create metadata file for Google Cloud processing
            metadata = {
                'dataset_info': {
                    'name': 'SCIN-2023',
                    'version': '1.0.0',
                    'description': 'Skin Condition Image Network Dataset',
                    'total_images': 0,  # Will be updated after download
                    'conditions': [
                        'acne', 'rosacea', 'melanoma', 'basal_cell_carcinoma',
                        'squamous_cell_carcinoma', 'actinic_keratosis', 'seborrheic_keratosis'
                    ]
                },
                'google_cloud_config': {
                    'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
                    'bucket_name': os.getenv('SCIN_BUCKET', 'your-scin-bucket'),
                    'region': 'us-central1',
                    'embedding_model': 'textembedding-gecko@003'
                },
                'processing_pipeline': {
                    'face_detection': True,
                    'embedding_generation': True,
                    'similarity_search': True,
                    'batch_size': 100
                }
            }
            
            with open(f"{self.dataset_dir}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ Created metadata.json for Google Cloud processing")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare metadata: {e}")
            return False
    
    def create_google_cloud_setup_script(self):
        """Create script to set up Google Cloud for SCIN processing"""
        setup_script = '''#!/bin/bash
# Google Cloud Setup for SCIN Dataset Processing

echo "🧠 Setting up Google Cloud for SCIN dataset processing..."

# 1. Create Google Cloud Storage bucket
echo "📦 Creating SCIN dataset bucket..."
gsutil mb gs://shine-scin-dataset

# 2. Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable vision.googleapis.com
gcloud services enable storage.googleapis.com

# 3. Set up IAM permissions
echo "🔐 Setting up IAM permissions..."
gcloud projects add-iam-policy-binding shine-skincare-app \\
    --member="serviceAccount:shine-skincare-app@appspot.gserviceaccount.com" \\
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding shine-skincare-app \\
    --member="serviceAccount:shine-skincare-app@appspot.gserviceaccount.com" \\
    --role="roles/storage.objectViewer"

# 4. Upload SCIN dataset (after manual download)
echo "📤 Uploading SCIN dataset to Google Cloud Storage..."
gsutil cp -r ./scin_dataset/raw/* gs://shine-scin-dataset/scin_dataset/

echo "✅ Google Cloud setup complete!"
echo "📋 Next steps:"
echo "   1. Download SCIN dataset manually"
echo "   2. Run: python scin_preprocessor.py"
echo "   3. Test with: python test_scin_integration.py"
'''
        
        with open("setup_google_cloud_scin.sh", "w") as f:
            f.write(setup_script)
        
        # Make executable (for Unix systems)
        os.chmod("setup_google_cloud_scin.sh", 0o755)
        
        logger.info("✅ Created setup_google_cloud_scin.sh")
    
    def run(self):
        """Main execution"""
        logger.info("🚀 Starting SCIN dataset preparation...")
        
        # Step 1: Create directories
        self.create_directories()
        
        # Step 2: Create download instructions
        self.download_scin_dataset()
        
        # Step 3: Prepare for Google Cloud
        self.prepare_for_google_cloud()
        
        # Step 4: Create setup script
        self.create_google_cloud_setup_script()
        
        logger.info("✅ SCIN dataset preparation complete!")
        logger.info("📋 Next steps:")
        logger.info("   1. Follow SCIN_DOWNLOAD_INSTRUCTIONS.md")
        logger.info("   2. Run: ./setup_google_cloud_scin.sh")
        logger.info("   3. Run: python scin_preprocessor.py")

if __name__ == "__main__":
    downloader = SCINDatasetDownloader()
    downloader.run() 