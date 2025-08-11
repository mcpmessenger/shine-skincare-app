# 🚀 **Shine Skincare App - Backend Services**

## 🎯 **Overview**

This directory contains the backend services for the Shine Skincare App, implementing a **hybrid deployment strategy** that ensures immediate deployment success while building toward full ML capabilities.

## 🏗️ **Architecture**

### **Service Components**
- **API Gateway**: Main API endpoints and request handling
- **ML Service**: Machine learning inference and skin analysis
- **Hybrid Approach**: Progressive ML integration with graceful fallbacks

### **Deployment Strategy**
- **Phase 1**: Simple health app (immediate 100% success)
- **Phase 2**: Progressive ML integration (graceful degradation)
- **Phase 3**: Full ML service (production-ready)

## 📁 **File Structure**

### **Core Applications**
- `simple_health_app.py` - **Phase 1**: Basic health checks, no ML dependencies
- `hybrid_ml_service.py` - **Phase 2**: Progressive ML integration with fallbacks
- `run_fixed_model_server.py` - **Phase 3**: Full ML service (when dependencies resolved)

### **Container Builds**
- `Dockerfile-simple` - Simple container (Flask + CORS only)
- `Dockerfile-hybrid` - Hybrid container (with ML dependency fallbacks)
- `Dockerfile` - Full ML container (original)

### **Dependencies**
- `requirements-minimal.txt` - Core dependencies only (~10MB)
- `requirements_full_ml.txt` - Full ML dependencies (~500MB)

### **Configuration**
- `simple-task-def.json` - ECS task definition for simple health app
- `clean-task-def.json` - Current production task definition

## 🚀 **Quick Start**

### **Phase 1: Deploy Simple Health App (Immediate Success)**
```bash
# Build and deploy simple container
cd backend
docker build -f Dockerfile-simple -t shine-api-gateway:simple .
docker push 396608803476.dkr.ecr.us-east-1.amazonaws.com/shine-api-gateway:simple

# Deploy to ECS
aws ecs register-task-definition --cli-input-json file://simple-task-def.json --region us-east-1
aws ecs update-service --cluster shine-ml-cluster --service shine-api-gateway --task-definition shine-api-gateway:simple --force-new-deployment --region us-east-1
```

### **Phase 2: Deploy Hybrid ML Service**
```bash
# Build and deploy hybrid container
docker build -f Dockerfile-hybrid -t shine-api-gateway:hybrid .
docker push 396608803476.dkr.ecr.us-east-1.amazonaws.com/shine-api-gateway:hybrid

# Update task definition and deploy
# (Update image in task definition to :hybrid)
```

## 🔍 **Service Endpoints**

### **Simple Health App**
- `GET /` - Service status and information
- `GET /health` - Health check endpoint

### **Hybrid ML Service**
- `GET /` - Service status with ML capabilities
- `GET /health` - Health check endpoint
- `GET /ml/status` - Detailed ML service status
- `POST /api/v5/skin/analyze-fixed` - Skin analysis (when ML ready)
- `POST /api/v4/face/detect` - Face detection (when ML ready)

### **Full ML Service**
- All endpoints from hybrid service
- Full ML inference capabilities
- S3 model integration

## 🛠️ **Development**

### **Local Testing**
```bash
# Test simple health app
python simple_health_app.py

# Test hybrid ML service
python hybrid_ml_service.py

# Test full ML service
python run_fixed_model_server.py
```

### **Dependency Management**
```bash
# Install minimal dependencies
pip install -r requirements-minimal.txt

# Install full ML dependencies
pip install -r requirements_full_ml.txt
```

## 📊 **Monitoring**

### **Health Checks**
- **Container Health**: ECS health checks on `/health` endpoint
- **ML Status**: `/ml/status` endpoint for ML service state
- **Service Status**: Root endpoint for overall service health

### **Logging**
- **Application Logs**: Structured logging with ML dependency status
- **Error Tracking**: Detailed error messages and stack traces
- **Performance Metrics**: Startup time and ML model loading status

## 🔧 **Troubleshooting**

### **Common Issues**
1. **Port Binding Failures**: Use simple health app for immediate success
2. **ML Dependency Failures**: Check `/ml/status` endpoint for detailed diagnostics
3. **S3 Model Access**: Verify AWS credentials and model file existence

### **Debug Commands**
```bash
# Check container logs
aws logs get-log-events --log-group-name "/ecs/shine-api-gateway" --region us-east-1

# Check service status
aws ecs describe-services --cluster shine-ml-cluster --services shine-api-gateway --region us-east-1

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:5000/ml/status
```

## 📚 **Documentation**

- **Deployment Strategy**: `HYBRID_DEPLOYMENT_STRATEGY.md`
- **Main Deployment**: `../DEPLOYMENTDOC.md`
- **Architecture**: `new-architecture/README.md`

---

**This hybrid approach ensures you get a working production system immediately while building toward full ML capabilities.** 🎯 