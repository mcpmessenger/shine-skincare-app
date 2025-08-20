# Shine Skin Collective - AI-Powered Skincare Analysis

A sophisticated web application that provides personalized skincare analysis and intelligent product recommendations using advanced AI and computer vision.

## ✨ Key Features

### 🧠 **Intelligent Product Recommendation Engine**
- **AI-Powered Scoring System**: Advanced algorithm that scores products based on multiple factors:
  - Skin health score analysis (0-100%)
  - Specific skin conditions (acne, hyperpigmentation, aging, etc.)
  - Product category matching (cleanser, treatment, serum, moisturizer, sunscreen)
  - Ingredient analysis (salicylic acid, retinol, vitamin C, niacinamide, etc.)
  - Brand reputation and medical-grade formulations
  - Price considerations and affordability
- **Dynamic Scoring**: Products receive scores based on relevance to detected skin concerns
- **Category Diversity**: Ensures balanced recommendations across different product types
- **Personalized Reasoning**: Each recommendation includes detailed explanation of why it was selected

### 🔍 **Advanced Face Detection & Analysis**
- **Mandatory Face Detection**: Every image analysis requires successful face detection
- **Real-time Processing**: Live camera feed with continuous face detection
- **Multiple Input Methods**: 
  - Live camera capture
  - Image upload with face validation
- **Face Validation**: Analysis only proceeds when face is detected with >90% confidence
- **OpenCV Integration**: Professional-grade face detection using Haar Cascade Classifiers

### 📊 **Enhanced ML Analysis (Hare Run 4)**
- **Multi-Condition Detection**: Identifies 8+ skin conditions simultaneously
- **Severity Assessment**: Provides detailed severity levels for each condition
- **Health Score Calculation**: Overall skin health assessment (0-100%)
- **Primary Concerns**: Identifies most significant skin issues
- **Model Accuracy**: 97.13% accuracy with enhanced facial ML

### 🛒 **Smart Product Management**
- **Dynamic Recommendations**: Products change based on analysis results
- **Session Persistence**: Analysis data maintained across page navigation
- **Cart Integration**: Seamless add-to-cart functionality
- **Image Optimization**: Robust image loading with fallbacks

## 🚀 Technology Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **AI/ML**: Python Flask, OpenCV, TensorFlow/Keras
- **Computer Vision**: Haar Cascade Classifiers for face detection
- **Deployment**: AWS Amplify (Frontend), AWS Elastic Beanstalk (Backend)
- **Image Processing**: Real-time face detection, image validation

## 📋 Requirements

### Face Analysis Requirements
- **Every Analysis Must Include Face Detection**: No analysis can proceed without successful face detection
- **Minimum Confidence**: 90% face detection confidence required
- **Image Validation**: Automatic rejection of images without detectable faces
- **Real-time Feedback**: Immediate visual feedback during face detection

### Product Recommendation Requirements
- **Intelligent Scoring**: All products scored using advanced algorithm
- **Condition Matching**: Products matched to specific detected skin conditions
- **Category Balance**: Maximum 2 products per category for diversity
- **Personalized Reasoning**: Clear explanation for each recommendation

## 🔧 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenCV
- Flask

### Frontend Setup
```bash
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python application_hare_run_v6.py
```

## 📱 Usage

### 1. **Face Detection & Analysis**
- Upload image or use live camera
- Face detection automatically validates image
- Analysis only proceeds with detected face

### 2. **Intelligent Recommendations**
- Products automatically scored and ranked
- Recommendations based on detected conditions
- Detailed reasoning for each product

### 3. **Product Management**
- Add recommended products to cart
- Navigate between analysis and catalog
- Persistent session data

## 🏗️ Architecture

### Frontend Architecture
```
app/
├── api/                    # API routes
├── components/            # Reusable components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
└── pages/                # Page components
```

### Backend Architecture
```
backend/
├── models/               # ML models
├── services/            # AI services
├── embeddings/          # Feature vectors
└── application_hare_run_v6.py  # Main Flask app
```

## 🔄 Recent Updates

### v2.0 - Intelligent Recommendation Engine
- ✅ Advanced product scoring algorithm
- ✅ Condition-based product matching
- ✅ Category diversity enforcement
- ✅ Personalized recommendation reasoning

### v1.5 - Enhanced Face Detection
- ✅ Mandatory face detection for all analyses
- ✅ Real-time camera integration
- ✅ OpenCV-based face validation
- ✅ Confidence threshold enforcement

### v1.0 - Core ML Analysis
- ✅ Hare Run V6 enhanced ML model
- ✅ Multi-condition detection
- ✅ Health score calculation
- ✅ Severity assessment

## 🚀 Deployment

### Frontend (AWS Amplify)
- Automatic deployments from GitHub
- Optimized for production
- CDN distribution

### Backend (AWS Elastic Beanstalk)
- Python 3.11 environment
- Auto-scaling configuration
- Load balancer integration

## 📊 Performance Metrics

- **Face Detection**: >90% accuracy
- **ML Analysis**: 97.13% model accuracy
- **Recommendation Engine**: Intelligent scoring with category diversity
- **Response Time**: <2 seconds for analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Test thoroughly
5. Submit pull request

## 📄 License

© 2025 SHINE SKIN COLLECTIVE. All Rights Reserved.

---

**Built with ❤️ using Next.js, Python, and AI/ML technologies**