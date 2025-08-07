# Version 4 Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Version 4 upgrades to the Shine Skincare App. The Version 4 system includes advanced face detection, robust embeddings, and comprehensive bias mitigation.

## Prerequisites

### System Requirements
- Python 3.9+ (for AWS Elastic Beanstalk compatibility)
- 4GB+ RAM (for ML model loading)
- GPU support recommended (for faster inference)
- 10GB+ storage space

### Dependencies
All required dependencies are listed in `backend/requirements_enhanced_v4.txt`

## Deployment Steps

### Step 1: Environment Setup

1. **Create a new GitHub branch**
   ```bash
   git checkout -b feature/version-4-upgrades
   ```

2. **Install new dependencies**
   ```bash
   cd backend
   pip install -r requirements_enhanced_v4.txt
   ```

3. **Verify installation**
   ```bash
   python v4/test_v4_components.py
   ```

### Step 2: Backend Deployment

1. **Update Elastic Beanstalk configuration**
   
   Create or update `.ebextensions/01_packages.config`:
   ```yaml
   packages:
     yum:
       gcc: []
       gcc-c++: []
       make: []
       cmake: []
       atlas-devel: []
       lapack-devel: []
       blas-devel: []
   ```

2. **Update Python version**
   
   Create or update `.ebextensions/02_python.config`:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: v4/enhanced_analysis_api_v4:app
   ```

3. **Update requirements**
   
   Copy the new requirements:
   ```bash
   cp requirements_enhanced_v4.txt requirements.txt
   ```

### Step 3: Frontend Integration

1. **Update API endpoints**
   
   Update `lib/direct-backend.ts` to include new V4 endpoints:
   ```typescript
   // Add new V4 endpoints
   export const V4_ENDPOINTS = {
     COMPREHENSIVE_ANALYSIS: '/api/v4/skin/analyze-comprehensive',
     ADVANCED_FACE_DETECTION: '/api/v4/face/detect-advanced',
     EMBEDDINGS_GENERATION: '/api/v4/embeddings/generate',
     BIAS_EVALUATION: '/api/v4/bias/evaluate',
     HEALTH_CHECK: '/health/v4'
   };
   ```

2. **Update analysis component**
   
   Modify `components/enhanced-analysis.tsx` to use V4 endpoints:
   ```typescript
   // Import V4 endpoints
   import { V4_ENDPOINTS } from '../lib/direct-backend';
   
   // Update analysis function
   const performV4Analysis = async (imageData: string, demographicData: any) => {
     const response = await fetch(V4_ENDPOINTS.COMPREHENSIVE_ANALYSIS, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         image: imageData,
         ...demographicData
       })
     });
     return response.json();
   };
   ```

### Step 4: Testing

1. **Run component tests**
   ```bash
   cd backend/v4
   python test_v4_components.py
   ```

2. **Test API endpoints**
   ```bash
   # Start the V4 API server
   python enhanced_analysis_api_v4.py
   
   # Test endpoints
   curl -X GET http://localhost:5000/health/v4
   ```

3. **Integration testing**
   ```bash
   # Test with sample image
   python -c "
   import requests
   import base64
   import cv2
   import numpy as np
   
   # Create test image
   img = np.zeros((480, 640, 3), dtype=np.uint8)
   _, buffer = cv2.imencode('.jpg', img)
   img_base64 = base64.b64encode(buffer).decode('utf-8')
   
   # Test comprehensive analysis
   response = requests.post('http://localhost:5000/api/v4/skin/analyze-comprehensive', 
                          json={'image': img_base64, 'age': 25, 'ethnicity': 'caucasian'})
   print(response.json())
   "
   ```

### Step 5: AWS Elastic Beanstalk Deployment

1. **Prepare deployment package**
   ```bash
   # Create deployment archive
   cd backend
   zip -r v4-deployment.zip . -x "*.pyc" "__pycache__/*" "*.git*"
   ```

2. **Deploy to Elastic Beanstalk**
   ```bash
   # Using EB CLI
   eb deploy v4-environment
   
   # Or using AWS Console
   # Upload v4-deployment.zip to Elastic Beanstalk
   ```

3. **Verify deployment**
   ```bash
   # Check health endpoint
   curl https://your-eb-environment.elasticbeanstalk.com/health/v4
   
   # Check application logs
   eb logs
   ```

### Step 6: Frontend Deployment

1. **Update environment variables**
   
   Add V4 API endpoints to your environment:
   ```bash
   # .env.local
   NEXT_PUBLIC_V4_API_BASE_URL=https://your-eb-environment.elasticbeanstalk.com
   ```

2. **Deploy to GitHub Pages/AWS Amplify**
   ```bash
   # Build and deploy
   npm run build
   npm run export
   
   # Deploy to your hosting platform
   ```

## Configuration

### Environment Variables

Add these to your Elastic Beanstalk environment:

```bash
# ML Model Configuration
MODEL_CACHE_DIR=/tmp/models
GPU_ENABLED=false
BATCH_SIZE=1

# Bias Mitigation
FAIRNESS_THRESHOLD=0.05
BIAS_CORRECTION_ENABLED=true

# Logging
LOG_LEVEL=INFO
ENABLE_DEBUG=false

# Performance
MAX_IMAGE_SIZE=10485760  # 10MB
REQUEST_TIMEOUT=30
```

### Performance Optimization

1. **Model caching**
   ```python
   # In your V4 components
   import os
   os.environ['TORCH_HOME'] = '/tmp/models'
   ```

2. **Memory optimization**
   ```python
   # Enable memory-efficient inference
   torch.backends.cudnn.benchmark = True
   torch.backends.cudnn.deterministic = False
   ```

3. **Batch processing**
   ```python
   # For multiple images
   def process_batch(images, batch_size=4):
       # Process images in batches
       pass
   ```

## Monitoring and Logging

### CloudWatch Integration

1. **Enable CloudWatch logs**
   ```yaml
   # .ebextensions/03_cloudwatch.config
   files:
     "/etc/cloudwatch-config.json":
       mode: "000600"
       owner: root
       group: root
       content: |
         {
           "logs": {
             "logs_collected": {
               "files": {
                 "collect_list": [
                   {
                     "file_path": "/var/log/app.log",
                     "log_group_name": "/aws/elasticbeanstalk/your-app/app.log",
                     "log_stream_name": "{instance_id}"
                   }
                 ]
               }
             }
           }
         }
   ```

2. **Custom metrics**
   ```python
   # Add custom metrics for monitoring
   import boto3
   
   def log_metric(metric_name, value, unit='Count'):
       cloudwatch = boto3.client('cloudwatch')
       cloudwatch.put_metric_data(
           Namespace='ShineSkincare/V4',
           MetricData=[{
               'MetricName': metric_name,
               'Value': value,
               'Unit': unit
           }]
       )
   ```

### Health Checks

1. **Enhanced health check**
   ```python
   @app.route('/health/v4/detailed', methods=['GET'])
   def detailed_health_check():
       return jsonify({
           'status': 'healthy',
           'version': '4.0.0',
           'components': {
               'face_detection': check_face_detection(),
               'embeddings': check_embeddings(),
               'bias_mitigation': check_bias_mitigation(),
               'analysis': check_analysis()
           },
           'performance': {
               'memory_usage': get_memory_usage(),
               'cpu_usage': get_cpu_usage(),
               'response_time': get_avg_response_time()
           }
       })
   ```

## Rollback Plan

### Quick Rollback

1. **Revert to previous version**
   ```bash
   git checkout main
   eb deploy previous-environment
   ```

2. **Database rollback** (if needed)
   ```sql
   -- Restore from backup if database changes were made
   ```

### Gradual Rollback

1. **Feature flags**
   ```python
   # Use feature flags for gradual rollout
   V4_ENABLED = os.environ.get('V4_ENABLED', 'false').lower() == 'true'
   
   if V4_ENABLED:
       # Use V4 components
       analysis_system = Version4AnalysisSystem()
   else:
       # Use V3 components
       analysis_system = Version3AnalysisSystem()
   ```

## Troubleshooting

### Common Issues

1. **Memory issues**
   ```bash
   # Increase memory limit
   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
   ```

2. **Model loading errors**
   ```bash
   # Clear model cache
   rm -rf /tmp/models/*
   ```

3. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install --force-reinstall -r requirements_enhanced_v4.txt
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```python
# Set debug environment variable
os.environ['DEBUG'] = 'true'

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Benchmarks

### Expected Performance

- **Face Detection**: < 2 seconds
- **Embedding Generation**: < 3 seconds
- **Skin Analysis**: < 5 seconds
- **Bias Evaluation**: < 1 second
- **Total Response Time**: < 10 seconds

### Monitoring Metrics

Track these key metrics:

- Response time percentiles (p50, p95, p99)
- Error rates by endpoint
- Memory usage
- CPU utilization
- Bias detection rates
- User satisfaction scores

## Security Considerations

1. **Input validation**
   ```python
   def validate_image(image_data):
       # Validate image size and format
       if len(image_data) > MAX_IMAGE_SIZE:
           raise ValueError("Image too large")
   ```

2. **Rate limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app)
   
   @app.route('/api/v4/skin/analyze-comprehensive', methods=['POST'])
   @limiter.limit("10 per minute")
   def analyze_skin_comprehensive():
       # Rate-limited endpoint
   ```

3. **Data privacy**
   ```python
   # Ensure no PII is logged
   def sanitize_logs(data):
       # Remove sensitive information
       return sanitized_data
   ```

## Success Criteria

### Technical Success Metrics

- [ ] All V4 components pass tests
- [ ] API response times < 10 seconds
- [ ] Error rate < 1%
- [ ] Memory usage < 2GB
- [ ] Bias detection working correctly

### Business Success Metrics

- [ ] User engagement maintained
- [ ] No increase in support tickets
- [ ] User satisfaction scores stable
- [ ] Performance metrics within acceptable ranges

## Post-Deployment Checklist

- [ ] Verify all endpoints are responding
- [ ] Check CloudWatch logs for errors
- [ ] Monitor performance metrics
- [ ] Test with real user data
- [ ] Validate bias mitigation is working
- [ ] Update documentation
- [ ] Train support team on new features

## Support and Maintenance

### Regular Maintenance

1. **Weekly health checks**
2. **Monthly performance reviews**
3. **Quarterly bias audits**
4. **Annual model updates**

### Emergency Contacts

- **Technical Lead**: [Your Contact]
- **DevOps**: [DevOps Contact]
- **Product Manager**: [PM Contact]

---

**Version**: 4.0.0  
**Last Updated**: [Current Date]  
**Next Review**: [Date + 3 months] 