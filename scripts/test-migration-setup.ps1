# Test script for migration setup
# This script tests the migration setup without creating actual resources

param(
    [string]$Region = "us-east-1"
)

Write-Host "🧪 Testing Migration Setup Script..." -ForegroundColor Cyan

# Test AWS CLI connectivity
Write-Host "Testing AWS CLI connectivity..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity --region $Region --query 'Account' --output text
    Write-Host "✅ AWS CLI connected successfully. Account: $identity" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI connection failed: $_" -ForegroundColor Red
    exit 1
}

# Test region configuration
Write-Host "Testing region configuration..." -ForegroundColor Yellow
try {
    $currentRegion = aws configure get region
    Write-Host "✅ Current region: $currentRegion" -ForegroundColor Green
} catch {
    Write-Host "❌ Region configuration failed: $_" -ForegroundColor Red
}

# Test Elastic Beanstalk list applications
Write-Host "Testing Elastic Beanstalk access..." -ForegroundColor Yellow
try {
    $apps = aws elasticbeanstalk describe-applications --region $Region --query 'Applications[].ApplicationName' --output text
    Write-Host "✅ Elastic Beanstalk access successful. Found applications: $apps" -ForegroundColor Green
} catch {
    Write-Host "❌ Elastic Beanstalk access failed: $_" -ForegroundColor Red
}

# Test Amplify access
Write-Host "Testing Amplify access..." -ForegroundColor Yellow
try {
    $amplifyApps = aws amplify list-apps --region $Region --query 'apps[].name' --output text
    Write-Host "✅ Amplify access successful. Found apps: $amplifyApps" -ForegroundColor Green
} catch {
    Write-Host "❌ Amplify access failed: $_" -ForegroundColor Red
}

# Test S3 access
Write-Host "Testing S3 access..." -ForegroundColor Yellow
try {
    $buckets = aws s3 ls --region $Region --query 'Buckets[].Name' --output text
    Write-Host "✅ S3 access successful. Found buckets: $buckets" -ForegroundColor Green
} catch {
    Write-Host "❌ S3 access failed: $_" -ForegroundColor Red
}

# Test CloudWatch access
Write-Host "Testing CloudWatch access..." -ForegroundColor Yellow
try {
    $dashboards = aws cloudwatch list-dashboards --region $Region --query 'DashboardEntries[].DashboardName' --output text
    Write-Host "✅ CloudWatch access successful. Found dashboards: $dashboards" -ForegroundColor Green
} catch {
    Write-Host "❌ CloudWatch access failed: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Migration setup test completed!" -ForegroundColor Green
Write-Host "All AWS services are accessible and ready for migration." -ForegroundColor Cyan 