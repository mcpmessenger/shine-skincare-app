# SCIN Dataset Integration Guide for Shine Skincare App

This guide provides comprehensive instructions for integrating the SCIN (Skin Condition Image Network) dataset into your Shine skincare application. The SCIN dataset offers a diverse collection of skin condition images with professional annotations, making it ideal for building robust AI-powered skin analysis features.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Setup Process](#setup-process)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Maintenance](#maintenance)

## Overview

The SCIN dataset integration provides:

- **Diverse Dataset**: Access to thousands of skin condition images with professional annotations
- **Rich Metadata**: Detailed information about conditions, skin types, demographics, and severity
- **Similarity Search**: Find similar skin conditions using AI-powered image vectorization
- **RAG Integration**: Enhanced recommendations based on similar cases
- **Scalable Architecture**: Efficient processing and caching for large datasets

### Key Features

- **Automatic Dataset Access**: Direct integration with Google Cloud Storage
- **Intelligent Caching**: Vector caching for improved performance
- **Batch Processing**: Efficient handling of large image datasets
- **Flexible Filtering**: Filter by conditions, skin types, and demographics
- **Real-time Search**: Fast similarity search using FAISS
- **Comprehensive API**: RESTful endpoints for all functionality

## Prerequisites

### System Requirements

- Python 3.8 or higher
- 8GB+ RAM (16GB+ recommended for large datasets)
- 10GB+ free disk space for caching
- Stable internet connection for dataset access

### Required Accounts

- **Google Cloud Platform**: For accessing the SCIN dataset
- **Supabase**: For database storage (optional, for enhanced features)

### Dependencies

All required dependencies are automatically installed via `requirements.txt`:

```bash
# Core dependencies
google-cloud-storage==2.10.0
gcsfs==2023.12.0
pandas==2.1.4
faiss-cpu==1.7.4
torch==2.1.0
timm==0.9.12

# Additional dependencies
scikit-learn==1.3.2
matplotlib==3.8.2
seaborn==0.13.0
tqdm==4.66.1
```

## Installation

### 1. Update Dependencies

The SCIN integration dependencies are already included in the updated `requirements.txt`. Install them:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the enhanced environment file and configure it:

```bash
cp env.enhanced.example .env
```

Edit `.env` and set the following variables:

```env
# SCIN Dataset Configuration
SCIN_BUCKET_PATH=gs://dx-scin-public-data/dataset/
SCIN_CACHE_DIR=scin_cache
SCIN_VECTOR_CACHE_DIR=vector_cache

# SCIN Dataset Processing Configuration
SCIN_BATCH_SIZE=100
SCIN_MAX_IMAGES=1000  # Set to None for full dataset
SCIN_FEATURE_DIMENSION=2048

# SCIN Model Configuration
SCIN_VECTORIZATION_MODEL=resnet50
SCIN_VECTORIZATION_DEVICE=cpu  # or 'cuda' if you have GPU

# Optional: Filter specific conditions
SCIN_INCLUDE_CONDITIONS=Acne,Eczema,Psoriasis,Melanoma
SCIN_INCLUDE_SKIN_TYPES=I,II,III,IV,V,VI
SCIN_INCLUDE_SKIN_TONES=1,2,3,4,5,6,7,8,9,10
```

### 3. Database Setup

Run database migrations to create SCIN integration tables:

```bash
# Create migration
flask db migrate -m "Add SCIN integration tables"

# Apply migration
flask db upgrade
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SCIN_BUCKET_PATH` | GCS bucket path for SCIN dataset | `gs://dx-scin-public-data/dataset/` | Yes |
| `SCIN_CACHE_DIR` | Directory for SCIN data caching | `scin_cache` | No |
| `SCIN_VECTOR_CACHE_DIR` | Directory for vector caching | `vector_cache` | No |
| `SCIN_BATCH_SIZE` | Batch size for processing | `100` | No |
| `SCIN_MAX_IMAGES` | Maximum images to process | `1000` | No |
| `SCIN_FEATURE_DIMENSION` | Feature vector dimension | `2048` | No |
| `SCIN_VECTORIZATION_MODEL` | Model for vectorization | `resnet50` | No |
| `SCIN_VECTORIZATION_DEVICE` | Device for processing | `cpu` | No |

### Dataset Filtering

You can filter the SCIN dataset during processing to focus on specific conditions or demographics:

```env
# Filter by specific conditions
SCIN_INCLUDE_CONDITIONS=Acne,Eczema,Psoriasis,Melanoma

# Filter by skin types (Fitzpatrick scale)
SCIN_INCLUDE_SKIN_TYPES=I,II,III,IV,V,VI

# Filter by skin tones (Monk scale)
SCIN_INCLUDE_SKIN_TONES=1,2,3,4,5,6,7,8,9,10
```

## Setup Process

### 1. Automated Setup

Run the automated setup script:

```bash
cd backend
python setup_scin_integration.py
```

This script will:
- Check environment configuration
- Initialize all services
- Test dataset access
- Validate vectorization service
- Test FAISS similarity search
- Generate setup report

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Test SCIN dataset access
python -c "
from app.services.scin_dataset_service import SCINDatasetService
service = SCINDatasetService()
print('Loading metadata...')
if service.load_metadata():
    print('Success! Dataset loaded.')
    info = service.get_dataset_info()
    print(f'Total records: {info[\"total_records\"]}')
else:
    print('Failed to load dataset.')
"

# 2. Test vectorization service
python -c "
from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
service = EnhancedImageVectorizationService()
print(f'Service available: {service.is_available()}')
print(f'Model info: {service.get_model_info()}')
"

# 3. Test FAISS service
python -c "
from app.services.faiss_service import FAISSService
service = FAISSService()
print(f'Service available: {service.is_available()}')
print(f'Index info: {service.get_index_info()}')
"
```

### 3. Build Initial Index

Build a similarity search index:

```bash
# Using the integration manager
python -c "
from app.services.scin_integration_manager import SCINIntegrationManager
manager = SCINIntegrationManager()
manager.initialize_integration()
result = manager.build_similarity_index(max_images=1000, batch_size=100)
print(f'Build result: {result}')
"
```

## Usage Examples

### 1. Basic Dataset Access

```python
from app.services.scin_dataset_service import SCINDatasetService

# Initialize service
service = SCINDatasetService()

# Load metadata
service.load_metadata()

# Get dataset information
info = service.get_dataset_info()
print(f"Total records: {info['total_records']}")

# Get sample images
samples = service.get_sample_images(n=5, conditions=['Acne'])
for sample in samples:
    print(f"Case {sample['case_id']}: {sample['condition']}")
```

### 2. Similarity Search

```python
from app.services.scin_integration_manager import SCINIntegrationManager

# Initialize manager
manager = SCINIntegrationManager()
manager.initialize_integration()

# Search for similar images
results = manager.search_similar_images(
    query_image_path="path/to/query/image.jpg",
    k=5,
    conditions=['Acne', 'Eczema']
)

if results['success']:
    for result in results['similar_images']:
        print(f"Similar case {result['case_id']}: distance {result['distance']}")
```

### 3. API Usage

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/scin/health')
print(response.json())

# Get integration status
response = requests.get('http://localhost:5000/api/scin/status')
print(response.json())

# Search similar images
data = {
    'query_image_path': '/path/to/image.jpg',
    'k': 5,
    'conditions': ['Acne']
}
response = requests.post('http://localhost:5000/api/scin/search', json=data)
print(response.json())
```

### 4. Building Custom Indexes

```python
from app.services.scin_integration_manager import SCINIntegrationManager

manager = SCINIntegrationManager()

# Build index for specific conditions
result = manager.build_similarity_index(
    conditions=['Acne', 'Eczema'],
    skin_types=['III', 'IV', 'V'],
    max_images=5000,
    batch_size=200
)

print(f"Processed {result['details']['processed_images']} images")
print(f"Added {result['details']['faiss_additions']} vectors to FAISS")
```

## API Reference

### Health Check

```http
GET /api/scin/health
```

**Response:**
```json
{
  "success": true,
  "healthy": true,
  "services": {
    "scin_service": true,
    "vectorization_service": true,
    "faiss_service": true
  },
  "integration_status": {
    "scin_loaded": true,
    "vectors_generated": true,
    "faiss_populated": true
  }
}
```

### Get Integration Status

```http
GET /api/scin/status
```

**Response:**
```json
{
  "success": true,
  "status": {
    "scin_loaded": true,
    "vectors_generated": true,
    "faiss_populated": true,
    "last_update": "2024-01-15T10:30:00Z",
    "services": {...},
    "dataset_info": {...},
    "faiss_info": {...}
  }
}
```

### Initialize Integration

```http
POST /api/scin/initialize
```

**Response:**
```json
{
  "success": true,
  "result": {
    "success": true,
    "errors": [],
    "warnings": [],
    "details": {...}
  }
}
```

### Build Similarity Index

```http
POST /api/scin/build-index
Content-Type: application/json

{
  "conditions": ["Acne", "Eczema"],
  "skin_types": ["III", "IV", "V"],
  "max_images": 1000,
  "batch_size": 100
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "success": true,
    "details": {
      "processed_images": 1000,
      "successful_vectors": 950,
      "failed_vectors": 50,
      "faiss_additions": 950
    }
  }
}
```

### Search Similar Images

```http
POST /api/scin/search
Content-Type: application/json

{
  "query_image_path": "/path/to/image.jpg",
  "k": 5,
  "conditions": ["Acne"],
  "skin_types": ["III", "IV"]
}
```

**Response:**
```json
{
  "success": true,
  "query_image": "/path/to/image.jpg",
  "similar_images": [
    {
      "case_id": "12345",
      "distance": 0.15,
      "image_path": "gs://dx-scin-public-data/dataset/images/12345.jpg",
      "condition": "Acne",
      "skin_type": "III",
      "skin_tone": "4",
      "age": 25,
      "gender": "F"
    }
  ]
}
```

### Get Dataset Information

```http
GET /api/scin/dataset/info
```

**Response:**
```json
{
  "success": true,
  "dataset_info": {
    "total_records": 50000,
    "condition_distribution": {...},
    "skin_type_distribution": {...},
    "skin_tone_distribution": {...}
  }
}
```

### Get Sample Images

```http
GET /api/scin/dataset/sample?n=5&conditions=Acne,Eczema
```

**Response:**
```json
{
  "success": true,
  "samples": [
    {
      "case_id": "12345",
      "image_filename": "12345.jpg",
      "condition": "Acne",
      "skin_type": "III",
      "skin_tone": "4",
      "age": 25,
      "gender": "F",
      "image_path": "gs://dx-scin-public-data/dataset/images/12345.jpg"
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. SCIN Service Not Available

**Error:** `SCIN service not available`

**Solution:**
- Check internet connectivity
- Verify Google Cloud Storage access
- Ensure `gcsfs` is properly installed

```bash
pip install gcsfs --upgrade
```

#### 2. Vectorization Service Failed

**Error:** `Vectorization service not available`

**Solution:**
- Check PyTorch installation
- Verify model download
- Check available memory

```bash
# Test PyTorch
python -c "import torch; print(torch.__version__)"

# Test timm
python -c "import timm; print(timm.list_models()[:5])"
```

#### 3. FAISS Index Issues

**Error:** `FAISS service not available`

**Solution:**
- Check FAISS installation
- Verify index file permissions
- Clear and rebuild index

```bash
# Reinstall FAISS
pip uninstall faiss-cpu
pip install faiss-cpu

# Clear index
python -c "
from app.services.faiss_service import FAISSService
service = FAISSService()
service.clear_index()
"
```

#### 4. Memory Issues

**Error:** `Out of memory`

**Solution:**
- Reduce batch size
- Process fewer images
- Use CPU instead of GPU
- Increase system memory

```env
SCIN_BATCH_SIZE=50
SCIN_MAX_IMAGES=500
SCIN_VECTORIZATION_DEVICE=cpu
```

#### 5. Slow Processing

**Issue:** Processing is very slow

**Solution:**
- Use GPU if available
- Increase batch size
- Enable vector caching
- Use SSD storage

```env
SCIN_VECTORIZATION_DEVICE=cuda
SCIN_BATCH_SIZE=200
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Monitoring

Monitor system resources during processing:

```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h

# Monitor network
iftop
```

## Performance Optimization

### 1. Caching Strategy

- **Vector Cache**: Caches computed feature vectors
- **Metadata Cache**: Caches dataset metadata
- **FAISS Index**: Persistent similarity search index

### 2. Batch Processing

- Process images in batches for efficiency
- Adjust batch size based on available memory
- Use parallel processing where possible

### 3. Model Optimization

- Use GPU acceleration if available
- Consider model quantization for faster inference
- Use smaller models for development

### 4. Storage Optimization

- Use SSD storage for better I/O performance
- Implement data compression
- Regular cleanup of temporary files

## Maintenance

### Regular Tasks

#### 1. Cache Management

```bash
# Clear vector cache
python -c "
from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
service = EnhancedImageVectorizationService()
service.clear_cache()
"

# Check cache size
python -c "
from app.services.enhanced_image_vectorization_service import EnhancedImageVectorizationService
service = EnhancedImageVectorizationService()
print(service.get_cache_info())
"
```

#### 2. Index Maintenance

```bash
# Check FAISS index health
python -c "
from app.services.faiss_service import FAISSService
service = FAISSService()
print(service.get_index_info())
"
```

#### 3. Dataset Updates

Monitor for SCIN dataset updates:

```bash
# Check dataset freshness
python -c "
from app.services.scin_dataset_service import SCINDatasetService
service = SCINDatasetService()
service.load_metadata()
info = service.get_dataset_info()
print(f'Dataset last updated: {info.get(\"last_update\", \"Unknown\")}')
"
```

### Backup and Recovery

#### 1. Backup FAISS Index

```bash
# Backup index files
cp faiss_index.index faiss_index.backup
cp faiss_index_ids.pkl faiss_index_ids.backup
```

#### 2. Backup Cache

```bash
# Backup vector cache
tar -czf vector_cache_backup.tar.gz vector_cache/
```

#### 3. Restore from Backup

```bash
# Restore FAISS index
cp faiss_index.backup faiss_index.index
cp faiss_index_ids.backup faiss_index_ids.pkl

# Restore cache
tar -xzf vector_cache_backup.tar.gz
```

### Monitoring

#### 1. Health Checks

Set up regular health checks:

```bash
# Daily health check
curl -X GET http://localhost:5000/api/scin/health
```

#### 2. Performance Monitoring

Monitor key metrics:

- Processing time per batch
- Memory usage
- Cache hit rates
- Search response times

#### 3. Error Tracking

Monitor error logs:

```bash
# Check application logs
tail -f logs/app.log | grep -i error
```

## Support

For additional support:

1. **Documentation**: Check this guide and inline code comments
2. **Logs**: Review application logs for detailed error information
3. **Testing**: Run the test suite to identify issues
4. **Community**: Check the SCIN dataset GitHub repository for updates

### Useful Commands

```bash
# Run setup
python setup_scin_integration.py

# Run tests
python test_scin_integration.py

# Check status
curl http://localhost:5000/api/scin/health

# Monitor logs
tail -f logs/app.log
```

---

**Note:** This integration provides a powerful foundation for AI-powered skin analysis. Regular maintenance and monitoring will ensure optimal performance and reliability. 