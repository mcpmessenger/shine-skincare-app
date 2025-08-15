# 🦫 SHINE SKINCARE APP - POC TERRAFORM CONFIGURATION
# Sprint Goal: Fix ALB-ECS connectivity in 2-3 days
# 
# This POC configuration fixes the immediate network connectivity issue
# without rebuilding the entire infrastructure.

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = {
      Project     = "Shine-Skincare-App"
      Environment = "Production"
      Purpose     = "POC-Infrastructure-Fix"
      Sprint      = "Sprint-1-ALB-ECS-Connectivity"
    }
  }
}

# Data sources to reference existing infrastructure
data "aws_vpc" "current" {
  # We'll use the default VPC for now to get things working
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.current.id]
  }
}

# Get existing ECS service information
data "aws_ecs_service" "shine_api_gateway" {
  cluster_name = "production-shine-cluster"
  service_name = "shine-api-gateway"
}

# Get existing ALB information
data "aws_lb" "production_alb" {
  name = "production-shine-skincare-alb"
}

# POC FIX 1: Create a properly configured target group
resource "aws_lb_target_group" "shine_api_tg_poc" {
  name        = "shine-api-tg-poc-${formatdate("YYYYMMDD", timestamp())}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.current.id
  target_type = "ip"
  
  # Fix the health check configuration
  health_check {
    path                = "/health"
    port                = "8000"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
    protocol            = "HTTP"
  }
  
  tags = {
    Name        = "shine-api-tg-poc"
    Description = "POC Target Group for ALB-ECS connectivity fix"
    Sprint      = "Sprint-1"
  }
}

# POC FIX 2: Create a listener rule to route traffic to our fixed target group
resource "aws_lb_listener_rule" "shine_api_rule_poc" {
  listener_arn = data.aws_lb.production_alb.arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.shine_api_tg_poc.arn
  }
  
  condition {
    path_pattern {
      values = ["/health", "/v6/skin/*", "/api/*"]
    }
  }
  
  tags = {
    Name        = "shine-api-rule-poc"
    Description = "POC listener rule for face detection API"
    Sprint      = "Sprint-1"
  }
}

# POC FIX 3: Get the current ECS task to register it with our target group
data "aws_ecs_task_definition" "shine_api_task" {
  task_definition = data.aws_ecs_service.shine_api_gateway.task_definition
}

# POC FIX 4: Register the ECS task with our target group
resource "aws_lb_target_group_attachment" "shine_api_target_poc" {
  target_group_arn = aws_lb_target_group.shine_api_tg_poc.arn
  
  # We'll need to get the private IP of the running ECS task
  # This is a temporary fix - in production we'd use service discovery
  target_id = "172.31.14.122"  # From our earlier investigation
  
  port = 8000
}

# Outputs for validation
output "target_group_arn" {
  description = "ARN of the POC target group"
  value       = aws_lb_target_group.shine_api_tg_poc.arn
}

output "target_group_name" {
  description = "Name of the POC target group"
  value       = aws_lb_target_group.shine_api_tg_poc.name
}

output "listener_rule_arn" {
  description = "ARN of the POC listener rule"
  value       = aws_lb_listener_rule.shine_api_rule_poc.arn
}

output "alb_dns_name" {
  description = "DNS name of the production ALB"
  value       = data.aws_lb.production_alb.dns_name
}

output "next_steps" {
  description = "Next steps after applying this POC configuration"
  value = [
    "1. Apply this configuration: terraform apply",
    "2. Test the /health endpoint",
    "3. Test the face detection API",
    "4. Validate ALB target health",
    "5. Document success and plan full implementation"
  ]
}
