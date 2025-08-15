# Fix ALB-ECS Network Connectivity Issues
Write-Host "Fixing ALB-ECS Network Connectivity Issues..." -ForegroundColor Green

# Set variables
$CLUSTER = "production-shine-cluster"
$SERVICE = "shine-api-gateway"
$SECURITY_GROUP = "sg-071029ab14d753733"
$TARGET_GROUP = "shine-api-tg-fixed"

Write-Host "Step 1: Adding port 8000 rule to ECS security group..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP --protocol tcp --port 8000 --cidr 0.0.0.0/0

Write-Host "Step 2: Checking current target group configuration..." -ForegroundColor Yellow
aws elbv2 describe-target-groups --names $TARGET_GROUP --query 'TargetGroups[0].{Port: Port, HealthCheckPort: HealthCheckPort, Protocol: Protocol}' --output table

Write-Host "Step 3: Checking ECS service load balancer configuration..." -ForegroundColor Yellow
aws ecs describe-services --cluster $CLUSTER --services $SERVICE --query 'services[0].loadBalancers[0]' --output table

Write-Host "Step 4: Checking current task definition..." -ForegroundColor Yellow
aws ecs describe-services --cluster $CLUSTER --services $SERVICE --query 'services[0].taskDefinition' --output text

Write-Host "Step 5: Force new deployment to apply security group changes..." -ForegroundColor Yellow
aws ecs update-service --cluster $CLUSTER --service $SERVICE --force-new-deployment

Write-Host "Network connectivity fixes applied!" -ForegroundColor Green
Write-Host "Monitor the deployment with: aws ecs describe-services --cluster $CLUSTER --services $SERVICE" -ForegroundColor Cyan
