#!/bin/bash

# Shine Skincare App - AWS Infrastructure Deployment Script
# This script deploys the complete infrastructure using AWS CLI

set -e  # Exit on any error

# Configuration
STACK_NAME="shine-infrastructure"
ENVIRONMENT=${1:-"production"}
REGION=${2:-"us-east-2"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if template file exists
    if [ ! -f "cloudformation-template.yaml" ]; then
        log_error "CloudFormation template not found: cloudformation-template.yaml"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secure passwords and keys
generate_secrets() {
    log_info "Generating secure secrets..."
    
    # Generate database password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
    
    # Save secrets to file (for reference)
    cat > .env.aws << EOF
# AWS Infrastructure Secrets (Generated)
# Keep this file secure and do not commit to version control

DATABASE_PASSWORD=$DB_PASSWORD
JWT_SECRET_KEY=$JWT_SECRET
ENVIRONMENT=$ENVIRONMENT
REGION=$REGION
STACK_NAME=$STACK_NAME

# You need to manually add these:
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret
# STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
EOF
    
    log_success "Secrets generated and saved to .env.aws"
    log_warning "Please add your Google OAuth and Stripe credentials to .env.aws"
}

# Load environment variables
load_env() {
    if [ -f ".env.aws" ]; then
        log_info "Loading environment variables..."
        export $(cat .env.aws | grep -v '^#' | xargs)
    else
        log_error ".env.aws file not found. Please run the script first to generate secrets."
        exit 1
    fi
}

# Create S3 bucket for CloudFormation artifacts
create_s3_bucket() {
    log_info "Creating S3 bucket for CloudFormation artifacts..."
    
    BUCKET_NAME="shine-cf-artifacts-$(aws sts get-caller-identity --query Account --output text)-${REGION}"
    
    # Check if bucket exists
    if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb "s3://$BUCKET_NAME" --region $REGION
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled \
            --region $REGION
        log_success "S3 bucket created: $BUCKET_NAME"
    else
        log_info "S3 bucket already exists: $BUCKET_NAME"
    fi
    
    export CF_BUCKET=$BUCKET_NAME
}

# Deploy CloudFormation stack
deploy_stack() {
    log_info "Deploying CloudFormation stack..."
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null; then
        log_info "Stack exists, updating..."
        OPERATION="update-stack"
    else
        log_info "Stack does not exist, creating..."
        OPERATION="create-stack"
    fi
    
    # Deploy the stack
    aws cloudformation $OPERATION \
        --stack-name $STACK_NAME \
        --template-body file://cloudformation-template.yaml \
        --parameters \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=DatabasePassword,ParameterValue="$DATABASE_PASSWORD" \
            ParameterKey=GoogleClientId,ParameterValue="$GOOGLE_CLIENT_ID" \
            ParameterKey=GoogleClientSecret,ParameterValue="$GOOGLE_CLIENT_SECRET" \
            ParameterKey=StripeSecretKey,ParameterValue="$STRIPE_SECRET_KEY" \
            ParameterKey=JwtSecretKey,ParameterValue="$JWT_SECRET_KEY" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --s3-bucket $CF_BUCKET \
        --s3-prefix cloudformation
    
    # Wait for stack completion
    log_info "Waiting for stack operation to complete..."
    aws cloudformation wait stack-$([ "$OPERATION" = "create-stack" ] && echo "create" || echo "update")-complete \
        --stack-name $STACK_NAME \
        --region $REGION
    
    log_success "Stack deployment completed successfully"
}

# Get stack outputs
get_outputs() {
    log_info "Getting stack outputs..."
    
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output table
    
    # Save outputs to file
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output json > stack-outputs.json
    
    log_success "Stack outputs saved to stack-outputs.json"
}

# Create ECR repository
create_ecr_repository() {
    log_info "Creating ECR repository for API..."
    
    REPO_NAME="shine-api"
    
    if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION &> /dev/null; then
        aws ecr create-repository \
            --repository-name $REPO_NAME \
            --region $REGION \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        
        log_success "ECR repository created: $REPO_NAME"
    else
        log_info "ECR repository already exists: $REPO_NAME"
    fi
    
    # Get repository URI
    REPO_URI=$(aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION --query 'repositories[0].repositoryUri' --output text)
    echo "ECR_REPOSITORY_URI=$REPO_URI" >> .env.aws
    
    log_success "ECR repository URI: $REPO_URI"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI
    
    # Build image
    docker build -t shine-api:latest ../backend/
    
    # Tag image
    docker tag shine-api:latest $ECR_REPOSITORY_URI:latest
    
    # Push image
    docker push $ECR_REPOSITORY_URI:latest
    
    log_success "Docker image pushed successfully"
}

# Update ECS service
update_ecs_service() {
    log_info "Updating ECS service..."
    
    CLUSTER_NAME="${ENVIRONMENT}-shine-cluster"
    SERVICE_NAME="${ENVIRONMENT}-shine-api-service"
    
    # Force new deployment
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --force-new-deployment \
        --region $REGION
    
    log_success "ECS service updated"
}

# Setup database
setup_database() {
    log_info "Setting up database..."
    
    # Get database endpoint from stack outputs
    DB_ENDPOINT=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
        --output text)
    
    # Wait for database to be available
    log_info "Waiting for database to be available..."
    aws rds wait db-instance-available \
        --db-instance-identifier "${ENVIRONMENT}-shine-db" \
        --region $REGION
    
    log_success "Database is ready: $DB_ENDPOINT"
}

# Deploy frontend to S3
deploy_frontend() {
    log_info "Deploying frontend to S3..."
    
    # Build frontend
    cd ../frontend
    npm run build
    
    # Get S3 bucket name from stack outputs
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`StaticAssetsBucketName`].OutputValue' \
        --output text)
    
    # Sync build files to S3
    aws s3 sync .next/ s3://$S3_BUCKET/ --delete
    
    # Invalidate CloudFront cache
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text)
    
    aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*" \
        --region $REGION
    
    cd ../aws-infrastructure
    log_success "Frontend deployed successfully"
}

# Main deployment function
main() {
    log_info "Starting Shine Skincare App deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Region: $REGION"
    log_info "Stack Name: $STACK_NAME"
    
    # Check prerequisites
    check_prerequisites
    
    # Generate secrets (only if .env.aws doesn't exist)
    if [ ! -f ".env.aws" ]; then
        generate_secrets
        log_warning "Please edit .env.aws to add your Google OAuth and Stripe credentials, then run this script again."
        exit 0
    fi
    
    # Load environment variables
    load_env
    
    # Create S3 bucket
    create_s3_bucket
    
    # Deploy CloudFormation stack
    deploy_stack
    
    # Get stack outputs
    get_outputs
    
    # Create ECR repository
    create_ecr_repository
    
    # Setup database
    setup_database
    
    # Build and push Docker image
    build_and_push_image
    
    # Update ECS service
    update_ecs_service
    
    # Deploy frontend
    deploy_frontend
    
    log_success "Deployment completed successfully!"
    log_info "Check stack-outputs.json for all the URLs and endpoints"
}

# Run main function
main "$@" 