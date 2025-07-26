# Shine - AI-Powered Skincare Analysis

A modern web application that provides AI-powered skin analysis and personalized skincare recommendations using advanced computer vision and machine learning.

## 🌟 Features

### **AI-Powered Skin Analysis**
- **Google Vision AI Integration** - Professional skin condition detection
- **FAISS Similarity Search** - Find similar skin conditions from professional dataset
- **SCIN Dataset Integration** - Access to 5,033 professional dermatology cases
- **Real-time Image Processing** - Instant analysis with vectorization

### **Professional Features**
- **Similarity Search** - Find similar skin conditions from professional dataset
- **Personalized Recommendations** - AI-powered product suggestions
- **Professional Annotations** - Dermatologist-verified case information
- **Advanced Filtering** - Filter by skin type, conditions, demographics

### **User Experience**
- **Camera Integration** - Take photos or upload images
- **Real-time Analysis** - Instant results with confidence scores
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Guest Access** - Try features without signing up
- **Authentication** - Secure Google OAuth login

## 🚀 Tech Stack

### **Frontend**
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Shadcn/ui** - Beautiful component library
- **AWS Amplify** - Hosting and CI/CD

### **Backend**
- **Flask** - Python web framework
- **Google Vision AI** - Professional image analysis
- **FAISS** - High-performance similarity search
- **Supabase** - PostgreSQL database and storage
- **Stripe** - Payment processing
- **Vercel** - Serverless hosting

### **AI & ML**
- **ResNet-50** - Image vectorization model
- **Cosine Similarity** - Advanced similarity matching
- **Professional Dataset** - 5,033 dermatology cases

## 📱 Live Demo

Visit the live application: [Shine Skincare App](https://main.d2wy4w2nf9bgxx.amplifyapp.com)

## 🚀 Deployment Configuration

### **Production URLs**
- **Frontend**: https://main.d2wy4w2nf9bgxx.amplifyapp.com
- **Backend**: https://backend-7yqorv3fz-williamtflynn-2750s-projects.vercel.app

### **Environment Variables**

#### **Frontend (AWS Amplify)**
Set these in Amplify Console → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://backend-7yqorv3fz-williamtflynn-2750s-projects.vercel.app
NEXT_PUBLIC_APP_URL=https://main.d2wy4w2nf9bgxx.amplifyapp.com
```

#### **Backend (Vercel)**
Set these in Vercel Dashboard → Environment Variables:

```env
DATABASE_URL=your_supabase_database_url
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_jwt_secret
STRIPE_SECRET_KEY=your_stripe_secret
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_key
SUPABASE_ANON_KEY=your_supabase_anon_key
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
GOOGLE_APPLICATION_CREDENTIALS=your_google_credentials_json
```

## 🔧 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Git
- Vercel CLI
- AWS Amplify CLI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mcpmessenger/shine.git
   cd shine
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
   NEXT_PUBLIC_API_URL=https://backend-7yqorv3fz-williamtflynn-2750s-projects.vercel.app
   NEXT_PUBLIC_APP_URL=https://main.d2wy4w2nf9bgxx.amplifyapp.com
   
   # Backend (.env)
   DATABASE_URL=your_supabase_database_url
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   JWT_SECRET_KEY=your_jwt_secret
   STRIPE_SECRET_KEY=your_stripe_secret
   ```

5. **Start development servers**
   ```bash
   # Frontend
   npm run dev
   
   # Backend (in another terminal)
   cd backend
   python run.py
   ```

6. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:5000

## 🚀 Deployment

### **Frontend Deployment (AWS Amplify)**
1. Connect your GitHub repository to Amplify
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
   ```
3. Set environment variables in Amplify Console
4. Deploy automatically on push to main branch

### **Backend Deployment (Vercel)**
1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to backend directory: `cd backend`
3. Link to Vercel project: `vercel link`
4. Deploy: `vercel --prod`
5. Set environment variables in Vercel Dashboard

### **Updating Backend URL**
When the backend URL changes:
1. Deploy new backend: `vercel --prod` (in backend directory)
2. Update `NEXT_PUBLIC_API_URL` in Amplify Console
3. No code push required!

## 🔧 Development Workflow

### **Efficient Development**
- **Batch Changes**: Group multiple related changes before pushing
- **Environment Variables**: Use Amplify Console for configuration changes
- **Local Testing**: Test changes locally before pushing
- **Backend Updates**: Use Vercel CLI directly (no GitHub push needed)

### **Testing**
- **Guest Access**: Test features without authentication
- **API Health**: Check `/api/health` endpoint
- **CORS**: Verify cross-origin requests work
- **Image Analysis**: Test skin analysis functionality

## 📁 Project Structure

```
shine-skincare-app/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   ├── auth/              # Authentication pages
│   ├── skin-analysis/     # Skin analysis pages
│   └── similarity-search/ # Similarity search page
├── backend/               # Flask backend
│   ├── app/              # Flask application
│   ├── api.py            # Vercel entry point
│   └── vercel.json       # Vercel configuration
├── components/           # React components
├── lib/                  # Utilities and API client
└── hooks/                # Custom React hooks
```

## 🔒 Security

- **Environment Variables**: All secrets stored securely
- **CORS Configuration**: Properly configured for production domains
- **Authentication**: Google OAuth with JWT tokens
- **Guest Access**: Limited features for unauthenticated users

## 🚀 Performance

- **Serverless Backend**: Auto-scaling with Vercel
- **CDN**: Global content delivery with Amplify
- **Image Optimization**: Next.js automatic optimization
- **Caching**: Efficient caching strategies

## 📞 Support

For issues or questions:
1. Check the deployment logs in Amplify Console
2. Verify environment variables are set correctly
3. Test API endpoints directly
4. Check Vercel function logs for backend issues

---

**Built with ❤️ using Next.js, Flask, and AI-powered skin analysis**