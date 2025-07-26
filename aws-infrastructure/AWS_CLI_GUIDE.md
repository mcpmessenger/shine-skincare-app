# 🚀 AWS CLI Integration Guide for Shine Skincare App

## **Overview**

This guide covers how to use AWS CLI to manage your Shine skincare app infrastructure, including database operations, deployment, monitoring, and maintenance.

## **Prerequisites**

### **1. AWS CLI Installation**
```bash
# Windows (using MSI installer)
# Download from: https://aws.amazon.com/cli/

# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### **2. AWS CLI Configuration**
```bash
# Configure AWS CLI with your credentials
aws configure

# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-2)
# - Default output format (json)
```

### **3. Verify Configuration**
```bash
# Test your configuration
aws sts get-caller-identity

# Should return your account info:
# {
#   "UserId": "AIDA...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

## **Infrastructure Deployment**

### **1. Initial Deployment**

#### **Step 1: Generate Secrets**
```bash
cd aws-infrastructure

# Run deployment script (first time)
./deploy.sh production us-east-2

# This will create .env.aws file with generated secrets
# Edit .env.aws to add your credentials:
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
# - STRIPE_SECRET_KEY
```

#### **Step 2: Deploy Infrastructure**
```bash
# Run deployment again with credentials
./deploy.sh production us-east-2
```

### **2. Windows PowerShell Deployment**
```powershell
# Navigate to infrastructure directory
cd aws-infrastructure

# Run PowerShell deployment script
.\deploy.ps1 -Environment production -Region us-east-2
```

## **Database Management**

### **1. Database Setup**

#### **Manual Database Setup**
```bash
# Get database connection info
./aws-utils.sh db-info

# Setup database with migrations
python database-setup.py \
    --host <db-endpoint> \
    --username shine_user \
    --password <password> \
    --database shine_production
```

#### **Using AWS Secrets Manager**
```bash
# Store database credentials in Secrets Manager
aws secretsmanager create-secret \
    --name "shine-database-credentials" \
    --description "Database credentials for Shine app" \
    --secret-string '{
        "host": "your-db-endpoint",
        "port": 5432,
        "username": "shine_user",
        "password": "your-password",
        "database": "shine_production"
    }' \
    --region us-east-2

# Use secret in database setup
python database-setup.py \
    --secret-name "shine-database-credentials" \
    --region us-east-2
```

### **2. Database Operations**

#### **Connect to Database**
```bash
# Get connection info
./aws-utils.sh db-info

# Connect using psql
psql -h <db-endpoint> -p 5432 -U shine_user -d shine_production
```

#### **Backup Database**
```bash
# Create manual backup
./aws-utils.sh backup

# Or using AWS CLI directly
aws rds create-db-snapshot \
    --db-instance-identifier production-shine-db \
    --db-snapshot-identifier production-shine-db-backup-$(date +%Y%m%d) \
    --region us-east-2
```

#### **List Snapshots**
```bash
./aws-utils.sh snapshots
```

#### **Restore from Snapshot**
```bash
# Restore database from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier production-shine-db-restored \
    --db-snapshot-identifier production-shine-db-backup-20241201 \
    --region us-east-2
```

## **Application Deployment**

### **1. Backend Deployment**

#### **Build and Push Docker Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-2 | \
docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com

# Build image
docker build -t shine-api:latest ../backend/

# Tag image
docker tag shine-api:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/shine-api:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/shine-api:latest
```

#### **Update ECS Service**
```bash
# Force new deployment
aws ecs update-service \
    --cluster production-shine-cluster \
    --service production-shine-api-service \
    --force-new-deployment \
    --region us-east-2
```

### **2. Frontend Deployment**

#### **Deploy to S3**
```bash
# Build frontend
cd ..
npm run build

# Get S3 bucket name
S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name shine-infrastructure \
    --region us-east-2 \
    --query 'Stacks[0].Outputs[?OutputKey==`StaticAssetsBucketName`].OutputValue' \
    --output text)

# Sync files to S3
aws s3 sync .next/ s3://$S3_BUCKET/ --delete
```

#### **Invalidate CloudFront Cache**
```bash
# Get distribution ID
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name shine-infrastructure \
    --region us-east-2 \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text)

# Invalidate cache
aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*" \
    --region us-east-2
```

## **Monitoring and Logging**

### **1. Application Logs**

#### **View CloudWatch Logs**
```bash
# Get recent logs
./aws-utils.sh logs 2

# Or using AWS CLI directly
aws logs filter-log-events \
    --log-group-name "/ecs/production-shine-api" \
    --start-time $(date -d "2 hours ago" +%s)000 \
    --region us-east-2 \
    --query 'events[*].{Timestamp:timestamp,Message:message}' \
    --output table
```

#### **Real-time Log Streaming**
```bash
# Stream logs in real-time
aws logs tail "/ecs/production-shine-api" \
    --follow \
    --region us-east-2
```

### **2. Service Monitoring**

#### **Check ECS Service Status**
```bash
./aws-utils.sh ecs-status
```

#### **Scale ECS Service**
```bash
# Scale to 3 instances
./aws-utils.sh scale 3

# Scale down to 1 instance
./aws-utils.sh scale 1
```

#### **Health Check**
```bash
./aws-utils.sh health
```

### **3. Performance Monitoring**

#### **CloudWatch Metrics**
```bash
# Get ECS service metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ServiceName,Value=production-shine-api-service \
    --start-time $(date -d "1 hour ago" -u +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average \
    --region us-east-2
```

#### **Database Metrics**
```bash
# Get RDS metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/RDS \
    --metric-name DatabaseConnections \
    --dimensions Name=DBInstanceIdentifier,Value=production-shine-db \
    --start-time $(date -d "1 hour ago" -u +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Average \
    --region us-east-2
```

## **Security Management**

### **1. Security Groups**

#### **View Security Groups**
```bash
./aws-utils.sh security
```

#### **Update Security Group Rules**
```bash
# Add rule to allow specific IP
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --cidr 192.168.1.0/24 \
    --region us-east-2
```

### **2. IAM Management**

#### **Create IAM User for Application**
```bash
# Create user
aws iam create-user --user-name shine-app-user

# Create access key
aws iam create-access-key --user-name shine-app-user

# Attach policy
aws iam attach-user-policy \
    --user-name shine-app-user \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

#### **Rotate Access Keys**
```bash
# List access keys
aws iam list-access-keys --user-name shine-app-user

# Deactivate old key
aws iam update-access-key \
    --user-name shine-app-user \
    --access-key-id AKIA... \
    --status Inactive

# Delete old key
aws iam delete-access-key \
    --user-name shine-app-user \
    --access-key-id AKIA...
```

## **Cost Management**

### **1. Cost Monitoring**

#### **View Current Costs**
```bash
./aws-utils.sh costs
```

#### **Set Up Cost Alerts**
```bash
# Create SNS topic for alerts
aws sns create-topic --name shine-cost-alerts

# Subscribe to topic
aws sns subscribe \
    --topic-arn arn:aws:sns:us-east-2:123456789012:shine-cost-alerts \
    --protocol email \
    --notification-endpoint your-email@example.com

# Create CloudWatch alarm
aws cloudwatch put-metric-alarm \
    --alarm-name "Shine-Monthly-Cost-Alert" \
    --alarm-description "Alert when monthly cost exceeds $100" \
    --metric-name EstimatedCharges \
    --namespace AWS/Billing \
    --statistic Maximum \
    --period 86400 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-2:123456789012:shine-cost-alerts
```

### **2. Resource Optimization**

#### **Right-size ECS Tasks**
```bash
# Get current task definition
aws ecs describe-task-definition \
    --task-definition production-shine-api \
    --region us-east-2

# Update task definition with optimized resources
aws ecs register-task-definition \
    --cli-input-json file://optimized-task-definition.json
```

#### **Enable RDS Performance Insights**
```bash
# Enable Performance Insights
aws rds modify-db-instance \
    --db-instance-identifier production-shine-db \
    --enable-performance-insights \
    --performance-insights-retention-period 7 \
    --region us-east-2
```

## **Backup and Disaster Recovery**

### **1. Automated Backups**

#### **Enable Automated Backups**
```bash
# Modify RDS instance to enable automated backups
aws rds modify-db-instance \
    --db-instance-identifier production-shine-db \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "sun:04:00-sun:05:00" \
    --region us-east-2
```

#### **Cross-Region Backup**
```bash
# Create cross-region snapshot copy
aws rds copy-db-snapshot \
    --source-db-snapshot-identifier arn:aws:rds:us-east-2:123456789012:snapshot:production-shine-db-backup \
    --target-db-snapshot-identifier production-shine-db-backup-dr \
    --source-region us-east-2 \
    --region us-west-2
```

### **2. Disaster Recovery Plan**

#### **Create DR Infrastructure**
```bash
# Deploy infrastructure in DR region
./deploy.sh production us-west-2

# Setup database replication
aws rds create-db-instance-read-replica \
    --db-instance-identifier production-shine-db-dr \
    --source-db-instance-identifier production-shine-db \
    --region us-west-2
```

## **Troubleshooting**

### **1. Common Issues**

#### **ECS Service Not Starting**
```bash
# Check service events
aws ecs describe-services \
    --cluster production-shine-cluster \
    --services production-shine-api-service \
    --region us-east-2 \
    --query 'services[0].events[0:5]'

# Check task definition
aws ecs describe-task-definition \
    --task-definition production-shine-api \
    --region us-east-2
```

#### **Database Connection Issues**
```bash
# Check database status
aws rds describe-db-instances \
    --db-instance-identifier production-shine-db \
    --region us-east-2 \
    --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint}'

# Test connectivity
nc -zv <db-endpoint> 5432
```

#### **CloudFront Issues**
```bash
# Check distribution status
./aws-utils.sh cloudfront

# Invalidate cache
./aws-utils.sh invalidate
```

### **2. Debug Commands**

#### **Check All Resources**
```bash
# Comprehensive health check
./aws-utils.sh health

# Check specific service
aws ecs describe-services \
    --cluster production-shine-cluster \
    --services production-shine-api-service \
    --region us-east-2
```

#### **Resource Cleanup**
```bash
# Delete stack (be careful!)
aws cloudformation delete-stack \
    --stack-name shine-infrastructure \
    --region us-east-2

# Wait for deletion
aws cloudformation wait stack-delete-complete \
    --stack-name shine-infrastructure \
    --region us-east-2
```

## **Best Practices**

### **1. Security**
- Use IAM roles instead of access keys when possible
- Enable CloudTrail for audit logging
- Regularly rotate access keys
- Use VPC endpoints for private communication

### **2. Monitoring**
- Set up CloudWatch alarms for critical metrics
- Use structured logging
- Monitor costs regularly
- Set up automated backups

### **3. Performance**
- Use auto-scaling for ECS services
- Enable RDS Performance Insights
- Use CloudFront for static assets
- Optimize Docker images

### **4. Cost Optimization**
- Use Spot instances for non-critical workloads
- Right-size resources based on usage
- Enable S3 lifecycle policies
- Monitor and optimize data transfer costs

## **Next Steps**

1. **Deploy your infrastructure** using the provided scripts
2. **Set up monitoring** and alerting
3. **Configure CI/CD** pipelines
4. **Implement backup** and disaster recovery
5. **Optimize costs** based on usage patterns

---

**Your Shine app is now ready for production deployment with full AWS CLI integration!** 🚀 