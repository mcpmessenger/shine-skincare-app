# Shine Skincare App - Minimal Backend Deployment

This is a minimal deployment package for the Shine Skincare App backend, designed to ensure successful deployment on Elastic Beanstalk.

## Features

- ✅ Basic Flask API with health endpoints
- ✅ CORS enabled for frontend integration
- ✅ File upload support (10MB limit)
- ✅ Error handling for common issues
- ✅ Minimal dependencies for fast deployment

## Endpoints

- `GET /` - Root endpoint with app info
- `GET /health` - Basic health check
- `GET /api/health` - Detailed health check for Elastic Beanstalk
- `GET /api/test` - Test endpoint

## Deployment

1. Zip this directory
2. Upload to Elastic Beanstalk
3. Deploy to your environment

## Configuration

- **Instance Type**: m5.3xlarge
- **Port**: 8000
- **Health Check**: /api/health
- **Timeout**: 1800 seconds

## Dependencies

- Flask 3.1.1
- Flask-CORS 3.0.10
- Gunicorn 21.2.0
- Python-dotenv 1.0.0
- Requests 2.31.0

## Success Criteria

- ✅ Health check passes
- ✅ All endpoints respond
- ✅ CORS working
- ✅ No deployment timeouts
- ✅ Stable performance 