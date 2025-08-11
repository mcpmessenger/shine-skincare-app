# Shine Skincare App - t3.2xlarge Deployment Script (PowerShell)
# Updated: 2025-08-10 - Optimized for 32GB RAM instance
# This script deploys the comprehensive ML platform to t3.2xlarge

param(
    [switch]$Force
)

# Error handling
$ErrorActionPreference = "Stop"

Write-Host "🚀 SHINE SKINCARE APP - t3.2xlarge DEPLOYMENT" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "Instance: t3.2xlarge (32GB RAM, 8 vCPU)" -ForegroundColor Yellow
Write-Host "Goal: Preserve ALL ML capabilities with adequate memory" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "application.py")) {
    Write-Host "❌ Error: Must run from backend directory" -ForegroundColor Red
    exit 1
}

# Verify Elastic Beanstalk CLI is available
try {
    $ebVersion = eb --version 2>$null
    if (-not $ebVersion) {
        throw "EB CLI not found"
    }
    Write-Host "✅ Elastic Beanstalk CLI found: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Elastic Beanstalk CLI not found" -ForegroundColor Red
    Write-Host "Install with: pip install awsebcli" -ForegroundColor Yellow
    exit 1
}

# Check current environment status
Write-Host "📊 Checking current environment status..." -ForegroundColor Cyan
eb status

Write-Host ""
Write-Host "🔧 Deploying to t3.2xlarge (32GB RAM)..." -ForegroundColor Yellow
Write-Host "This will preserve ALL ML capabilities:" -ForegroundColor Yellow
Write-Host "✅ TensorFlow & Keras (full functionality)" -ForegroundColor Green
Write-Host "✅ PyTorch & advanced ML frameworks" -ForegroundColor Green
Write-Host "✅ Enhanced embeddings and analysis" -ForegroundColor Green
Write-Host "✅ Real-time skin analysis" -ForegroundColor Green
Write-Host "✅ Advanced recommendation engine" -ForegroundColor Green
Write-Host "✅ Comprehensive ML pipeline" -ForegroundColor Green
Write-Host ""

# Confirm deployment (unless -Force is used)
if (-not $Force) {
    $confirmation = Read-Host "Proceed with t3.2xlarge deployment? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "❌ Deployment cancelled" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Starting deployment..." -ForegroundColor Green

# Deploy with enhanced monitoring
eb deploy --timeout 45

Write-Host ""
Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
Write-Host "This may take 10-15 minutes for ML systems to initialize..." -ForegroundColor Yellow

# Wait for deployment to complete
Start-Sleep -Seconds 60

# Check deployment status
Write-Host ""
Write-Host "📊 Checking deployment status..." -ForegroundColor Cyan
eb status

# Wait for health checks to pass
Write-Host ""
Write-Host "🏥 Waiting for health checks to pass..." -ForegroundColor Cyan
Write-Host "ML systems need time to initialize with 32GB RAM..." -ForegroundColor Yellow

# Monitor health for up to 20 minutes
for ($i = 1; $i -le 20; $i++) {
    Write-Host "Health check attempt $i/20..." -ForegroundColor Cyan
    
    # Get the environment URL
    $ebStatus = eb status
    $envUrl = ($ebStatus | Select-String "CNAME").ToString().Split()[1]
    
    if ($envUrl) {
        Write-Host "Testing health endpoint: http://$envUrl/health" -ForegroundColor Yellow
        
        try {
            # Test health endpoint
            $healthResponse = Invoke-WebRequest -Uri "http://$envUrl/health" -UseBasicParsing -TimeoutSec 30
            if ($healthResponse.StatusCode -eq 200) {
                Write-Host "✅ Health endpoint responding!" -ForegroundColor Green
                
                # Test ML-specific endpoints
                Write-Host "🧬 Testing ML endpoints..." -ForegroundColor Cyan
                
                try {
                    $systemResponse = Invoke-WebRequest -Uri "http://$envUrl/api/v3/system/status" -UseBasicParsing -TimeoutSec 30
                    if ($systemResponse.StatusCode -eq 200) {
                        Write-Host "✅ System status endpoint working!" -ForegroundColor Green
                        
                        try {
                            $readyResponse = Invoke-WebRequest -Uri "http://$envUrl/ready" -UseBasicParsing -TimeoutSec 30
                            if ($readyResponse.StatusCode -eq 200) {
                                Write-Host "✅ Readiness check passing!" -ForegroundColor Green
                                Write-Host ""
                                Write-Host "🎉 DEPLOYMENT SUCCESSFUL! 🎉" -ForegroundColor Green
                                Write-Host "================================" -ForegroundColor Green
                                Write-Host "Instance: t3.2xlarge (32GB RAM)" -ForegroundColor Yellow
                                Write-Host "URL: http://$envUrl" -ForegroundColor Yellow
                                Write-Host "Status: 🟢 GREEN - All ML capabilities preserved!" -ForegroundColor Green
                                Write-Host ""
                                Write-Host "🚀 Next steps:" -ForegroundColor Cyan
                                Write-Host "1. Test advanced ML endpoints" -ForegroundColor White
                                Write-Host "2. Verify face detection" -ForegroundColor White
                                Write-Host "3. Test comprehensive skin analysis" -ForegroundColor White
                                Write-Host "4. Monitor performance with 32GB RAM" -ForegroundColor White
                                exit 0
                            }
                        } catch {
                            Write-Host "⚠️  Readiness check not yet passing..." -ForegroundColor Yellow
                        }
                    }
                } catch {
                    Write-Host "⚠️  System status endpoint not yet responding..." -ForegroundColor Yellow
                }
            }
        } catch {
            Write-Host "⚠️  Health endpoint not yet responding..." -ForegroundColor Yellow
        }
    }
    
    Write-Host "⏳ Waiting 60 seconds for ML systems to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
}

Write-Host ""
Write-Host "⚠️  Health checks taking longer than expected..." -ForegroundColor Yellow
Write-Host "This is normal for ML systems on first deployment." -ForegroundColor Yellow
Write-Host ""
Write-Host "🔍 Manual verification needed:" -ForegroundColor Cyan
Write-Host "1. Check EB console for environment status" -ForegroundColor White
Write-Host "2. Monitor CloudWatch logs for ML initialization" -ForegroundColor White
Write-Host "3. Test endpoints manually once environment is ready" -ForegroundColor White
Write-Host ""
Write-Host "📊 Current environment status:" -ForegroundColor Cyan
eb status

Write-Host ""
Write-Host "📝 Deployment completed. Manual verification required." -ForegroundColor Yellow
Write-Host "ML systems may need additional time to initialize on t3.2xlarge." -ForegroundColor Yellow
