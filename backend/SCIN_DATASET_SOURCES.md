# SCIN Dataset Sources and Download Guide

## 🎯 **Real SCIN Dataset Sources**

### **Option 1: Official SCIN Challenge**
- **Source**: https://scin.grand-challenge.org/
- **Access**: Requires registration for the challenge
- **Size**: ~10,000+ dermatological images
- **Conditions**: 7 skin conditions including melanoma, basal cell carcinoma, etc.

### **Option 2: ISIC Archive (Alternative)**
- **Source**: https://www.isic-archive.com/
- **Access**: Free registration required
- **Size**: 100,000+ dermatological images
- **Conditions**: Melanoma, nevus, seborrheic keratosis, etc.

### **Option 3: HAM10000 Dataset**
- **Source**: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
- **Access**: Free with Kaggle account
- **Size**: 10,000+ images
- **Conditions**: 7 different skin conditions

## 🚀 **Quick Setup Commands**

### **For ISIC Archive:**
```bash
# Install ISIC API client
pip install isic-cli

# Download images (requires registration)
isic image download --limit 1000 --output-dir ./scin_dataset/raw
```

### **For HAM10000:**
```bash
# Install kaggle
pip install kaggle

# Download dataset
kaggle datasets download -d kmader/skin-cancer-mnist-ham10000
unzip skin-cancer-mnist-ham10000.zip -d ./scin_dataset/raw
```

### **For Custom Dataset:**
```bash
# Create your own dataset structure
mkdir -p scin_dataset/raw/{acne,rosacea,melanoma,normal}

# Add your images to appropriate folders
# Then run the preprocessing pipeline
```

## 📊 **Dataset Structure Requirements**

Your SCIN dataset should have this structure:
```
scin_dataset/
├── raw/
│   ├── acne/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   ├── rosacea/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   ├── melanoma/
│   │   └── ...
│   └── normal/
│       └── ...
└── processed/
    └── scin_processed_data.json
```

## 🔧 **Google Cloud Setup**

After obtaining your dataset:

```bash
# 1. Create Google Cloud Storage bucket
gsutil mb gs://shine-scin-dataset

# 2. Upload your dataset
gsutil cp -r ./scin_dataset/raw/* gs://shine-scin-dataset/scin_dataset/

# 3. Run preprocessing
python scin_preprocessor.py

# 4. Test integration
python test_scin_integration.py
```

## 📋 **Next Steps**

1. **Choose a dataset source** from the options above
2. **Download and organize** your images in the required structure
3. **Run the Google Cloud setup** script
4. **Execute the preprocessing pipeline**
5. **Test the integration** with your Operation Right Brain backend

## 🎯 **Recommended Approach**

For immediate testing, use the **HAM10000 dataset** from Kaggle as it's:
- ✅ Free and accessible
- ✅ Well-documented
- ✅ Contains 7 skin conditions
- ✅ High-quality images
- ✅ Perfect for testing the Operation Right Brain pipeline 