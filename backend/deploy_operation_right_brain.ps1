# Operation Right Brain 🧠 - Backend Deployment Script
# Deploys the AI-powered skin analysis backend to AWS Elastic Beanstalk
# Author: Manus AI
# Date: August 2, 2025

param(
    [string]$Environment = "development",
    [string]$Region = "us-east-1",
    [switch]$SkipTests,
    [switch]$Force
)

Write-Host "=== Operation Right Brain 🧠 Backend Deployment ===" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

# Step 1: Validate Configuration
Write-Host "`nStep 1: Validating Configuration..." -ForegroundColor Yellow

# Check required environment variables
$requiredEnvVars = @(
    "GOOGLE_CLOUD_PROJECT",
    "VECTOR_DB_INDEX_ENDPOINT_ID", 
    "VECTOR_DB_DEPLOYED_INDEX_ID",
    "GOOGLE_APPLICATION_CREDENTIALS"
)

$missingVars = @()
foreach ($var in $requiredEnvVars) {
    if (-not (Get-ChildItem "env:$var" -ErrorAction SilentlyContinue)) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "❌ Missing required environment variables:" -ForegroundColor Red
    foreach ($var in $missingVars) {
        Write-Host "   - $var" -ForegroundColor Red
    }
    Write-Host "Please set these variables before deployment." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Configuration validation passed" -ForegroundColor Green

# Step 2: Run Tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "`nStep 2: Running Tests..." -ForegroundColor Yellow
    
    try {
        python -m pytest tests/ -v --cov=backend --cov-report=html
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Tests failed. Deployment aborted." -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ All tests passed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error running tests: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ Skipping tests (--SkipTests flag used)" -ForegroundColor Yellow
}

# Step 3: Install Dependencies
Write-Host "`nStep 3: Installing Dependencies..." -ForegroundColor Yellow

try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error installing dependencies: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Create Deployment Package
Write-Host "`nStep 4: Creating Deployment Package..." -ForegroundColor Yellow

$deploymentDir = "deployment-package"
if (Test-Path $deploymentDir) {
    Remove-Item $deploymentDir -Recurse -Force
}

New-Item -ItemType Directory -Path $deploymentDir | Out-Null

# Copy necessary files
$filesToCopy = @(
    "operation_right_brain.py",
    "config.py",
    "requirements.txt",
    "services/",
    "models/",
    "utils/",
    "tests/",
    ".ebextensions/",
    "Procfile"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        if (Test-Path $file -PathType Container) {
            Copy-Item $file -Destination $deploymentDir -Recurse
        } else {
            Copy-Item $file -Destination $deploymentDir
        }
    }
}

# Create .ebextensions if it doesn't exist
if (-not (Test-Path ".ebextensions")) {
    New-Item -ItemType Directory -Path ".ebextensions" | Out-Null
}

# Create Procfile if it doesn't exist
if (-not (Test-Path "Procfile")) {
    @"
web: gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 operation_right_brain:create_app()
"@ | Out-File -FilePath "Procfile" -Encoding UTF8
}

Write-Host "✅ Deployment package created" -ForegroundColor Green

# Step 5: Initialize EB CLI (if needed)
Write-Host "`nStep 5: Initializing Elastic Beanstalk..." -ForegroundColor Yellow

try {
    # Check if EB CLI is installed
    eb --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ EB CLI not found. Please install it first." -ForegroundColor Red
        Write-Host "Install with: pip install awsebcli" -ForegroundColor Yellow
        exit 1
    }
    
    # Initialize EB application if needed
    if (-not (Test-Path ".elasticbeanstalk")) {
        eb init --region $Region --platform "Python 3.9" --application-name "shine-operation-right-brain"
    }
    
    Write-Host "✅ Elastic Beanstalk initialized" -ForegroundColor Green
} catch {
    Write-Host "❌ Error initializing Elastic Beanstalk: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 6: Deploy to Elastic Beanstalk
Write-Host "`nStep 6: Deploying to Elastic Beanstalk..." -ForegroundColor Yellow

try {
    $envName = "shine-operation-right-brain-$Environment"
    
    # Check if environment exists
    eb status $envName --region $Region | Out-Null
    if ($LASTEXITCODE -eq 0) {
        # Environment exists, deploy to it
        eb deploy $envName --region $Region --staged
    } else {
        # Create new environment
        eb create $envName --region $Region --platform "Python 3.9" --instance-type "t3.small" --single-instance
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Deployment completed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error during deployment: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 7: Health Check
Write-Host "`nStep 7: Performing Health Check..." -ForegroundColor Yellow

try {
    # Get the application URL
    $appUrl = eb status $envName --region $Region | Select-String "CNAME" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
    
    if ($appUrl) {
        $healthUrl = "https://$appUrl/api/health"
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 30
        
        if ($response.status -eq "healthy") {
            Write-Host "✅ Health check passed" -ForegroundColor Green
            Write-Host "Application URL: https://$appUrl" -ForegroundColor Cyan
        } else {
            Write-Host "⚠ Health check returned: $($response.status)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠ Could not retrieve application URL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 8: Cleanup
Write-Host "`nStep 8: Cleaning up..." -ForegroundColor Yellow

if (Test-Path $deploymentDir) {
    Remove-Item $deploymentDir -Recurse -Force
}

Write-Host "✅ Cleanup completed" -ForegroundColor Green

# Final Summary
Write-Host "`n=== Deployment Summary ===" -ForegroundColor Green
Write-Host "✅ Operation Right Brain 🧠 backend deployed successfully" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Configure Google Cloud credentials" -ForegroundColor White
Write-Host "2. Set up SCIN dataset embeddings" -ForegroundColor White
Write-Host "3. Test the /api/v3/skin/analyze-enhanced endpoint" -ForegroundColor White
Write-Host "4. Monitor application logs and metrics" -ForegroundColor White

Write-Host "`nDeployment completed! 🚀" -ForegroundColor Green 