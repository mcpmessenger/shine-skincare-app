# Environment Setup Guide - Operation Kitty Whiskers

## 🔐 Supabase Credentials Configuration

### 1. Local Development Environment

Create `.env.local` in the root directory:
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend URL (for local development)
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

### 2. Elastic Beanstalk Environment Variables

Configure these in your EB environment:
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_KEY=your_supabase_anon_key

# Application Configuration
FLASK_ENV=production
FLASK_APP=app
```

### 3. Amplify Environment Variables (if using Amplify for frontend)

Configure these in your Amplify app:
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend URL (point to your EB environment)
NEXT_PUBLIC_BACKEND_URL=https://your-eb-environment.elasticbeanstalk.com
```

## 🚀 Deployment Steps

### Step 1: Update Elastic Beanstalk
1. **Update requirements-eb.txt** ✅ (Already done)
2. **Deploy backend changes:**
   ```bash
   cd backend
   eb deploy
   ```

### Step 2: Configure Environment Variables
1. **In EB Console:**
   - Go to your EB environment
   - Configuration → Software
   - Add environment variables listed above

2. **In Amplify Console (if applicable):**
   - Go to your Amplify app
   - App settings → Environment variables
   - Add the frontend variables listed above

### Step 3: Verify Deployment
1. **Test backend health:**
   ```bash
   curl https://your-eb-environment.elasticbeanstalk.com/api/health
   ```

2. **Test frontend connectivity:**
   - Visit your frontend URL
   - Check browser console for connection errors

## 🔍 Verification Checklist

- [ ] Backend deploys successfully with new dependencies
- [ ] Supabase connection works from backend
- [ ] Frontend can connect to Supabase
- [ ] Medical analysis endpoints are accessible
- [ ] Authentication flow works end-to-end

## 🆘 Troubleshooting

### Common Issues:
1. **Package installation fails:** Check EB platform version compatibility
2. **Supabase connection errors:** Verify credentials in all environments
3. **CORS issues:** Ensure backend URL is correctly configured in frontend

### Support:
- Check EB logs: `eb logs`
- Check Amplify logs: Amplify Console → Build logs
- Verify Supabase project settings and API keys 