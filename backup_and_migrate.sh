#!/bin/bash

# Shine Skincare App Backup and Migration Script
# This script helps create separate repositories for frontend and backend

echo "🚀 Starting Shine Skincare App Backup and Migration..."

# Create backup directory
BACKUP_DIR="shine-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

echo "📁 Creating backup in: $BACKUP_DIR"

# Backup current repository
cp -r . $BACKUP_DIR/
echo "✅ Full backup created in $BACKUP_DIR"

# Create backend repository structure
echo "🔧 Creating backend repository structure..."
mkdir -p ../shine-backend

# Copy backend files
cp -r backend/* ../shine-backend/
cp backend/requirements.txt ../shine-backend/
cp backend/Procfile ../shine-backend/
cp backend/deploy.sh ../shine-backend/
cp backend/.ebextensions ../shine-backend/ -r

# Copy deployment documentation
cp DEPLOYMENT_GUIDE.md ../shine-backend/
cp DEPLOYMENT_CHECKLIST.md ../shine-backend/
cp REPOSITORY_STRATEGY.md ../shine-backend/

# Create backend README
cat > ../shine-backend/README.md << 'EOF'
# Shine Skincare Backend

Flask API server for the Shine Skincare App with ML model integration.

## Features
- Skin condition analysis with ML model
- Face detection
- Product recommendations
- RESTful API endpoints

## Deployment
- AWS Elastic Beanstalk
- Python 3.11
- Gunicorn server

## Environment Variables
- FLASK_ENV=production
- MODEL_PATH=/var/app/current/fixed_model_final.h5

## Quick Start
```bash
cd shine-backend
pip install -r requirements.txt
python run_fixed_model_server.py
```

## Deployment
```bash
eb deploy
```
EOF

echo "✅ Backend repository structure created in ../shine-backend"

# Create frontend cleanup script
cat > cleanup_frontend.sh << 'EOF'
#!/bin/bash

echo "🧹 Cleaning frontend repository..."

# Remove backend files
rm -rf backend/
rm -rf ML-2folder/
rm -rf *.md
rm -rf *.png
rm -rf *.jpg
rm -rf *.webp
rm -rf *.zip

# Keep only frontend files
echo "✅ Frontend repository cleaned"
echo "📁 Files kept:"
ls -la

echo "🎯 Next steps:"
echo "1. Create new GitHub repository for backend"
echo "2. Push backend files to new repo"
echo "3. Update environment variables"
echo "4. Deploy both repositories"
EOF

chmod +x cleanup_frontend.sh

echo "✅ Migration script created"
echo ""
echo "📋 Next Steps:"
echo "1. Review ../shine-backend/ for backend files"
echo "2. Run ./cleanup_frontend.sh to clean frontend"
echo "3. Create GitHub repositories"
echo "4. Update environment variables"
echo "5. Deploy to AWS"
echo ""
echo "🔒 Backup available in: $BACKUP_DIR"
