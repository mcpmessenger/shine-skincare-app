# Google Auth Credentials Update Guide

This guide explains how to update Google OAuth credentials for the Shine Skincare App running on AWS ECS.

## Overview

The application uses Google OAuth 2.0 for user authentication. The credentials are stored as environment variables in the ECS task definition and managed through AWS CloudFormation.

## Prerequisites

- AWS CLI installed and configured
- PowerShell 5.1 or later
- Access to Google Cloud Console
- Existing ECS deployment (run `deploy.ps1` first if not done)

## Method 1: Automated Update (Recommended)

Use the provided script to update credentials interactively:

```powershell
# Navigate to aws-infrastructure directory
cd aws-infrastructure

# Run the update script
.\update-google-auth.ps1
```

The script will:
1. Prompt you for new Google Client ID and Secret
2. Update the `.env.aws` file
3. Update the CloudFormation stack
4. Force a new ECS deployment

## Method 2: Non-Interactive Update

If you have the credentials ready, you can provide them directly:

```powershell
.\update-google-auth.ps1 -GoogleClientId "your-client-id" -GoogleClientSecret "your-client-secret" -Interactive:$false
```

## Method 3: Manual Update

If you prefer to update manually:

### Step 1: Get New Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API
4. Go to **Credentials** > **Create Credentials** > **OAuth 2.0 Client IDs**
5. Set Application Type to **Web application**
6. Add authorized redirect URIs for your domain:
   - `https://your-domain.com/auth/callback`
   - `http://localhost:3000/auth/callback` (for local development)
7. Copy the Client ID and Client Secret

### Step 2: Update Environment File

Edit the `.env.aws` file in the `aws-infrastructure` directory:

```bash
# Update these lines in .env.aws
GOOGLE_CLIENT_ID=your-new-client-id
GOOGLE_CLIENT_SECRET=your-new-client-secret
```

### Step 3: Update CloudFormation Stack

```powershell
# Load environment variables
Get-Content ".env.aws" | ForEach-Object {
    if ($_ -match "^([^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Update the stack
$StackName = "production-shine-stack"
$Region = "us-east-2"

aws cloudformation update-stack `
    --stack-name $StackName `
    --template-body file://cloudformation-template.yaml `
    --parameters `
        ParameterKey=Environment,ParameterValue="production" `
        ParameterKey=DatabasePassword,ParameterValue="$env:DATABASE_PASSWORD" `
        ParameterKey=GoogleClientId,ParameterValue="$env:GOOGLE_CLIENT_ID" `
        ParameterKey=GoogleClientSecret,ParameterValue="$env:GOOGLE_CLIENT_SECRET" `
        ParameterKey=StripeSecretKey,ParameterValue="$env:STRIPE_SECRET_KEY" `
        ParameterKey=JwtSecretKey,ParameterValue="$env:JWT_SECRET_KEY" `
    --capabilities CAPABILITY_NAMED_IAM `
    --region $Region

# Wait for update to complete
aws cloudformation wait stack-update-complete --stack-name $StackName --region $Region
```

### Step 4: Update ECS Service

```powershell
# Force new deployment
aws ecs update-service `
    --cluster production-shine-cluster `
    --service production-shine-api-service `
    --force-new-deployment `
    --region us-east-2

# Wait for service to stabilize
aws ecs wait services-stable `
    --cluster production-shine-cluster `
    --services production-shine-api-service `
    --region us-east-2
```

## Verification

### Check ECS Service Status

```powershell
aws ecs describe-services `
    --cluster production-shine-cluster `
    --services production-shine-api-service `
    --region us-east-2
```

### Check Environment Variables

```powershell
# Get task definition
aws ecs describe-task-definition `
    --task-definition production-shine-api `
    --region us-east-2
```

### Test Authentication

1. Try logging in with Google OAuth
2. Check CloudWatch logs for authentication errors
3. Verify the callback URL is working

## Troubleshooting

### Common Issues

#### 1. CloudFormation Update Fails
```
Error: No updates are to be performed
```
**Solution**: This means the stack is already up to date. The credentials might already be correct.

#### 2. ECS Service Won't Start
Check CloudWatch logs:
```powershell
aws logs filter-log-events `
    --log-group-name "/ecs/production-shine-api" `
    --start-time $([DateTimeOffset]::Now.AddMinutes(-30).ToUnixTimeMilliseconds()) `
    --region us-east-2
```

#### 3. Authentication Still Fails
- Verify the Google Client ID and Secret are correct
- Check that the redirect URIs are properly configured
- Ensure the Google OAuth APIs are enabled

#### 4. Environment Variables Not Updated
The ECS task definition might need to be updated manually:
```powershell
# Get current task definition
aws ecs describe-task-definition --task-definition production-shine-api --region us-east-2
```

## Security Best Practices

1. **Rotate Credentials Regularly**: Update Google OAuth credentials periodically
2. **Use Environment-Specific Credentials**: Use different credentials for staging and production
3. **Monitor Access**: Check Google Cloud Console for unusual access patterns
4. **Secure Storage**: Never commit credentials to version control

## Environment Variables

The following environment variables are automatically configured in the ECS task:

- `GOOGLE_CLIENT_ID`: Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret
- `JWT_SECRET_KEY`: JWT signing key
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_SECRET_KEY`: Stripe API key
- `ENVIRONMENT`: Current environment name

## Next Steps

After updating credentials:

1. **Test Authentication**: Verify Google OAuth login works
2. **Update Frontend**: If needed, update frontend Google Client ID
3. **Monitor Logs**: Watch for authentication errors
4. **Update Documentation**: Update any documentation with new credentials

## Support

For issues with Google Auth updates:

1. Check CloudWatch logs for detailed error messages
2. Verify Google Cloud Console configuration
3. Test authentication flow manually
4. Review ECS service events in AWS Console

## Quick Reference

### Update Credentials
```powershell
.\update-google-auth.ps1
```

### Check Service Status
```powershell
aws ecs describe-services --cluster production-shine-cluster --services production-shine-api-service --region us-east-2
```

### View Logs
```powershell
aws logs tail "/ecs/production-shine-api" --follow --region us-east-2
```

### Force Redeploy
```powershell
aws ecs update-service --cluster production-shine-cluster --service production-shine-api-service --force-new-deployment --region us-east-2
``` 