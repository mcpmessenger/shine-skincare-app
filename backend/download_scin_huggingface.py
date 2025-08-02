"""
Download SCIN dataset from Hugging Face
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_datasets():
    """Install the datasets library if not already installed"""
    try:
        import datasets
        logger.info("✅ datasets library already installed")
        return True
    except ImportError:
        logger.info("📦 Installing datasets library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "datasets"])
        return True

def download_scin_dataset():
    """Download SCIN dataset from Hugging Face"""
    try:
        logger.info("🔍 Downloading SCIN dataset from Hugging Face...")
        
        # Create download script
        download_script = '''
import os
from datasets import load_dataset

# Create directory
os.makedirs("scin_dataset/raw", exist_ok=True)

# Download SCIN dataset
print("📥 Downloading SCIN-2023 dataset...")
dataset = load_dataset("SCIN-2023/SCIN-2023")

print(f"✅ Dataset downloaded successfully!")
print(f"📊 Dataset info:")
print(f"   - Train split: {len(dataset['train'])} samples")
print(f"   - Test split: {len(dataset['test'])} samples")
print(f"   - Validation split: {len(dataset['validation'])} samples")

# Save to disk
print("💾 Saving dataset to disk...")
dataset.save_to_disk("./scin_dataset/raw")

print("✅ SCIN dataset saved to ./scin_dataset/raw/")
print("📋 Next steps:")
print("   1. Run: python scin_preprocessor.py")
print("   2. Run: python test_scin_integration.py")
'''
        
        # Write and execute the script
        with open("download_scin_temp.py", "w", encoding="utf-8") as f:
            f.write(download_script)
        
        logger.info("🚀 Executing download script...")
        subprocess.check_call([sys.executable, "download_scin_temp.py"])
        
        # Cleanup
        os.remove("download_scin_temp.py")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to download SCIN dataset: {e}")
        return False

def main():
    """Main execution"""
    logger.info("🚀 Starting SCIN dataset download...")
    
    # Step 1: Install datasets library
    if not install_datasets():
        logger.error("❌ Failed to install datasets library")
        return
    
    # Step 2: Download dataset
    if download_scin_dataset():
        logger.info("✅ SCIN dataset download completed successfully!")
    else:
        logger.error("❌ SCIN dataset download failed")

if __name__ == "__main__":
    main() 