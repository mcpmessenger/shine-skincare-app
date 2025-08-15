# 🦫 POC Variables Configuration
# Customize these values for your environment

variable "aws_region" {
  description = "AWS region for the POC infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "ecs_cluster_name" {
  description = "Name of the existing ECS cluster"
  type        = string
  default     = "production-shine-cluster"
}

variable "ecs_service_name" {
  description = "Name of the existing ECS service"
  type        = string
  default     = "shine-api-gateway"
}

variable "alb_name" {
  description = "Name of the existing Application Load Balancer"
  type        = string
  default     = "production-shine-skincare-alb"
}

variable "target_port" {
  description = "Port that the ECS service is listening on"
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Path for the health check endpoint"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Interval between health checks in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Timeout for health checks in seconds"
  type        = number
  default     = 5
}

variable "healthy_threshold" {
  description = "Number of consecutive successful health checks required"
  type        = number
  default     = 2
}

variable "unhealthy_threshold" {
  description = "Number of consecutive failed health checks required"
  type        = number
  default     = 2
}

variable "ecs_task_private_ip" {
  description = "Private IP address of the running ECS task (temporary fix)"
  type        = string
  default     = "172.31.14.122"  # From our investigation
}

variable "environment" {
  description = "Environment name for tagging"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "Shine-Skincare-App"
}

variable "sprint_name" {
  description = "Sprint name for tracking"
  type        = string
  default     = "Sprint-1-ALB-ECS-Connectivity"
}
