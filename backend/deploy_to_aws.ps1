# SWAN Production API - AWS Deployment Script
# This script deploys the SWAN API to AWS Elastic Beanstalk

param(
    [string]$EnvironmentName = "swan-production-v1",
    [string]$ApplicationName = "shine-skincare-swan",
    [string]$Region = "us-east-1",
    [string]$InstanceType = "t3.medium",
    [switch]$CreateNew,
    [switch]$UpdateExisting
)

Write-Host "🚀 SWAN Production API - AWS Deployment Script" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check if EB CLI is installed
try {
    $ebVersion = eb --version
    Write-Host "✅ EB CLI found: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ EB CLI not found. Installing EB CLI..." -ForegroundColor Yellow
    pip install awsebcli
}

# Verify production model exists
$modelPath = "production-models/swan_production_pipeline.pkl.gz"
if (-not (Test-Path $modelPath)) {
    Write-Host "❌ Production model not found at: $modelPath" -ForegroundColor Red
    Write-Host "Please run the export script first." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Production model found: $modelPath" -ForegroundColor Green

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

# Create deployment directory
$deployDir = "deploy-package"
if (Test-Path $deployDir) {
    Remove-Item -Recurse -Force $deployDir
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy necessary files
Write-Host "   Copying production model..." -ForegroundColor Gray
Copy-Item -Recurse "production-models" -Destination $deployDir

Write-Host "   Copying API code..." -ForegroundColor Gray
Copy-Item "swan_production_api.py" -Destination $deployDir
Copy-Item "production_requirements.txt" -Destination $deployDir

Write-Host "   Copying EB configuration..." -ForegroundColor Gray
Copy-Item -Recurse ".ebextensions" -Destination $deployDir

# Create Procfile
$procfileContent = "web: python swan_production_api.py"
$procfileContent | Out-File -FilePath "$deployDir/Procfile" -Encoding UTF8

# Create application.py for EB
$appContent = @"
from swan_production_api import SWANProductionAPI

# Create API instance
api = SWANProductionAPI()
app = api.app

if __name__ == '__main__':
    app.run()
"@
$appContent | Out-File -FilePath "$deployDir/application.py" -Encoding UTF8

Write-Host "✅ Deployment package created in: $deployDir" -ForegroundColor Green

# Deploy to AWS
Write-Host "🚀 Deploying to AWS..." -ForegroundColor Yellow

# Change to deployment directory
Push-Location $deployDir

try {
    if ($CreateNew) {
        Write-Host "   Creating new EB environment..." -ForegroundColor Gray
        
        # Initialize EB application
        eb init $ApplicationName --region $Region --platform "python-3.11" --interactive false
        
        # Create environment
        eb create $EnvironmentName --instance-type $InstanceType --elb-type application --single-instance
        
    } elseif ($UpdateExisting) {
        Write-Host "   Updating existing EB environment..." -ForegroundColor Gray
        
        # Deploy to existing environment
        eb deploy $EnvironmentName
        
    } else {
        Write-Host "   Please specify --CreateNew or --UpdateExisting flag" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    
    # Get environment info
    Write-Host "📊 Getting environment information..." -ForegroundColor Yellow
    eb status $EnvironmentName
    
    # Get environment URL
    $envUrl = eb status $EnvironmentName | Select-String "CNAME" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
    if ($envUrl) {
        Write-Host "🌐 Your API is available at: http://$envUrl" -ForegroundColor Green
        Write-Host "📋 Health check: http://$envUrl/health" -ForegroundColor Green
        Write-Host "🔍 Model info: http://$envUrl/api/v1/model-info" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
    
} finally {
    # Return to original directory
    Pop-Location
}

Write-Host "🎉 Deployment script completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test your API endpoints" -ForegroundColor White
Write-Host "2. Monitor performance and logs" -ForegroundColor White
Write-Host "3. Set up monitoring and alerting" -ForegroundColor White
Write-Host "4. Configure custom domain if needed" -ForegroundColor White
