# Shine Skincare App

A comprehensive skincare analysis application with advanced AI capabilities for skin condition detection and personalized recommendations.

## 🚀 **Latest Features (v2.1 - Operation Kitty Whiskers)**

### **Dual Skin Analysis System**
- **Selfie Analysis**: Google Vision API face isolation with SCIN dataset integration
- **General Skin Analysis**: Any skin photo analysis with advanced condition detection
- **Real-time Facial Matrix**: Visual feedback during selfie capture
- **Medical-grade AI**: Professional skin condition detection and recommendations

### **Enhanced AI Stack**
- **Level 4 Full AI**: FAISS, TIMM, Transformers, PyTorch integration
- **SCIN Dataset**: Medical-grade skin condition database
- **Google Vision API**: Face detection and isolation
- **Progressive Fallback**: 5-step AI loading protocol

### **Authentication & Data Management**
- **Supabase Integration**: User authentication and data storage
- **Medical Analysis Records**: Secure storage of skin condition data
- **Guest Login**: No registration required for basic analysis

## 🏗️ **Architecture**

### **Frontend (Next.js 15)**
```
/app
├── /selfie-analysis     # Selfie analysis with face isolation
├── /skin-analysis       # General skin condition analysis
├── /medical-analysis    # Medical-grade analysis results
├── /recommendations     # Personalized product recommendations
└── /profile            # User profile and history
```

### **Backend (Flask + AI Stack)**
```
/backend
├── /app
│   ├── /medical_analysis    # Medical analysis endpoints
│   ├── /services            # AI services and integrations
│   ├── /auth               # Supabase authentication
│   └── /enhanced_skin_analysis  # Advanced AI processing
└── /deployment-packages    # EB deployment packages
```

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 20+ (required for Supabase)
- Python 3.9+
- AWS Account (for deployment)
- Supabase Project
- Google Cloud Vision API

### **Local Development**

1. **Clone Repository**
```bash
git clone https://github.com/mcpmessenger/shine-skincare-app.git
cd shine-skincare-app
```

2. **Frontend Setup**
```bash
npm install
cp .env.example .env.local
# Add your environment variables to .env.local
npm run dev
```

3. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python app/__init__.py
```

### **Environment Variables**

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

**Backend (.env)**
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_google_credentials.json
```

## 🚀 **Deployment**

### **Frontend (AWS Amplify)**
- ✅ **Automatically deployed** on push to main branch
- ✅ **Latest version**: v2.1 with dual skin analysis
- ✅ **Status**: Live and operational

### **Backend (AWS Elastic Beanstalk)**
- 📦 **Latest Package**: `DUAL_SKIN_ANALYSIS_DEPLOYMENT_20250731_142309.zip`
- 🔧 **Instance Type**: m5.2xlarge (32GB RAM, 8 vCPUs)
- 🎯 **Features**: Full AI stack with SCIN dataset integration

### **Deployment Steps**

1. **Upload Backend Package**
```bash
# Use the latest deployment package
aws elasticbeanstalk create-application-version \
  --application-name shine-backend \
  --version-label v2.1-dual-analysis \
  --source-bundle S3Bucket="your-bucket",S3Key="DUAL_SKIN_ANALYSIS_DEPLOYMENT_20250731_142309.zip"
```

2. **Configure Environment Variables**
```bash
# Set in EB environment
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_APPLICATION_CREDENTIALS=your_google_credentials
```

3. **Deploy**
```bash
aws elasticbeanstalk update-environment \
  --environment-name shine-backend-prod \
  --version-label v2.1-dual-analysis
```

## 🔧 **API Endpoints**

### **Dual Skin Analysis**
- `POST /api/v2/selfie/analyze` - Selfie analysis with face isolation
- `POST /api/v2/skin/analyze` - General skin condition analysis
- `GET /api/v2/medical/history` - User analysis history
- `GET /api/v2/medical/analysis/<id>` - Specific analysis details

### **Health & Status**
- `GET /health` - Service health check
- `GET /api/health` - Detailed AI capabilities status

## 🎯 **AI Capabilities**

### **5-Step AI Loading Protocol**
1. **Core AI**: NumPy, Pillow, OpenCV
2. **Heavy AI**: FAISS, TIMM, Transformers, PyTorch
3. **Full AI**: Complete AI stack integration
4. **SCIN Dataset**: Medical database integration
5. **Google Vision**: Face detection and isolation

### **Fallback Strategy**
- **Primary**: Full AI with SCIN dataset
- **Secondary**: Heavy AI with core features
- **Tertiary**: Core AI with basic analysis
- **Final**: Mock responses for testing

## 📊 **Current Status**

### **✅ Operational**
- Frontend deployment (Amplify)
- Dual skin analysis pages
- API integration
- Navigation and routing
- Supabase authentication setup

### **🔄 In Progress**
- Backend deployment to Elastic Beanstalk
- Environment variable configuration
- End-to-end testing

### **📋 Next Steps**
1. Deploy backend package to EB
2. Configure environment variables
3. Test dual analysis workflows
4. Monitor performance and stability

## 🛠️ **Troubleshooting**

### **Build Issues**
- **Supabase URL Error**: Ensure environment variables are set in Amplify
- **Node.js Version**: Upgrade to Node.js 20+ for Supabase compatibility
- **Missing Dependencies**: Run `npm install` and check package.json

### **Deployment Issues**
- **EB Timeout**: Use lighter deployment packages for faster deployment
- **Memory Issues**: Ensure m5.2xlarge instance type for heavy AI workloads
- **CORS Errors**: Check CloudFront and backend CORS configuration

## 📚 **Documentation**

- [Operation Kitty Whiskers Guide](./Operation%20Kitty%20Whiskers.md)
- [Deployment Guide](./OPERATION_KITTY_WHISKERS_DEPLOYMENT_GUIDE.md)
- [Environment Setup](./ENVIRONMENT_SETUP_GUIDE.md)
- [Backend Deployment](./BACKEND_DEPLOYMENT_GUIDE.md)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated**: July 31, 2025  
**Version**: v2.1 - Operation Kitty Whiskers  
**Status**: Frontend Deployed, Backend Ready for Deployment