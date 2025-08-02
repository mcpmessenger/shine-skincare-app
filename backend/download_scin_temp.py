
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
