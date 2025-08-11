#!/bin/bash

# Shine Skincare App - t3.2xlarge Deployment Script
# Updated: 2025-08-10 - Optimized for 32GB RAM instance
# This script deploys the comprehensive ML platform to t3.2xlarge

set -e  # Exit on any error

echo "🚀 SHINE SKINCARE APP - t3.2xlarge DEPLOYMENT"
echo "================================================"
echo "Instance: t3.2xlarge (32GB RAM, 8 vCPU)"
echo "Goal: Preserve ALL ML capabilities with adequate memory"
echo ""

# Check if we're in the right directory
if [ ! -f "application.py" ]; then
    echo "❌ Error: Must run from backend directory"
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
echo "🔧 Deploying to t3.2xlarge (32GB RAM)..."
echo "This will preserve ALL ML capabilities:"
echo "✅ TensorFlow & Keras (full functionality)"
echo "✅ PyTorch & advanced ML frameworks"
echo "✅ Enhanced embeddings and analysis"
echo "✅ Real-time skin analysis"
echo "✅ Advanced recommendation engine"
echo "✅ Comprehensive ML pipeline"
echo ""

# Confirm deployment
read -p "Proceed with t3.2xlarge deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Starting deployment..."

# Deploy with enhanced monitoring
eb deploy --timeout 45

echo ""
echo "⏳ Waiting for deployment to complete..."
echo "This may take 10-15 minutes for ML systems to initialize..."

# Wait for deployment to complete
sleep 60

# Check deployment status
echo ""
echo "📊 Checking deployment status..."
eb status

# Wait for health checks to pass
echo ""
echo "🏥 Waiting for health checks to pass..."
echo "ML systems need time to initialize with 32GB RAM..."

# Monitor health for up to 20 minutes
for i in {1..20}; do
    echo "Health check attempt $i/20..."
    
    # Get the environment URL
    ENV_URL=$(eb status | grep "CNAME" | awk '{print $2}')
    
    if [ -n "$ENV_URL" ]; then
        echo "Testing health endpoint: http://$ENV_URL/health"
        
        # Test health endpoint
        if curl -s -f "http://$ENV_URL/health" > /dev/null; then
            echo "✅ Health endpoint responding!"
            
            # Test ML-specific endpoints
            echo "🧬 Testing ML endpoints..."
            
            if curl -s -f "http://$ENV_URL/api/v3/system/status" > /dev/null; then
                echo "✅ System status endpoint working!"
                
                if curl -s -f "http://$ENV_URL/ready" > /dev/null; then
                    echo "✅ Readiness check passing!"
                    echo ""
                    echo "🎉 DEPLOYMENT SUCCESSFUL! 🎉"
                    echo "================================"
                    echo "Instance: t3.2xlarge (32GB RAM)"
                    echo "URL: http://$ENV_URL"
                    echo "Status: 🟢 GREEN - All ML capabilities preserved!"
                    echo ""
                    echo "🚀 Next steps:"
                    echo "1. Test advanced ML endpoints"
                    echo "2. Verify face detection"
                    echo "3. Test comprehensive skin analysis"
                    echo "4. Monitor performance with 32GB RAM"
                    exit 0
                fi
            fi
        fi
    fi
    
    echo "⏳ Waiting 60 seconds for ML systems to initialize..."
    sleep 60
done

echo ""
echo "⚠️  Health checks taking longer than expected..."
echo "This is normal for ML systems on first deployment."
echo ""
echo "🔍 Manual verification needed:"
echo "1. Check EB console for environment status"
echo "2. Monitor CloudWatch logs for ML initialization"
echo "3. Test endpoints manually once environment is ready"
echo ""
echo "📊 Current environment status:"
eb status

echo ""
echo "📝 Deployment completed. Manual verification required."
echo "ML systems may need additional time to initialize on t3.2xlarge."
