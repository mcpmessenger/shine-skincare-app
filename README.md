# 🌟 Shine Skincare App

A comprehensive AI-powered skincare analysis application that provides personalized skin condition analysis, face detection, and product recommendations.

## 🚀 Features

### Core Functionality
- **Advanced Face Detection**: OpenCV-based face detection with multiple cascade classifiers
- **Skin Condition Analysis**: Comprehensive analysis of acne, redness, dark spots, and other skin conditions
- **Enhanced Embedding System**: Multi-model embedding (CLIP, DINO, custom skin-specific) with 2304-dimensional vectors
- **Demographic-Aware Analysis**: Normalized analysis comparing against demographic-specific healthy baselines
- **Real Database Integration**: Integration with actual skin condition datasets (UTKFace, facial skin diseases)
- **Personalized Recommendations**: AI-driven product recommendations based on analysis results
- **E-commerce Integration**: Shopping cart and checkout functionality

### Technical Features
- **Hybrid Architecture**: Flask backend + Next.js frontend
- **Direct Backend Communication**: Fallback mechanism for reliable API communication
- **Face Detection Reuse**: Optimized workflow to avoid redundant face detection
- **JSON Serialization**: Robust handling of NumPy data types
- **Error Handling**: Comprehensive error handling with graceful degradation

## 🏗️ Architecture

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **State Management**: React hooks
- **API Communication**: Direct backend client with proxy fallback

### Backend (Flask)
- **Framework**: Flask with CORS support
- **Face Detection**: OpenCV Haar cascades
- **Image Processing**: OpenCV, PIL, NumPy
- **Machine Learning**: Scikit-learn, TensorFlow
- **Embedding System**: Multi-model approach with fallback mechanisms

### Key Components
```
shine-skincare-app/
├── app/                    # Next.js frontend
│   ├── api/v3/           # API routes (proxies to backend)
│   ├── page.tsx          # Main application page
│   └── globals.css       # Global styles
├── backend/               # Flask backend
│   ├── enhanced_app.py   # Main Flask application
│   ├── enhanced_analysis_api.py  # API endpoints
│   ├── integrated_skin_analysis.py  # Core analysis logic
│   ├── enhanced_embeddings.py     # Embedding system
│   └── data/             # Dataset storage
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
python enhanced_app.py
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
```

## 🚀 Quick Start

1. **Start Backend**:
   ```bash
   cd backend
   python enhanced_app.py
   ```
   Backend will be available at `http://localhost:5000`

2. **Start Frontend**:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

3. **Access Application**:
   - Open `http://localhost:3000` in your browser
   - Upload an image for analysis
   - Choose between Basic, Enhanced, or Comprehensive analysis

## 📊 API Endpoints

### Core Analysis Endpoints
- `POST /api/v3/skin/analyze-basic` - Basic skin analysis
- `POST /api/v3/skin/analyze-enhanced-embeddings` - Enhanced analysis with embeddings
- `POST /api/v3/skin/analyze-comprehensive` - Comprehensive analysis
- `POST /api/v3/skin/analyze-normalized` - Demographic-normalized analysis

### System Endpoints
- `GET /api/v3/system/health` - Health check
- `GET /api/v3/system/status` - System status
- `GET /api/v3/system/capabilities` - Available features

### Face Detection
- `POST /api/v3/face/detect` - Face detection endpoint

## 🔧 Current Status

### ✅ Working Features
- Backend API endpoints
- Face detection (OpenCV Haar cascades)
- Enhanced embedding system
- Direct backend communication
- Basic and enhanced analysis workflows
- Error handling and fallback mechanisms

### 🔴 Known Issues
- **Face Detection Accuracy**: OpenCV Haar cascades may fail with certain image types
- **Proxy Communication**: Frontend proxy routes may have intermittent issues
- **Analysis Accuracy**: May need fine-tuning for real-world images

### 🚧 In Progress
- Enhanced face detection with multiple methods
- Alternative face detection implementations (MediaPipe, dlib)
- Performance optimization
- Comprehensive testing with real user images

## 📁 Project Structure

### Key Files
- `backend/enhanced_app.py` - Main Flask application
- `backend/enhanced_analysis_api.py` - API endpoints
- `backend/integrated_skin_analysis.py` - Core analysis logic
- `app/page.tsx` - Main frontend page
- `lib/direct-backend.ts` - Direct backend communication
- `components/enhanced-analysis.tsx` - Analysis component

### Documentation
- `BUG_BOUNTY_REPORT.md` - Detailed issue tracking
- `SOLUTION_SUMMARY.md` - Technical solutions implemented
- `TESTING_GUIDE.md` - Testing instructions
- `INTEGRATED_SKIN_ANALYSIS_SYSTEM.md` - System architecture

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -c "from enhanced_app import app; print('Backend ready')"
```

### Frontend Testing
```bash
npm run build
npm start
```

### End-to-End Testing
1. Start both backend and frontend
2. Upload an image through the web interface
3. Test different analysis types
4. Verify face detection and analysis results

## 🚀 Deployment

### Backend Deployment
- **Platform**: Elastic Beanstalk (Python 3.9)
- **Requirements**: `requirements.txt`
- **Entry Point**: `enhanced_app.py`

### Frontend Deployment
- **Platform**: Vercel/Netlify
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
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
**Version**: 2.0  
**Status**: Active Development