# ✨ Shine Skincare - AI-Powered Skin Analysis

## **🎯 Project Overview**

Shine Skincare is a sophisticated AI-powered skin analysis application that provides real-time dermatological insights using advanced computer vision, machine learning, and Google OAuth authentication.

### **🌟 Key Features**
- 🔐 **Google OAuth Authentication**: Secure user login with Google
- 📸 **Enhanced Photo Upload**: Face detection for uploaded images
- 🎥 **Real-time Camera Analysis**: Live face detection and capture
- 🧠 **AI-Powered Skin Analysis**: Advanced computer vision analysis
- 🛒 **Shopping Cart System**: Integrated e-commerce functionality
- 📧 **Abandoned Cart Emails**: Automated email campaigns
- 🎨 **Theme Support**: Light and dark mode
- 📱 **Responsive Design**: Mobile-first interface

---

## **🚀 Quick Start**

### **Prerequisites**
```bash
# Node.js 18+
# Python 3.9+ (for backend)
# Git
```

### **Installation**

1. **Clone Repository**
```bash
git clone <repository-url>
cd shine-skincare-app
```

2. **Install Dependencies**
```bash
npm install
```

3. **Environment Setup**
```bash
# Create .env.local file
cp .env.example .env.local

# Add your environment variables:
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. **Start Development Server**
```bash
npm run dev
```

5. **Access Application**
- Frontend: http://localhost:3000
- Backend: http://localhost:5001 (if running separately)

---

## **🔧 Architecture**

### **Frontend (Next.js 14)**
```
📁 app/
├── page.tsx                    # Main skin analysis page
├── catalog/page.tsx            # Product catalog
├── checkout/page.tsx           # Checkout process
├── auth/callback/page.tsx      # OAuth callback handler
└── api/                        # API routes
    ├── auth/login/route.ts     # OAuth initiation
    ├── auth/callback/route.ts  # OAuth processing
    └── abandoned-cart-email/   # Email campaigns
```

### **Core Components**
```
📁 components/
├── sign-in-modal.tsx           # Authentication modal
├── cart-drawer.tsx             # Shopping cart
├── theme-toggle.tsx            # Theme switcher
└── checkout-form.tsx           # Checkout form
```

### **State Management**
```
📁 hooks/
├── useAuth.tsx                 # Authentication state
├── useCart.tsx                 # Shopping cart state
└── useTheme.tsx                # Theme management
```

### **Services**
```
📁 lib/
├── supabase.ts                 # Database client
├── cart-service.ts             # Cart operations
└── products.ts                 # Product data
```

---

## **🔐 Authentication System**

### **Google OAuth Flow**
1. **User clicks "Sign In"** → Redirects to Google
2. **Google authentication** → User grants permissions
3. **Callback processing** → User data stored in Supabase
4. **Session management** → Local storage + database sync

### **Features**
- ✅ **Secure OAuth 2.0** implementation
- ✅ **Supabase integration** for user persistence
- ✅ **Automatic session management**
- ✅ **Protected cart functionality**
- ✅ **Theme-aware UI** components

---

## **📸 Enhanced Upload System**

### **Face Detection for Uploads**
- **Automatic Detection**: Face detection runs on uploaded images
- **Visual Feedback**: Green bounding box around detected faces
- **Quality Assessment**: Lighting and positioning metrics
- **User Confidence**: Clear status indicators

### **Upload Features**
- ✅ **Drag & Drop** support
- ✅ **File validation** (images only)
- ✅ **Preview with face overlay**
- ✅ **Quality metrics** display
- ✅ **Theme-aware** styling
- ✅ **Progress indicators**

---

## **🛒 Shopping Cart System**

### **Features**
- **Authentication Required**: Users must sign in to add items
- **Persistent Storage**: Cart data saved to Supabase
- **Real-time Updates**: Live cart state management
- **Abandoned Cart Tracking**: Email campaign integration

### **Cart Operations**
- ✅ **Add/Remove Items**
- ✅ **Quantity Management**
- ✅ **Total Calculation**
- ✅ **Supabase Sync**
- ✅ **Abandoned Cart Detection**

---

## **📧 Abandoned Cart Email System**

### **Automated Campaigns**
- **3-Email Sequence**: Progressive engagement
- **Smart Scheduling**: Time-based delivery
- **Recovery Tracking**: Conversion monitoring
- **Nodemailer Integration**: Professional email delivery

### **Email Features**
- ✅ **Personalized Content**
- ✅ **Product Recommendations**
- ✅ **Recovery Tracking**
- ✅ **Unsubscribe Support**
- ✅ **Analytics Integration**

---

## **🎨 Theme System**

### **Light/Dark Mode**
- **Automatic Detection**: System preference detection
- **Manual Toggle**: User-controlled switching
- **Persistent State**: Local storage sync
- **Theme-Aware Colors**: Dynamic styling

### **Theme Features**
- ✅ **Responsive Design**
- ✅ **Accessibility Support**
- ✅ **Smooth Transitions**
- ✅ **Consistent Styling**

---

## **🔧 Development Commands**

### **Frontend Development**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### **Database Setup**
```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_id TEXT UNIQUE,
  email TEXT UNIQUE,
  name TEXT,
  profile_picture_url TEXT,
  is_active BOOLEAN DEFAULT true,
  subscription_tier TEXT DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP
);

-- Carts table
CREATE TABLE carts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  items JSONB,
  total DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_abandoned BOOLEAN DEFAULT false,
  abandoned_at TIMESTAMP,
  email_sent_count INTEGER DEFAULT 0,
  last_email_sent_at TIMESTAMP
);

-- Abandoned carts table
CREATE TABLE abandoned_carts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  user_email TEXT,
  user_name TEXT,
  cart_items JSONB,
  cart_total DECIMAL(10,2),
  abandoned_at TIMESTAMP DEFAULT NOW(),
  email_sent_count INTEGER DEFAULT 0,
  last_email_sent_at TIMESTAMP,
  next_email_scheduled_at TIMESTAMP,
  is_recovered BOOLEAN DEFAULT false,
  recovered_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Email campaigns table
CREATE TABLE email_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  user_email TEXT,
  campaign_type TEXT,
  subject TEXT,
  content TEXT,
  sent_at TIMESTAMP DEFAULT NOW(),
  opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  unsubscribed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## **📊 API Endpoints**

### **Authentication**
- `GET /api/auth/login` - Initiate Google OAuth
- `POST /api/auth/callback` - Process OAuth callback

### **Cart Management**
- `POST /api/abandoned-cart-email` - Cart email operations

### **Health Checks**
- `GET /api/health` - Application health status

---

## **🔒 Security Features**

### **OAuth Security**
- ✅ **State Parameter** verification
- ✅ **CSRF Protection**
- ✅ **Secure Token Storage**
- ✅ **Session Management**

### **Data Protection**
- ✅ **Supabase RLS** (Row Level Security)
- ✅ **Environment Variables**
- ✅ **Secure API Keys**
- ✅ **Input Validation**

---

## **📈 Performance**

### **Frontend Optimization**
- ✅ **Next.js 14** with App Router
- ✅ **Image Optimization**
- ✅ **Code Splitting**
- ✅ **Lazy Loading**

### **Backend Performance**
- ✅ **Efficient Database Queries**
- ✅ **Caching Strategies**
- ✅ **Error Handling**
- ✅ **Monitoring**

---

## **🤝 Contributing**

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### **Code Standards**
- Follow TypeScript best practices
- Use consistent formatting
- Add comprehensive comments
- Include error handling

---

## **📞 Support**

### **Getting Help**
- Check the documentation
- Review existing issues
- Test with the development server
- Verify environment variables

### **Common Issues**
- **OAuth Setup**: Ensure Google Client ID is configured
- **Database**: Verify Supabase connection
- **Theme Issues**: Check browser compatibility
- **Upload Problems**: Verify file permissions

---

## **📝 License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Last Updated: December 2024*
*Version: 2.0.0*
*Status: Production Ready*