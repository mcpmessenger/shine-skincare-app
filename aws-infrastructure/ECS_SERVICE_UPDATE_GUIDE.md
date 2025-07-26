# ECS Service Update Guide for Shine Skincare App

This guide explains how to update your ECS service with a new Docker image deployment using the provided PowerShell scripts.

## Overview

The Shine Skincare App backend runs on AWS ECS (Elastic Container Service) using Fargate. When you make changes to your backend code, you need to:

1. Build a new Docker image
2. Push it to Amazon ECR (Elastic Container Registry)
3. Update the ECS service to use the new image

## Prerequisites

Before updating the ECS service, ensure you have:

- [ ] AWS CLI installed and configured
- [ ] Docker installed (if building new images)
- [ ] PowerShell 5.1 or later
- [ ] Completed initial deployment using `deploy.ps1` or `deploy-simple.ps1`
- [ ] `.env.aws` file exists in the `aws-infrastructure` directory

## Methods to Update ECS Service

### Method 1: Standalone Update Script (Recommended)

Use the dedicated `update-ecs-service.ps1` script for quick updates:

```powershell
# Navigate to aws-infrastructure directory
cd aws-infrastructure

# Update service with existing image (force new deployment)
.\update-ecs-service.ps1

# Build new image and update service
.\update-ecs-service.ps1 -BuildImage

# Quick update without waiting for completion
.\update-ecs-service.ps1 -BuildImage -SkipWait

# Update for different environment
.\update-ecs-service.ps1 -Environment staging -Region us-west-2
```

### Method 2: Full Deployment Script

Use the main deployment script which includes ECS service update:

```powershell
# Run complete deployment (includes ECS update)
.\deploy.ps1

# Or use the simplified version
.\deploy-simple.ps1
```

## Script Parameters

### update-ecs-service.ps1 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `Environment` | String | "production" | Target environment (production, staging, development) |
| `Region` | String | "us-east-2" | AWS region |
| `BuildImage` | Switch | False | Build and push new Docker image before updating service |
| `SkipWait` | Switch | False | Don't wait for deployment completion |

## Usage Examples

### Example 1: Quick Service Restart

If you just want to restart the service with the existing image:

```powershell
.\update-ecs-service.ps1
```

### Example 2: Deploy New Code Changes

When you have new backend code to deploy:

```powershell
# Build new image and update service
.\update-ecs-service.ps1 -BuildImage
```

### Example 3: Fast Development Cycle

For rapid development iterations:

```powershell
# Build, deploy, and don't wait for completion
.\update-ecs-service.ps1 -BuildImage -SkipWait
```

### Example 4: Different Environment

To update a staging environment:

```powershell
.\update-ecs-service.ps1 -Environment staging -BuildImage
```

## What Happens During Update

1. **Prerequisites Check**: Verifies AWS CLI, Docker (if needed), and credentials
2. **Environment Loading**: Loads configuration from `.env.aws`
3. **Service Status Check**: Shows current service status and deployments
4. **Image Build** (if `-BuildImage` specified):
   - Logs into ECR
   - Builds Docker image from `../backend/`
   - Tags image with ECR repository URI
   - Pushes image to ECR
5. **Service Update**: Forces new deployment of ECS service
6. **Wait for Completion** (unless `-SkipWait` specified)
7. **Status Report**: Shows final service status and recent logs

## Monitoring Deployment

### Check Service Status

The script automatically shows service status, but you can also check manually:

```powershell
# Get service details
aws ecs describe-services `
    --cluster production-shine-cluster `
    --services production-shine-api-service `
    --region us-east-2

# Get task details
aws ecs list-tasks `
    --cluster production-shine-cluster `
    --service-name production-shine-api-service `
    --region us-east-2
```

### View Logs

```powershell
# View recent logs
aws logs filter-log-events `
    --log-group-name "/ecs/production-shine-api" `
    --start-time $([DateTimeOffset]::Now.AddMinutes(-30).ToUnixTimeMilliseconds()) `
    --region us-east-2

# Stream live logs
aws logs tail "/ecs/production-shine-api" --follow --region us-east-2
```

### AWS Console

Monitor deployment progress in the AWS Console:
- **ECS Service**: `https://console.aws.amazon.com/ecs/home?region=us-east-2#/clusters/production-shine-cluster/services/production-shine-api-service/details`
- **CloudWatch Logs**: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-2#logsV2:log-groups/log-group/$252Fecs$252Fproduction-shine-api`

## Troubleshooting

### Common Issues

#### 1. ECR Login Failed
```
Error: Failed to login to ECR
```
**Solution**: Check AWS credentials and ECR repository exists:
```powershell
aws sts get-caller-identity
aws ecr describe-repositories --repository-names shine-api --region us-east-2
```

#### 2. Docker Build Failed
```
Error: Failed to build Docker image
```
**Solution**: Check Dockerfile and build context:
- Ensure you're in the `aws-infrastructure` directory
- Verify `../backend/Dockerfile` exists
- Check Docker daemon is running

#### 3. Service Update Failed
```
Error: Failed to update ECS service
```
**Solution**: Check service exists and you have permissions:
```powershell
aws ecs describe-services --cluster production-shine-cluster --services production-shine-api-service --region us-east-2
```

#### 4. Deployment Stuck
If deployment appears stuck, check:
- Service events in AWS Console
- Task definition is valid
- Security groups allow traffic
- Subnets have internet access (for Fargate)

### Health Check Endpoint

The service includes a health check endpoint at `/api/health`. Ensure your backend application responds to this endpoint for proper load balancer health checks.

## Best Practices

1. **Test Locally First**: Always test your backend changes locally before deploying
2. **Use Staging**: Deploy to staging environment first for testing
3. **Monitor Logs**: Watch CloudWatch logs during deployment
4. **Rollback Plan**: Keep previous working image tags for quick rollback
5. **Blue/Green Deployment**: For zero-downtime deployments, consider using ECS blue/green deployments

## Rollback Process

If you need to rollback to a previous version:

1. **Find Previous Task Definition**:
   ```powershell
   aws ecs list-task-definitions --family-prefix production-shine-api --region us-east-2
   ```

2. **Update Service with Previous Task Definition**:
   ```powershell
   aws ecs update-service `
       --cluster production-shine-cluster `
       --service production-shine-api-service `
       --task-definition production-shine-api:PREVIOUS_REVISION `
       --region us-east-2
   ```

## Environment Variables

The ECS service automatically receives these environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `JWT_SECRET_KEY`: JWT signing key
- `STRIPE_SECRET_KEY`: Stripe API key
- `ENVIRONMENT`: Current environment name

## Security Considerations

- ECR repositories use encryption at rest
- ECS tasks run with minimal IAM permissions
- Database credentials are passed securely through environment variables
- All traffic uses HTTPS through the Application Load Balancer

## Support

For issues with ECS service updates:

1. Check CloudWatch logs for application errors
2. Verify AWS infrastructure status
3. Review ECS service events in AWS Console
4. Ensure all environment variables are correctly set

## Next Steps

After successful ECS service update:

1. **Test Application**: Verify all endpoints work correctly
2. **Monitor Performance**: Watch CloudWatch metrics
3. **Update Frontend**: Deploy frontend changes if needed
4. **Document Changes**: Update changelog and documentation 