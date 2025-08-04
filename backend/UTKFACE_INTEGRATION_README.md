# UTKFace Integration for Demographically-Normalized Healthy Image Embeddings

## Overview

This document describes the implementation of UTKFace integration in the Shine Skincare App, which provides demographically-normalized healthy image embeddings for enhanced skin analysis. This system addresses algorithmic bias by comparing user skin images against demographically-relevant healthy baselines rather than a single generic baseline.

## 🎯 Objectives

1. **Demographically-Aware Healthy Baselines**: Establish healthy skin baselines stratified by age, gender, and ethnicity
2. **Enhanced Model Fairness**: Reduce bias by using demographic-specific comparisons
3. **Foundation for Personalization**: Enable future development of highly personalized recommendations

## 🏗️ Architecture

### Core Components

1. **UTKFaceIntegration Class** (`utkface_integration.py`)
   - Handles dataset processing and metadata extraction
   - Manages embedding model (ResNet50)
   - Creates and manages demographic baselines
   - Provides demographic-aware analysis

2. **API Endpoints** (`enhanced_app.py`)
   - `/api/v3/skin/analyze-demographic`: Main analysis endpoint
   - `/api/v3/utkface/status`: System status endpoint

3. **Setup and Testing**
   - `setup_utkface.ps1`: Automated setup script
   - `test_utkface_integration.py`: Comprehensive test suite

## 📊 Demographic Categories

### Age Bins
- 0-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, 70-79, 80-89, 90-99, 110+

### Gender
- 0: Male
- 1: Female

### Ethnicity
- 0: White
- 1: Black
- 2: Asian
- 3: Indian
- 4: Others

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required packages
pip install tensorflow opencv-python pillow pandas numpy scipy requests
```

### 2. Download UTKFace Dataset

```bash
# Manual download (recommended)
# 1. Visit: https://susanqq.github.io/UTKFace/
# 2. Download UTKFace.tar.gz
# 3. Extract to: backend/data/utkface/raw_images/
```

### 3. Setup Integration

```powershell
# Run setup script
.\setup_utkface.ps1

# Or with force rebuild
.\setup_utkface.ps1 -ForceRebuild
```

### 4. Test Integration

```bash
# Run test suite
python test_utkface_integration.py
```

### 5. Start Backend

```bash
# Start Flask app
python enhanced_app.py
```

## 🔧 API Usage

### Demographic Analysis Endpoint

**POST** `/api/v3/skin/analyze-demographic`

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
  "analysis_type": "demographic_utkface",
  "timestamp": "2025-01-04T12:00:00",
  "demographic_analysis": {
    "status": "success",
    "health_score": 85.5,
    "assessment": "Healthy",
    "demographic_baseline_used": "20-29_0_0",
    "age": 25,
    "gender": "Male",
    "ethnicity": "White"
  },
  "recommendations": [
    "Maintain your current skincare routine",
    "Continue with regular skin monitoring"
  ],
  "demographic_info": {
    "age": 25,
    "gender": "Male",
    "ethnicity": "White",
    "demographic_key": "20-29_0_0",
    "baseline_available": true
  },
  "system_info": {
    "utkface_available": true,
    "system_initialized": true,
    "enabled": true,
    "total_baselines": 150
  }
}
```

### Status Endpoint

**GET** `/api/v3/utkface/status`

**Response:**
```json
{
  "status": "available",
  "system_info": {
    "utkface_available": true,
    "system_initialized": true,
    "enabled": true
  },
  "demographic_stats": {
    "total_baselines": 150,
    "available_demographics": ["20-29_0_0", "20-29_1_0", ...],
    "age_bins": ["0-9", "10-19", "20-29", ...],
    "ethnicity_mapping": {"0": "White", "1": "Black", ...},
    "gender_mapping": {"0": "Male", "1": "Female"}
  },
  "capabilities": {
    "analysis_types": ["demographic_normalization", "healthy_baseline_comparison"],
    "embedding_model": "ResNet50",
    "demographic_awareness": true
  }
}
```

## 🧪 Testing

### Automated Tests

```bash
# Run comprehensive test suite
python test_utkface_integration.py
```

The test suite includes:
- Core integration testing
- API endpoint testing
- Demographic fairness testing

### Manual Testing

```bash
# Test with curl
curl -X POST http://localhost:5000/api/v3/skin/analyze-demographic \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data",
    "age": 25,
    "gender": 0,
    "ethnicity": 0
  }'

# Check status
curl http://localhost:5000/api/v3/utkface/status
```

## 📁 File Structure

```
backend/
├── utkface_integration.py          # Core integration class
├── enhanced_app.py                 # Flask app with UTKFace endpoints
├── setup_utkface.ps1              # Setup script
├── test_utkface_integration.py    # Test suite
├── UTKFACE_INTEGRATION_README.md   # This file
└── data/
    └── utkface/
        ├── raw_images/             # UTKFace dataset
        ├── utkface_metadata.csv    # Extracted metadata
        ├── demographic_baselines.npy # Pre-computed baselines
        └── setup_summary.md        # Setup report
```

## 🔍 Technical Details

### Embedding Model

- **Architecture**: ResNet50 (pre-trained on ImageNet)
- **Input**: 224x224 RGB images
- **Output**: 2048-dimensional embeddings
- **Normalization**: ImageNet mean/std normalization

### Baseline Generation

1. **Metadata Extraction**: Parse UTKFace filenames for age/gender/ethnicity
2. **Image Preprocessing**: Resize, normalize, and verify images
3. **Embedding Generation**: Extract features using ResNet50
4. **Demographic Stratification**: Group by age bins, gender, ethnicity
5. **Centroid Calculation**: Compute mean embeddings for each demographic group

### Health Score Calculation

```python
# Cosine similarity between user embedding and demographic baseline
similarity = 1 - cosine(user_embedding, baseline_embedding)
health_score = max(0, min(100, similarity * 100))
```

### Assessment Categories

- **85-100**: Healthy
- **70-84**: Good
- **50-69**: Needs attention
- **0-49**: Consult professional

## ⚖️ Fairness Considerations

### Bias Mitigation

1. **Demographic Stratification**: Separate baselines for different groups
2. **Fallback Mechanisms**: Use overall mean when specific baseline unavailable
3. **Fairness Testing**: Comprehensive testing across demographic groups
4. **Transparency**: Clear reporting of baseline usage

### Monitoring

- Track baseline availability across demographics
- Monitor health score distributions
- Log demographic key usage
- Regular fairness assessments

## 🚨 Troubleshooting

### Common Issues

1. **Dataset Not Found**
   ```
   ❌ UTKFace dataset not found in data/utkface/raw_images/
   ```
   **Solution**: Download and extract UTKFace dataset manually

2. **TensorFlow Not Available**
   ```
   ❌ Embedding model not available
   ```
   **Solution**: Install TensorFlow: `pip install tensorflow`

3. **No Baselines Found**
   ```
   ⚠️ No demographic baselines found
   ```
   **Solution**: Run setup script: `.\setup_utkface.ps1`

4. **API Endpoint Errors**
   ```
   ❌ UTKFace integration system not available
   ```
   **Solution**: Check Flask app is running and UTKFace is initialized

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from utkface_integration import UTKFaceIntegration
utkface = UTKFaceIntegration()
print(f"Baselines: {len(utkface.demographic_baselines)}")
```

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Embedding Models**
   - FaceNet/ArcFace for facial recognition
   - CLIP for general image understanding
   - Custom skin-specific models

2. **Enhanced Demographics**
   - Skin tone classification
   - Geographic region consideration
   - Lifestyle factors

3. **Continuous Learning**
   - Online baseline updates
   - User feedback integration
   - Adaptive thresholds

4. **Medical Integration**
   - Lesion detection integration
   - Professional validation
   - Clinical guidelines

### Research Opportunities

1. **Fairness Metrics**: Implement advanced fairness metrics
2. **Explainable AI**: Add saliency maps and feature importance
3. **Multi-modal Analysis**: Combine with text and metadata
4. **Longitudinal Studies**: Track changes over time

## 📚 References

- [UTKFace Dataset](https://susanqq.github.io/UTKFace/)
- [Technical Implementation Guide](Nomalize.md)
- [ResNet50 Architecture](https://arxiv.org/abs/1512.03385)
- [Fairness in Machine Learning](https://fairmlbook.org/)

## 🤝 Contributing

1. Follow the existing code style
2. Add comprehensive tests for new features
3. Update documentation
4. Consider fairness implications
5. Test across diverse demographics

## 📄 License

This integration is part of the Shine Skincare App project. See the main project license for details.

---

**Author**: Manus AI  
**Date**: January 4, 2025  
**Version**: 1.0.0 