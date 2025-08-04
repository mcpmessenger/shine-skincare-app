# UTKFace Integration Manual Setup Guide

## Overview
This guide will help you set up the UTKFace integration for demographically-normalized healthy image embeddings in the Shine Skincare App.

## Prerequisites
- Python 3.8+ installed
- Required packages: tensorflow, opencv-python, pillow, pandas, numpy, scipy
- Kaggle API credentials (kaggle.json file in project root)

## Step 1: Install Required Packages
```bash
pip install tensorflow opencv-python pillow pandas numpy scipy
```

## Step 2: Download UTKFace Dataset

### Option A: Automated Download via Kaggle (Recommended)
```bash
# Download dataset using Kaggle API
python download_utkface_kaggle.py
```

This script will:
- Install Kaggle CLI if needed
- Configure your Kaggle credentials from `kaggle.json`
- Download the UTKFace dataset automatically
- Extract and organize the files in `data/utkface/raw_images/`

### Option B: Manual Download
1. Visit: https://susanqq.github.io/UTKFace/
2. Download the UTKFace.tar.gz file
3. Extract the contents to: `backend/data/utkface/raw_images/`

## Step 3: Run Setup Scripts
Navigate to the backend directory and run:

```bash
# Setup the UTKFace integration
python setup_utkface_setup.py

# Test the integration
python setup_utkface_test.py
```

## Step 4: Start the Backend
```bash
python enhanced_app.py
```

## Step 5: Test the API Endpoints

### Check UTKFace Status
```bash
curl -X GET http://localhost:5000/api/v3/utkface/status
```

### Test Demographic Analysis
```bash
curl -X POST http://localhost:5000/api/v3/skin/analyze-demographic \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data",
    "age": 25,
    "gender": 0,
    "ethnicity": 0
  }'
```

## API Endpoints

### GET /api/v3/utkface/status
Returns the status of the UTKFace integration system.

**Response:**
```json
{
  "utkface_available": true,
  "system_initialized": true,
  "enabled": true,
  "total_baselines": 150,
  "available_demographics": ["age_20-30_gender_0_ethnicity_0", ...],
  "age_bins": ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-100"],
  "ethnicity_mapping": {"0": "White", "1": "Black", "2": "Asian", "3": "Indian", "4": "Others"},
  "gender_mapping": {"0": "Male", "1": "Female"},
  "capabilities": ["demographic_analysis", "health_score_calculation", "baseline_comparison"]
}
```

### POST /api/v3/skin/analyze-demographic
Analyzes a skin image with demographic context.

**Request Body:**
```json
{
  "image_data": "base64_encoded_image_data",
  "age": 25,
  "gender": 0,
  "ethnicity": 0
}
```

**Response:**
```json
{
  "status": "success",
  "health_score": 0.85,
  "assessment": "healthy",
  "demographic_baseline_used": "age_20-30_gender_0_ethnicity_0",
  "recommendations": ["Continue current skincare routine", "Monitor for any changes"],
  "demographic_info": {
    "age_bin": "20-30",
    "gender": "Male",
    "ethnicity": "White"
  }
}
```

## Troubleshooting

### Common Issues

1. **Dataset not found error**
   - Make sure you've downloaded and extracted the UTKFace dataset to `data/utkface/raw_images/`
   - The directory should contain .jpg files with UTKFace naming convention

2. **Kaggle API errors**
   - Ensure your `kaggle.json` file is in the project root directory
   - Check that your Kaggle API key is valid and has download permissions
   - Try running `kaggle datasets list` to test your credentials

3. **Import errors**
   - Ensure all required packages are installed
   - Check Python version (3.8+ required)

4. **Memory issues**
   - The embedding model requires significant memory
   - Consider using a machine with at least 8GB RAM

5. **TensorFlow warnings**
   - These are normal and don't affect functionality
   - Can be suppressed by setting environment variables

## Directory Structure
```
backend/
├── data/
│   └── utkface/
│       ├── raw_images/          # UTKFace dataset images
│       ├── embeddings/          # Generated embeddings
│       └── baselines/           # Demographic baselines
├── utkface_integration.py       # Main integration class
├── download_utkface_kaggle.py   # Kaggle download script
├── setup_utkface_setup.py       # Setup script
├── setup_utkface_test.py        # Test script
└── enhanced_app.py              # Flask application
```

## Quick Start (Automated)
```bash
# 1. Download dataset
python download_utkface_kaggle.py

# 2. Setup integration
python setup_utkface_setup.py

# 3. Test integration
python setup_utkface_test.py

# 4. Start backend
python enhanced_app.py
```

## Next Steps
1. Monitor system performance
2. Consider implementing additional demographic categories
3. Add fairness testing and bias monitoring
4. Implement continuous learning capabilities

## Support
For issues or questions, check the logs in the backend directory or refer to the main README.md file. 