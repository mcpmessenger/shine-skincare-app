# Vercel Deployment Checklist

## ✅ Prerequisites Complete
- [x] Google Vision API credentials obtained
- [x] Supabase credentials available
- [x] Credentials files added to .gitignore
- [x] Environment variables identified

## 🚀 Deployment Steps

### 1. Set Environment Variables in Vercel
Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these variables:
```
GOOGLE_CREDENTIALS_JSON = [paste the JSON as one line]
SUPABASE_URL = https://nkuczadhfmfmqk.supabase.co
SUPABASE_KEY = [your supabase anon key]
SECRET_KEY = [generate a random secret key]
LOG_LEVEL = INFO
USE_MOCK_SERVICES = false
```

### 2. Deploy to Vercel
```bash
cd backend
vercel --prod
```

### 3. Test Endpoints
After deployment, test these endpoints:
- `GET /api/health` - Basic health check
- `GET /api/enhanced/health/enhanced` - Enhanced services health
- `POST /api/v2/analyze/guest` - Image analysis (with file upload)

### 4. Verify Services
Check that these services are working:
- ✅ Google Vision API integration
- ✅ Supabase database connection
- ✅ FAISS vector search
- ✅ Error handling and logging

## 🔧 Troubleshooting

### Common Issues:
1. **Google Vision fails**: Check GOOGLE_CREDENTIALS_JSON is properly formatted
2. **Supabase fails**: Verify SUPABASE_URL and SUPABASE_KEY
3. **Cold start timeout**: Services will initialize on first request
4. **Memory issues**: App uses memory-efficient configuration

### Debug Endpoints:
- `/api/services/config` - Check service configuration
- `/api/performance/vercel` - Check Vercel performance stats
- `/api/performance/models` - Check model loading stats

## 📝 Post-Deployment
- [ ] Test image analysis with real images
- [ ] Monitor error logs in Vercel dashboard
- [ ] Check Google Cloud Vision API usage
- [ ] Verify Supabase database connections