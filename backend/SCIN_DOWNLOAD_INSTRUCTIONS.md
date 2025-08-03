
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
