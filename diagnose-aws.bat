@echo off
echo 🔍 AWS CLI Diagnostic
echo.

echo 1. Testing AWS CLI installation...
aws --version
if errorlevel 1 (
    echo ❌ AWS CLI not installed or not in PATH
    echo Please install AWS CLI from: https://aws.amazon.com/cli/
    exit /b 1
)
echo ✅ AWS CLI found
echo.

echo 2. Testing AWS credentials...
aws sts get-caller-identity
if errorlevel 1 (
    echo ❌ AWS credentials not configured
    echo Please run: aws configure
    exit /b 1
)
echo ✅ AWS credentials working
echo.

echo 3. Testing region access...
aws elasticbeanstalk describe-applications --region us-east-1 --max-items 1
if errorlevel 1 (
    echo ❌ Cannot access Elastic Beanstalk in us-east-1
    echo Check your IAM permissions
    exit /b 1
)
echo ✅ Region access working
echo.

echo 4. Testing S3 access...
aws s3 ls --region us-east-1
if errorlevel 1 (
    echo ❌ Cannot access S3
    echo Check your IAM permissions
    exit /b 1
)
echo ✅ S3 access working
echo.

echo 5. Checking application...
aws elasticbeanstalk describe-applications --application-names shine-backend-poc --region us-east-1
if errorlevel 1 (
    echo ❌ Application 'shine-backend-poc' not found
    echo Check application name
    exit /b 1
)
echo ✅ Application found
echo.

echo 6. Checking environment...
aws elasticbeanstalk describe-environments --environment-names Shine-backend-poc-env --region us-east-1
if errorlevel 1 (
    echo ❌ Environment 'Shine-backend-poc-env' not found
    echo Check environment name
    exit /b 1
)
echo ✅ Environment found
echo.

echo 🎉 All AWS CLI tests passed!
echo You should be able to deploy manually using the commands in MANUAL_DEPLOYMENT_GUIDE.md 