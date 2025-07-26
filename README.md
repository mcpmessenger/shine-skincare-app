# Shine - AI-Powered Skincare Analysis

## How to Trigger an Amplify Redeploy

1. Make any change to this README or your frontend code.
2. Commit and push to GitHub:
   ```
   git add README.md
   git commit -m "Trigger Amplify redeploy"
   git push
   ```
3. AWS Amplify will automatically rebuild and redeploy your frontend.

## Backend API

The frontend communicates with the backend API at:
`https://shine-skincare-rdrp39n2c-williamtflynn-2750s-projects.vercel.app`

# Shine - AI-Powered Skincare Analysis

A modern web application that provides AI-powered skin analysis and personalized skincare recommendations using advanced computer vision and machine learning.

## 🌟 Features

### **AI-Powered Skin Analysis**

### **Professional Features**

### **User Experience**

## 🚀 Tech Stack

### **Frontend**

### **Backend**

### **AI & ML**

## 📱 Live Demo

Visit the live application: [Shine Skincare App](https://main.d2wy4w2nf9bgxx.amplifyapp.com)

## 🚀 Deployment Configuration

### **Production URLs**

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

### **Testing**

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


## 🚀 Performance


## 📞 Support

For issues or questions:
1. Check the deployment logs in Amplify Console
2. Verify environment variables are set correctly
3. Test API endpoints directly
4. Check Vercel function logs for backend issues


**Built with ❤️ using Next.js, Flask, and AI-powered skin analysis**