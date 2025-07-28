@echo off
echo 🔍 Verifying Instance Configuration
echo.

set ENVIRONMENT_NAME=Shine-backend-poc-env
set REGION=us-east-1

echo 📋 Checking environment status...
aws elasticbeanstalk describe-environments --environment-names %ENVIRONMENT_NAME% --region %REGION%

echo.
echo 📊 To check instance type manually:
echo 1. Go to AWS Console
echo 2. Navigate to Elastic Beanstalk
echo 3. Click on environment: %ENVIRONMENT_NAME%
echo 4. Check Configuration > Instances
echo 5. Look for Instance Type
echo.
echo 💡 If instance type is still small (t3.micro, t3.small), we need to upgrade manually 