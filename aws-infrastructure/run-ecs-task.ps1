# Run ECS task manually
Write-Host "[INFO] Running ECS task manually..."

$Region = "us-east-1"
$ClusterName = "production-shine-cluster"
$TaskDefinition = "production-shine-api"
$SubnetId = "subnet-0943dabcd371adbd4"  # We'll get this from existing resources
$SecurityGroupId = "sg-0a89289aa0a834001"  # We'll get this from existing resources

# Get the latest task definition revision
Write-Host "[INFO] Getting latest task definition..."
$TaskDefinitionArn = aws ecs describe-task-definition --task-definition $TaskDefinition --region $Region --query 'taskDefinition.taskDefinitionArn' --output text

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to get task definition"
    exit 1
}

Write-Host "[INFO] Task Definition ARN: $TaskDefinitionArn"

# Run the task
Write-Host "[INFO] Running ECS task..."
$TaskArn = aws ecs run-task `
    --cluster $ClusterName `
    --task-definition $TaskDefinitionArn `
    --launch-type FARGATE `
    --network-configuration "awsvpcConfiguration={subnets=[$SubnetId],securityGroups=[$SecurityGroupId],assignPublicIp=ENABLED}" `
    --region $Region `
    --query 'tasks[0].taskArn' `
    --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Task started: $TaskArn"
    Write-Host "[INFO] Waiting for task to be running..."
    
    # Wait for task to be running
    aws ecs wait tasks-running --cluster $ClusterName --tasks $TaskArn --region $Region
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Task is running!"
        
        # Get task details to find the public IP
        $TaskDetails = aws ecs describe-tasks --cluster $ClusterName --tasks $TaskArn --region $Region | ConvertFrom-Json
        $PublicIP = $TaskDetails.tasks[0].attachments[0].details | Where-Object { $_.name -eq "publicIPv4Address" } | Select-Object -ExpandProperty value
        
        if ($PublicIP) {
            Write-Host "[SUCCESS] Your API is available at: http://$PublicIP`:5000"
            Write-Host "[INFO] Health check: http://$PublicIP`:5000/api/health"
        } else {
            Write-Host "[INFO] Task is running but public IP not available yet"
        }
    } else {
        Write-Host "[ERROR] Task failed to start"
    }
} else {
    Write-Host "[ERROR] Failed to start task"
    exit 1
} 