# Check Current Status - Run this to see what's happening
Write-Host "🔍 Checking Current ECS Service Status..." -ForegroundColor Green

Write-Host "`n📋 Service Status:" -ForegroundColor Yellow
aws ecs describe-services --cluster shine-ml-cluster --services shine-api-gateway --region us-east-1 --query 'services[0].{ServiceName:serviceName,Status:status,TaskDefinition:taskDefinition,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount}' --output table

Write-Host "`n📋 Current Tasks:" -ForegroundColor Yellow
aws ecs list-tasks --cluster shine-ml-cluster --service-name shine-api-gateway --region us-east-1 --query 'taskArns' --output table

Write-Host "`n📋 Task Details:" -ForegroundColor Yellow
$TASKS = aws ecs list-tasks --cluster shine-ml-cluster --service-name shine-api-gateway --region us-east-1 --query 'taskArns' --output text
if ($TASKS) {
    aws ecs describe-tasks --cluster shine-ml-cluster --tasks $TASKS --region us-east-1 --query 'tasks[0].{TaskArn:taskArn,LastStatus:lastStatus,HealthStatus:healthStatus,TaskDefinitionArn:taskDefinitionArn}' --output table
}

Write-Host "`n🎯 Target Group Health:" -ForegroundColor Yellow
$TARGET_GROUP_ARN = aws ecs describe-services --cluster shine-ml-cluster --services shine-api-gateway --region us-east-1 --query 'services[0].loadBalancers[0].targetGroupArn' --output text
if ($TARGET_GROUP_ARN) {
    aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN --region us-east-1 --query 'TargetHealthDescriptions[0].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State,Description:TargetHealth.Description}' --output table
}
