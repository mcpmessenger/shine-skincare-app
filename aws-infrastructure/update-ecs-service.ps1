# ECS Service Update Script for Shine Skincare App
param(
    [string]$Environment = "production",
    [string]$Region = "us-east-2",
    [switch]$BuildImage = $false,
    [switch]$SkipWait = $false
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

# Check prerequisites
function Test-Prerequisites {
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
    
    # Check Docker (only if building image)
    if ($BuildImage) {
        try {
            docker --version | Out-Null
            Write-Success "Docker is installed"
        }
        catch {
            Write-Error "Docker is not installed or not in PATH"
            exit 1
        }
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
}

# Get current service status
function Get-ServiceStatus {
    param([string]$ClusterName, [string]$ServiceName)
    
    Write-Info "Getting current service status..."
    
    $ServiceInfo = aws ecs describe-services `
        --cluster $ClusterName `
        --services $ServiceName `
        --region $Region `
        --output json | ConvertFrom-Json
    
    if ($ServiceInfo.services.Count -gt 0) {
        $Service = $ServiceInfo.services[0]
        Write-Info "Service Status: $($Service.status)"
        Write-Info "Desired Count: $($Service.desiredCount)"
        Write-Info "Running Count: $($Service.runningCount)"
        Write-Info "Pending Count: $($Service.pendingCount)"
        
        if ($Service.deployments) {
            Write-Info "Current Deployments:"
            foreach ($deployment in $Service.deployments) {
                Write-Info "  - Status: $($deployment.status), Created: $($deployment.createdAt)"
            }
        }
        
        return $Service
    }
    else {
        Write-Error "Service not found"
        return $null
    }
}

# Build and push Docker image
function Build-AndPushImage {
    Write-Info "Building and pushing Docker image..."
    
    $EcrRepositoryUri = $env:ECR_REPOSITORY_URI
    if (-not $EcrRepositoryUri) {
        Write-Error "ECR_REPOSITORY_URI not found in environment variables"
        return $false
    }
    
    Write-Info "ECR Repository: $EcrRepositoryUri"
    
    # Get ECR login token
    Write-Info "Logging in to ECR..."
    $LoginPassword = aws ecr get-login-password --region $Region
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to get ECR login password"
        return $false
    }
    
    $LoginPassword | docker login --username AWS --password-stdin $EcrRepositoryUri
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to login to ECR"
        return $false
    }
    
    # Build image
    Write-Info "Building Docker image..."
    docker build -t shine-api:latest ../backend/
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build Docker image"
        return $false
    }
    
    # Tag image
    Write-Info "Tagging image..."
    docker tag shine-api:latest "${EcrRepositoryUri}:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to tag Docker image"
        return $false
    }
    
    # Push image
    Write-Info "Pushing image to ECR..."
    docker push "${EcrRepositoryUri}:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to push Docker image"
        return $false
    }
    
    Write-Success "Docker image built and pushed successfully"
    return $true
}

# Update ECS service
function Update-ECSService {
    param([string]$ClusterName, [string]$ServiceName)
    
    Write-Info "Updating ECS service..."
    
    # Force new deployment
    aws ecs update-service `
        --cluster $ClusterName `
        --service $ServiceName `
        --force-new-deployment `
        --region $Region
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to update ECS service"
        return $false
    }
    
    Write-Success "ECS service update initiated"
    
    if (-not $SkipWait) {
        # Wait for deployment to complete
        Write-Info "Waiting for service deployment to complete..."
        Write-Info "This may take several minutes..."
        
        aws ecs wait services-stable `
            --cluster $ClusterName `
            --services $ServiceName `
            --region $Region
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "ECS service deployment completed successfully"
        }
        else {
            Write-Warning "Service deployment may still be in progress or failed"
            Write-Info "Check the AWS Console for detailed status"
        }
    }
    
    return $true
}

# Get service logs
function Get-ServiceLogs {
    param([string]$LogGroupName)
    
    Write-Info "Getting recent service logs..."
    
    aws logs filter-log-events `
        --log-group-name $LogGroupName `
        --start-time $([DateTimeOffset]::Now.AddMinutes(-10).ToUnixTimeMilliseconds()) `
        --region $Region `
        --query 'events[*].{Timestamp:timestamp,Message:message}' `
        --output table
}

# Main execution
function Main {
    Write-Info "Starting ECS Service Update..."
    Write-Info "Environment: $Environment"
    Write-Info "Region: $Region"
    Write-Info "Build Image: $BuildImage"
    Write-Info "Skip Wait: $SkipWait"
    
    # Check prerequisites
    Test-Prerequisites
    
    # Load environment variables
    Load-Environment
    
    $ClusterName = "${Environment}-shine-cluster"
    $ServiceName = "${Environment}-shine-api-service"
    $LogGroupName = "/ecs/${Environment}-shine-api"
    
    Write-Info "Cluster: $ClusterName"
    Write-Info "Service: $ServiceName"
    
    # Get current service status
    $CurrentService = Get-ServiceStatus -ClusterName $ClusterName -ServiceName $ServiceName
    if (-not $CurrentService) {
        Write-Error "Cannot proceed without valid service"
        exit 1
    }
    
    # Build and push image if requested
    if ($BuildImage) {
        $BuildSuccess = Build-AndPushImage
        if (-not $BuildSuccess) {
            Write-Error "Failed to build and push image"
            exit 1
        }
    }
    else {
        Write-Info "Skipping image build (use -BuildImage to build and push new image)"
    }
    
    # Update ECS service
    $UpdateSuccess = Update-ECSService -ClusterName $ClusterName -ServiceName $ServiceName
    if (-not $UpdateSuccess) {
        Write-Error "Failed to update ECS service"
        exit 1
    }
    
    # Get final service status
    Write-Info "Final service status:"
    Get-ServiceStatus -ClusterName $ClusterName -ServiceName $ServiceName | Out-Null
    
    # Show recent logs
    Get-ServiceLogs -LogGroupName $LogGroupName
    
    Write-Success "ECS service update completed!"
    Write-Info "You can monitor the service in the AWS Console:"
    Write-Info "https://console.aws.amazon.com/ecs/home?region=${Region}#/clusters/${ClusterName}/services/${ServiceName}/details"
}

# Run main function
Main 