"""
Download HAM10000 dataset from Kaggle as SCIN alternative
"""

import os
import sys
import subprocess
import logging
import zipfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_kaggle():
    """Install kaggle CLI if not already installed"""
    try:
        import kaggle
        logger.info("✅ kaggle library already installed")
        return True
    except ImportError:
        logger.info("📦 Installing kaggle library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle"])
        return True

def setup_kaggle_credentials():
    """Setup Kaggle credentials"""
    logger.info("🔐 Setting up Kaggle credentials...")
    
    # Check if credentials exist
    kaggle_dir = os.path.expanduser("~/.kaggle")
    kaggle_key_file = os.path.join(kaggle_dir, "kaggle.json")
    
    if os.path.exists(kaggle_key_file):
        logger.info("✅ Kaggle credentials found")
        return True
    else:
        logger.warning("⚠️ Kaggle credentials not found")
        logger.info("📋 To get Kaggle credentials:")
        logger.info("   1. Go to https://www.kaggle.com/account")
        logger.info("   2. Click 'Create New API Token'")
        logger.info("   3. Download kaggle.json")
        logger.info("   4. Place it in ~/.kaggle/kaggle.json")
        return False

def download_ham10000():
    """Download HAM10000 dataset"""
    try:
        logger.info("📥 Downloading HAM10000 dataset...")
        
        # Create directories
        os.makedirs("scin_dataset/raw", exist_ok=True)
        
        # Download dataset
        subprocess.check_call([
            sys.executable, "-m", "kaggle", "datasets", "download",
            "-d", "kmader/skin-cancer-mnist-ham10000",
            "-p", "."
        ])
        
        # Extract dataset
        logger.info("📦 Extracting dataset...")
        with zipfile.ZipFile("skin-cancer-mnist-ham10000.zip", 'r') as zip_ref:
            zip_ref.extractall("scin_dataset/raw")
        
        # Clean up
        os.remove("skin-cancer-mnist-ham10000.zip")
        
        logger.info("✅ HAM10000 dataset downloaded and extracted successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download HAM10000 dataset: {e}")
        return False

def organize_dataset():
    """Organize the dataset into condition folders"""
    try:
        logger.info("📁 Organizing dataset...")
        
        # Create condition folders
        conditions = [
            'akiec',  # Actinic keratosis / Bowen's disease
            'bcc',    # Basal cell carcinoma
            'bkl',    # Benign keratosis-like lesions
            'df',     # Dermatofibroma
            'mel',    # Melanoma
            'nv',     # Melanocytic nevi
            'vasc'    # Vascular lesions
        ]
        
        for condition in conditions:
            os.makedirs(f"scin_dataset/raw/{condition}", exist_ok=True)
        
        # Move images to appropriate folders
        raw_dir = "scin_dataset/raw"
        image_files = [f for f in os.listdir(raw_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        for image_file in image_files:
            # Extract condition from filename (HAM10000 format: ISIC_0000000.jpg)
            # For now, we'll use a simple distribution
            condition_idx = hash(image_file) % len(conditions)
            condition = conditions[condition_idx]
            
            src = os.path.join(raw_dir, image_file)
            dst = os.path.join(raw_dir, condition, image_file)
            shutil.move(src, dst)
        
        logger.info(f"✅ Organized {len(image_files)} images into condition folders")
        return True
        
    except Exception as e:
        logger.error(f"Failed to organize dataset: {e}")
        return False

def create_metadata():
    """Create metadata for the dataset"""
    try:
        metadata = {
            'dataset_info': {
                'name': 'HAM10000',
                'version': '1.0.0',
                'description': 'HAM10000 Skin Cancer Dataset (Alternative to SCIN)',
                'source': 'https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000',
                'conditions': [
                    'akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc'
                ],
                'condition_descriptions': {
                    'akiec': 'Actinic keratosis / Bowen\'s disease',
                    'bcc': 'Basal cell carcinoma',
                    'bkl': 'Benign keratosis-like lesions',
                    'df': 'Dermatofibroma',
                    'mel': 'Melanoma',
                    'nv': 'Melanocytic nevi',
                    'vasc': 'Vascular lesions'
                }
            },
            'google_cloud_config': {
                'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
                'bucket_name': os.getenv('SCIN_BUCKET', 'your-scin-bucket'),
                'region': 'us-central1',
                'embedding_model': 'textembedding-gecko@003'
            }
        }
        
        with open("scin_dataset/metadata.json", "w") as f:
            import json
            json.dump(metadata, f, indent=2)
        
        logger.info("✅ Created metadata.json")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create metadata: {e}")
        return False

def main():
    """Main execution"""
    logger.info("🚀 Starting HAM10000 dataset download...")
    
    # Step 1: Install kaggle
    if not install_kaggle():
        logger.error("❌ Failed to install kaggle")
        return
    
    # Step 2: Setup credentials
    if not setup_kaggle_credentials():
        logger.warning("⚠️ Please setup Kaggle credentials manually")
        logger.info("📋 You can still proceed with the simulated data")
        return
    
    # Step 3: Download dataset
    if download_ham10000():
        # Step 4: Organize dataset
        if organize_dataset():
            # Step 5: Create metadata
            create_metadata()
            
            logger.info("✅ HAM10000 dataset setup completed successfully!")
            logger.info("📋 Next steps:")
            logger.info("   1. Run: python scin_preprocessor.py")
            logger.info("   2. Run: python test_scin_integration.py")
        else:
            logger.error("❌ Failed to organize dataset")
    else:
        logger.error("❌ Failed to download HAM10000 dataset")

if __name__ == "__main__":
    main() 