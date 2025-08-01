# Shine Skincare App

**🧠 Operation Left Brain v2.2 - Advanced AI Integration Complete!**

A comprehensive skincare analysis platform powered by advanced AI, featuring real-time skin condition detection, personalized product recommendations, and medical-grade analysis capabilities.

## 🚀 Latest Updates - Operation Left Brain v2.2

### ✅ **New Features Added:**
- **🧠 Advanced ML Pipeline**: Complete AI integration with deep feature extraction
- **🔍 Enhanced Skin Analysis**: Texture analysis, color analysis, and condition detection
- **📊 SCIN Dataset Integration**: Medical-grade similarity search using FAISS
- **💊 Treatment Recommendations**: AI-powered personalized treatment suggestions
- **🔧 V2 API Endpoints**: New advanced endpoints for enhanced analysis
- **📈 Real-time Progress**: Live analysis progress indicators
- **🎨 Enhanced Results Display**: Better visualization of skin conditions

### 🏗️ **Architecture:**
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: Flask with advanced ML services (EfficientNet-B0, FAISS, Google Vision API)
- **AI Pipeline**: Image preprocessing → Face detection → Feature extraction → Condition detection → SCIN search → Treatment recommendations
- **Deployment**: AWS Amplify (Frontend) + Elastic Beanstalk (Backend)

## 🎯 **Key Features**

### **AI-Powered Analysis**
- **Selfie Analysis**: Advanced facial feature detection and skin condition analysis
- **General Skin Analysis**: Comprehensive skin texture and color analysis
- **Medical Analysis**: Professional-grade analysis with SCIN dataset integration
- **Treatment Recommendations**: Personalized treatment plans based on AI analysis

### **Advanced ML Capabilities**
- **Deep Feature Extraction**: Using EfficientNet-B0 for image embedding
- **FAISS Vector Search**: High-performance similarity search on medical dataset
- **Google Vision API**: Professional face detection and isolation
- **Texture Analysis**: Local Binary Patterns (LBP) for skin texture analysis
- **Color Analysis**: HSV color space analysis for skin condition assessment

### **User Experience**
- **Real-time Progress**: Live analysis progress indicators
- **Enhanced Results**: Beautiful visualization of analysis results
- **Treatment Recommendations**: Personalized product and treatment suggestions
- **Medical Integration**: Access to medical-grade skin condition database

## 🛠️ **Technology Stack**

### **Frontend**
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React hooks and context
- **API Integration**: Custom API client with advanced ML endpoints

### **Backend**
- **Framework**: Flask with CORS support
- **AI Services**: 
  - `timm` for deep feature extraction (EfficientNet-B0)
  - `faiss-cpu` for vector similarity search
  - `google-cloud-vision` for face detection
  - `opencv-python-headless` for image processing
  - `scikit-learn` for machine learning utilities
- **Deployment**: AWS Elastic Beanstalk with environment variables

### **AI Pipeline**
1. **Image Preprocessing**: Resize, normalize, and prepare images
2. **Face Detection**: Google Vision API for facial feature extraction
3. **Feature Extraction**: Deep learning models for image embedding
4. **Condition Detection**: AI-powered skin condition classification
5. **SCIN Search**: Medical dataset similarity search
6. **Treatment Generation**: Personalized recommendations

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm
- Python 3.9+ and pip
- AWS account (for deployment)
- Google Cloud account (for Vision API)

### **Local Development**

1. **Clone the repository**
```bash
git clone https://github.com/mcpmessenger/shine-skincare-app.git
cd shine-skincare-app
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Frontend (.env.local)
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend (environment variables)
GOOGLE_CLOUD_PROJECT=your_google_cloud_project
GOOGLE_VISION_API_KEY=your_google_vision_api_key
```

5. **Start development servers**
```bash
# Frontend (from root)
npm run dev

# Backend (from backend directory)
python app.py
```

### **Testing the New V2 API**
Visit `http://localhost:3000/test-v2-api` to test the new Operation Left Brain endpoints:
- **AI Status Check**: Monitor AI service health
- **Selfie Analysis V2**: Advanced facial analysis
- **Skin Analysis V2**: Enhanced skin condition detection
- **SCIN Search Advanced**: Medical dataset similarity search

## 📊 **API Endpoints**

### **Operation Left Brain v2.2 Endpoints**
- `POST /api/v2/selfie/analyze` - Advanced selfie analysis
- `POST /api/v2/skin/analyze` - Enhanced skin analysis
- `GET /api/v2/ai/status` - AI service status
- `GET /api/v2/ai/health` - AI service health check
- `POST /api/scin/search` - Advanced SCIN dataset search

### **Legacy Endpoints**
- `POST /api/v2/selfie/analyze` - Basic selfie analysis
- `POST /api/v2/skin/analyze` - Basic skin analysis
- `GET /api/health` - Health check
- `GET /api/test` - Test endpoint

## 🚀 **Deployment**

### **Frontend (AWS Amplify)**
- Connected to GitHub repository
- Automatic deployments on push to main branch
- Environment variables configured in Amplify console

### **Backend (AWS Elastic Beanstalk)**
- Environment: `shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com`
- Platform: Python 3.9
- Environment variables configured for Google Cloud services

## 🔧 **Environment Variables**

### **Frontend (.env.local)**
```bash
NEXT_PUBLIC_BACKEND_URL=https://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### **Backend (Elastic Beanstalk)**
```bash
GOOGLE_CLOUD_PROJECT=shine-466907
GOOGLE_VISION_API_KEY=your_complete_service_account_json
```

## 📈 **Performance & Monitoring**

### **Health Checks**
- **Frontend**: Available at `https://www.shineskincollective.com`
- **Backend**: Available at `http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/health`
- **AI Services**: Monitor via `/api/v2/ai/health` endpoint

### **Current Status**
- ✅ **Frontend**: Deployed and operational
- ✅ **Backend**: Deployed with Operation Left Brain v2.2
- ✅ **AI Services**: Advanced ML pipeline operational
- ✅ **Database**: SCIN dataset integration active
- ✅ **API Integration**: All v2 endpoints functional

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For support and questions:
- **Documentation**: Check the various `.md` files in the repository
- **Issues**: Open an issue on GitHub
- **Testing**: Use the test endpoints at `/test-v2-api`

---

**🧠 Operation Left Brain v2.2 - Advanced AI Integration Complete!** 

*Last updated: January 2025*