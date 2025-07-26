# Enhanced Shine App Backend Features

This document describes the enhanced features added to the Shine app backend, including Google Vision AI integration, FAISS similarity search, and Supabase integration.

## 🚀 New Features Overview

### 1. Google Vision AI Integration
- **Face Detection**: Detect faces and facial expressions in images
- **Image Properties**: Extract dominant colors and image characteristics
- **Label Detection**: Identify objects and concepts in images
- **Safe Search**: Detect inappropriate content

### 2. FAISS Similarity Search
- **Image Vectorization**: Convert images to feature vectors using ResNet-50
- **Similarity Search**: Find similar images using FAISS index
- **Real-time Indexing**: Add new images to the similarity search index

### 3. Supabase Integration
- **Image Storage**: Store images in Supabase Storage
- **Database Management**: Store metadata, analysis results, and vectors
- **Scalable Architecture**: PostgreSQL database with real-time capabilities

## 📁 Project Structure

```
backend/
├── app/
│   ├── services/                    # New service layer
│   │   ├── google_vision_service.py
│   │   ├── image_vectorization_service.py
│   │   ├── faiss_service.py
│   │   ├── supabase_service.py
│   │   └── __init__.py
│   ├── enhanced_image_analysis/     # New API endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   └── models/
│       └── enhanced_image_models.py # New database models
├── test_enhanced_services.py        # Comprehensive test suite
├── env.enhanced.example             # Environment configuration template
└── ENHANCED_FEATURES_README.md      # This file
```

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment template and configure your services:

```bash
cp env.enhanced.example .env
```

Edit `.env` and add your service credentials:

#### Google Cloud Vision AI
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Cloud Vision API
4. Create a service account and download the JSON key file
5. Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your JSON key file

#### Supabase
1. Go to [Supabase](https://supabase.com/)
2. Create a new project
3. Go to Settings > API to get your URL and keys
4. Create a storage bucket named 'images' for image uploads

### 3. Database Setup

Run these SQL commands in your Supabase SQL editor:

```sql
-- Images table
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    image_url TEXT NOT NULL,
    faiss_index_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis results table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    google_vision_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Image vectors table
CREATE TABLE image_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID REFERENCES images(id) ON DELETE CASCADE,
    vector_data JSONB NOT NULL,
    vector_dimension INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Storage Bucket Setup

1. In Supabase dashboard, go to Storage
2. Create a bucket named 'images'
3. Set it to public for image access
4. Configure RLS policies as needed

## 🚀 API Endpoints

### Base URL: `/api/v2`

### 1. Analyze Image
**POST** `/analyze`

Upload and analyze an image with Google Vision AI and FAISS indexing.

**Request:**
```bash
curl -X POST http://localhost:5000/api/v2/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@path/to/your/image.jpg"
```

**Response:**
```json
{
  "image_id": "uuid-here",
  "image_url": "https://supabase.co/storage/v1/object/public/images/filename.jpg",
  "analysis": {
    "status": "success",
    "results": {
      "face_detection": {
        "faces_found": 1,
        "face_data": [...]
      },
      "image_properties": {
        "dominant_colors": [...],
        "color_count": 5
      },
      "label_detection": {
        "labels_found": 10,
        "label_data": [...]
      }
    }
  },
  "vector_created": true,
  "faiss_indexed": true,
  "status": "success"
}
```

### 2. Find Similar Images
**GET** `/similar/{image_id}?k=5`

Find similar images using FAISS similarity search.

**Request:**
```bash
curl -X GET "http://localhost:5000/api/v2/similar/image-uuid-here?k=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "query_image_id": "image-uuid-here",
  "similar_images": [
    {
      "image_id": "similar-image-uuid",
      "image_url": "https://supabase.co/storage/v1/object/public/images/similar.jpg",
      "similarity_score": 0.85,
      "distance": 0.15
    }
  ],
  "total_found": 1
}
```

### 3. Get User Images
**GET** `/images`

Get all images for the current user with analysis summaries.

**Request:**
```bash
curl -X GET http://localhost:5000/api/v2/images \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "images": [
    {
      "id": "image-uuid",
      "user_id": "user-uuid",
      "image_url": "https://supabase.co/storage/v1/object/public/images/image.jpg",
      "created_at": "2024-01-01T00:00:00Z",
      "has_analysis": true,
      "analysis_summary": {
        "faces_found": 1,
        "dominant_colors": 5,
        "labels_found": 10
      },
      "has_vector": true,
      "vector_model": "resnet50"
    }
  ],
  "total_count": 1
}
```

### 4. Get Image Analysis
**GET** `/analysis/{image_id}`

Get detailed analysis for a specific image.

**Request:**
```bash
curl -X GET http://localhost:5000/api/v2/analysis/image-uuid-here \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "image": {
    "id": "image-uuid",
    "user_id": "user-uuid",
    "image_url": "https://supabase.co/storage/v1/object/public/images/image.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "analysis": {
    "status": "success",
    "results": {
      "face_detection": {...},
      "image_properties": {...},
      "label_detection": {...},
      "safe_search": {...}
    }
  },
  "vector_info": {
    "id": "vector-uuid",
    "image_id": "image-uuid",
    "vector_dimension": 2048,
    "model_name": "resnet50",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 5. Health Check
**GET** `/health`

Check the status of all enhanced services.

**Request:**
```bash
curl -X GET http://localhost:5000/api/v2/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "google_vision": true,
    "vectorization": true,
    "faiss": true,
    "supabase": true
  },
  "faiss_index": {
    "total_vectors": 10,
    "dimension": 2048,
    "index_path": "faiss_index",
    "image_ids_count": 10
  },
  "vectorization_model": {
    "model_name": "resnet50",
    "feature_dimension": 2048,
    "device": "cpu",
    "available": true
  }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend
python test_enhanced_services.py
```

This will test:
- Service initialization
- Image vectorization
- FAISS similarity search
- Google Vision AI analysis
- API endpoints (if server is running)

## 🔍 Service Details

### Google Vision Service
- **Features**: Face detection, image properties, label detection, safe search
- **Fallback**: Gracefully handles missing credentials
- **Error Handling**: Comprehensive error handling and logging

### Image Vectorization Service
- **Model**: ResNet-50 pre-trained on ImageNet
- **Features**: 2048-dimensional feature vectors
- **Device**: CPU or CUDA (automatic detection)
- **Input**: Supports file paths, bytes, and PIL images

### FAISS Service
- **Index Type**: IndexFlatL2 (Euclidean distance)
- **Persistence**: Saves index and image IDs to disk
- **Operations**: Add, search, remove vectors
- **Scalability**: Handles thousands of images efficiently

### Supabase Service
- **Storage**: Image upload to Supabase Storage
- **Database**: CRUD operations for images, analyses, and vectors
- **Security**: User-based access control
- **Error Handling**: Comprehensive error handling

## 🚨 Error Handling

All services include comprehensive error handling:

- **Missing Credentials**: Services gracefully disable when credentials are missing
- **Network Errors**: Retry logic and fallback mechanisms
- **Invalid Input**: Input validation and helpful error messages
- **Database Errors**: Transaction rollback and error logging

## 📊 Performance Considerations

### Memory Usage
- **FAISS Index**: Loaded in memory for fast similarity search
- **Model Loading**: ResNet-50 model loaded once at startup
- **Vector Storage**: Vectors stored as JSON in database

### Scalability
- **FAISS**: Can handle millions of vectors efficiently
- **Supabase**: Built for scale with PostgreSQL and real-time features
- **Google Vision**: Pay-per-use API with rate limits

### Optimization Tips
1. Use GPU for vectorization if available
2. Batch process multiple images
3. Implement caching for frequently accessed data
4. Monitor FAISS index size and optimize as needed

## 🔐 Security

- **Authentication**: JWT-based authentication required for all endpoints
- **Authorization**: Users can only access their own images
- **Input Validation**: File type and size validation
- **Secure Storage**: Images stored in Supabase with proper access controls

## 🐛 Troubleshooting

### Common Issues

1. **Google Vision not working**
   - Check `GOOGLE_APPLICATION_CREDENTIALS` path
   - Verify Cloud Vision API is enabled
   - Check service account permissions

2. **FAISS index errors**
   - Ensure sufficient disk space
   - Check file permissions for index directory
   - Verify vector dimensions match

3. **Supabase connection issues**
   - Verify URL and API keys
   - Check network connectivity
   - Ensure tables exist in database

4. **Vectorization failures**
   - Check PyTorch installation
   - Verify model download permissions
   - Monitor memory usage

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment.

## 📈 Future Enhancements

Potential improvements for future versions:

1. **GPU Acceleration**: CUDA support for faster vectorization
2. **Advanced Indexing**: HNSW or IVF indices for better performance
3. **Batch Processing**: Process multiple images simultaneously
4. **Caching Layer**: Redis caching for frequently accessed data
5. **WebSocket Support**: Real-time updates for analysis progress
6. **Custom Models**: Fine-tuned models for skincare-specific features

## 🤝 Contributing

When contributing to the enhanced features:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for new endpoints
4. Ensure backward compatibility
5. Test with various image types and sizes

## 📞 Support

For issues or questions about the enhanced features:

1. Check the troubleshooting section above
2. Review the test suite for examples
3. Check service logs for detailed error messages
4. Verify environment configuration 