#!/bin/bash

# Shine Skincare App - Minimal Requirements Deployment Script
# Updated: 2025-08-10 - Deploy minimal ML capabilities for stability
# This script deploys the minimal version to t3.large for successful deployment

set -e  # Exit on any error

echo "🚀 SHINE SKINCARE APP - MINIMAL REQUIREMENTS DEPLOYMENT"
echo "======================================================="
echo "Instance: t3.large (8GB RAM, 2 vCPU)"
echo "Goal: Deploy stable minimal ML capabilities first"
echo "Strategy: Build foundation, then gradually add advanced features"
echo ""

# Check if we're in the right directory
if [ ! -f "application_minimal.py" ]; then
    echo "❌ Error: Must run from backend directory with minimal app"
    exit 1
fi

# Verify Elastic Beanstalk CLI is available
if ! command -v eb &> /dev/null; then
    echo "❌ Error: Elastic Beanstalk CLI not found"
    echo "Install with: pip install awsebcli"
    exit 1
fi

# Check current environment status
echo "📊 Checking current environment status..."
eb status

echo ""
echo "🔧 Deploying minimal requirements to t3.large (8GB RAM)..."
echo "This approach prioritizes stability over advanced features:"
echo "✅ Basic face detection (OpenCV)"
echo "✅ Basic skin analysis (numpy + OpenCV)"
echo "✅ S3 model integration"
echo "✅ Health monitoring"
echo "❌ Advanced ML frameworks (TensorFlow, PyTorch, etc.)"
echo "❌ Enhanced embeddings and analysis"
echo "❌ Advanced recommendation engine"
echo ""

# Confirm deployment
read -p "Proceed with minimal requirements deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting minimal deployment..."

# Backup current application.py
echo "📦 Backing up current application.py..."
cp application.py application_comprehensive_backup.py

# Replace with minimal version
echo "🔄 Switching to minimal application..."
cp application_minimal.py application.py

# Deploy with standard timeout
eb deploy --timeout 30

echo ""
echo "⏳ Waiting for deployment to complete..."
echo "This should complete within 10-15 minutes for minimal workloads..."

# Wait for deployment to complete
sleep 60

# Check deployment status
echo ""
echo "📊 Checking deployment status..."
eb status

# Wait for health checks to pass
echo ""
echo "🏥 Waiting for health checks to pass..."
echo "Minimal workloads should become healthy quickly..."

# Monitor health for up to 10 minutes (much faster for minimal)
for i in {1..10}; do
    echo "Health check attempt $i/10..."
    
    # Get the environment URL
    ENV_URL=$(eb status | grep "CNAME" | awk '{print $2}')
    
    if [ -n "$ENV_URL" ]; then
        echo "Testing health endpoint: http://$ENV_URL/health"
        
        # Test health endpoint
        if curl -s -f "http://$ENV_URL/health" > /dev/null; then
            echo "✅ Health endpoint responding!"
            
            # Test ML-specific endpoints
            echo "🧬 Testing minimal ML endpoints..."
            
            if curl -s -f "http://$ENV_URL/api/v1/system/status" > /dev/null; then
                echo "✅ System status endpoint working!"
                
                if curl -s -f "http://$ENV_URL/ready" > /dev/null; then
                    echo "✅ Readiness check passing!"
                    echo ""
                    echo "🎉 MINIMAL DEPLOYMENT SUCCESSFUL! 🎉"
                    echo "====================================="
                    echo "Instance: t3.large (8GB RAM)"
                    echo "URL: http://$ENV_URL"
                    echo "Status: 🟢 GREEN - Minimal ML capabilities stable!"
                    echo ""
                    echo "🚀 Next steps:"
                    echo "1. Test basic face detection endpoint"
                    echo "2. Test basic skin analysis endpoint"
                    echo "3. Monitor stability and performance"
                    echo "4. Gradually add back advanced ML features"
                    echo ""
                    echo "📝 Note: Advanced ML capabilities temporarily disabled"
                    echo "for deployment stability. Will be restored gradually."
                    
                    # Restore comprehensive app for future use
                    echo ""
                    echo "🔄 Restoring comprehensive application for future use..."
                    cp application_comprehensive_backup.py application.py
                    
                    exit 0
                fi
            fi
        fi
    fi
    
    echo "⏳ Waiting 60 seconds for minimal systems to initialize..."
    sleep 60
done

echo ""
echo "⚠️  Health checks taking longer than expected..."
echo "This is unusual for minimal workloads."
echo ""
echo "🔍 Manual verification needed:"
echo "1. Check EB console for environment status"
echo "2. Monitor CloudWatch logs for initialization issues"
echo "3. Test endpoints manually once environment is ready"
echo ""
echo "📊 Current environment status:"
eb status

echo ""
echo "📝 Deployment completed. Manual verification required."
echo "Minimal workloads should initialize much faster than comprehensive ML."

# Restore comprehensive app
echo ""
echo "🔄 Restoring comprehensive application..."
cp application_comprehensive_backup.py application.py
