# Backend AI Upgrade Deployment Configuration

This document describes the configuration options for deploying the enhanced backend AI services.

## Environment Variables

### Service Selection

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK_SERVICES` | `false` | Use mock services for all AI components (development/testing) |
| `USE_PRODUCTION_FAISS` | `true` | Use production FAISS service with persistence |
| `GOOGLE_VISION_ENABLED` | `true` | Enable Google Vision API integration |

### FAISS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FAISS_DIMENSION` | `2048` | Vector dimension for FAISS index |
| `FAISS_INDEX_PATH` | `faiss_index` | Base path for FAISS index files |
| `FAISS_PERSISTENCE_ENABLED` | `true` | Enable persistent storage for FAISS index |

### Demographic Search Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMOGRAPHIC_WEIGHT` | `0.3` | Weight for demographic similarity (0.0-1.0) |
| `ETHNICITY_WEIGHT` | `0.6` | Weight for ethnicity matching within demographic similarity |
| `SKIN_TYPE_WEIGHT` | `0.3` | Weight for skin type matching within demographic similarity |
| `AGE_GROUP_WEIGHT` | `0.1` | Weight for age group matching within demographic similarity |

### Skin Classification Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CLASSIFICATION_CONFIDENCE_THRESHOLD` | `0.7` | Minimum confidence for high-confidence classifications |

### Google Cloud Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | No* | Path to Google Cloud service account key file |
| `GOOGLE_CREDENTIALS_JSON` | No* | JSON content of Google Cloud service account key |

*At least one Google Cloud credential method is required for production Google Vision API usage.

### Database Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase service role key |

## Deployment Environments

### Development Environment

```bash
# Use mock services for rapid development
export USE_MOCK_SERVICES=true
export GOOGLE_VISION_ENABLED=false
export FAISS_PERSISTENCE_ENABLED=false
export LOG_LEVEL=DEBUG
```

### Staging Environment

```bash
# Mix of production and mock services for testing
export USE_MOCK_SERVICES=false
export GOOGLE_VISION_ENABLED=true
export FAISS_PERSISTENCE_ENABLED=true
export USE_PRODUCTION_FAISS=true
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/staging-credentials.json
export FAISS_DIMENSION=2048
export DEMOGRAPHIC_WEIGHT=0.3
export LOG_LEVEL=INFO
```

### Production Environment

```bash
# Full production services
export USE_MOCK_SERVICES=false
export GOOGLE_VISION_ENABLED=true
export FAISS_PERSISTENCE_ENABLED=true
export USE_PRODUCTION_FAISS=true
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/production-credentials.json
export FAISS_INDEX_PATH=/persistent/storage/faiss_index
export FAISS_DIMENSION=2048
export DEMOGRAPHIC_WEIGHT=0.3
export ETHNICITY_WEIGHT=0.6
export SKIN_TYPE_WEIGHT=0.3
export AGE_GROUP_WEIGHT=0.1
export CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
export LOG_LEVEL=INFO
```

## Service Dependencies

### Required Dependencies

```
Flask==3.0.0
flask-cors==4.0.0
python-dotenv==1.0.0
numpy==1.24.3
```

### AI Services Dependencies

```
google-cloud-vision==3.4.4  # For Google Vision API
faiss-cpu==1.7.4            # For production FAISS service
opencv-python==4.8.1.78     # For image processing
Pillow==10.0.1              # For image handling
```

### Optional Dependencies

```
# For enhanced logging and monitoring
structlog==23.1.0
prometheus-client==0.17.1

# For development and testing
pytest==7.4.3
pytest-cov==4.1.0
```

## Vercel Deployment Configuration

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "USE_MOCK_SERVICES": "false",
    "USE_PRODUCTION_FAISS": "true",
    "GOOGLE_VISION_ENABLED": "true",
    "FAISS_DIMENSION": "2048",
    "DEMOGRAPHIC_WEIGHT": "0.3"
  }
}
```

### Environment Variables in Vercel Dashboard

Set the following in your Vercel project settings:

- `GOOGLE_CREDENTIALS_JSON`: Your Google Cloud service account key as JSON string
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service role key
- `USE_MOCK_SERVICES`: `false`
- `USE_PRODUCTION_FAISS`: `true`

## Health Monitoring

### Health Check Endpoints

- `GET /api/health` - Overall system health
- `GET /api/services/config` - Service configuration status
- `GET /api/enhanced/health` - Enhanced image analysis services health

### Service Status Monitoring

The service manager provides comprehensive status monitoring:

```python
# Check if all services are initialized
service_manager.is_initialized()

# Get service availability status
service_status = service_manager.get_service_status()

# Get detailed service information
service_info = service_manager.get_service_info()
```

## Performance Considerations

### Memory Usage

- **FAISS Index**: ~8MB per 1000 vectors (2048 dimensions)
- **Google Vision API**: Minimal memory footprint
- **Skin Classifier**: ~50MB for model loading (when using real models)

### API Rate Limits

- **Google Vision API**: 1800 requests per minute (default)
- **Supabase**: Based on your plan limits

### Optimization Settings

```bash
# For high-traffic production environments
export FAISS_DIMENSION=1024  # Reduce dimension for faster search
export DEMOGRAPHIC_WEIGHT=0.2  # Reduce demographic processing
export CLASSIFICATION_CONFIDENCE_THRESHOLD=0.6  # Lower threshold for faster classification
```

## Troubleshooting

### Common Issues

1. **Google Vision API Errors**
   - Check credentials configuration
   - Verify API is enabled in Google Cloud Console
   - Check quota limits

2. **FAISS Index Issues**
   - Ensure write permissions for index path
   - Check available disk space
   - Verify vector dimensions match

3. **Service Initialization Failures**
   - Check environment variables
   - Review service logs
   - Verify dependencies are installed

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=true
```

### Service Fallback

The system automatically falls back to mock services if production services fail:

1. Production Service → Regular Service → Mock Service
2. All fallbacks maintain the same API interface
3. Service status is tracked and reported via health endpoints

## Security Considerations

### Credential Management

- Never commit credentials to version control
- Use environment variables or secure secret management
- Rotate credentials regularly
- Use least-privilege service accounts

### API Security

- Implement rate limiting
- Use HTTPS in production
- Validate all input data
- Sanitize file uploads

### Data Privacy

- Process images in memory when possible
- Implement data retention policies
- Comply with privacy regulations (GDPR, CCPA)
- Audit data access and processing