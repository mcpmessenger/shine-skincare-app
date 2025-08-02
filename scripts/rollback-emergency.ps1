# Shine Skincare App - Emergency Rollback Script
# Provides immediate rollback capability during migration

param(
    [string]$Region = "us-east-1",
    [string]$OldEnvName = "SHINE-env",
    [string]$NewEnvName = "shine-new-staging",
    [switch]$Immediate,
    [switch]$Gradual,
    [switch]$Full,
    [switch]$Status
)

Write-Host "🚨 Emergency Rollback Management" -ForegroundColor Red

# Function to get environment status
function Get-EnvironmentStatus {
    param([string]$EnvName)
    
    try {
        $status = aws elasticbeanstalk describe-environments --environment-names $EnvName --region $Region --query 'Environments[0].Status' --output text
        $health = aws elasticbeanstalk describe-environments --environment-names $EnvName --region $Region --query 'Environments[0].Health' --output text
        return @{
            Status = $status
            Health = $health
        }
    } catch {
        return @{
            Status = "Unknown"
            Health = "Unknown"
        }
    }
}

# Function to send alert
function Send-Alert {
    param([string]$Message, [string]$Severity = "High")
    
    Write-Host "🚨 ALERT: $Message" -ForegroundColor Red
    
    # Log to CloudWatch
    try {
        $logMessage = @{
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            severity = $Severity
            message = $Message
            action = "rollback"
        } | ConvertTo-Json
        
        aws logs put-log-events `
            --log-group-name "/aws/elasticbeanstalk/shine-rollback" `
            --log-stream-name "emergency-rollback" `
            --log-events timestamp=[$(Get-Date -UFormat %s)],message="$logMessage" `
            --region $Region
    } catch {
        Write-Host "⚠️ Could not log to CloudWatch" -ForegroundColor Yellow
    }
}

# Immediate rollback (0-1 hour)
if ($Immediate) {
    Write-Host "🚨 EXECUTING IMMEDIATE ROLLBACK..." -ForegroundColor Red
    Send-Alert "Immediate rollback initiated - routing all traffic back to old environment"
    
    # Check old environment health
    $oldStatus = Get-EnvironmentStatus $OldEnvName
    if ($oldStatus.Health -ne "Ok") {
        Write-Host "❌ WARNING: Old environment is not healthy: $($oldStatus.Health)" -ForegroundColor Red
        Write-Host "Proceeding with rollback anyway..." -ForegroundColor Yellow
    }
    
    # Set traffic routing to 0% (all traffic to old system)
    try {
        aws elasticbeanstalk update-environment `
            --environment-name $OldEnvName `
            --region $Region `
            --option-settings "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_ENABLED,Value=false"
        
        Write-Host "✅ Immediate rollback completed - all traffic routed to old environment" -ForegroundColor Green
        Send-Alert "Immediate rollback completed successfully"
    } catch {
        Write-Host "❌ Failed to execute immediate rollback: $_" -ForegroundColor Red
        Send-Alert "Immediate rollback failed: $_"
        exit 1
    }
    
    exit 0
}

# Gradual rollback (1-24 hours)
if ($Gradual) {
    Write-Host "🔄 EXECUTING GRADUAL ROLLBACK..." -ForegroundColor Yellow
    Send-Alert "Gradual rollback initiated - reducing traffic to new environment"
    
    # Step 1: Reduce to 25% traffic
    Write-Host "Step 1: Reducing traffic to 25%..." -ForegroundColor Yellow
    try {
        aws elasticbeanstalk update-environment `
            --environment-name $OldEnvName `
            --region $Region `
            --option-settings "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_PERCENTAGE,Value=25"
        
        Write-Host "✅ Traffic reduced to 25%" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to reduce traffic: $_" -ForegroundColor Red
        exit 1
    }
    
    # Step 2: Monitor for 1 hour
    Write-Host "Step 2: Monitoring for 1 hour..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3600
    
    # Step 3: Reduce to 0% traffic
    Write-Host "Step 3: Reducing traffic to 0%..." -ForegroundColor Yellow
    try {
        aws elasticbeanstalk update-environment `
            --environment-name $OldEnvName `
            --region $Region `
            --option-settings "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_PERCENTAGE,Value=0"
        
        Write-Host "✅ Gradual rollback completed - all traffic routed to old environment" -ForegroundColor Green
        Send-Alert "Gradual rollback completed successfully"
    } catch {
        Write-Host "❌ Failed to complete gradual rollback: $_" -ForegroundColor Red
        Send-Alert "Gradual rollback failed: $_"
        exit 1
    }
    
    exit 0
}

# Full rollback (24+ hours)
if ($Full) {
    Write-Host "🔄 EXECUTING FULL ROLLBACK..." -ForegroundColor Yellow
    Send-Alert "Full rollback initiated - complete migration back to old system"
    
    # Step 1: Disable new architecture
    Write-Host "Step 1: Disabling new architecture..." -ForegroundColor Yellow
    try {
        aws elasticbeanstalk update-environment `
            --environment-name $OldEnvName `
            --region $Region `
            --option-settings "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_ENABLED,Value=false"
        
        Write-Host "✅ New architecture disabled" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to disable new architecture: $_" -ForegroundColor Red
        exit 1
    }
    
    # Step 2: Investigate issues
    Write-Host "Step 2: Investigating issues..." -ForegroundColor Yellow
    Write-Host "Please investigate the following:" -ForegroundColor Cyan
    Write-Host "1. Check CloudWatch logs for errors" -ForegroundColor White
    Write-Host "2. Review application metrics" -ForegroundColor White
    Write-Host "3. Analyze user feedback" -ForegroundColor White
    Write-Host "4. Review system performance" -ForegroundColor White
    
    # Step 3: Plan re-migration
    Write-Host "Step 3: Planning re-migration..." -ForegroundColor Yellow
    Write-Host "After fixing issues, plan the re-migration:" -ForegroundColor Cyan
    Write-Host "1. Fix identified issues" -ForegroundColor White
    Write-Host "2. Re-test the new architecture" -ForegroundColor White
    Write-Host "3. Update migration plan" -ForegroundColor White
    Write-Host "4. Schedule new migration timeline" -ForegroundColor White
    
    Send-Alert "Full rollback completed - investigation and re-migration planning required"
    Write-Host "✅ Full rollback completed" -ForegroundColor Green
    
    exit 0
}

# Show status
if ($Status) {
    Write-Host "`n📊 Rollback Status:" -ForegroundColor Cyan
    
    $oldStatus = Get-EnvironmentStatus $OldEnvName
    $newStatus = Get-EnvironmentStatus $NewEnvName
    
    Write-Host "Old Environment ($OldEnvName):" -ForegroundColor Yellow
    Write-Host "  Status: $($oldStatus.Status)" -ForegroundColor White
    Write-Host "  Health: $($oldStatus.Health)" -ForegroundColor White
    
    Write-Host "`nNew Environment ($NewEnvName):" -ForegroundColor Yellow
    Write-Host "  Status: $($newStatus.Status)" -ForegroundColor White
    Write-Host "  Health: $($newStatus.Health)" -ForegroundColor White
    
    # Check current traffic routing
    try {
        $settings = aws elasticbeanstalk describe-configuration-settings `
            --application-name "shine-skincare-app" `
            --environment-name $OldEnvName `
            --region $Region `
            --query 'ConfigurationSettings[0].OptionSettings[?Namespace==`aws:elasticbeanstalk:application:environment`]' `
            --output json
        
        Write-Host "`n🔧 Current Traffic Routing:" -ForegroundColor Cyan
        $settings | ConvertFrom-Json | ForEach-Object {
            if ($_.OptionName -eq "NEW_ARCHITECTURE_ENABLED" -or $_.OptionName -eq "NEW_ARCHITECTURE_PERCENTAGE") {
                Write-Host "  $($_.OptionName): $($_.Value)" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "⚠️ Could not retrieve current settings" -ForegroundColor Yellow
    }
    
    exit 0
}

# Show usage if no parameters provided
Write-Host "`n🚨 Emergency Rollback Options:" -ForegroundColor Red
Write-Host "  .\rollback-emergency.ps1 -Status" -ForegroundColor White
Write-Host "  .\rollback-emergency.ps1 -Immediate" -ForegroundColor White
Write-Host "  .\rollback-emergency.ps1 -Gradual" -ForegroundColor White
Write-Host "  .\rollback-emergency.ps1 -Full" -ForegroundColor White

Write-Host "`n⏱️ Rollback Types:" -ForegroundColor Cyan
Write-Host "  Immediate (0-1 hour): Instant rollback to old system" -ForegroundColor White
Write-Host "  Gradual (1-24 hours): Step-by-step rollback with monitoring" -ForegroundColor White
Write-Host "  Full (24+ hours): Complete rollback with investigation" -ForegroundColor White

Write-Host "`n⚠️ WARNING: Use emergency rollback only when necessary!" -ForegroundColor Red
Write-Host "This will interrupt the migration process and may affect user experience." -ForegroundColor Yellow 