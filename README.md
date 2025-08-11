# Shine Skincare App

A comprehensive skincare analysis application that uses AI/ML to analyze skin conditions and provide personalized recommendations.

## 🏗️ **Current Architecture**

### **Frontend**
- **Framework**: Next.js 14 with TypeScript
- **Deployment**: AWS Amplify via GitHub
- **Styling**: Tailwind CSS
- **Authentication**: Google OAuth + Supabase

### **Backend**
- **Services**: ECS Fargate with Application Load Balancer
- **API Gateway**: Port 8080 (main API endpoints)
- **ML Service**: Port 5000 (skin analysis & ML features)
- **Load Balancer**: `production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com`

## 🚀 **Deployment Status**

✅ **Backend**: Successfully deployed with new ALB  
✅ **Frontend**: Ready for deployment with updated endpoints  
🔄 **Next**: Update Amplify environment variables and redeploy

## 🔧 **Environment Variables (Amplify)**

**Required for deployment:**
```
NEXT_PUBLIC_BACKEND_URL=http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com
BACKEND_URL=http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com
NEXT_PUBLIC_API_URL=http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com
REACT_APP_API_BASE_URL=http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com
```

## 📱 **Features**

- **Skin Analysis**: AI-powered skin condition detection
- **Facial Recognition**: Advanced face detection and analysis
- **ML Integration**: Enhanced ML models with SCIN dataset
- **Product Recommendations**: Personalized skincare suggestions
- **User Management**: Authentication and profile management
- **Payment Integration**: Stripe payment processing

## 🛠️ **Development Setup**

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 🌐 **API Endpoints**

### **V5 (Latest)**
- `/api/v5/skin/analyze-fixed` - Enhanced skin analysis
- `/api/v5/skin/model-status` - ML model status
- `/api/v5/skin/health` - Health check

### **V4 (Stable)**
- `/api/v4/face/detect` - Face detection
- `/api/v4/skin/analyze-enhanced` - Enhanced skin analysis

### **ML Service**
- `/ml/*` - All ML-related endpoints

## 📚 **Documentation**

- **Deployment**: `DEPLOYMENTDOC.md` - Complete deployment guide
- **Backend**: `backend/new-architecture/` - Current backend architecture
- **API**: `lib/api.ts` - API client and endpoints

## 🔄 **Deployment Process**

### **1. Update Environment Variables**
In AWS Amplify Console:
- Set all backend URLs to new ALB endpoint
- Save and trigger redeployment

### **2. Verify Backend**
```bash
# Test API Gateway
curl http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com/health

# Test ML Service
curl http://production-shine-skincare-alb-1879927784.us-east-1.elb.amazonaws.com/ml/health
```

### **3. Deploy Frontend**
- Commit environment variable changes
- Push to GitHub
- Amplify auto-deploys

## 🎯 **Current Focus**

- **Mixed Content Resolution**: Frontend HTTPS → Backend HTTP (temporary)
- **HTTPS Upgrade**: Ready for SSL certificate when available
- **Performance**: ALB routing and load balancing
- **Stability**: ECS service health monitoring

## 📞 **Support**

For deployment issues, refer to `DEPLOYMENTDOC.md` for detailed troubleshooting and current status.

---

*Last Updated: 2025-08-11 - Backend deployed, frontend ready for deployment*