# Shine Skincare App

**🧠 Operation Left Brain v2.3 - Enhanced AI Integration with Google OAuth!**

A comprehensive skincare analysis platform powered by advanced AI, featuring real-time skin condition detection, personalized product recommendations, medical-grade analysis capabilities, and secure Google OAuth authentication.

## 🚀 Latest Updates - Operation Left Brain v2.3

### ✅ **New Features Added:**
- **🔐 Google OAuth Integration**: Secure authentication with Google accounts
- **🧠 Enhanced Skin Analysis**: OpenAI embeddings + Google Vision API integration
- **🔍 Advanced Face Detection**: Isolated facial analysis with cropping
- **📊 SCIN Dataset Search**: Medical-grade similarity matching
- **💊 AI-Powered Recommendations**: Personalized treatment suggestions
- **🎨 Enhanced UI**: New "Enhanced Analysis" page with progress tracking
- **🔧 V3 API Endpoints**: Latest advanced endpoints for enhanced analysis
- **📈 Real-time Progress**: Live analysis progress indicators
- **🎯 Dual Analysis Modes**: Standard and Enhanced analysis options

### 🏗️ **Architecture:**
- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: Flask with OpenAI embeddings and Google Vision API
- **AI Pipeline**: Image preprocessing → Face detection → OpenAI embeddings → SCIN search → AI analysis
- **Authentication**: Google OAuth 2.0 integration
- **Deployment**: AWS Amplify (Frontend) + Elastic Beanstalk (Backend)

## 🎯 **Key Features**

### **AI-Powered Analysis**
- **Enhanced Skin Analysis**: OpenAI embeddings + Google Vision API
- **Standard Skin Analysis**: Traditional Google Vision API analysis
- **Face Detection & Isolation**: Advanced facial feature cropping
- **Medical-Grade Search**: SCIN dataset similarity matching
- **Treatment Recommendations**: AI-powered personalized suggestions

### **Advanced ML Capabilities**
- **OpenAI Embeddings**: Text-embedding-ada-002 model for image analysis
- **Google Vision API**: Professional face detection and image analysis
- **SCIN Dataset Integration**: Medical-grade skin condition database
- **Face Isolation**: Automatic cropping to facial regions
- **AI-Generated Analysis**: OpenAI-powered skin condition assessment

### **User Experience**
- **Google OAuth**: Secure login with Google accounts
- **Dual Analysis Modes**: Choose between standard and enhanced analysis
- **Real-time Progress**: Live analysis progress indicators
- **Enhanced Results**: Beautiful visualization with detailed breakdowns
- **Treatment Recommendations**: Personalized product and treatment suggestions

## 🛠️ **Technology Stack**

### **Frontend**
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with shadcn/ui components
- **Authentication**: Google OAuth 2.0
- **State Management**: React hooks and context
- **API Integration**: Custom API client with V3 endpoints

### **Backend**
- **Framework**: Flask with CORS support
- **AI Services**: 
  - `openai==1.3.5` for embeddings generation
  - `google-cloud-vision==3.4.4` for face detection
  - `Pillow` for image processing
  - `numpy` for data processing
- **Authentication**: Google OAuth client integration
- **Deployment**: AWS Elastic Beanstalk with environment variables

### **AI Pipeline (Enhanced)**
1. **Image Upload**: User uploads skin image
2. **Face Detection**: Google Vision API detects facial regions
3. **Face Isolation**: Automatic cropping to facial area
4. **OpenAI Embeddings**: Generate image embeddings using text-embedding-ada-002
5. **SCIN Search**: Medical dataset similarity search
6. **AI Analysis**: OpenAI-powered skin condition assessment
7. **Recommendations**: Personalized treatment suggestions

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm
- Python 3.9+ and pip
- AWS account (for deployment)
- Google Cloud account (for Vision API and OAuth)
- OpenAI API key (for enhanced analysis)

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
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_VISION_API_KEY=your_google_vision_api_key
OPENAI_API_KEY=your_openai_api_key
```

5. **Start development servers**
```bash
# Frontend (from root)
npm run dev

# Backend (from backend directory)
python application.py
```

### **Testing the Enhanced Features**
- **Enhanced Analysis**: Visit `/enhanced-skin-analysis` for the new AI-powered analysis
- **Google OAuth**: Test login functionality at `/auth/login`
- **Standard Analysis**: Use `/skin-analysis` for traditional analysis

## 📊 **API Endpoints**

### **Enhanced Analysis (V3)**
- `POST /api/v3/skin/analyze-enhanced` - Enhanced skin analysis with OpenAI embeddings
- `POST /api/auth/login` - Google OAuth login
- `POST /api/auth/callback` - Google OAuth callback

### **Standard Analysis (V2)**
- `POST /api/v2/selfie/analyze` - Standard selfie analysis
- `POST /api/v2/skin/analyze` - Standard skin analysis
- `GET /api/v2/ai/status` - AI service status

### **Health & Testing**
- `GET /api/health` - Health check
- `GET /api/test` - Test endpoint

## 🚀 **Deployment**

### **Frontend (AWS Amplify)**
- **GitHub Integration**: Automatic deployments on push to main branch
- **Environment Variables**: Configured for production
- **Custom Domain**: Available at production URL

### **Backend (AWS Elastic Beanstalk)**
- **Platform**: Python 3.9
- **Environment Variables**: All credentials properly configured
- **Health Monitoring**: Continuous health checks

## 🔧 **Environment Variables**

### **Frontend (Amplify)**
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.elasticbeanstalk.com
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_APP_URL=https://your-app-url.amplifyapp.com
```

### **Backend (Elastic Beanstalk)**
```bash
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_VISION_API_KEY=your_google_vision_service_account_json
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

## 📈 **Performance & Monitoring**

### **Health Checks**
- **Frontend**: Available at production domain
- **Backend**: Available at Elastic Beanstalk URL
- **AI Services**: Monitor via `/api/v2/ai/health` endpoint

### **Current Status**
- ✅ **Frontend**: Deployed and operational with Google OAuth
- ✅ **Backend**: Deployed with enhanced AI integration
- ✅ **Google OAuth**: Properly configured and working
- ✅ **Enhanced Analysis**: OpenAI embeddings + Google Vision operational
- ✅ **Database**: Supabase integration active
- ✅ **API Integration**: All V3 endpoints functional

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
- **Testing**: Use the enhanced analysis at `/enhanced-skin-analysis`

---

**🧠 Operation Left Brain v2.3 - Enhanced AI Integration with Google OAuth Complete!** 

*Last updated: August 2025*