# Register ECS task definition
Write-Host "[INFO] Registering ECS task definition..."

$Region = "us-east-1"
$ClusterName = "production-shine-cluster"

# Register task definition
Write-Host "[INFO] Registering task definition..."
$TaskDefinitionArn = aws ecs register-task-definition --cli-input-json file://task-definition.json --region $Region --query 'taskDefinition.taskDefinitionArn' --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Task definition registered: $TaskDefinitionArn"
    
    # Get subnet and security group from existing VPC
    Write-Host "[INFO] Getting network configuration..."
    $VPCs = aws ec2 describe-vpcs --filters "Name=tag:Name,Values=*shine*" --region $Region --query 'Vpcs[0]' | ConvertFrom-Json
    
    if ($VPCs) {
        $VPCId = $VPCs.VpcId
        $Subnets = aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPCId" --region $Region --query 'Subnets[0]' | ConvertFrom-Json
        $SecurityGroups = aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPCId" "Name=group-name,Values=*shine*" --region $Region --query 'SecurityGroups[0]' | ConvertFrom-Json
        
        if ($Subnets -and $SecurityGroups) {
            $SubnetId = $Subnets.SubnetId
            $SecurityGroupId = $SecurityGroups.GroupId
            
            Write-Host "[INFO] Using Subnet: $SubnetId"
            Write-Host "[INFO] Using Security Group: $SecurityGroupId"
            
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
            }
        } else {
            Write-Host "[ERROR] Could not find subnet or security group"
        }
    } else {
        Write-Host "[ERROR] Could not find VPC"
    }
} else {
    Write-Host "[ERROR] Failed to register task definition"
    exit 1
} 