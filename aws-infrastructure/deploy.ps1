# Shine Skincare App - AWS Infrastructure Deployment Script (PowerShell)
# This script deploys the complete infrastructure using AWS CLI

param(
    [string]$Environment = "production",
    [string]$Region = "us-east-2"
)

# Configuration
$StackName = "shine-infrastructure"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Logging functions
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

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check AWS CLI
    try {
        $null = Get-Command aws -ErrorAction Stop
    }
    catch {
        Write-Error "AWS CLI is not installed. Please install it first."
        exit 1
    }
    
    # Check AWS credentials
    try {
        $null = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "AWS credentials not configured"
        }
    }
    catch {
        Write-Error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    }
    
    # Check if template file exists
    if (-not (Test-Path "cloudformation-template.yaml")) {
        Write-Error "CloudFormation template not found: cloudformation-template.yaml"
        exit 1
    }
    
    Write-Success "Prerequisites check passed"
}

# Generate secure passwords and keys
function New-Secrets {
    Write-Info "Generating secure secrets..."
    
    # Generate database password
    $DbPassword = -join ((33..126) | Get-Random -Count 25 | ForEach-Object {[char]$_})
    
    # Generate JWT secret
    $JwtSecret = -join ((33..126) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    
    # Save secrets to file
    @"
# AWS Infrastructure Secrets (Generated)
# Keep this file secure and do not commit to version control

DATABASE_PASSWORD=$DbPassword
JWT_SECRET_KEY=$JwtSecret
ENVIRONMENT=$Environment
REGION=$Region
STACK_NAME=$StackName

# You need to manually add these:
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret
# STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
"@ | Out-File -FilePath ".env.aws" -Encoding UTF8
    
    Write-Success "Secrets generated and saved to .env.aws"
    Write-Warning "Please add your Google OAuth and Stripe credentials to .env.aws"
}

# Load environment variables
function Load-Environment {
    if (Test-Path ".env.aws") {
        Write-Info "Loading environment variables..."
        Get-Content ".env.aws" | ForEach-Object {
            if ($_ -match '^([^#][^=]+)=(.*)$') {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
    }
    else {
        Write-Error ".env.aws file not found. Please run the script first to generate secrets."
        exit 1
    }
}

# Create S3 bucket for CloudFormation artifacts
function New-S3Bucket {
    Write-Info "Creating S3 bucket for CloudFormation artifacts..."
    
    $AccountId = aws sts get-caller-identity --query Account --output text
    $BucketName = "shine-cf-artifacts-$AccountId-$Region"
    
    # Check if bucket exists
    $null = aws s3 ls "s3://$BucketName" 2>$null
    if ($LASTEXITCODE -ne 0) {
        aws s3 mb "s3://$BucketName" --region $Region
        aws s3api put-bucket-versioning --bucket "$BucketName" --versioning-configuration Status=Enabled --region $Region
        Write-Success "S3 bucket created: $BucketName"
    }
    else {
        Write-Info "S3 bucket already exists: $BucketName"
    }
    
    $script:CfBucket = $BucketName
}

# Deploy CloudFormation stack
function Deploy-Stack {
    Write-Info "Deploying CloudFormation stack..."
    
    # Check if stack exists
    $null = aws cloudformation describe-stacks --stack-name $StackName --region $Region 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Stack exists, updating..."
        $Operation = "update-stack"
    }
    else {
        Write-Info "Stack does not exist, creating..."
        $Operation = "create-stack"
    }
    
    # Deploy the stack
    aws cloudformation $Operation `
        --stack-name $StackName `
        --template-body file://cloudformation-template.yaml `
        --parameters `
            ParameterKey=Environment,ParameterValue="$Environment" `
            ParameterKey=DatabasePassword,ParameterValue="$env:DATABASE_PASSWORD" `
            ParameterKey=GoogleClientId,ParameterValue="$env:GOOGLE_CLIENT_ID" `
            ParameterKey=GoogleClientSecret,ParameterValue="$env:GOOGLE_CLIENT_SECRET" `
            ParameterKey=StripeSecretKey,ParameterValue="$env:STRIPE_SECRET_KEY" `
            ParameterKey=JwtSecretKey,ParameterValue="$env:JWT_SECRET_KEY" `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $Region
    
    # Wait for stack completion
    Write-Info "Waiting for stack operation to complete..."
    if ($Operation -eq "create-stack") {
        aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region
    }
    else {
        aws cloudformation wait stack-update-complete --stack-name $StackName --region $Region
    }
    
    Write-Success "Stack deployment completed successfully"
}

# Get stack outputs
function Get-StackOutputs {
    Write-Info "Getting stack outputs..."
    
    aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query 'Stacks[0].Outputs' `
        --output table
    
    # Save outputs to file
    aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query 'Stacks[0].Outputs' `
        --output json | Out-File -FilePath "stack-outputs.json" -Encoding UTF8
    
    Write-Success "Stack outputs saved to stack-outputs.json"
}

# Create ECR repository
function New-ECRRepository {
    Write-Info "Creating ECR repository for API..."
    
    $RepoName = "shine-api"
    
    $null = aws ecr describe-repositories --repository-names $RepoName --region $Region 2>$null
    if ($LASTEXITCODE -ne 0) {
        aws ecr create-repository `
            --repository-name $RepoName `
            --region $Region `
            --image-scanning-configuration scanOnPush=true `
            --encryption-configuration encryptionType=AES256
        
        Write-Success "ECR repository created: $RepoName"
    }
    else {
        Write-Info "ECR repository already exists: $RepoName"
    }
    
    # Get repository URI
    $RepoUri = aws ecr describe-repositories --repository-names $RepoName --region $Region --query 'repositories[0].repositoryUri' --output text
    Add-Content -Path ".env.aws" -Value "ECR_REPOSITORY_URI=$RepoUri"
    
    Write-Success "ECR repository URI: $RepoUri"
}

# Setup database
function Setup-Database {
    Write-Info "Setting up database..."
    
    # Get database endpoint from stack outputs
    $DbEndpoint = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $Region `
        --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' `
        --output text
    
    # Wait for database to be available
    Write-Info "Waiting for database to be available..."
    aws rds wait db-instance-available `
        --db-instance-identifier "${Environment}-shine-db" `
        --region $Region
    
    Write-Success "Database is ready: $DbEndpoint"
}

# Build and push Docker image
function Build-AndPushImage {
    Write-Info "Building and pushing Docker image..."
    
    # Load environment variables to get ECR URI
    if (Test-Path ".env.aws") {
        Get-Content ".env.aws" | ForEach-Object {
            if ($_ -match "^([^=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
            }
        }
    }
    
    $EcrRepositoryUri = $env:ECR_REPOSITORY_URI
    if (-not $EcrRepositoryUri) {
        Write-Error "ECR_REPOSITORY_URI not found in .env.aws"
        return
    }
    
    # Get ECR login token
    $LoginPassword = aws ecr get-login-password --region $Region
    if ($LASTEXITCODE -eq 0) {
        $LoginPassword | docker login --username AWS --password-stdin $EcrRepositoryUri
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Building Docker image..."
        docker build -t shine-api:latest ../backend/
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Tagging image..."
        docker tag shine-api:latest "${EcrRepositoryUri}:latest"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Pushing image to ECR..."
        docker push "${EcrRepositoryUri}:latest"
        Write-Success "Docker image pushed successfully"
    }
    else {
        Write-Error "Failed to build or push Docker image"
    }
}

# Update ECS service
function Update-ECSService {
    Write-Info "Updating ECS service..."
    
    $ClusterName = "${Environment}-shine-cluster"
    $ServiceName = "${Environment}-shine-api-service"
    
    # Force new deployment
    aws ecs update-service `
        --cluster $ClusterName `
        --service $ServiceName `
        --force-new-deployment `
        --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ECS service update initiated"
        
        # Wait for deployment to complete
        Write-Info "Waiting for service deployment to complete..."
        aws ecs wait services-stable `
            --cluster $ClusterName `
            --services $ServiceName `
            --region $Region
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "ECS service updated successfully"
        }
        else {
            Write-Warning "Service update initiated but may still be in progress"
        }
    }
    else {
        Write-Error "Failed to update ECS service"
    }
}

# Check ECS service status
function Get-ECSServiceStatus {
    Write-Info "Checking ECS service status..."
    
    $ClusterName = "${Environment}-shine-cluster"
    $ServiceName = "${Environment}-shine-api-service"
    
    aws ecs describe-services `
        --cluster $ClusterName `
        --services $ServiceName `
        --region $Region `
        --query 'services[0].{ServiceName:serviceName,Status:status,RunningCount:runningCount,PendingCount:pendingCount,DesiredCount:desiredCount}' `
        --output table
}

# Main deployment function
function Start-Deployment {
    Write-Info "Starting Shine Skincare App deployment..."
    Write-Info "Environment: $Environment"
    Write-Info "Region: $Region"
    Write-Info "Stack Name: $StackName"
    
    # Check prerequisites
    Test-Prerequisites
    
    # Generate secrets (only if .env.aws doesn't exist)
    if (-not (Test-Path ".env.aws")) {
        New-Secrets
        Write-Warning "Please edit .env.aws to add your Google OAuth and Stripe credentials, then run this script again."
        exit 0
    }
    
    # Load environment variables
    Load-Environment
    
    # Create S3 bucket
    New-S3Bucket
    
    # Deploy CloudFormation stack
    Deploy-Stack
    
    # Get stack outputs
    Get-StackOutputs
    
    # Create ECR repository
    New-ECRRepository
    
    # Setup database
    Setup-Database
    
    # Build and push Docker image
    Build-AndPushImage
    
    # Update ECS service
    Update-ECSService
    
    Write-Success "Deployment completed successfully!"
    Write-Info "Check stack-outputs.json for all the URLs and endpoints"
    
    # Show service status
    Get-ECSServiceStatus
}

# Run main deployment function
Start-Deployment 