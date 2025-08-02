# Shine Skincare App - Traffic Routing Script
# Manages gradual traffic migration between old and new architectures

param(
    [string]$Region = "us-east-1",
    [string]$OldEnvName = "SHINE-env",
    [string]$NewEnvName = "shine-new-staging",
    [int]$NewArchitecturePercentage = 0,
    [switch]$EnableNewArchitecture,
    [switch]$DisableNewArchitecture,
    [switch]$ShowStatus
)

Write-Host "🚦 Traffic Routing Management" -ForegroundColor Green

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

# Function to update environment variables for traffic routing
function Update-TrafficRouting {
    param(
        [int]$Percentage,
        [string]$EnvName
    )
    
    Write-Host "Updating traffic routing to $Percentage% for $EnvName..." -ForegroundColor Yellow
    
    $optionSettings = @(
        "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_ENABLED,Value=true",
        "Namespace=aws:elasticbeanstalk:application:environment,OptionName=NEW_ARCHITECTURE_PERCENTAGE,Value=$Percentage"
    )
    
    try {
        aws elasticbeanstalk update-environment `
            --environment-name $EnvName `
            --region $Region `
            --option-settings $optionSettings
        
        Write-Host "✅ Traffic routing updated successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to update traffic routing: $_" -ForegroundColor Red
    }
}

# Show current status
if ($ShowStatus) {
    Write-Host "`n📊 Current Environment Status:" -ForegroundColor Cyan
    
    $oldStatus = Get-EnvironmentStatus $OldEnvName
    $newStatus = Get-EnvironmentStatus $NewEnvName
    
    Write-Host "Old Environment ($OldEnvName):" -ForegroundColor Yellow
    Write-Host "  Status: $($oldStatus.Status)" -ForegroundColor White
    Write-Host "  Health: $($oldStatus.Health)" -ForegroundColor White
    
    Write-Host "`nNew Environment ($NewEnvName):" -ForegroundColor Yellow
    Write-Host "  Status: $($newStatus.Status)" -ForegroundColor White
    Write-Host "  Health: $($newStatus.Health)" -ForegroundColor White
    
    # Get current traffic routing settings
    try {
        $oldSettings = aws elasticbeanstalk describe-configuration-settings `
            --application-name "shine-skincare-app" `
            --environment-name $OldEnvName `
            --region $Region `
            --query 'ConfigurationSettings[0].OptionSettings[?Namespace==`aws:elasticbeanstalk:application:environment`]' `
            --output json
        
        Write-Host "`n🔧 Current Traffic Routing Settings:" -ForegroundColor Cyan
        $oldSettings | ConvertFrom-Json | ForEach-Object {
            if ($_.OptionName -eq "NEW_ARCHITECTURE_ENABLED" -or $_.OptionName -eq "NEW_ARCHITECTURE_PERCENTAGE") {
                Write-Host "  $($_.OptionName): $($_.Value)" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "⚠️ Could not retrieve current settings" -ForegroundColor Yellow
    }
    
    exit 0
}

# Enable new architecture
if ($EnableNewArchitecture) {
    Write-Host "Enabling new architecture with $NewArchitecturePercentage% traffic..." -ForegroundColor Yellow
    Update-TrafficRouting -Percentage $NewArchitecturePercentage -EnvName $OldEnvName
    exit 0
}

# Disable new architecture
if ($DisableNewArchitecture) {
    Write-Host "Disabling new architecture (rolling back to 0%)..." -ForegroundColor Yellow
    Update-TrafficRouting -Percentage 0 -EnvName $OldEnvName
    exit 0
}

# Gradual rollout based on percentage
if ($NewArchitecturePercentage -gt 0) {
    Write-Host "Setting traffic routing to $NewArchitecturePercentage% for new architecture..." -ForegroundColor Yellow
    
    # Validate percentage
    if ($NewArchitecturePercentage -lt 0 -or $NewArchitecturePercentage -gt 100) {
        Write-Host "❌ Percentage must be between 0 and 100" -ForegroundColor Red
        exit 1
    }
    
    # Check environment health before routing
    $oldStatus = Get-EnvironmentStatus $OldEnvName
    $newStatus = Get-EnvironmentStatus $NewEnvName
    
    if ($newStatus.Health -ne "Ok") {
        Write-Host "❌ New environment is not healthy: $($newStatus.Health)" -ForegroundColor Red
        Write-Host "Please ensure the new environment is healthy before routing traffic" -ForegroundColor Yellow
        exit 1
    }
    
    Update-TrafficRouting -Percentage $NewArchitecturePercentage -EnvName $OldEnvName
    
    Write-Host "`n📈 Migration Progress:" -ForegroundColor Cyan
    switch ($NewArchitecturePercentage) {
        5 { Write-Host "Phase 2: A/B Testing (5% traffic)" -ForegroundColor Green }
        25 { Write-Host "Phase 3: Gradual Rollout (25% traffic)" -ForegroundColor Green }
        75 { Write-Host "Phase 3: Majority Traffic (75% traffic)" -ForegroundColor Green }
        100 { Write-Host "Phase 4: Full Migration (100% traffic)" -ForegroundColor Green }
        default { Write-Host "Custom traffic percentage: $NewArchitecturePercentage%" -ForegroundColor Yellow }
    }
    
    exit 0
}

# Show usage if no parameters provided
Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "  .\traffic-routing.ps1 -ShowStatus" -ForegroundColor White
Write-Host "  .\traffic-routing.ps1 -EnableNewArchitecture -NewArchitecturePercentage 5" -ForegroundColor White
Write-Host "  .\traffic-routing.ps1 -NewArchitecturePercentage 25" -ForegroundColor White
Write-Host "  .\traffic-routing.ps1 -NewArchitecturePercentage 75" -ForegroundColor White
Write-Host "  .\traffic-routing.ps1 -NewArchitecturePercentage 100" -ForegroundColor White
Write-Host "  .\traffic-routing.ps1 -DisableNewArchitecture" -ForegroundColor White

Write-Host "`n🎯 Migration Phases:" -ForegroundColor Cyan
Write-Host "  Phase 2 (A/B Testing): 5% traffic" -ForegroundColor White
Write-Host "  Phase 3 (Gradual): 25% → 75% traffic" -ForegroundColor White
Write-Host "  Phase 4 (Full): 100% traffic" -ForegroundColor White 