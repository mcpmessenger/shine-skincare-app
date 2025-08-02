# Shine Skincare App - Migration Setup Script
# Sets up new environments for the Embeddings Model architecture

param(
    [string]$Region = "us-east-1",
    [string]$NewAppName = "shine-skincare-new",
    [string]$NewEnvName = "shine-new-staging"
)

Write-Host "🚀 Setting up new environments for migration..." -ForegroundColor Green

# Set AWS region
Write-Host "Setting AWS region to $Region..." -ForegroundColor Yellow
aws configure set region $Region

# Create new Elastic Beanstalk application
Write-Host "Creating new Elastic Beanstalk application: $NewAppName..." -ForegroundColor Yellow
try {
    aws elasticbeanstalk create-application --application-name $NewAppName --region $Region
    Write-Host "✅ New EB application created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Application may already exist, continuing..." -ForegroundColor Yellow
}

# Create new Elastic Beanstalk environment
Write-Host "Creating new Elastic Beanstalk environment: $NewEnvName..." -ForegroundColor Yellow
try {
    aws elasticbeanstalk create-environment `
        --application-name $NewAppName `
        --environment-name $NewEnvName `
        --solution-stack-name "64bit Amazon Linux 2023 v4.6.2 running Python 3.9" `
        --region $Region `
        --option-settings Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=aws-elasticbeanstalk-ec2-role
    Write-Host "✅ New EB environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create environment: $_" -ForegroundColor Red
    Write-Host "This might be because the environment already exists or there's a configuration issue." -ForegroundColor Yellow
}

# Create new Amplify app for frontend
Write-Host "Creating new Amplify app for frontend..." -ForegroundColor Yellow
try {
    $amplifyApp = aws amplify create-app --name "shine-frontend-new" --region $Region --query 'app.appId' --output text
    Write-Host "✅ New Amplify app created: $amplifyApp" -ForegroundColor Green
    
    # Create staging branch
    aws amplify create-branch --app-id $amplifyApp --branch-name "staging" --region $Region
    Write-Host "✅ Staging branch created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Amplify app: $_" -ForegroundColor Red
}

# Create deployment bucket
Write-Host "Creating S3 deployment bucket..." -ForegroundColor Yellow
$bucketName = "shine-deployments-$Region-$(Get-Date -Format 'yyyyMMdd')"
try {
    aws s3 mb "s3://$bucketName" --region $Region
    Write-Host "✅ Deployment bucket created: $bucketName" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create bucket: $_" -ForegroundColor Red
}

# Create CloudWatch dashboard for monitoring
Write-Host "Setting up CloudWatch monitoring..." -ForegroundColor Yellow

# Create a simpler dashboard configuration
$dashboardBody = '{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["AWS/ElasticBeanstalk", "ApplicationRequestsTotal", "EnvironmentName", "' + $NewEnvName + '"]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "' + $Region + '",
                "title": "Application Requests"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    ["AWS/ElasticBeanstalk", "ApplicationLatencyP95", "EnvironmentName", "' + $NewEnvName + '"]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "' + $Region + '",
                "title": "Application Latency P95"
            }
        }
    ]
}'

try {
    aws cloudwatch put-dashboard --dashboard-name "Shine-Migration-Monitoring" --dashboard-body $dashboardBody --region $Region
    Write-Host "✅ CloudWatch dashboard created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create dashboard: $_" -ForegroundColor Red
    Write-Host "Dashboard creation failed, but this is not critical for migration." -ForegroundColor Yellow
}

Write-Host "`n🎉 Migration setup completed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Deploy new backend to staging environment" -ForegroundColor White
Write-Host "2. Deploy new frontend to Amplify staging branch" -ForegroundColor White
Write-Host "3. Set up traffic routing for A/B testing" -ForegroundColor White
Write-Host "4. Begin Phase 1 of migration plan" -ForegroundColor White

Write-Host "`nEnvironment Details:" -ForegroundColor Cyan
Write-Host "Backend: $NewAppName/$NewEnvName" -ForegroundColor White
Write-Host "Frontend: shine-frontend-new/staging" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host "Deployment Bucket: $bucketName" -ForegroundColor White 