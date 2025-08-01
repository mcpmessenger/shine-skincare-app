# Operation Left Brain 🧠 - Deployment Guide

This guide provides step-by-step instructions for deploying and testing the Operation Left Brain AI integration for the Shine Skincare application.

## Overview

Operation Left Brain implements the complete AI analysis pipeline as outlined in the architecture design:

1. **Image Preprocessing** - Handling raw image uploads, resizing, and normalization
2. **Face Detection and Isolation** - Using Google Vision API for selfie analysis
3. **Image Embedding Generation** - Extracting high-dimensional feature vectors using pre-trained CNN models
4. **Skin Condition Detection** - AI-powered analysis of skin conditions
5. **SCIN Dataset Integration** - FAISS-based vector search for similar cases
6. **Treatment Recommendation Generation** - Personalized recommendations based on AI analysis

## Prerequisites

### 1. Python Environment

Ensure you have Python 3.8+ installed with the following dependencies:

```bash
# Core dependencies
pip install flask flask-cors gunicorn python-dotenv requests

# AI dependencies
pip install numpy pillow opencv-python-headless faiss-cpu timm transformers torch

# Google Cloud dependencies
pip install google-cloud-vision google-cloud-storage gcsfs google-auth

# Additional dependencies
pip install scikit-learn joblib pandas
```

### 2. Google Cloud Setup

For full functionality, you'll need:

1. **Google Cloud Project** with Vision API enabled
2. **Service Account** with appropriate permissions
3. **Authentication** configured via `gcloud auth application-default login`

### 3. SCIN Dataset Access

The SCIN dataset is hosted on Google Cloud Storage. You'll need:

- Access to the `dx-scin-public-data` bucket
- Permissions to download `scin_cases.csv` and `scin_labels.csv`

## Deployment Steps

### Step 1: Environment Setup

1. **Clone the repository** (if not already done):
```bash
git clone <repository-url>
cd shine-skincare-app
```

2. **Set up virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r backend/requirements.txt
```

### Step 2: Configuration

1. **Environment Variables** - Create a `.env` file in the backend directory:
```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Application Configuration
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
FLASK_ENV=production

# Optional: SCIN Dataset Configuration
SCIN_BUCKET_NAME=dx-scin-public-data
SCIN_CASES_CSV=dataset/scin_cases.csv
SCIN_LABELS_CSV=dataset/scin_labels.csv
```

2. **Google Cloud Authentication**:
```bash
gcloud auth application-default login
gcloud config set project your-project-id
```

### Step 3: Build SCIN Index (Optional)

If you have access to the SCIN dataset, you can build a FAISS index for faster similarity search:

```python
# Run this script to build the SCIN index
python backend/build_scin_index.py
```

This will create:
- `scin_faiss_index.bin` - FAISS index file
- `scin_metadata.pkl` - Metadata file

### Step 4: Test the Implementation

1. **Run the test script**:
```bash
cd backend
python test_operation_left_brain.py
```

This will test all components:
- ✅ AI Embedding Service
- ✅ SCIN Vector Search Service
- ✅ Enhanced Vision Service
- ✅ Skin Condition Detection Service
- ✅ AI Analysis Orchestrator
- ✅ API Endpoints

### Step 5: Deploy the Backend

1. **Local Development**:
```bash
cd backend
python -m flask run --host=0.0.0.0 --port=5000
```

2. **Production Deployment** (using Gunicorn):
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

3. **Docker Deployment** (if using Docker):
```bash
docker build -t shine-skincare-backend .
docker run -p 5000:5000 shine-skincare-backend
```

## API Endpoints

### New Operation Left Brain Endpoints

1. **Selfie Analysis** - `/api/v2/selfie/analyze`
   - Method: POST
   - Content-Type: multipart/form-data
   - Body: `image` file
   - Returns: Complete AI analysis with facial features, skin conditions, and SCIN matches

2. **Skin Analysis** - `/api/v2/skin/analyze`
   - Method: POST
   - Content-Type: multipart/form-data
   - Body: `image` file
   - Returns: Complete AI analysis with skin conditions and SCIN matches

3. **AI Status** - `/api/v2/ai/status`
   - Method: GET
   - Returns: Status of all AI services

4. **AI Health Check** - `/api/v2/ai/health`
   - Method: GET
   - Returns: Health status of AI services

### Example Usage

```bash
# Test selfie analysis
curl -X POST \
  -F "image=@test_selfie.jpg" \
  http://localhost:5000/api/v2/selfie/analyze

# Test skin analysis
curl -X POST \
  -F "image=@test_skin.jpg" \
  http://localhost:5000/api/v2/skin/analyze

# Check AI status
curl http://localhost:5000/api/v2/ai/status

# Health check
curl http://localhost:5000/api/v2/ai/health
```

## Response Format

### Successful Analysis Response

```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "user_id": "user-id",
  "timestamp": "2024-01-01T12:00:00Z",
  "processing_time": 2.5,
  "facial_features": {
    "face_detected": true,
    "face_isolated": true,
    "landmarks": [...],
    "face_bounds": {...},
    "isolation_complete": true,
    "confidence_score": 0.95
  },
  "skin_conditions": [
    {
      "id": "condition_001",
      "type": "acne_vulgaris",
      "confidence": 0.85,
      "location": {"x": 50, "y": 50, "width": 100, "height": 100},
      "characteristics": {
        "severity": "mild",
        "type": "inflammatory"
      },
      "scin_match_score": 0.88,
      "recommendation": "Consider topical retinoids and gentle cleansing"
    }
  ],
  "scin_similar_cases": [
    {
      "case_id": "scin_001",
      "condition_type": "acne_vulgaris",
      "age_group": "18-25",
      "ethnicity": "mixed",
      "treatment_history": "topical_retinoids",
      "outcome": "improved",
      "similarity_score": 0.85,
      "image_path": "dataset/images/scin_001.jpg"
    }
  ],
  "image_size": [480, 640, 3],
  "ai_processed": true,
  "ai_level": "full_ai",
  "google_vision_api": true,
  "scin_dataset": true,
  "core_ai": true,
  "enhanced_features": {
    "face_isolation": true,
    "skin_condition_detection": true,
    "scin_dataset_query": true,
    "facial_landmarks": true,
    "treatment_recommendations": true
  },
  "message": "AI analysis completed successfully",
  "operation": "left_brain",
  "version": "2.0",
  "total_conditions": 1,
  "similar_cases_found": 3
}
```

## Testing

### 1. Unit Tests

Run the comprehensive test suite:

```bash
cd backend
python test_operation_left_brain.py
```

### 2. Integration Tests

Test the API endpoints with real images:

```bash
# Test with a selfie image
curl -X POST \
  -F "image=@test_images/selfie.jpg" \
  http://localhost:5000/api/v2/selfie/analyze

# Test with a skin condition image
curl -X POST \
  -F "image=@test_images/skin_condition.jpg" \
  http://localhost:5000/api/v2/skin/analyze
```

### 3. Frontend Integration

Update the frontend to use the new endpoints:

```javascript
// Example frontend integration
const analyzeSelfie = async (imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/api/v2/selfie/analyze', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path and virtual environment

2. **Google Cloud Authentication**
   - Verify service account credentials
   - Check API permissions
   - Ensure Vision API is enabled

3. **FAISS Index Issues**
   - Check if index files exist
   - Verify index compatibility with FAISS version

4. **Memory Issues**
   - Reduce batch sizes for large images
   - Use CPU-only FAISS if GPU memory is limited

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m flask run --debug
```

### Service Status Check

Check the status of all AI services:

```bash
curl http://localhost:5000/api/v2/ai/status
```

## Performance Optimization

### 1. Model Optimization

- Use GPU acceleration when available
- Implement model caching
- Optimize image preprocessing

### 2. Memory Management

- Implement proper cleanup of model resources
- Use streaming for large files
- Monitor memory usage

### 3. Caching

- Cache embeddings for repeated images
- Cache SCIN search results
- Implement Redis for session storage

## Security Considerations

1. **Image Privacy**
   - Implement secure file upload
   - Add image validation
   - Consider encryption for sensitive data

2. **API Security**
   - Implement rate limiting
   - Add authentication for sensitive endpoints
   - Validate input data

3. **Data Protection**
   - Follow HIPAA guidelines for medical data
   - Implement data retention policies
   - Secure storage of analysis results

## Monitoring and Logging

### 1. Application Logs

Monitor application logs for:
- Service initialization
- Analysis performance
- Error rates
- User activity

### 2. Performance Metrics

Track:
- Analysis processing time
- Memory usage
- API response times
- Error rates

### 3. Health Checks

Regular health checks:
```bash
curl http://localhost:5000/api/v2/ai/health
```

## Next Steps

### 1. Production Deployment

- Set up proper monitoring and alerting
- Implement database storage for analysis results
- Add user authentication and authorization
- Set up CI/CD pipeline

### 2. Model Improvements

- Train custom skin condition detection models
- Fine-tune embedding models on dermatological data
- Implement ensemble methods for better accuracy

### 3. Feature Enhancements

- Add support for video analysis
- Implement real-time analysis
- Add support for multiple skin conditions
- Implement treatment tracking

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review application logs
3. Test individual components
4. Contact the development team

---

**Operation Left Brain** 🧠 is now ready for deployment! This implementation provides a solid foundation for AI-powered skin analysis with real-time processing, accurate condition detection, and personalized recommendations. 