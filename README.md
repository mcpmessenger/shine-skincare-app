# Shine Skin Collective

A comprehensive skincare analysis application that uses AI/ML to analyze skin conditions and provide personalized recommendations.

## 🚀 **Current Status**

### **Production Status: 95% RESOLVED - ALB-ECS Network Connectivity Issue**
- ✅ **Infrastructure**: Correctly configured with proper port alignment
- ✅ **ML Cluster**: Successfully redeployed and working
- ✅ **Resource Cleanup**: Removed unused target groups and old ECR images
- ✅ **Container Image**: RESOLVED with Hare Run V6 container
- ❌ **Production Face Detection**: ALB cannot reach ECS container (network connectivity issue)
- 🔄 **Next Step**: Fix ALB-ECS network connectivity (security groups, routing)

### **What's Working:**
- **Frontend**: Next.js 14 with TypeScript, deployed via AWS Amplify
- **ML Cluster**: `shine-ml-cluster` with working face detection
- **Infrastructure**: ECS, ALB, and target groups properly configured
- **Authentication**: Google OAuth + Supabase integration

### **What's Been Fixed:**
- ✅ **Production Container**: RESOLVED with Hare Run V6 container that respects environment variables
- ✅ **Port Configuration Chaos**: RESOLVED - All components now use port 8000 consistently
- ✅ **Container Image**: RESOLVED - Hare Run V6 container runs on port 8000 correctly
- ❌ **ALB-ECS Network**: ALB cannot reach ECS container (health check timeouts)
- ❌ **Health Checks**: Failing due to network connectivity issues between ALB and ECS

## 🏗️ **Architecture**

### **Frontend**
- **Framework**: Next.js 14 with TypeScript
- **Deployment**: AWS Amplify via GitHub
- **Styling**: Tailwind CSS
- **Authentication**: Google OAuth + Supabase

### **Backend**
- **Services**: ECS Fargate with Application Load Balancer
- **API Gateway**: Port 8000 (main API endpoints)
- **ML Service**: Enhanced ML models with SCIN dataset
- **Load Balancer**: `api.shineskincollective.com`

### **Infrastructure**
- **ECS Clusters**: `production-shine-cluster` (production), `shine-ml-cluster` (ML services)
- **Load Balancer**: Application Load Balancer with health checks
- **Storage**: S3 for ML models and embeddings
- **Monitoring**: CloudWatch logs and metrics

## 🔧 **Development Setup**

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 🌐 **API Endpoints**

### **Production (Port 8000)**
- `/health` - Health check endpoint
- `/api/health` - Detailed API status with model information

### **ML Services**
- `/api/v6/skin/analyze-hare-run` - Latest Hare Run V6 analysis
- `/api/v5/skin/analyze-fixed` - Enhanced skin analysis
- `/api/v4/face/detect` - Face detection
- `/api/v4/skin/analyze-enhanced` - Enhanced skin analysis

## 📚 **Documentation**

### **Backend Documentation**
- **Operation Tortoise Wisdom**: `docs/markdown/backend/OPERATION_TORTOISE_WISDOM.md` - Critical architecture principles and lessons learned
- **Production Face Detection**: `docs/markdown/backend/PRODUCTION_FACE_DETECTION_ISSUE_ANALYSIS.md` - Current production issue analysis
- **Backend README**: `docs/markdown/backend/README.md` - Backend architecture and setup

### **Frontend Documentation**
- **Frontend README**: `docs/markdown/frontend/README.md` - Frontend setup and development

## 🎯 **Current Focus**

### **Immediate Priorities**
1. **🔄 Fix ALB-ECS Network Connectivity**: Resolve health check timeouts between ALB and ECS
2. **✅ Infrastructure Cleanup**: Removed unused target groups and old ECR images
3. **✅ Container Image Fix**: RESOLVED with Hare Run V6 container
4. **✅ Port Alignment**: RESOLVED - All components use port 8000 consistently
5. **Performance Optimization**: Reduce response times
6. **Monitoring Enhancement**: Better visibility into system health

### **Infrastructure Cleanup**
- **✅ Completed**: Deleted `tubby-test` cluster (unused test environment)
- **✅ Completed**: Fixed `shine-ml-cluster` (redeployed working services)
- **✅ Completed**: Removed unused target groups and old ECR images
- **🔄 Next**: Clean up old task definitions (keep only revisions 19, 20)

## 🐢 **Development Philosophy**

We follow the **Tortoise Approach**: *"Slow and steady wins the race"*

### **Core Principles**
- **Incremental Improvement**: Small, testable changes over radical rewrites
- **Defensive Programming**: Always handle failures gracefully
- **Systematic Problem Solving**: Understand the problem before attempting fixes
- **Preserve Working Infrastructure**: Fix broken components instead of starting over

### **Recent Lessons Learned**
- **Port Configuration Mismatches**: Can hide in multiple layers (ALB, target groups, ECS, containers)
- **Container Image Overrides**: Hardcoded defaults can ignore environment variables
- **Redeployment Strategy**: Often better to fix broken services than delete and recreate

## 📞 **Support & Troubleshooting**

For current issues and troubleshooting:
1. **Production Face Detection**: See `docs/markdown/backend/PRODUCTION_FACE_DETECTION_ISSUE_ANALYSIS.md`
2. **Architecture Principles**: See `docs/markdown/backend/OPERATION_TORTOISE_WISDOM.md`
3. **Backend Setup**: See `docs/markdown/backend/README.md`

---

*Last Updated: 2025-08-15 - Hare Run V6 Container Deployed ✅ - ALB-ECS Network Connectivity Issue Identified*