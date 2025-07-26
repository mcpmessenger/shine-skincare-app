#!/bin/bash

# AWS CLI Utility Scripts for Shine Skincare App
# Common operations for managing AWS resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
STACK_NAME="shine-infrastructure"
ENVIRONMENT=${ENVIRONMENT:-"production"}
REGION=${REGION:-"us-east-2"}

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

# Get stack outputs
get_stack_output() {
    local output_key=$1
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
        --output text
}

# Check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &>/dev/null
}

# Get database connection info
get_database_info() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local db_endpoint=$(get_stack_output "DatabaseEndpoint")
    local db_port=$(get_stack_output "DatabasePort")
    
    echo "Database Endpoint: $db_endpoint"
    echo "Database Port: $db_port"
    echo "Database Name: shine_$ENVIRONMENT"
    echo "Username: shine_user"
    echo "Password: (from .env.aws file)"
}

# Get API endpoints
get_api_endpoints() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local api_gateway_url=$(get_stack_output "ApiGatewayUrl")
    local load_balancer_url=$(get_stack_output "LoadBalancerUrl")
    
    echo "API Gateway URL: $api_gateway_url"
    echo "Load Balancer URL: $load_balancer_url"
}

# Get ECS service status
get_ecs_status() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local cluster_name="${ENVIRONMENT}-shine-cluster"
    local service_name="${ENVIRONMENT}-shine-api-service"
    
    log_info "ECS Cluster: $cluster_name"
    log_info "ECS Service: $service_name"
    
    aws ecs describe-services \
        --cluster $cluster_name \
        --services $service_name \
        --region $REGION \
        --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount,PendingCount:pendingCount}' \
        --output table
}

# Get CloudWatch logs
get_logs() {
    local log_group="/ecs/${ENVIRONMENT}-shine-api"
    local hours=${1:-1}
    
    log_info "Getting logs from last $hours hour(s)..."
    
    aws logs filter-log-events \
        --log-group-name $log_group \
        --start-time $(date -d "$hours hours ago" +%s)000 \
        --region $REGION \
        --query 'events[*].{Timestamp:timestamp,Message:message}' \
        --output table
}

# Scale ECS service
scale_service() {
    local desired_count=$1
    
    if [ -z "$desired_count" ]; then
        log_error "Please specify desired count"
        echo "Usage: $0 scale <desired_count>"
        return 1
    fi
    
    local cluster_name="${ENVIRONMENT}-shine-cluster"
    local service_name="${ENVIRONMENT}-shine-api-service"
    
    log_info "Scaling service to $desired_count instances..."
    
    aws ecs update-service \
        --cluster $cluster_name \
        --service $service_name \
        --desired-count $desired_count \
        --region $REGION
    
    log_success "Service scaled to $desired_count instances"
}

# Backup database
backup_database() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local db_identifier="${ENVIRONMENT}-shine-db"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_id="${db_identifier}-snapshot-${timestamp}"
    
    log_info "Creating database snapshot: $snapshot_id"
    
    aws rds create-db-snapshot \
        --db-instance-identifier $db_identifier \
        --db-snapshot-identifier $snapshot_id \
        --region $REGION
    
    log_success "Database snapshot created: $snapshot_id"
}

# List database snapshots
list_snapshots() {
    local db_identifier="${ENVIRONMENT}-shine-db"
    
    log_info "Database snapshots for: $db_identifier"
    
    aws rds describe-db-snapshots \
        --db-instance-identifier $db_identifier \
        --region $REGION \
        --query 'DBSnapshots[*].{SnapshotId:DBSnapshotIdentifier,Status:Status,CreateTime:SnapshotCreateTime}' \
        --output table
}

# Get CloudFront distribution info
get_cloudfront_info() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local distribution_id=$(get_stack_output "CloudFrontDistributionId")
    
    log_info "CloudFront Distribution ID: $distribution_id"
    
    aws cloudfront get-distribution \
        --id $distribution_id \
        --region $REGION \
        --query 'Distribution.{DomainName:DomainName,Status:Status,Enabled:DistributionConfig.Enabled}' \
        --output table
}

# Invalidate CloudFront cache
invalidate_cache() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local distribution_id=$(get_stack_output "CloudFrontDistributionId")
    
    log_info "Invalidating CloudFront cache..."
    
    aws cloudfront create-invalidation \
        --distribution-id $distribution_id \
        --paths "/*" \
        --region $REGION
    
    log_success "Cache invalidation initiated"
}

# Get S3 bucket info
get_s3_info() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    local bucket_name=$(get_stack_output "StaticAssetsBucketName")
    
    log_info "S3 Bucket: $bucket_name"
    
    aws s3 ls s3://$bucket_name --recursive --summarize --region $REGION
}

# Monitor costs
monitor_costs() {
    local start_date=$(date -d "30 days ago" +%Y-%m-%d)
    local end_date=$(date +%Y-%m-%d)
    
    log_info "Cost analysis for the last 30 days..."
    
    aws ce get-cost-and-usage \
        --time-period Start=$start_date,End=$end_date \
        --granularity MONTHLY \
        --metrics BlendedCost \
        --group-by Type=DIMENSION,Key=SERVICE \
        --region $REGION \
        --query 'ResultsByTime[0].Groups[?Metrics.BlendedCost.Amount>`0`].{Service:Keys[0],Cost:Metrics.BlendedCost.Amount}' \
        --output table
}

# Get security group rules
get_security_groups() {
    if ! stack_exists; then
        log_error "Stack does not exist. Deploy infrastructure first."
        return 1
    fi
    
    log_info "Security Groups:"
    
    aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=*shine*" \
        --region $REGION \
        --query 'SecurityGroups[*].{GroupName:GroupName,GroupId:GroupId,Description:Description}' \
        --output table
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check stack status
    if stack_exists; then
        local stack_status=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].StackStatus' \
            --output text)
        log_info "Stack Status: $stack_status"
    else
        log_warning "Stack does not exist"
    fi
    
    # Check ECS service
    if stack_exists; then
        get_ecs_status
    fi
    
    # Check database
    if stack_exists; then
        local db_identifier="${ENVIRONMENT}-shine-db"
        local db_status=$(aws rds describe-db-instances \
            --db-instance-identifier $db_identifier \
            --region $REGION \
            --query 'DBInstances[0].DBInstanceStatus' \
            --output text 2>/dev/null || echo "Not found")
        log_info "Database Status: $db_status"
    fi
}

# Show usage
show_usage() {
    echo "AWS CLI Utilities for Shine Skincare App"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  db-info          - Get database connection information"
    echo "  api-endpoints    - Get API endpoints"
    echo "  ecs-status       - Get ECS service status"
    echo "  logs [hours]     - Get CloudWatch logs (default: 1 hour)"
    echo "  scale <count>    - Scale ECS service"
    echo "  backup           - Create database backup"
    echo "  snapshots        - List database snapshots"
    echo "  cloudfront       - Get CloudFront distribution info"
    echo "  invalidate       - Invalidate CloudFront cache"
    echo "  s3-info          - Get S3 bucket information"
    echo "  costs            - Monitor AWS costs"
    echo "  security         - Get security group information"
    echo "  health           - Perform health check"
    echo "  help             - Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT      - Environment name (default: production)"
    echo "  REGION           - AWS region (default: us-east-2)"
}

# Main function
main() {
    case "${1:-help}" in
        "db-info")
            get_database_info
            ;;
        "api-endpoints")
            get_api_endpoints
            ;;
        "ecs-status")
            get_ecs_status
            ;;
        "logs")
            get_logs $2
            ;;
        "scale")
            scale_service $2
            ;;
        "backup")
            backup_database
            ;;
        "snapshots")
            list_snapshots
            ;;
        "cloudfront")
            get_cloudfront_info
            ;;
        "invalidate")
            invalidate_cache
            ;;
        "s3-info")
            get_s3_info
            ;;
        "costs")
            monitor_costs
            ;;
        "security")
            get_security_groups
            ;;
        "health")
            health_check
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function
main "$@" 