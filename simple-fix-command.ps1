# Simple Fix Command - Run this to fix the health check issue
Write-Host "🔧 Fixing ECS Task Definition Health Check..." -ForegroundColor Green

# Step 1: Register new task definition
Write-Host "`n📝 Registering new task definition..." -ForegroundColor Yellow
$NEW_TASK_DEF = aws ecs register-task-definition --cli-input-json file://clean-task-def.json --region us-east-1 --query 'taskDefinition.taskDefinitionArn' --output text

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ New task definition registered: $NEW_TASK_DEF" -ForegroundColor Green
    
    # Step 2: Update service
    Write-Host "`n🔄 Updating ECS service..." -ForegroundColor Yellow
    aws ecs update-service --cluster shine-ml-cluster --service shine-api-gateway --task-definition $NEW_TASK_DEF --region us-east-1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Service updated successfully!" -ForegroundColor Green
        Write-Host "`n⏳ Waiting for service to stabilize..." -ForegroundColor Yellow
        aws ecs wait services-stable --cluster shine-ml-cluster --services shine-api-gateway --region us-east-1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "🎉 Fix completed! Service should now be healthy." -ForegroundColor Green
        } else {
            Write-Host "⚠️  Service may still be stabilizing" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Failed to update service" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Failed to register task definition" -ForegroundColor Red
}
