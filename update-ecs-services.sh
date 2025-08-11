#!/bin/sh

# Update ECS Services to use new ALB
# This script updates the ECS services to use the new Application Load Balancer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Updating ECS Services to use new ALB...${NC}"

# Configuration
CLUSTER_NAME="shine-ml-cluster"
REGION="us-east-1"

# New ALB Target Groups
API_GATEWAY_TG_ARN="arn:aws:elasticloadbalancing:us-east-1:396608803476:targetgroup/production-shine-api-gateway-tg/b6325282835611e0"
ML_SERVICE_TG_ARN="arn:aws:elasticloadbalancing:us-east-1:396608803476:targetgroup/production-shine-ml-service-tg/7d196101311093a3"

# Subnets from our new ALB (same as specified in CloudFormation)
SUBNET1="subnet-03a5a7ff60d28eabf"
SUBNET2="subnet-0a333c7bd5dd3de5c"
SUBNET3="subnet-06bf35e62da939f3b"
SUBNET4="subnet-002f8c5465d1448a6"
SUBNET5="subnet-08924ec7f5d6af857"
SUBNET6="subnet-0f21f5f0d6dd2474d"

# Security group for ECS services (we'll create a new one)
SECURITY_GROUP_NAME="production-shine-ecs-sg"

echo -e "${YELLOW}📋 Current ECS Services:${NC}"
aws ecs list-services --cluster $CLUSTER_NAME --region $REGION

echo -e "\n${YELLOW}🔍 Checking current service configurations...${NC}"

# Update API Gateway Service
echo -e "\n${GREEN}🔄 Updating shine-api-gateway service...${NC}"

# Create new security group for ECS services
echo -e "${YELLOW}🔒 Creating new security group for ECS services...${NC}"
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for ECS services behind new ALB" \
    --vpc-id vpc-0ab2e8965e091065a \
    --region $REGION \
    --query 'GroupId' \
    --output text)

echo -e "${GREEN}✅ Created security group: $SECURITY_GROUP_ID${NC}"

# Add rules to security group
echo -e "${YELLOW}🔒 Adding security group rules...${NC}"
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 8080 \
    --source-group sg-01614790ef9195d92 \
    --region $REGION

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 5000 \
    --source-group sg-01614790ef9195d92 \
    --region $REGION

echo -e "${GREEN}✅ Security group rules added${NC}"

# Update API Gateway service
echo -e "${YELLOW}🔄 Updating API Gateway service configuration...${NC}"
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service shine-api-gateway \
    --load-balancers targetGroupArn=$API_GATEWAY_TG_ARN,containerName=shine-api-gateway,containerPort=8080 \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2,$SUBNET3,$SUBNET4,$SUBNET5,$SUBNET6],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=DISABLED}" \
    --region $REGION

echo -e "${GREEN}✅ API Gateway service updated${NC}"

# Update ML Service
echo -e "\n${GREEN}🔄 Updating shine-ml-service...${NC}"
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service shine-ml-service \
    --load-balancers targetGroupArn=$ML_SERVICE_TG_ARN,containerName=shine-ml-service,containerPort=5000 \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2,$SUBNET3,$SUBNET4,$SUBNET5,$SUBNET6],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=DISABLED}" \
    --region $REGION

echo -e "${GREEN}✅ ML Service updated${NC}"

# Wait for services to stabilize
echo -e "\n${YELLOW}⏳ Waiting for services to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster $CLUSTER_NAME \
    --services shine-api-gateway shine-ml-service \
    --region $REGION

echo -e "${GREEN}✅ Services are stable${NC}"

# Check target group health
echo -e "\n${YELLOW}🔍 Checking target group health...${NC}"
echo -e "${YELLOW}API Gateway Target Group:${NC}"
aws elbv2 describe-target-health \
    --target-group-arn $API_GATEWAY_TG_ARN \
    --region $REGION

echo -e "\n${YELLOW}ML Service Target Group:${NC}"
aws elbv2 describe-target-health \
    --target-group-arn $ML_SERVICE_TG_ARN \
    --region $REGION

echo -e "\n${GREEN}🎉 ECS Services updated successfully!${NC}"
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "   1. Test the new ALB endpoints"
echo -e "   2. Update frontend environment variables"
echo -e "   3. Deploy frontend to use new backend"
