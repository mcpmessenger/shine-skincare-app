@echo off
echo 🔧 Manual Instance Upgrade for ML Workloads
echo.

set ENVIRONMENT_NAME=Shine-backend-poc-env
set REGION=us-east-1
set NEW_INSTANCE_TYPE=c5.large

echo 📋 Current Configuration:
echo   Environment: %ENVIRONMENT_NAME%
echo   Region: %REGION%
echo   Target Instance Type: %NEW_INSTANCE_TYPE%
echo.

echo 🚀 Upgrading instance type to %NEW_INSTANCE_TYPE%...
echo ⏱️ This will take 10-15 minutes...
echo.

aws elasticbeanstalk update-environment --environment-name %ENVIRONMENT_NAME% --option-settings Namespace=aws:autoscaling:launchconfiguration,OptionName=InstanceType,Value=%NEW_INSTANCE_TYPE% --region %REGION%

if errorlevel 1 (
    echo ❌ Failed to upgrade instance
    echo 💡 Try upgrading manually in AWS Console:
    echo 1. Go to AWS Elastic Beanstalk Console
    echo 2. Select environment: %ENVIRONMENT_NAME%
    echo 3. Click "Configuration"
    echo 4. Click "Edit" on Instances
    echo 5. Change Instance Type to %NEW_INSTANCE_TYPE%
    echo 6. Click "Apply"
    exit /b 1
)

echo.
echo ✅ Instance upgrade initiated!
echo 📊 Monitor in AWS Console or run:
echo aws elasticbeanstalk describe-environments --environment-names %ENVIRONMENT_NAME% --region %REGION%
echo.
echo 💡 After upgrade completes, run: .\deploy-after-upgrade.bat 