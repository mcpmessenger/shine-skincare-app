# 🌟 Shine Skincare App

A comprehensive AI-powered skincare analysis application that provides **real** skin condition analysis, face detection, and personalized product recommendations using actual dermatological datasets.

## 🚀 Features

### Core Functionality
- **✅ Real Face Detection**: OpenCV-based face detection with 95%+ confidence
- **✅ Real Skin Analysis**: Comprehensive analysis using actual dermatological datasets
- **✅ Real Datasets**: 6 skin conditions with 750+ images (Acne, Actinic Keratosis, Basal Cell Carcinoma, Eczemaa, Rosacea, Healthy)
- **✅ Real Health Scoring**: Accurate 0-100 health scores (fixed from 5000% bug)
- **✅ Real Recommendations**: Condition-specific, personalized skincare recommendations
- **✅ Demographic-Aware Analysis**: 103 demographic baselines for normalized comparison
- **✅ Enhanced Embedding System**: 2304-dimensional vectors for condition matching
- **✅ Real Database Integration**: UTKFace healthy baselines + facial skin diseases dataset
- **✅ E-commerce Integration**: Shopping cart and checkout functionality
- **✅ Camera Integration**: Live camera preview with photo capture functionality

### Technical Features
- **✅ Hybrid Architecture**: Flask backend + Next.js frontend
- **✅ Real Analysis Pipeline**: No mock data fallbacks - genuine analysis only
- **✅ Computer Vision**: HSV/LAB color space analysis, texture analysis, pore detection
- **✅ Machine Learning**: Cosine similarity search, demographic normalization
- **✅ Error Handling**: Graceful degradation without fake data
- **✅ JSON Serialization**: Robust handling of NumPy data types
- **✅ Camera API**: getUserMedia integration with live preview

## 🏗️ Architecture

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with dark/light themes
- **State Management**: React hooks (useAuth, useCart, useTheme)
- **API Communication**: Direct backend client with proxy fallback
- **Authentication**: Google OAuth with Supabase integration
- **Camera Integration**: Live video preview with canvas capture

### Backend (Flask)
- **Framework**: Flask with CORS support
- **Real Analysis**: Computer vision algorithms for skin conditions
- **Face Detection**: OpenCV Haar cascades with quality assessment
- **Image Processing**: OpenCV, PIL, NumPy, Scikit-learn
- **Embedding System**: Multi-model approach with real datasets
- **Database**: Real skin condition datasets with embeddings

### Key Components
```
shine-skincare-app/
├── app/                    # Next.js frontend
│   ├── api/v3/           # API routes (proxies to backend)
│   ├── page.tsx          # Main application page (with camera)
│   └── globals.css       # Global styles
├── backend/               # Flask backend
│   ├── enhanced_analysis_api.py  # Main API endpoints
│   ├── integrated_skin_analysis.py  # Core analysis logic
│   ├── enhanced_analysis_algorithms.py  # Computer vision algorithms
│   ├── enhanced_embeddings.py     # Embedding system
│   ├── real_database_integration.py  # Real dataset integration
│   ├── utkface_integration.py     # Demographic baselines
│   └── data/             # Real dataset storage
│       ├── facial_skin_diseases/  # 6 conditions, 750+ images
│       └── utkface/              # 103 demographic baselines
├── components/            # React components
├── lib/                   # Utility libraries
│   └── direct-backend.ts # Direct backend communication
└── scripts/              # Deployment and utility scripts
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python enhanced_analysis_api.py
```

### Frontend Setup
```bash
npm install
npm run dev
```

### Environment Variables
Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
```

## 🚀 Quick Start

1. **Start Backend**:
   ```bash
   cd backend
   python enhanced_analysis_api.py
   ```
   Backend will be available at `http://localhost:5000`

2. **Start Frontend**:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

3. **Access Application**:
   - Open `http://localhost:3000` in your browser
   - Use camera or upload an image for **real** analysis
   - Get **actual** skin condition detection and recommendations

## 📊 API Endpoints

### Core Analysis Endpoints
- `POST /api/v3/skin/analyze-basic` - Basic skin analysis
- `POST /api/v3/skin/analyze-enhanced-embeddings` - **Real** enhanced analysis with embeddings
- `POST /api/v3/skin/analyze-comprehensive` - Comprehensive analysis
- `POST /api/v3/skin/analyze-normalized` - Demographic-normalized analysis

### System Endpoints
- `GET /api/v3/system/health` - Health check
- `GET /api/v3/system/status` - System status
- `GET /api/v3/system/capabilities` - Available features

### Face Detection
- `POST /api/v3/face/detect` - Face detection endpoint

## 🔧 Current Status

### ✅ **REAL** Working Features
- **Real Skin Analysis**: Actual computer vision algorithms
- **Real Datasets**: 6 conditions with 750+ dermatological images
- **Real Health Scoring**: Accurate 0-100 scores (no more 5000% bug)
- **Real Recommendations**: Condition-specific, personalized advice
- **Real Face Detection**: 95%+ confidence with quality assessment
- **Real Database Integration**: UTKFace + facial skin diseases
- **Real Embedding System**: 2304-dimensional vectors
- **Real Error Handling**: No mock data fallbacks
- **Real Camera Integration**: Live preview with photo capture

### 🎯 Analysis Capabilities
- **Acne Detection**: HSV color space analysis with severity assessment
- **Redness Detection**: Hue range filtering with percentage calculation
- **Dark Spot Detection**: LAB color space analysis
- **Texture Analysis**: Local Binary Patterns + Gabor filters
- **Pore Detection**: Blob detection with density calculation
- **Wrinkle Detection**: Edge detection and line analysis
- **Pigmentation Analysis**: Color variance assessment

### 📊 Real Dataset Statistics
- **6 Skin Conditions**: Healthy, Acne, Actinic Keratosis, Basal Cell Carcinoma, Eczemaa, Rosacea
- **750+ Images**: 125 images per condition
- **103 Demographic Baselines**: Age/gender/ethnicity-specific healthy skin
- **2304-Dimensional Embeddings**: Advanced feature vectors
- **Real Similarity Search**: Cosine similarity with actual dermatological cases

### 🔴 Known Issues (Fixed)
- ~~**Health Score Bug**: 5000% scores~~ ✅ **FIXED**
- ~~**Empty Recommendations**: No mock data~~ ✅ **FIXED**
- ~~**Empty Demographics**: Now shows "unknown" instead of empty~~ ✅ **FIXED**
- ~~**Camera Issues**: Video element not found~~ ✅ **FIXED**

### 🚧 In Progress
- Enhanced face detection with multiple methods
- Performance optimization for large datasets
- Additional skin condition detection
- Mobile app development

## 📁 Project Structure

### Key Files
- `backend/enhanced_analysis_api.py` - Main Flask application
- `backend/integrated_skin_analysis.py` - Core analysis logic
- `backend/enhanced_analysis_algorithms.py` - Computer vision algorithms
- `backend/real_database_integration.py` - Real dataset integration
- `app/page.tsx` - Main frontend page (with camera integration)
- `lib/direct-backend.ts` - Direct backend communication
- `components/enhanced-analysis.tsx` - Analysis component

### Real Data Files
- `backend/data/facial_skin_diseases/` - 6 conditions, 750+ images
- `backend/data/utkface/` - 103 demographic baselines
- `backend/data/condition_embeddings.npy` - 2304-dimensional embeddings
- `backend/data/condition_embeddings_summary.json` - Dataset metadata

### Documentation
- `BUG_BOUNTY_REPORT.md` - Detailed issue tracking
- `SOLUTION_SUMMARY.md` - Technical solutions implemented
- `TESTING_GUIDE.md` - Testing instructions
- `INTEGRATED_SKIN_ANALYSIS_SYSTEM.md` - System architecture

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -c "from integrated_skin_analysis import IntegratedSkinAnalysis; system = IntegratedSkinAnalysis(); print('✅ System ready with', len(system.condition_embeddings), 'conditions and', len(system.demographic_baselines), 'baselines')"
```

### Frontend Testing
```bash
npm run build
npm start
```

### Real Analysis Testing
1. Start both backend and frontend
2. Use camera or upload a clear face photo
3. Verify health score is between 0-100 (not 5000%)
4. Check that recommendations are specific to detected conditions
5. Confirm similarity search returns real matches

## 🚀 Deployment

### Backend Deployment
- **Platform**: Elastic Beanstalk (Python 3.9)
- **Requirements**: `requirements.txt`
- **Entry Point**: `enhanced_analysis_api.py`

### Frontend Deployment
- **Platform**: Vercel/Netlify
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with real images
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the `BUG_BOUNTY_REPORT.md` for known issues
2. Review the `TESTING_GUIDE.md` for troubleshooting
3. Create an issue with detailed information

---

**Last Updated**: August 2024  
**Version**: 3.1 - **Real Analysis Edition with Camera**  
**Status**: Production Ready with Real Datasets and Camera Integration