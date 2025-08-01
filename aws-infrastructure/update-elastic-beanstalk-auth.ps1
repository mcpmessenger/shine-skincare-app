# Elastic Beanstalk Google Auth Update Script
param(
    [string]$EnvironmentName = "SHINE-env",
    [string]$Region = "us-east-1",
    [string]$GoogleClientId = "",
    [string]$GoogleClientSecret = "",
    [string]$OpenAIKey = "",
    [switch]$Interactive = $true
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Get credentials interactively
function Get-Credentials {
    Write-Info "Setting up Google OAuth credentials for Elastic Beanstalk..."
    
    if ($Interactive) {
        Write-Host "`n=== Google OAuth Setup ===" -ForegroundColor $Yellow
        Write-Host "Your Google OAuth Client ID: 315103925773-b4fg266mo0kmp18uik6urupf8nu1ilbf.apps.googleusercontent.com"
        Write-Host "Your Elastic Beanstalk URL: http://shine-env.eba-azwgu4dc.us-east-1.elasticbeanstalk.com/"
        Write-Host "`nEnter your credentials:" -ForegroundColor $Yellow
        
        $script:GoogleClientId = Read-Host "Google Client ID (or press Enter to use default)"
        if ([string]::IsNullOrEmpty($GoogleClientId)) {
            $script:GoogleClientId = "315103925773-b4fg266mo0kmp18uik6urupf8nu1ilbf.apps.googleusercontent.com"
        }
        
        $script:GoogleClientSecret = Read-Host "Google Client Secret"
        $script:OpenAIKey = Read-Host "OpenAI API Key (optional)"
    }
    else {
        if ([string]::IsNullOrEmpty($GoogleClientId)) {
            $script:GoogleClientId = "315103925773-b4fg266mo0kmp18uik6urupf8nu1ilbf.apps.googleusercontent.com"
        }
        $script:GoogleClientSecret = $GoogleClientSecret
        $script:OpenAIKey = $OpenAIKey
    }
}

# Check AWS CLI
function Test-AWSCLI {
    Write-Info "Checking AWS CLI..."
    
    try {
        aws --version | Out-Null
        Write-Success "AWS CLI is installed"
    }
    catch {
        Write-Error "AWS CLI is not installed or not in PATH"
        exit 1
    }
    
    try {
        aws sts get-caller-identity | Out-Null
        Write-Success "AWS credentials are configured"
    }
    catch {
        Write-Error "AWS credentials are not configured"
        exit 1
    }
}

# Check Elastic Beanstalk environment
function Test-Environment {
    Write-Info "Checking Elastic Beanstalk environment..."
    
    $envInfo = aws elasticbeanstalk describe-environments `
        --environment-names $EnvironmentName `
        --region $Region `
        --output json | ConvertFrom-Json
    
    if ($envInfo.Environments.Count -eq 0) {
        Write-Error "Environment '$EnvironmentName' not found"
        exit 1
    }
    
    $environment = $envInfo.Environments[0]
    Write-Success "Environment found: $($environment.EnvironmentName)"
    Write-Info "Status: $($environment.Status)"
    Write-Info "Health: $($environment.Health)"
    Write-Info "URL: $($environment.CNAME)"
    
    if ($environment.Status -ne "Ready") {
        Write-Warning "Environment is not ready. Status: $($environment.Status)"
    }
}

# Update environment variables
function Update-EnvironmentVariables {
    Write-Info "Updating Elastic Beanstalk environment variables..."
    
    $optionSettings = @(
        "Namespace=aws:elasticbeanstalk:application:environment,OptionName=GOOGLE_CLIENT_ID,Value=$GoogleClientId",
        "Namespace=aws:elasticbeanstalk:application:environment,OptionName=GOOGLE_CLIENT_SECRET,Value=$GoogleClientSecret"
    )
    
    # Add OpenAI key if provided
    if (-not [string]::IsNullOrEmpty($OpenAIKey)) {
        $optionSettings += "Namespace=aws:elasticbeanstalk:application:environment,OptionName=OPENAI_API_KEY,Value=$OpenAIKey"
    }
    
    # Build the command
    $command = "aws elasticbeanstalk update-environment " +
               "--environment-name $EnvironmentName " +
               "--region $Region " +
               "--option-settings " + ($optionSettings -join " ")
    
    Write-Info "Executing: $command"
    
    # Execute the command
    $result = Invoke-Expression $command
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Environment update initiated successfully"
        Write-Info "Waiting for update to complete..."
        
        # Wait for update to complete
        aws elasticbeanstalk wait environment-updated `
            --environment-names $EnvironmentName `
            --region $Region
        
        Write-Success "Environment update completed successfully"
    }
    else {
        Write-Error "Failed to update environment"
        exit 1
    }
}

# Verify the update
function Verify-Update {
    Write-Info "Verifying environment variables..."
    
    # Get the updated environment info
    $envInfo = aws elasticbeanstalk describe-environments `
        --environment-names $EnvironmentName `
        --region $Region `
        --output json | ConvertFrom-Json
    
    $environment = $envInfo.Environments[0]
    Write-Success "Environment is ready: $($environment.Status)"
    
    Write-Host "`n=== Verification Complete ===" -ForegroundColor $Green
    Write-Host "Environment: $EnvironmentName" -ForegroundColor $Blue
    Write-Host "Status: $($environment.Status)" -ForegroundColor $Blue
    Write-Host "Health: $($environment.Health)" -ForegroundColor $Blue
    Write-Host "URL: $($environment.CNAME)" -ForegroundColor $Blue
    
    Write-Host "`nNext steps:" -ForegroundColor $Yellow
    Write-Host "1. Test Google OAuth login at: http://$($environment.CNAME)/" -ForegroundColor $Blue
    Write-Host "2. Try the enhanced skin analysis feature" -ForegroundColor $Blue
    Write-Host "3. Check application logs if needed: eb logs" -ForegroundColor $Blue
}

# Main execution
function Main {
    Write-Host "=== Elastic Beanstalk Google Auth Update ===" -ForegroundColor $Green
    Write-Host "Environment: $EnvironmentName" -ForegroundColor $Blue
    Write-Host "Region: $Region" -ForegroundColor $Blue
    
    # Check prerequisites
    Test-AWSCLI
    
    # Get credentials
    Get-Credentials
    
    # Check environment
    Test-Environment
    
    # Update environment
    Update-EnvironmentVariables
    
    # Verify update
    Verify-Update
    
    Write-Success "Google Auth credentials updated successfully!"
}

# Run main function
Main 