@echo off
echo 🔧 Upgrading Instance for ML Workloads
echo.

REM Configuration
set ENVIRONMENT_NAME=Shine-backend-poc-env
set REGION=us-east-1
set NEW_INSTANCE_TYPE=c5.large

echo 📋 Configuration:
echo   Environment: %ENVIRONMENT_NAME%
echo   Region: %REGION%
echo   New Instance Type: %NEW_INSTANCE_TYPE%
echo.

echo 🔍 Current instance is too small for ML workloads
echo 📈 Upgrading to %NEW_INSTANCE_TYPE% for better performance
echo.

echo 🚀 Upgrading instance type...
aws elasticbeanstalk update-environment --environment-name %ENVIRONMENT_NAME% --option-settings Namespace=aws:autoscaling:launchconfiguration,OptionName=InstanceType,Value=%NEW_INSTANCE_TYPE% --region %REGION%

if errorlevel 1 (
    echo ❌ Failed to upgrade instance
    exit /b 1
)

echo.
echo ✅ Instance upgrade initiated!
echo ⏱️ This will take 10-15 minutes...
echo 📊 Monitor progress in AWS Console
echo.
echo 📊 Monitor upgrade:
echo aws elasticbeanstalk describe-environments --environment-names %ENVIRONMENT_NAME% --region %REGION%
echo.
echo 💡 After upgrade completes, we can deploy the full ML package! 