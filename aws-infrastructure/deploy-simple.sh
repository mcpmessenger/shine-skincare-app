#!/bin/bash
# Simple CLI deployment for Shine ML backend

set -e

APPLICATION_NAME="shine-backend"
ENVIRONMENT_NAME="shine-backend-final"
REGION="us-east-1"
BACKEND_PATH="backend"

echo "🚀 Deploying Shine ML Backend to AWS Elastic Beanstalk"
echo "Environment: $ENVIRONMENT_NAME"
echo "Region: $REGION"

# Quick prerequisite check
echo ""
echo "📋 Checking prerequisites..."
if aws sts get-caller-identity --output table; then
    echo "✓ AWS CLI configured"
else
    echo "❌ AWS CLI not configured. Run: aws configure"
    exit 1
fi

if eb --version; then
    echo "✓ EB CLI available"
else
    echo "❌ EB CLI not found. Install with: pip install awsebcli"
    exit 1
fi

# Navigate to backend directory
if [ ! -d "$BACKEND_PATH" ]; then
    echo "❌ Backend directory not found: $BACKEND_PATH"
    exit 1
fi

cd $BACKEND_PATH

# Initialize EB if needed
echo ""
echo "🔧 Initializing EB application..."
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    eb init $APPLICATION_NAME --region $REGION --platform python-3.11
    echo "✓ EB application initialized"
else
    echo "✓ EB application already initialized"
fi

# Check if environment exists
echo ""
echo "🔍 Checking environment status..."
ENV_EXISTS=false
if aws elasticbeanstalk describe-environments --environment-names $ENVIRONMENT_NAME --region $REGION --output json > /dev/null 2>&1; then
    ENV_INFO=$(aws elasticbeanstalk describe-environments --environment-names $ENVIRONMENT_NAME --region $REGION --output json)
    if echo "$ENV_INFO" | jq -r '.Environments | length' | grep -q "1"; then
        ENV_EXISTS=true
        STATUS=$(echo "$ENV_INFO" | jq -r '.Environments[0].Status')
        HEALTH=$(echo "$ENV_INFO" | jq -r '.Environments[0].Health')
        echo "✓ Environment exists: $STATUS - $HEALTH"
    fi
fi

# Deploy or create
if [ "$ENV_EXISTS" = true ]; then
    echo ""
    echo "🚀 Deploying to existing environment..."
    eb deploy $ENVIRONMENT_NAME --timeout 20
else
    echo ""
    echo "🏗️ Creating new environment and deploying..."
    eb create $ENVIRONMENT_NAME --instance-type c5.2xlarge --timeout 20
fi

# Quick health check
echo ""
echo "🏥 Running basic health check..."
sleep 30

ENV_INFO=$(aws elasticbeanstalk describe-environments --environment-names $ENVIRONMENT_NAME --region $REGION --output json)
STATUS=$(echo "$ENV_INFO" | jq -r '.Environments[0].Status')
HEALTH=$(echo "$ENV_INFO" | jq -r '.Environments[0].Health')
URL=$(echo "$ENV_INFO" | jq -r '.Environments[0].CNAME')

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "Status: $STATUS"
echo "Health: $HEALTH"
echo "URL: https://$URL"

# Test basic endpoint
if curl -f "https://$URL/api/health" > /dev/null 2>&1; then
    echo "✓ Health check passed"
else
    echo "⚠️ Health check failed (app may still be starting)"
fi

echo ""
echo "🎉 Deployment script completed!"
echo "Check AWS EB Console for detailed status"

cd ..