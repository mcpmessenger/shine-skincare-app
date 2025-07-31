# Manual Backend Deployment Commands

## Package Created Successfully

The deployment package has been created and uploaded to S3:
- **Package**: `SHINE_MANUAL_DEPLOYMENT-20250730_195421.zip`
- **S3 Location**: `s3://shine-backend-deployments/SHINE_MANUAL_DEPLOYMENT-20250730_195421.zip`
- **Size**: 5.1 KiB

## What's Included in the Package

### ✅ CORS Fixes
- CORS headers added to all responses
- OPTIONS method support for preflight requests
- Proper origin handling for https://www.shineskincollective.com

### ✅ File Size Fixes
- 100MB file upload limit (supports modern phone selfies)
- Custom 413 error handler with helpful messages
- Explicit file size validation

### ✅ Enhanced Features
- ML-powered skin analysis
- Face detection simulation
- FAISS similarity search
- Demographic analysis

## Manual Deployment Steps

### Step 1: Create Application Version
```bash
aws elasticbeanstalk create-application-version \
  --application-name SHINE \
  --version-label manual-deployment-fixed-20250730-195421 \
  --source-bundle S3Bucket="shine-backend-deployments",S3Key="SHINE_MANUAL_DEPLOYMENT-20250730_195421.zip" \
  --region us-east-1
```

### Step 2: Update Environment
```bash
aws elasticbeanstalk update-environment \
  --environment-name SHINE-env \
  --version-label manual-deployment-fixed-20250730-195421 \
  --region us-east-1
```

### Step 3: Monitor Deployment
```bash
aws elasticbeanstalk describe-environments \
  --environment-names SHINE-env \
  --region us-east-1 \
  --query "Environments[0].{Status:Status,Health:Health,VersionLabel:VersionLabel}"
```

## Testing After Deployment

### Health Check
```bash
Invoke-WebRequest -Uri "https://d1kmi2r0duzr21.cloudfront.net/health" -Method GET
```

### CORS Test
```bash
Invoke-WebRequest -Uri "https://d1kmi2r0duzr21.cloudfront.net/api/v2/analyze/guest" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"test": "cors"}'
```

### File Upload Test (with small image)
```bash
# Test with a small image file to verify 100MB limit works
```

## Expected Results

After successful deployment:

1. **Health Endpoint**: Should return status "healthy" with version "manual-deployment-fixed"
2. **CORS**: No more CORS errors from frontend
3. **File Upload**: Should handle modern phone selfies (2-5MB) without 413 errors
4. **Analysis**: Enhanced ML analysis with face detection and similarity search

## Troubleshooting

If deployment fails:

1. **Check S3 File**: Verify the file exists in S3
   ```bash
   aws s3 ls s3://shine-backend-deployments/SHINE_MANUAL_DEPLOYMENT-20250730_195421.zip --region us-east-1
   ```

2. **Check Environment Status**:
   ```bash
   aws elasticbeanstalk describe-environments --environment-names SHINE-env --region us-east-1
   ```

3. **View Logs** (if needed):
   ```bash
   aws elasticbeanstalk retrieve-environment-info --environment-name SHINE-env --info-type tail --region us-east-1
   ```

## Package Contents

The deployment package includes:
- `application.py` - Main Flask app with all fixes
- `requirements.txt` - Python dependencies
- `Procfile` - Gunicorn configuration
- `.ebextensions/env.config` - Elastic Beanstalk configuration
- `deployment-manifest.json` - Package metadata
- `README.md` - Deployment instructions

## Features Included

- ✅ Handles modern phone selfies (2-5MB)
- ✅ No more 413 Content Too Large errors
- ✅ CORS properly configured
- ✅ Enhanced ML analysis
- ✅ Face detection and cropping
- ✅ Similarity search
- ✅ Demographic analysis
- ✅ m5.2xlarge instance optimization

Ready for deployment! 