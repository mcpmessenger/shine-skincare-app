# Google Auth Credentials Update Script for Shine Skincare App
param(
    [string]$Environment = "production",
    [string]$Region = "us-east-2",
    [string]$GoogleClientId = "",
    [string]$GoogleClientSecret = "",
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

# Load environment variables
function Load-Environment {
    if (Test-Path ".env.aws") {
        Write-Info "Loading environment variables from .env.aws..."
        Get-Content ".env.aws" | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
            }
        }
        Write-Success "Environment variables loaded"
    }
    else {
        Write-Error ".env.aws file not found. Please run the main deployment script first."
        exit 1
    }
}

# Get Google Auth credentials interactively
function Get-GoogleCredentials {
    Write-Info "Setting up Google Auth credentials..."
    
    if ($Interactive) {
        Write-Host "`n=== Google OAuth Setup ===" -ForegroundColor $Yellow
        Write-Host "You need to create a Google OAuth 2.0 client in the Google Cloud Console:"
        Write-Host "1. Go to https://console.cloud.google.com/"
        Write-Host "2. Create a new project or select existing one"
        Write-Host "3. Enable Google+ API and Google OAuth2 API"
        Write-Host "4. Go to Credentials > Create Credentials > OAuth 2.0 Client IDs"
        Write-Host "5. Set Application Type to 'Web application'"
        Write-Host "6. Add authorized redirect URIs for your domain"
        Write-Host "`nEnter your Google OAuth credentials:" -ForegroundColor $Yellow
        
        $script:GoogleClientId = Read-Host "Google Client ID"
        $script:GoogleClientSecret = Read-Host "Google Client Secret"
    }
    else {
        if ([string]::IsNullOrEmpty($GoogleClientId) -or [string]::IsNullOrEmpty($GoogleClientSecret)) {
            Write-Error "Google Client ID and Secret must be provided when not in interactive mode"
            exit 1
        }
        $script:GoogleClientId = $GoogleClientId
        $script:GoogleClientSecret = $GoogleClientSecret
    }
}

# Update .env.aws file
function Update-EnvironmentFile {
    Write-Info "Updating .env.aws file with new Google Auth credentials..."
    
    # Read existing content
    $content = Get-Content ".env.aws" -ErrorAction SilentlyContinue
    
    # Create new content with updated Google credentials
    $newContent = @()
    $googleIdUpdated = $false
    $googleSecretUpdated = $false
    
    foreach ($line in $content) {
        if ($line -match "^GOOGLE_CLIENT_ID=") {
            $newContent += "GOOGLE_CLIENT_ID=$GoogleClientId"
            $googleIdUpdated = $true
        }
        elseif ($line -match "^GOOGLE_CLIENT_SECRET=") {
            $newContent += "GOOGLE_CLIENT_SECRET=$GoogleClientSecret"
            $googleSecretUpdated = $true
        }
        else {
            $newContent += $line
        }
    }
    
    # Add if not found
    if (-not $googleIdUpdated) {
        $newContent += "GOOGLE_CLIENT_ID=$GoogleClientId"
    }
    if (-not $googleSecretUpdated) {
        $newContent += "GOOGLE_CLIENT_SECRET=$GoogleClientSecret"
    }
    
    # Write back to file
    $newContent | Out-File -FilePath ".env.aws" -Encoding UTF8
    
    Write-Success "Updated .env.aws with new Google Auth credentials"
}

# Update CloudFormation stack
function Update-CloudFormationStack {
    Write-Info "Updating CloudFormation stack with new Google Auth credentials..."
    
    $StackName = "${Environment}-shine-stack"
    
    # Check if stack exists
    $null = aws cloudformation describe-stacks --stack-name $StackName --region $Region 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Stack $StackName does not exist. Please run the main deployment script first."
        exit 1
    }
    
    # Update the stack
    aws cloudformation update-stack `
        --stack-name $StackName `
        --template-body file://cloudformation-template.yaml `
        --parameters `
            ParameterKey=Environment,ParameterValue="$Environment" `
            ParameterKey=DatabasePassword,ParameterValue="$env:DATABASE_PASSWORD" `
            ParameterKey=GoogleClientId,ParameterValue="$GoogleClientId" `
            ParameterKey=GoogleClientSecret,ParameterValue="$GoogleClientSecret" `
            ParameterKey=StripeSecretKey,ParameterValue="$env:STRIPE_SECRET_KEY" `
            ParameterKey=JwtSecretKey,ParameterValue="$env:JWT_SECRET_KEY" `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $StackName --region $Region
        Write-Success "CloudFormation stack updated successfully"
    }
    else {
        Write-Error "Failed to update CloudFormation stack"
        exit 1
    }
}

# Update ECS service
function Update-ECSService {
    Write-Info "Updating ECS service to use new credentials..."
    
    $ClusterName = "${Environment}-shine-cluster"
    $ServiceName = "${Environment}-shine-api-service"
    
    # Force new deployment
    aws ecs update-service `
        --cluster $ClusterName `
        --service $ServiceName `
        --force-new-deployment `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Waiting for ECS service update to complete..."
        aws ecs wait services-stable `
            --cluster $ClusterName `
            --services $ServiceName `
            --region $Region
        
        Write-Success "ECS service updated successfully"
    }
    else {
        Write-Error "Failed to update ECS service"
        exit 1
    }
}

# Main execution
function Main {
    Write-Host "=== Google Auth Credentials Update ===" -ForegroundColor $Green
    Write-Host "Environment: $Environment" -ForegroundColor $Blue
    Write-Host "Region: $Region" -ForegroundColor $Blue
    
    # Check prerequisites
    Write-Info "Checking prerequisites..."
    
    # Check AWS CLI
    try {
        aws --version | Out-Null
        Write-Success "AWS CLI is installed"
    }
    catch {
        Write-Error "AWS CLI is not installed or not in PATH"
        exit 1
    }
    
    # Check AWS credentials
    try {
        aws sts get-caller-identity | Out-Null
        Write-Success "AWS credentials are configured"
    }
    catch {
        Write-Error "AWS credentials are not configured"
        exit 1
    }
    
    # Load environment
    Load-Environment
    
    # Get Google credentials
    Get-GoogleCredentials
    
    # Update environment file
    Update-EnvironmentFile
    
    # Update CloudFormation stack
    Update-CloudFormationStack
    
    # Update ECS service
    Update-ECSService
    
    Write-Success "Google Auth credentials updated successfully!"
    Write-Host "`nNext steps:" -ForegroundColor $Yellow
    Write-Host "1. Test the authentication flow in your application"
    Write-Host "2. Verify Google OAuth is working correctly"
    Write-Host "3. Check CloudWatch logs for any authentication errors"
    Write-Host "4. Update your frontend application with the new Google Client ID if needed"
}

# Run main function
Main 