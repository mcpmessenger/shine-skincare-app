# Manual Elastic Beanstalk Deployment Guide

## Overview
This guide covers manual deployment to Elastic Beanstalk through the AWS Console for the Shine Skincare App.

## Prerequisites
- AWS CLI configured for us-east-1 region
- Application code ready for deployment
- Elastic Beanstalk environment created

## Step-by-Step Deployment

### 1. Prepare Application Bundle

```powershell
# Create deployment bundle
git add .
git commit -m "Prepare for EB deployment"
git push

# Or create a ZIP file manually
Compress-Archive -Path . -DestinationPath "shine-app-deployment.zip" -Force
```

### 2. AWS Console Deployment

1. **Open AWS Console** (us-east-1 region)
2. **Navigate to Elastic Beanstalk**
3. **Select your environment** (e.g., "shine-backend-final")
4. **Click "Upload and deploy"**
5. **Choose deployment method**:
   - Upload your code
   - Select the ZIP file or use Git repository

### 3. Configuration Files Included

The following files are now properly configured for EB deployment:

- **`.ebextensions/01_timeout.config`** - 30-minute timeout
- **`.ebextensions/02_build_optimization.config`** - Build process
- **`.ebextensions/03_health_check.config`** - Health checks
- **`.ebextensions/04_platform_hooks.config`** - Platform hooks
- **`.ebextensions/05_platform_config.config`** - Platform settings
- **`Procfile`** - Application startup command

### 4. Environment Variables

The following environment variables are automatically set:
- `NODE_ENV=production`
- `AWS_REGION=us-east-1`
- `PORT=8081`

### 5. Build Process

The deployment will automatically:
1. Install Node.js 18
2. Install dependencies (`npm ci`)
3. Install Tailwind CSS globally
4. Build Tailwind CSS (`npx tailwindcss -i ./app/globals.css -o ./app/output.css --minify`)
5. Build Next.js application (`npm run build`)
6. Start the application (`npm start`)

### 6. Monitoring Deployment

1. **Check Environment Health** in EB Console
2. **View Logs** in CloudWatch
3. **Monitor Events** in EB Events tab
4. **Test Health Endpoint**: `https://your-env-url/api/health`

### 7. Troubleshooting

#### If Deployment Hangs:
```powershell
# Run the cleanup script
.\scripts\terminate-hanging-deployment.ps1
```

#### If Build Fails:
1. Check CloudWatch logs
2. Verify all files are included in deployment
3. Check environment variables
4. Ensure region is us-east-1

#### Common Issues:
- **Timeout**: Increased to 1800 seconds (30 minutes)
- **Memory**: Using c5.2xlarge instances
- **Port**: Application runs on port 8081
- **Health Check**: Configured for `/api/health`

### 8. Post-Deployment Verification

1. **Health Check**: Visit `/api/health` endpoint
2. **Application**: Test main application functionality
3. **Tailwind**: Verify styles are loading correctly
4. **Performance**: Monitor application performance

### 9. Rollback (if needed)

1. Go to EB Console
2. Select your environment
3. Click "Application versions"
4. Select previous version
5. Click "Deploy"

## Files Structure for Deployment

```
shine-skincare-app/
├── .ebextensions/
│   ├── 01_timeout.config
│   ├── 02_build_optimization.config
│   ├── 03_health_check.config
│   ├── 04_platform_hooks.config
│   └── 05_platform_config.config
├── app/
│   ├── globals.css
│   └── ...
├── components/
├── lib/
├── package.json
├── Procfile
├── next.config.mjs
├── tailwind.config.ts
└── postcss.config.mjs
```

## Success Indicators

- ✅ Environment status: "Ready"
- ✅ Environment health: "Ok"
- ✅ Health check endpoint responds
- ✅ Application loads without errors
- ✅ Tailwind CSS styles are applied
- ✅ All pages render correctly

## Next Steps

After successful deployment:
1. Update DNS if needed
2. Configure custom domain
3. Set up monitoring and alerts
4. Configure SSL certificate
5. Set up CI/CD pipeline 