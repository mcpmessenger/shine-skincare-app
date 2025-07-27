# Railway Environment Variables Setup

## Required Environment Variables

Set these in your Railway project dashboard:

### Core Configuration
```
FLASK_ENV=production
PORT=5000
```

### Service Configuration
```
USE_MOCK_SERVICES=false
USE_PRODUCTION_FAISS=true
GOOGLE_VISION_ENABLED=true
FAISS_PERSISTENCE_ENABLED=true
```

### Google Cloud Vision API
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"shine-466907",...}
```
*Note: Paste your complete Google Cloud service account JSON here*

### Supabase Database
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### FAISS Configuration
```
FAISS_DIMENSION=2048
FAISS_INDEX_PATH=/app/faiss_index
```

### Demographic Search Weights
```
DEMOGRAPHIC_WEIGHT=0.3
ETHNICITY_WEIGHT=0.6
SKIN_TYPE_WEIGHT=0.3
AGE_GROUP_WEIGHT=0.1
```

### Classification Settings
```
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
LOG_LEVEL=INFO
```

## Railway Dashboard Setup Steps

1. Go to your Railway project dashboard
2. Click on "Variables" tab
3. Add each environment variable above
4. For `GOOGLE_CREDENTIALS_JSON`, paste the entire JSON content as a single line
5. Save all variables
6. Trigger a new deployment

## Testing Environment Variables

After deployment, test with:
```bash
curl https://your-railway-app.railway.app/api/health
```

Should return service status and configuration info.