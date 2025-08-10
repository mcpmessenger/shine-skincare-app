# 🚀 ML Model S3 Upload Guide

## **Overview**
This guide explains how to upload the ML model file to S3 and deploy the updated Elastic Beanstalk application that automatically downloads the model at runtime.

## **Why S3?**
- ✅ **No Size Limits**: S3 can handle large model files (our model is 214MB)
- ✅ **Faster Deployments**: EB packages stay small without large files
- ✅ **Easier Updates**: Update models without redeploying the entire app
- ✅ **Cost Effective**: S3 storage is cheaper than EB storage

## **Prerequisites**
- AWS CLI configured with appropriate permissions
- Python 3.x with boto3 installed
- Access to create S3 buckets and upload files

## **Step 1: Upload Model to S3**

### **Option A: Use the Helper Script (Recommended)**
```bash
cd backend
python upload_model_to_s3.py
```

This script will:
- Create the S3 bucket `shine-ml-models-2025` if it doesn't exist
- Upload `models/fixed_model_best.h5` to S3
- Verify the upload was successful

### **Option B: Manual AWS CLI Commands**
```bash
# Create S3 bucket
aws s3 mb s3://shine-ml-models-2025

# Upload model file
aws s3 cp models/fixed_model_best.h5 s3://shine-ml-models-2025/

# Verify upload
aws s3 ls s3://shine-ml-models-2025/
```

## **Step 2: Deploy Updated Application**
```bash
cd backend
eb deploy
```

The updated application will:
- Automatically download the model from S3 at startup
- Store it locally at `/opt/python/current/app/models/fixed_model_best.h5`
- Make it available for ML analysis endpoints

## **Step 3: Verify Model Integration**
```bash
# Check if the model is available
curl http://shine-backend-light.eba-ueb7him5.us-east-1.elasticbeanstalk.com/ready

# Expected response:
{
  "status": "ready",
  "service": "shine-backend-combined",
  "model_available": true,
  "model_path": "/opt/python/current/app/models/fixed_model_best.h5",
  "s3_location": "s3://shine-ml-models-2025/fixed_model_best.h5",
  "message": "Service is ready"
}
```

## **Configuration**
The application uses these environment variables (with defaults):
- `S3_BUCKET`: S3 bucket name (default: `shine-ml-models-2025`)
- `S3_MODEL_KEY`: Model file name in S3 (default: `fixed_model_best.h5`)
- `MODEL_PATH`: Local path to store downloaded model (default: `/opt/python/current/app/models/fixed_model_best.h5`)

## **Troubleshooting**

### **Model Download Fails**
- Check S3 bucket permissions
- Verify model file exists in S3
- Check EB instance IAM role has S3 read permissions

### **Deployment Still Fails**
- Ensure `.ebignore` excludes `models/` directory
- Check that `boto3` is in `requirements.txt`
- Verify S3 bucket name is correct

### **Model Not Found After Deployment**
- Check EB logs: `eb logs --all`
- Verify S3 bucket and file names
- Check IAM permissions for EB instance

## **Benefits of This Approach**
1. **Smaller Deployments**: No large files in EB package
2. **Faster Iteration**: Deploy code changes without model files
3. **Model Management**: Update models independently of application code
4. **Scalability**: Multiple instances can download models as needed
5. **Cost Optimization**: S3 storage is cheaper than EB storage

## **Next Steps**
After successful deployment:
1. Test all ML endpoints
2. Implement actual ML analysis logic
3. Add model versioning and updates
4. Configure CloudWatch monitoring for model downloads

---

**Note**: The model file is automatically downloaded when the application starts or when the first request is made to an endpoint that requires it.
