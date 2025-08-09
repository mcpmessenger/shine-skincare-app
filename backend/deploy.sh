#!/bin/bash

# Shine Skincare Backend Deployment Script
# Deploys to AWS Elastic Beanstalk

echo "🚀 Starting Shine Backend Deployment..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "❌ EB CLI not found. Please install with: pip install awsebcli"
    exit 1
fi

# Initialize EB if not already done
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    echo "📝 Initializing Elastic Beanstalk..."
    eb init shine-backend --platform python-3.11 --region us-east-1
fi

# Create environment if it doesn't exist
if ! eb status &> /dev/null; then
    echo "🏗️ Creating Elastic Beanstalk environment..."
    eb create shine-backend-prod --instance-type t3.medium --single-instance
else
    echo "🔄 Deploying to existing environment..."
    eb deploy
fi

echo "✅ Backend deployment complete!"
echo "🌐 Backend URL: $(eb status | grep CNAME | awk '{print $2}')"
