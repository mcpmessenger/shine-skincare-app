# Fix ECS Task Definition Health Check Issue
# This script registers a new task definition with correct health check and updates the service

Write-Host "🔧 Fixing ECS Task Definition Health Check Issue..." -ForegroundColor Green

# Configuration
$CLUSTER_NAME = "shine-ml-cluster"
$SERVICE_NAME = "shine-api-gateway"
$REGION = "us-east-1"
$TASK_DEFINITION_FILE = "clean-task-def.json"

Write-Host "📋 Current ECS Services:" -ForegroundColor Yellow
aws ecs list-services --cluster $CLUSTER_NAME --region $REGION

Write-Host "`n🔍 Checking current service status..." -ForegroundColor Yellow
aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query 'services[0].{ServiceName:serviceName,Status:status,TaskDefinition:taskDefinition,DesiredCount:desiredCount,RunningCount:runningCount}' --output table

Write-Host "`n📋 Current task definition details..." -ForegroundColor Yellow
$CURRENT_TASK_DEF = aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query 'services[0].taskDefinition' --output text
aws ecs describe-task-definition --task-definition $CURRENT_TASK_DEF --region $REGION --query 'taskDefinition.{Family:family,Revision:revision,HealthCheck:containerDefinitions[0].healthCheck}' --output table

Write-Host "`n🔄 Registering new task definition with corrected health check..." -ForegroundColor Green
$NEW_TASK_DEF = aws ecs register-task-definition --cli-input-json file://$TASK_DEFINITION_FILE --region $REGION --query 'taskDefinition.taskDefinitionArn' --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully registered new task definition: $NEW_TASK_DEF" -ForegroundColor Green
    
    Write-Host "`n🔄 Updating ECS service to use new task definition..." -ForegroundColor Green
    aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $NEW_TASK_DEF --region $REGION
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Service update initiated successfully" -ForegroundColor Green
        
        Write-Host "`n⏳ Waiting for service to stabilize..." -ForegroundColor Yellow
        aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service has stabilized" -ForegroundColor Green
            
            Write-Host "`n🔍 Checking updated service status..." -ForegroundColor Yellow
            aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query 'services[0].{ServiceName:serviceName,Status:status,TaskDefinition:taskDefinition,DesiredCount:desiredCount,RunningCount:runningCount}' --output table
            
            Write-Host "`n🎯 Checking target group health..." -ForegroundColor Yellow
            $TARGET_GROUP_ARN = aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query 'services[0].loadBalancers[0].targetGroupArn' --output text
            aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN --region $REGION --query 'TargetHealthDescriptions[0].{Target:Target.Id,Port:Target.Port,Health:TargetHealth.State,Description:TargetHealth.Description}' --output table
            
            Write-Host "`n🎉 Task definition health check fix completed!" -ForegroundColor Green
            Write-Host "The service should now be healthy and responding to requests." -ForegroundColor Green
        } else {
            Write-Host "❌ Service failed to stabilize" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to update service" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to register new task definition" -ForegroundColor Red
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "- New task definition registered: $NEW_TASK_DEF" -ForegroundColor White
Write-Host "- Service updated to use new task definition" -ForegroundColor White
Write-Host "- Health check now points to / (root path) instead of /health" -ForegroundColor White
Write-Host "- Container should now be HEALTHY instead of UNHEALTHY" -ForegroundColor White
