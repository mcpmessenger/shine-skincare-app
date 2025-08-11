#!/bin/bash

# Shine Skincare App - Comprehensive Deployment Script
# Updated: 2025-08-10 - Full functional app deployment

set -e  # Exit on any error

echo "🚀 Starting Comprehensive Shine Skincare App Deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "application.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    print_error "EB CLI is not installed. Please install it first:"
    echo "pip install awsebcli"
    exit 1
fi

# Check if we're logged into AWS
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "Not logged into AWS. Please run:"
    echo "aws configure"
    exit 1
fi

print_status "Pre-deployment checks completed successfully"

# Step 1: Verify application.py is comprehensive
print_status "Step 1: Verifying comprehensive application.py..."
if grep -q "IntegratedSkinAnalysis" application.py; then
    print_success "✅ Comprehensive application.py detected"
else
    print_error "❌ application.py does not appear to be comprehensive"
    exit 1
fi

# Step 2: Check requirements
print_status "Step 2: Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    print_success "✅ requirements.txt found"
    print_status "Dependencies to be installed:"
    cat requirements.txt | grep -v "^#" | grep -v "^$" | while read line; do
        echo "  - $line"
    done
else
    print_error "❌ requirements.txt not found"
    exit 1
fi

# Step 3: Verify configuration files
print_status "Step 3: Verifying configuration files..."
if [ -f ".ebextensions/03_resources.config" ]; then
    print_success "✅ Enhanced resources configuration found"
else
    print_warning "⚠️  Enhanced resources configuration not found"
fi

# Step 4: Deploy to Elastic Beanstalk
print_status "Step 4: Deploying to Elastic Beanstalk..."
print_warning "This will deploy to environment: shine-backend-light"
print_warning "Press Enter to continue or Ctrl+C to cancel..."
read

print_status "Starting deployment..."
eb deploy

if [ $? -eq 0 ]; then
    print_success "✅ Deployment completed successfully!"
else
    print_error "❌ Deployment failed"
    exit 1
fi

# Step 5: Wait for deployment to complete
print_status "Step 5: Waiting for deployment to complete..."
print_status "This may take 5-10 minutes..."

# Get the environment URL
ENV_URL=$(eb status | grep "CNAME" | awk '{print $2}')
if [ -n "$ENV_URL" ]; then
    print_success "Environment URL: $ENV_URL"
else
    print_warning "Could not determine environment URL"
fi

# Step 6: Health check
print_status "Step 6: Performing health checks..."
sleep 30  # Wait for deployment to stabilize

if [ -n "$ENV_URL" ]; then
    print_status "Testing basic health endpoint..."
    if curl -f "http://$ENV_URL/health" > /dev/null 2>&1; then
        print_success "✅ Basic health check passed"
    else
        print_warning "⚠️  Basic health check failed"
    fi
    
    print_status "Testing comprehensive system status..."
    if curl -f "http://$ENV_URL/api/v3/system/status" > /dev/null 2>&1; then
        print_success "✅ System status endpoint working"
    else
        print_warning "⚠️  System status endpoint failed"
    fi
else
    print_warning "Skipping health checks - no environment URL"
fi

# Step 7: Final verification
print_status "Step 7: Final verification..."
print_success "🎉 Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Visit your environment URL to test the app"
echo "2. Check the comprehensive API documentation at /"
echo "3. Test face detection at /api/v1/face/detect"
echo "4. Test skin analysis at /api/v3/skin/analyze-basic"
echo "5. Monitor system status at /api/v3/system/status"
echo ""
echo "If you encounter issues:"
echo "- Check logs: eb logs"
echo "- SSH into instance: eb ssh"
echo "- View environment status: eb status"
echo ""
echo "Happy analyzing! 🧬✨"
