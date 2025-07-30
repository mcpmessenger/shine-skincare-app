# Recovery Script for Failed CloudFormation Stack Deployment
param(
    [string]$Environment = "production",
    [string]$Region = "us-east-2"
)

$StackName = "shine-infrastructure"

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

function Get-StackStatus {
    try {
        $Status = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].StackStatus' --output text 2>$null
        return $Status
    }
    catch {
        return $null
    }
}

function Remove-OrphanedResources {
    Write-Info "Checking for orphaned resources..."
    
    # Check if ECS cluster exists
    $ClusterName = "${Environment}-shine-cluster"
    try {
        $ClusterInfo = aws ecs describe-clusters --clusters $ClusterName --region $Region --output json | ConvertFrom-Json
        if ($ClusterInfo.clusters.Count -gt 0 -and $ClusterInfo.clusters[0].status -eq "ACTIVE") {
            Write-Warning "Found orphaned ECS cluster: $ClusterName"
            
            # Check if there are any services or tasks
            $Services = aws ecs list-services --cluster $ClusterName --region $Region --output json | ConvertFrom-Json
            if ($Services.serviceArns.Count -gt 0) {
                Write-Warning "Cluster has active services. Please delete them manually first."
                return $false
            }
            
            # Try to delete the cluster
            Write-Info "Attempting to delete orphaned ECS cluster..."
            aws ecs delete-cluster --cluster $ClusterName --region $Region
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Orphaned ECS cluster deleted successfully"
            }
            else {
                Write-Warning "Could not delete ECS cluster. You may need to delete it manually from AWS Console."
                Write-Info "Continuing with stack recovery..."
            }
        }
    }
    catch {
        Write-Info "No orphaned ECS cluster found"
    }
    
    return $true
}

function Force-DeleteStack {
    Write-Info "Attempting to force delete the failed stack..."
    
    # Try to continue deletion of the stack
    aws cloudformation continue-update-rollback --stack-name $StackName --region $Region
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Initiated stack rollback continuation..."
        
        # Wait for rollback to complete
        Write-Info "Waiting for rollback to complete..."
        aws cloudformation wait stack-rollback-complete --stack-name $StackName --region $Region
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Stack rollback completed"
            return $true
        }
    }
    
    # If continue-update-rollback doesn't work, try deleting with retain resources
    Write-Info "Attempting to delete stack with resource retention..."
    
    # Get the resources that failed to delete
    $FailedResources = aws cloudformation describe-stack-resources --stack-name $StackName --region $Region --query 'StackResources[?ResourceStatus==`DELETE_FAILED`].LogicalResourceId' --output text
    
    if ($FailedResources) {
        Write-Warning "The following resources failed to delete and will be retained:"
        Write-Host $FailedResources -ForegroundColor Yellow
        
        # Delete stack but retain problematic resources
        $ResourcesArray = $FailedResources -split "`t"
        $RetainResourcesParam = ""
        foreach ($Resource in $ResourcesArray) {
            if ($Resource.Trim()) {
                $RetainResourcesParam += " --retain-resources $($Resource.Trim())"
            }
        }
        
        $DeleteCommand = "aws cloudformation delete-stack --stack-name $StackName --region $Region$RetainResourcesParam"
        Write-Info "Executing: $DeleteCommand"
        Invoke-Expression $DeleteCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Waiting for stack deletion to complete..."
            aws cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Stack deleted successfully (with retained resources)"
                return $true
            }
        }
    }
    
    return $false
}

function Main {
    Write-Info "Starting CloudFormation stack recovery..."
    Write-Info "Stack Name: $StackName"
    Write-Info "Region: $Region"
    
    # Check current stack status
    $CurrentStatus = Get-StackStatus
    Write-Info "Current stack status: $CurrentStatus"
    
    if ($CurrentStatus -eq "DELETE_FAILED") {
        Write-Warning "Stack is in DELETE_FAILED state. Attempting recovery..."
        
        # Try to remove orphaned resources first
        $CanProceed = Remove-OrphanedResources
        if (-not $CanProceed) {
            Write-Error "Cannot proceed due to active resources. Please clean up manually."
            exit 1
        }
        
        # Try to force delete the stack
        $DeleteSuccess = Force-DeleteStack
        if (-not $DeleteSuccess) {
            Write-Error "Could not delete the failed stack. Manual intervention required."
            Write-Info "Please delete the stack manually from AWS Console and retry deployment."
            exit 1
        }
        
        Write-Success "Stack cleanup completed!"
    }
    elseif ($CurrentStatus) {
        Write-Info "Stack exists with status: $CurrentStatus"
        if ($CurrentStatus -ne "CREATE_COMPLETE" -and $CurrentStatus -ne "UPDATE_COMPLETE") {
            Write-Warning "Stack is not in a stable state. Consider manual cleanup."
        }
    }
    else {
        Write-Info "No existing stack found. Ready for fresh deployment."
    }
    
    # Now run the deployment
    Write-Info "Starting fresh deployment..."
    Write-Info "Running deploy-simple.ps1..."
    
    .\deploy-simple.ps1 -Environment $Environment -Region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Deployment completed successfully!"
        Write-Info "You can now use the ECS service update script:"
        Write-Info "  .\update-ecs-service.ps1 -BuildImage"
    }
    else {
        Write-Error "Deployment failed. Check the output above for details."
    }
}

# Run main function
Main 