#!/usr/bin/env pwsh
# Direct AWS CLI deployment (bypasses EB CLI issues)

$EnvironmentName = "shine-backend-poc"
$ApplicationName = "shine-backend"
$Region = "us-east-1"

Write-Host "Direct AWS CLI deployment to $EnvironmentName" -ForegroundColor Green

# Navigate to backend
cd backend

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipFile = "deploy-$timestamp.zip"

# Create zip excluding unnecessary files
Compress-Archive -Path * -DestinationPath $zipFile -Force -CompressionLevel Optimal

Write-Host "Created $zipFile" -ForegroundColor Green

# Get S3 bucket for EB deployments
Write-Host "Getting EB S3 bucket..." -ForegroundColor Cyan
try {
    $buckets = aws s3 ls | Select-String "elasticbeanstalk"
    if ($buckets) {
        $bucketName = ($buckets[0] -split '\s+')[-1]
        Write-Host "Using bucket: $bucketName" -ForegroundColor Green
    } else {
        Write-Host "No EB S3 bucket found. Creating one..." -ForegroundColor Yellow
        $bucketName = "elasticbeanstalk-$Region-$(aws sts get-caller-identity --query Account --output text)"
        aws s3 mb s3://$bucketName --region $Region
    }
} catch {
    Write-Host "Error with S3 bucket: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Upload to S3
Write-Host "Uploading to S3..." -ForegroundColor Cyan
aws s3 cp $zipFile s3://$bucketName/$zipFile --region $Region

# Create application version
Write-Host "Creating application version..." -ForegroundColor Cyan
$versionLabel = "v$timestamp"
aws elasticbeanstalk create-application-version --application-name $ApplicationName --version-label $versionLabel --source-bundle S3Bucket=$bucketName,S3Key=$zipFile --region $Region

# Deploy to environment
Write-Host "Deploying to environment..." -ForegroundColor Cyan
aws elasticbeanstalk update-environment --environment-name $EnvironmentName --version-label $versionLabel --region $Region

Write-Host "Deployment initiated! This will take 10-15 minutes..." -ForegroundColor Yellow
Write-Host "Monitor progress in AWS Console or run:" -ForegroundColor White
Write-Host "aws elasticbeanstalk describe-environments --environment-names $EnvironmentName --region $Region" -ForegroundColor Gray

# Cleanup
Remove-Item $zipFile -Force

Write-Host "Deployment script completed!" -ForegroundColor Green