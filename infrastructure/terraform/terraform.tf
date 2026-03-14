terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure the S3 backend for state management
  # Before first use, create the S3 bucket:
  # aws s3api create-bucket --bucket viyapar-terraform-state-XXXX --region us-east-1
  # Then enable versioning:
  # aws s3api put-bucket-versioning --bucket viyapar-terraform-state-XXXX --versioning-configuration Status=Enabled
  backend "s3" {
    bucket         = "viyapar-terraform-state-XXXX" # Replace XXXX with random suffix
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "viyapar"
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedAt   = timeadd(timestamp(), "0s")
    }
  }
}

# CloudWatch Log Group for Terraform operations
resource "aws_cloudwatch_log_group" "terraform" {
  name              = "/aws/terraform/viyapar"
  retention_in_days = 30

  tags = {
    Name = "viyapar-terraform-logs"
  }
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

# Output values for reference
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.backend.name
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "elasticache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "s3_bucket_name" {
  description = "S3 bucket for file uploads"
  value       = aws_s3_bucket.uploads.id
}

output "application_url" {
  description = "Application URL"
  value       = "https://${var.domain_name}"
}
