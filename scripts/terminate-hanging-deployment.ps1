#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Terminate hanging Elastic Beanstalk deployment
    
.DESCRIPTION
    Clean up hanging deployment and prepare for fresh deployment
    
.EXAMPLE
    .\terminate-hanging-deployment.ps1
#>

Write-Host "Terminating Hanging Elastic Beanstalk Deployment" -ForegroundColor Red

# Set region
aws configure set region us-east-1

$EnvironmentName = "shine-backend-final"

Write-Host "`nChecking current deployment status..." -ForegroundColor Cyan

try {
    $envInfo = aws elasticbeanstalk describe-environments --environment-names $EnvironmentName --region us-east-1 --output json | ConvertFrom-Json
    if ($envInfo.Environments.Count -gt 0) {
        $env = $envInfo.Environments[0]
        Write-Host "Environment Status: $($env.Status)" -ForegroundColor White
        Write-Host "Environment Health: $($env.Health)" -ForegroundColor White
        
        if ($env.Status -eq "Updating") {
            Write-Host "Environment is currently updating (hanging). Terminating..." -ForegroundColor Yellow
            
            # Terminate the environment
            Write-Host "Terminating environment..." -ForegroundColor Red
            aws elasticbeanstalk terminate-environment --environment-name $EnvironmentName --region us-east-1
            
            Write-Host "Waiting for termination to complete..." -ForegroundColor Cyan
            do {
                Start-Sleep -Seconds 30
                try {
                    $envInfo = aws elasticbeanstalk describe-environments --environment-names $EnvironmentName --region us-east-1 --output json | ConvertFrom-Json
                    if ($envInfo.Environments.Count -gt 0) {
                        $env = $envInfo.Environments[0]
                        Write-Host "Status: $($env.Status)" -ForegroundColor White
                    } else {
                        Write-Host "Environment terminated" -ForegroundColor Green
                        break
                    }
                } catch {
                    Write-Host "Environment terminated" -ForegroundColor Green
                    break
                }
            } while ($true)
            
            Write-Host "Environment terminated successfully" -ForegroundColor Green
        } else {
            Write-Host "Environment is not updating. Status: $($env.Status)" -ForegroundColor White
        }
    } else {
        Write-Host "Environment not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error checking environment: $($_.Exception.Message)" -ForegroundColor Red
}

# Clean up any orphaned resources
Write-Host "`nCleaning up orphaned resources..." -ForegroundColor Cyan

try {
    # List and clean up any orphaned Auto Scaling Groups
    $asgGroups = aws autoscaling describe-auto-scaling-groups --region us-east-1 --output json | ConvertFrom-Json
    foreach ($group in $asgGroups.AutoScalingGroups) {
        if ($group.AutoScalingGroupName -like "*awseb*" -and $group.AutoScalingGroupName -like "*immutable*") {
            Write-Host "Found orphaned ASG: $($group.AutoScalingGroupName)" -ForegroundColor Yellow
            Write-Host "Terminating orphaned ASG..." -ForegroundColor Red
            aws autoscaling delete-auto-scaling-group --auto-scaling-group-name $group.AutoScalingGroupName --force-delete --region us-east-1
        }
    }
} catch {
    Write-Host "Error cleaning up ASG groups: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Wait a bit before allowing new deployment
Write-Host "`nWaiting 60 seconds before allowing new deployment..." -ForegroundColor Cyan
Start-Sleep -Seconds 60

Write-Host "`nCleanup completed!" -ForegroundColor Green
Write-Host "You can now run a fresh deployment with:" -ForegroundColor White
Write-Host ".\aws-infrastructure\deploy-optimized.ps1" -ForegroundColor Cyan 