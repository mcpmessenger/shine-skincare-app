# 🐳 Docker + ECS Full ML Deployment Guide

## 🎯 **Overview**
Deploy the complete Shine ML backend with full TensorFlow capabilities using Docker and AWS ECS.

## ✅ **Prerequisites**
- AWS CLI configured with appropriate permissions
- Docker installed and running
- AWS account with ECS, ECR, and VPC access

## 🚀 **Quick Start**

### **1. Test Locally First**
```bash
cd backend

# Build and test locally
docker build -t shine-ml-backend .
docker run -p 5000:5000 -e AWS_ACCESS_KEY_ID=xxx -e AWS_SECRET_ACCESS_KEY=xxx shine-ml-backend

# Test endpoints
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/v4/face/detect -H "Content-Type: application/json" -d '{"image_data":"base64..."}'
```

### **2. Deploy to AWS ECS**
```bash
# Make deployment script executable
chmod +x deploy-ecs.sh

# Run deployment
./deploy-ecs.sh
```

## 🏗️ **Architecture**

### **Container Specifications**
- **Base Image**: Python 3.11-slim
- **CPU**: 1 vCPU (1024 units)
- **Memory**: 3GB (3072 MB)
- **Platform**: AWS Fargate
- **Networking**: awsvpc mode

### **Full ML Stack**
```
✅ TensorFlow 2.13.0
✅ OpenCV (headless)
✅ scikit-learn
✅ NumPy, Pandas
✅ Matplotlib, Seaborn
✅ boto3 (S3 integration)
```

### **Endpoints Available**
- `GET /api/health` - Health check
- `POST /api/v4/face/detect` - Face detection
- `POST /api/v5/skin/analyze-fixed` - Full ML skin analysis

## 🔧 **Manual Setup Steps**

### **1. Create Required AWS Resources**

#### **ECR Repository**
```bash
aws ecr create-repository --repository-name shine-ml-backend --region us-east-1
```

#### **ECS Cluster**
```bash
aws ecs create-cluster --cluster-name shine-ml-cluster --capacity-providers FARGATE --region us-east-1
```

#### **IAM Roles**
Create task execution role and task role with appropriate permissions:
- ECR access
- CloudWatch logs
- S3 access for model files

### **2. Network Configuration**
Update `deploy-ecs.sh` with your VPC details:
- Subnet IDs
- Security Group IDs
- Load Balancer configuration

### **3. Domain Setup**
Configure Application Load Balancer and Route 53 for custom domain.

## 📊 **Expected Performance**

### **Startup Time**
- **Cold Start**: 2-3 minutes (model download from S3)
- **Warm Start**: 30-60 seconds

### **Response Times**
- **Face Detection**: 200-500ms
- **ML Skin Analysis**: 1-3 seconds
- **Health Check**: <100ms

### **Resource Usage**
- **CPU**: 20-60% during analysis
- **Memory**: 1.5-2.5GB (models loaded)
- **Network**: Minimal (S3 model download on startup)

## 💰 **Cost Estimation**

### **AWS ECS Fargate**
- **Compute**: ~$35-50/month (1 vCPU, 3GB RAM, 24/7)
- **Data Transfer**: ~$5-10/month
- **Storage**: ~$2-5/month (ECR, logs)
- **Total**: ~$40-65/month

### **Cost Optimization**
- Use scheduled scaling for non-24/7 usage
- Implement auto-scaling based on demand
- Optimize container resource allocation

## 🔍 **Monitoring & Troubleshooting**

### **CloudWatch Logs**
```bash
# View logs
aws logs describe-log-groups --log-group-name-prefix "/ecs/shine-ml"
aws logs get-log-events --log-group-name "/ecs/shine-ml-backend" --log-stream-name "ecs/shine-ml-container/TASK_ID"
```

### **ECS Service Status**
```bash
# Check service status
aws ecs describe-services --cluster shine-ml-cluster --services shine-ml-service

# Check tasks
aws ecs list-tasks --cluster shine-ml-cluster --service-name shine-ml-service
aws ecs describe-tasks --cluster shine-ml-cluster --tasks TASK_ARN
```

### **Common Issues**
1. **Model Download Timeout**: Increase task startup time
2. **Memory Issues**: Increase memory allocation
3. **Network Issues**: Check security groups and VPC configuration

## 🎉 **Benefits Over EB**

### **Advantages**
✅ **No size limits** (vs EB's 512MB)
✅ **Full ML stack** (TensorFlow, scikit-learn)
✅ **Better resource control** (CPU, memory)
✅ **Scalability** (auto-scaling, load balancing)
✅ **Production-ready** (health checks, monitoring)

### **Trade-offs**
⚠️ **Higher complexity** (more AWS services)
⚠️ **Slightly higher cost** (~$40-65/month vs ~$25-40/month)
⚠️ **Longer setup time** (2-3 hours vs 30 minutes)

## 🎯 **Next Steps After Deployment**

1. **Update Frontend**: Point to new ECS service URL
2. **Test ML Functions**: Verify all ML models work
3. **Performance Tuning**: Optimize based on usage patterns
4. **Monitoring Setup**: Configure alerts and dashboards
5. **Auto-scaling**: Set up scaling policies

---

**Ready to deploy the full ML stack!** 🚀
