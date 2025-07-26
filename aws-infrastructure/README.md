# AWS Infrastructure for Shine Skincare App

This directory contains all the AWS infrastructure configuration and deployment scripts for the Shine Skincare App.

## Quick Start

1. **Initial Deployment**:
   ```powershell
   .\deploy-simple.ps1
   ```

2. **Update Backend Service**:
   ```powershell
   .\update-ecs-service.ps1 -BuildImage
   ```

## Files Overview

### Deployment Scripts
- `deploy.ps1` - Complete deployment script with all features
- `deploy-simple.ps1` - Simplified deployment for quick setup
- `update-ecs-service.ps1` - **NEW**: Standalone ECS service update script

### Configuration Files
- `cloudformation-template.yaml` - AWS CloudFormation infrastructure template
- `parameters.json` - Generated parameters file for CloudFormation
- `.env.aws` - Environment variables (generated during deployment)

### Documentation
- `ECS_SERVICE_UPDATE_GUIDE.md` - **NEW**: Comprehensive guide for updating ECS services
- `AWS_CLI_GUIDE.md` - AWS CLI commands and troubleshooting
- `stack-outputs.json` - Generated stack outputs after deployment

## ECS Service Update (NEW Feature)

The `update-ecs-service.ps1` script provides an easy way to update your backend service with new Docker images:

### Quick Usage Examples

```powershell
# Update service with existing image (restart)
.\update-ecs-service.ps1

# Build new image and update service
.\update-ecs-service.ps1 -BuildImage

# Quick deployment without waiting
.\update-ecs-service.ps1 -BuildImage -SkipWait

# Update staging environment
.\update-ecs-service.ps1 -Environment staging -BuildImage
```

### Features
- ✅ Automated Docker image building and pushing to ECR
- ✅ ECS service update with zero-downtime deployment
- ✅ Service status monitoring and health checks
- ✅ CloudWatch logs integration
- ✅ Comprehensive error handling and rollback guidance
- ✅ Support for multiple environments (production, staging, development)

For detailed usage instructions, see [ECS_SERVICE_UPDATE_GUIDE.md](./ECS_SERVICE_UPDATE_GUIDE.md).

## Infrastructure Components

The CloudFormation template creates:

- **Networking**: VPC, subnets, internet gateway, security groups
- **Load Balancing**: Application Load Balancer with health checks
- **Container Service**: ECS Fargate cluster and service
- **Database**: RDS PostgreSQL instance
- **Storage**: S3 bucket for static assets
- **Container Registry**: ECR repository for Docker images
- **Monitoring**: CloudWatch logs and metrics

## Prerequisites

- AWS CLI installed and configured
- PowerShell 5.1 or later
- Docker installed (for building images)
- Valid AWS credentials with appropriate permissions

## Environment Variables

The following environment variables are automatically configured:

- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `JWT_SECRET_KEY` - JWT signing key
- `STRIPE_SECRET_KEY` - Stripe API key
- `ENVIRONMENT` - Current environment name

## Monitoring and Logs

- **ECS Service**: Monitor in AWS Console
- **CloudWatch Logs**: `/ecs/production-shine-api`
- **Application Load Balancer**: Health check endpoint at `/api/health`

## Support

For deployment issues:
1. Check CloudWatch logs
2. Verify AWS credentials and permissions
3. Ensure all prerequisites are installed
4. Review the troubleshooting section in the guides

## Next Steps

After deployment:
1. Update your backend code as needed
2. Use `update-ecs-service.ps1 -BuildImage` to deploy changes
3. Monitor service health and performance
4. Deploy frontend changes separately 