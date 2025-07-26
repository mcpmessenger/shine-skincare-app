# 🔐 Google OAuth Setup Guide for Shine Skincare App

## 🚨 **Current Issue: OAuth Flow Failing**

The Google OAuth flow is currently failing because the backend is using placeholder values for Google OAuth credentials. This causes the following issues:

1. **Invalid Client ID**: Backend uses `your-google-client-id` instead of a real Google OAuth client ID
2. **OAuth Rejection**: Google rejects the OAuth request due to invalid credentials
3. **Redirect Loop**: Frontend gets redirected to `localhost:3000/auth/login/undefined/` because the OAuth flow never completes

## 🔧 **How to Fix the OAuth Issue**

### **Option 1: Set Up Real Google OAuth (Recommended for Production)**

#### **Step 1: Create Google OAuth Credentials**

1. **Go to Google Cloud Console**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google+ API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it
   - Also enable "Google OAuth2 API"

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application" as the application type

4. **Configure OAuth Consent Screen**:
   - Add your app name: "Shine Skincare App"
   - Add your email as the developer contact
   - Add scopes: `openid`, `email`, `profile`

5. **Configure Authorized Redirect URIs**:
   - Add: `http://localhost:3000/auth/callback` (for development)
   - Add: `https://your-production-domain.com/auth/callback` (for production)

6. **Get Your Credentials**:
   - Copy the **Client ID** and **Client Secret**

#### **Step 2: Update Backend Environment**

Update `backend/.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
```

#### **Step 3: Update Frontend Environment**

Create/update `.env.local` in the project root:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# Google OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_actual_google_client_id_here
```

#### **Step 4: Restart Servers**

```bash
# Restart backend
cd backend
python run.py

# Restart frontend (in another terminal)
npm run dev
```

### **Option 2: Mock OAuth for Development (Quick Fix)**

If you want to test the app without setting up real Google OAuth:

#### **Step 1: Create Mock OAuth Endpoint**

Create `backend/app/auth/mock_routes.py`:

```python
from flask import jsonify, request
from app.auth import auth_bp
from app.models.user import User, UserPreferences, UserSession
from app import db
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta

@auth_bp.route('/mock-login', methods=['POST'])
def mock_login():
    """Mock OAuth login for development"""
    try:
        # Create a mock authorization URL that redirects to our callback
        mock_auth_url = "http://localhost:3000/auth/callback?code=mock_code&state=mock_state"
        
        return jsonify({
            'authorization_url': mock_auth_url,
            'state': 'mock_state',
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/mock-callback', methods=['POST'])
def mock_callback():
    """Mock OAuth callback for development"""
    try:
        # Create a mock user
        user = User.query.filter_by(email='test@example.com').first()
        
        if not user:
            user = User(
                google_id='mock_google_id_123',
                email='test@example.com',
                name='Test User',
                profile_picture_url='https://via.placeholder.com/150',
                last_login_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.flush()
            
            # Create default preferences
            preferences = UserPreferences(user_id=user.id)
            db.session.add(preferences)
        
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_profile': user.to_dict(),
            'expires_in': 3600
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### **Step 2: Update Frontend to Use Mock OAuth**

Update `lib/api.ts` to use mock endpoints in development:

```typescript
// Auth endpoints - ALWAYS use real API calls
async login(): Promise<{ authorization_url: string; state: string; expires_in: number }> {
  const endpoint = process.env.NODE_ENV === 'development' ? '/auth/mock-login' : '/auth/login';
  return this.request<{ authorization_url: string; state: string; expires_in: number }>(endpoint, {
    method: 'POST',
    body: JSON.stringify({ client_type: 'web' }),
  });
}

async oauthCallback(code: string, state: string): Promise<{ access_token: string; refresh_token: string; user_profile: User; expires_in: number }> {
  const endpoint = process.env.NODE_ENV === 'development' ? '/auth/mock-callback' : '/auth/callback';
  const response = await this.request<{ access_token: string; refresh_token: string; user_profile: User; expires_in: number }>(endpoint, {
    method: 'POST',
    body: JSON.stringify({ code, state }),
  });

  // Store tokens in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('shine_token', response.access_token);
    localStorage.setItem('shine_refresh_token', response.refresh_token);
  }

  return response;
}
```

## 🧪 **Testing the OAuth Flow**

### **Test with Real Google OAuth**

1. **Start both servers**:
   ```bash
   # Terminal 1: Backend
   cd backend && python run.py
   
   # Terminal 2: Frontend
   npm run dev
   ```

2. **Test the flow**:
   - Go to `http://localhost:3000`
   - Click "Login" or try to access a protected page
   - You should be redirected to Google OAuth
   - After authentication, you should be redirected back to the app

### **Test with Mock OAuth**

1. **Start both servers** (with mock endpoints)
2. **Test the flow**:
   - Go to `http://localhost:3000`
   - Click "Login"
   - You should be automatically logged in as "Test User"

## 🔍 **Debugging OAuth Issues**

### **Common Issues and Solutions**

1. **"Invalid Client ID" Error**:
   - Ensure `GOOGLE_CLIENT_ID` is set correctly in backend `.env`
   - Verify the client ID in Google Cloud Console

2. **"Redirect URI Mismatch" Error**:
   - Add `http://localhost:3000/auth/callback` to authorized redirect URIs in Google Cloud Console
   - Ensure `GOOGLE_REDIRECT_URI` matches exactly in backend `.env`

3. **"Undefined" in URL**:
   - This happens when the OAuth flow fails and the frontend tries to redirect with undefined parameters
   - Fix the OAuth credentials and the issue will resolve

4. **CORS Issues**:
   - Ensure backend has CORS configured for `http://localhost:3000`
   - Check that frontend is making requests to the correct backend URL

### **Check OAuth Configuration**

```bash
# Test backend OAuth endpoint
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"client_type": "web"}'

# Expected response should have a valid Google OAuth URL
# NOT: client_id=your-google-client-id
```

## 🎯 **Next Steps**

1. **Choose an option**: Real OAuth (production) or Mock OAuth (development)
2. **Follow the setup steps** for your chosen option
3. **Test the OAuth flow** to ensure it works
4. **Deploy with proper credentials** when ready for production

## 📞 **Support**

If you encounter issues:
1. Check that both servers are running
2. Verify environment variables are set correctly
3. Check browser console for errors
4. Verify Google Cloud Console configuration
5. Test with the mock OAuth option first

**The OAuth flow will work once the credentials are properly configured!** 🔐 