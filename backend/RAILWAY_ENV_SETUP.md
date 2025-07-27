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

---

You are now successfully linked to your Railway project (`believable-wholeness`) in the `production` environment!

To open your Railway project dashboard (and see your deployment URL), use the correct command:
```sh
railway open
```
*(You had a typo with an extra backtick in your previous command.)*

---

### Once you run `railway open`:
- Your browser will open the Railway dashboard for your project.
- At the top of the dashboard, you’ll see your public deployment URL, which will look like:
  ```
  https://believable-wholeness.up.railway.app
  ```
  or similar.

---

### To get your backend health status from the terminal:
You can also run:
```sh
<code_block_to_apply_changes_from>
```
or, if your service is at a different subdomain, use the correct URL as shown in your dashboard.

---

**Let me know if you want to verify the health endpoint or need help with anything else!**

---

## What is `SECRET_KEY`?
- It should be a long, random string.
- It does **not** need to be a credential from a third-party service.
- You can generate it yourself.

---

## How to Generate a Secure `SECRET_KEY`

### **Option 1: Use Python**
Open a Python shell and run:
```python
import secrets
print(secrets.token_urlsafe(32))
```
Copy the output and use it as your `SECRET_KEY`.

### **Option 2: Use an Online Generator**
You can use any secure random string generator, such as:
- [https://randomkeygen.com/](https://randomkeygen.com/)
- [https://djecrety.ir/](https://djecrety.ir/)

Choose a long, random string (at least 32 characters).

---

## Example
```
SECRET_KEY=QwErTyUiOp1234567890!@#$%^&*()_+zxcvbnmASDFGHJKL
```
Or, if you used Python:
```
SECRET_KEY=3Qw8n2kL9pXz7vB5sT1rY6uJ0oP4mC2dF8gH5jK1lM0nQ3wR
```

---

**Add this to your Railway environment variables, save, and redeploy.**

Let me know if you want me to generate one for you or if you need help with any other variable!