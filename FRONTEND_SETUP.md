# Frontend Setup Guide

## Environment Configuration

Create a `.env.local` file in the root directory with the following configuration:

```env
# Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# Google OAuth Configuration (for frontend reference)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id-here
```

## Backend Connection

The frontend is now connected to the Flask backend with the following features:

### ✅ Authentication
- Google OAuth integration
- JWT token management
- Automatic token refresh
- Protected routes

### ✅ API Integration
- Real-time product recommendations
- Image analysis upload and processing
- User profile management
- Payment processing (Stripe)

### ✅ Components Updated
- Header with authentication state
- Product cards with real data
- Login page with Google OAuth
- OAuth callback handling

## Running the Application

1. **Start the Backend** (in the `backend` directory):
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python run.py
   ```

2. **Start the Frontend** (in the root directory):
   ```bash
   npm run dev
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## Features Implemented

### Authentication Flow
- Google OAuth login
- Automatic token management
- Protected routes
- User profile display

### Product Recommendations
- Real-time trending products
- Fallback to mock data if API unavailable
- Product filtering and search

### Image Analysis
- File upload to backend
- Real-time processing status
- Analysis results display

### Payment Integration
- Stripe payment processing
- Order management
- Payment history

## API Endpoints Used

- `POST /api/auth/login` - Initiate OAuth
- `POST /api/auth/callback` - OAuth callback
- `GET /api/auth/profile` - User profile
- `POST /api/analysis/upload` - Image upload
- `GET /api/recommendations/trending` - Trending products
- `POST /api/payments/create-intent` - Payment processing

## Next Steps

1. **Database Setup**: Run the backend database migrations
2. **OAuth Configuration**: Set up Google OAuth credentials
3. **Stripe Setup**: Configure Stripe API keys
4. **Testing**: Test the full authentication and payment flow 