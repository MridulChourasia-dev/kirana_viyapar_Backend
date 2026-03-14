# Viyapar Production Deployment Guide

## Overview

This guide covers the complete production deployment process for Viyapar, a comprehensive business management solution with backend FastAPI services, React Native mobile app, and AWS cloud infrastructure.

## Architecture Overview

The production deployment follows a **three-tier architecture**:

```
┌─────────────────┐
│   Users (Mobile)│
│   & Web Clients │
└────────┬────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │  AWS CloudFront (Optional CDN)           │
    │  + AWS ACM (SSL/TLS Certificates)        │
    └────┬──────────────────────────────────────┘
         │ HTTPS
    ┌────▼────────────────────────────┐
    │  Application Load Balancer       │
    │  IP: Public (Multi-AZ)           │
    │  Port: 80 (HTTP) → 443 (HTTPS)   │
    └────┬─────────────────────────────┘
         │
    ┌────▼────────────────────────────┐
    │  ECS Fargate Cluster             │
    │  AZ-1: Task 1, Task 2            │
    │  AZ-2: Task 1, Task 2            │
    │  Auto-scaling: 2-10 tasks        │
    └────┬─────────────────────────────┘
         │
    ┌────┴────────────────────────────┐
    │             │                   │
┌───▼──┐  ┌──────▼──────┐  ┌─────────▼────┐
│ RDS  │  │  ElastiCache │  │   S3 Bucket  │
│ DBS  │  │    Redis     │  │ (File Upload)│
│(M-AZ)│  │              │  │              │
└──────┘  └──────────────┘  └──────────────┘

Public: ALB, NAT Gateway
Private: ECS, RDS, ElastiCache
```

## Prerequisites

### Required AWS Account Setup
- AWS account with appropriate permissions
- IAM user with programmatic access (for Terraform)
- S3 bucket for Terraform state management (versioning enabled)
- DynamoDB table for Terraform locks (optional but recommended)

### Local Requirements
- Terraform >= 1.0
- AWS CLI v2
- Docker & Docker Compose
- Git
- Environment variables configured (see `.env.example`)

### Domain Configuration
- Domain registered (Route53 or external registrar)
- Nameservers configured if using external registrar
- SSL/TLS certificate (auto-provisioned via ACM in Terraform)

## Deployment Steps

### Phase 1: Pre-Deployment Setup

#### 1.1 Prepare Environment Variables

```bash
cp .env.example .env.production
# Edit .env.production with production values:
# - Database credentials (strong passwords)
# - JWT secret key
# - SMTP configuration
# - Redis password
# - AWS credentials
```

**Critical Variables:**
```
DATABASE_URL=postgresql://postgres:PASSWORD@rds-endpoint:5432/viyapar
REDIS_URL=redis://:PASSWORD@elasticache-endpoint:6379
JWT_SECRET_KEY=<very_strong_random_key>
SMTP_PASSWORD=<email_app_password>
DOMAIN=yourdomain.com
```

#### 1.2 Configure Terraform

```bash
cd infrastructure/terraform

# Create S3 bucket for Terraform state (one-time setup)
aws s3api create-bucket --bucket viyapar-terraform-state-$(date +%s) --region us-east-1

# Enable versioning on the bucket
aws s3api put-bucket-versioning \
  --bucket viyapar-terraform-state-XXXX \
  --versioning-configuration Status=Enabled

# Update terraform.tf with the bucket name
```

#### 1.3 Create terraform.tfvars

```bash
cat > terraform.tfvars <<EOF
aws_region                    = "us-east-1"
domain_name                   = "your-domain.com"
docker_image_url              = "docker.io/your-username/viyapar-backend:latest"
database_password             = "GenerateStrongPassword123!"
database_instance_class       = "db.t3.small"
redis_node_type               = "cache.t3.small"
ecs_task_cpu                  = "512"
ecs_task_memory               = "1024"
ecs_desired_count             = 3
ecs_min_capacity              = 2
ecs_max_capacity              = 10
jwt_secret_key                = "$(openssl rand -base64 32)"
smtp_host                     = "smtp.gmail.com"
smtp_port                     = 587
smtp_user                      = "your-email@gmail.com"
smtp_password                 = "your-app-password"
backend_allowed_origins       = ["https://your-domain.com"]
EOF
```

### Phase 2: Build Docker Image

```bash
# Build the Docker image
docker build -t viyapar-backend:latest ./backend

# Tag for Docker Hub
docker tag viyapar-backend:latest your-username/viyapar-backend:latest

# Push to Docker Hub (requires authentication)
docker push your-username/viyapar-backend:latest

# Verify the image
docker run --rm your-username/viyapar-backend:latest --version
```

### Phase 3: Initialize Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform (downloads AWS provider, sets up state backend)
terraform init

# Validate configuration
terraform validate

# Review planned changes
terraform plan -out=tfplan
```

### Phase 4: Deploy Infrastructure

```bash
# Apply Terraform configuration (creates all AWS resources)
terraform apply tfplan

# Wait for ALB and RDS to initialize (5-10 minutes)

# Retrieve outputs
terraform output -json > deployment_outputs.json
```

**Resources Created:**
- VPC with public/private subnets across 2 AZs
- Application Load Balancer with SSL/TLS
- ECS Fargate cluster with task definition
- RDS PostgreSQL multi-AZ database
- ElastiCache Redis cluster
- S3 bucket for uploads
- CloudWatch Logs, IAM roles, security groups
- Route53 DNS records

### Phase 5: Database Initialization

```bash
# Get RDS endpoint from Terraform outputs
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Run database migrations
# Option 1: Run locally
DATABASE_URL="postgresql://postgres:PASSWORD@${RDS_ENDPOINT}/viyapar" \
  alembic upgrade head

# Option 2: SSH into ECS task and run
# This requires port forwarding or bastion host setup
```

### Phase 6: Configure GitHub Actions

```bash
# In your GitHub repository settings, add these secrets:

# AWS Credentials
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Docker Registry
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Services
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# ECS Cluster
ECS_CLUSTER_NAME=viyapar-cluster
ECS_SERVICE_NAME=viyapar-backend
AWS_REGION=us-east-1
```

### Phase 7: Deploy Mobile App to Play Store

```bash
cd mobile

# Update app.json with production settings
# - Update version number
# - Set bundleIdentifier to production package

# Build and submit
eas build --platform android --auto-submit

# Monitor build progress in Expo dashboard
# Submission to Google Play Store takes 2-4 hours for review
```

## Post-Deployment Verification

### Health Checks

```bash
# Check ALB health
curl https://your-domain.com/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}

# Check CloudWatch logs
aws logs tail /ecs/viyapar-backend --follow

# Verify database connections
aws rds describe-db-instances --query "DBInstances[0].DBInstanceStatus"

# Check ECS tasks
aws ecs list-tasks --cluster viyapar-cluster
aws ecs describe-tasks --cluster viyapar-cluster --tasks <task-arn>
```

### Monitoring Setup

```bash
# Enable detailed CloudWatch monitoring
aws monitoring put-metric-alarm \
  --alarm-name viyapar-backend-cpu \
  --alarm-description "Alert if CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## Rollback Procedure

### If Deployment Fails

```bash
# Option 1: Revert ECS service to previous task definition
aws ecs update-service \
  --cluster viyapar-cluster \
  --service viyapar-backend \
  --task-definition viyapar-backend:PREVIOUS_REVISION

# Option 2: Destroy all infrastructure (if critical)
cd infrastructure/terraform
terraform destroy -auto-approve
```

### If Database Migration Fails

```bash
# Rollback to previous migration
alembic downgrade -1

# Then redeploy
terraform apply
```

## Scaling Configuration

### Auto-Scaling Policies

The infrastructure includes automatic scaling based on:
- **CPU Utilization**: Scale up at 70%, down at 30%
- **Memory Utilization**: Scale up at 80%, down at 50%
- **Min Tasks**: 2 (redundancy)
- **Max Tasks**: 10 (cost control)

### Manual Scaling

```bash
# Update desired task count
aws ecs update-service \
  --cluster viyapar-cluster \
  --service viyapar-backend \
  --desired-count 5
```

## Monitoring & Logging

### CloudWatch Logs

```bash
# View live logs
aws logs tail /ecs/viyapar-backend --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/viyapar-backend \
  --filter-pattern "ERROR"
```

### Container Insights

```bash
# Enable Container Insights for detailed metrics
# Already enabled in ECS task definition

# View in CloudWatch console:
# CloudWatch > Insights > Container Insights > ECS > viyapar-cluster
```

## Security Best Practices

✅ **Implemented:**
- HTTPS/SSL-TLS encryption (ACM)
- Non-root user in containers (uid 1000)
- Security groups (least privilege)
- Secrets Manager for credentials (auto-rotation)
- VPC isolation (private subnets for compute)
- Database encryption (RDS)
- Multi-AZ for high availability
- Rate limiting in Nginx
- CORS configuration

🔄 **Additional Recommendations:**
- Enable CloudTrail for AWS API audit logs
- Enable S3 bucket logging
- Set up AWS Config for compliance monitoring
- Implement WAF (Web Application Firewall) on ALB
- Enable GuardDuty for threat detection
- Regular security group audits
- Implement secrets rotation policies

## Troubleshooting

### ALB not routing traffic to ECS

```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Common issues:
# - Security group not allowing port 8000
# - Health check path not returning 200
# - Task hasn't reached RUNNING state yet
```

### Database connection failures

```bash
# Verify security group allows traffic
aws ec2 describe-security-groups \
  --group-ids sg-xxx

# Check RDS availability
aws rds describe-db-instances --query "DBInstances[0].[DBInstanceStatus, Endpoint]"

# Verify environment variables in ECS task
aws ecs describe-task-definition --task-definition viyapar-backend:1
```

### High memory usage on tasks

```bash
# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=viyapar-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum

# Solutions:
# - Increase task memory in terraform.tfvars
# - Optimize application code for memory leaks
```

## Maintenance & Updates

### Regular Updates

```bash
# Weekly: Check for updates
terraform plan

# Monthly: Update Docker base image
docker pull python:3.11-slim
docker build --no-cache -t viyapar-backend:latest ./backend

# Apply updates:
git push origin main  # This triggers GitHub Actions
```

### Backup Strategy

```bash
# RDS backups (automatic)
# - Daily automated backups (30-day retention)
# - Multi-region backup enabled (optional)

# Database export
aws rds start-export-task \
  --export-task-identifier viyapar-backup-2024-01-01 \
  --source-arn arn:aws:rds:region:account:db:viyapar \
  --s3-bucket-name viyapar-backups \
  --s3-prefix backups/
```

## Disaster Recovery

### RTO / RPO Targets
- **RTO (Recovery Time Objective)**: 15 minutes
- **RPO (Recovery Point Objective)**: 5 minutes

### Recovery Steps

1. **ECS Task Failure**: Auto-recovery (new task launches in <2 minutes)
2. **RDS Failure**: Multi-AZ automatic failover (1-5 minutes)
3. **ALB Failure**: Cross-AZ setup ensures availability
4. **Full Region Failure**: Manual failover to secondary region (requires setup)

### Cross-Region Setup (Optional)

```bash
# Replicate infrastructure in secondary region
cd infrastructure/terraform
terraform init -backend=false  # Skip state for now
terraform apply -var="aws_region=us-west-2"
```

## Cost Optimization

### Estimated Monthly Costs (Small Deployment)

- **ALB**: ~$15
- **ECS (2 tasks, t3.small)**: ~$30
- **RDS (db.t3.small)**: ~$30
- **ElastiCache (cache.t3.micro)**: ~$15
- **NAT Gateway**: ~$32 (per AZ)
- **Data Transfer**: ~$20
- **S3**: ~$5
- **Total**: ~$150-200/month

### Cost Reduction Strategies

```bash
# Use Spot instances for non-critical tasks
# Modify terraform.tfvars:
ecs_min_capacity = 1
ecs_desired_count = 1  # Scale down off-peak

# Use smaller database instance
database_instance_class = "db.t3.micro"
```

## Useful Commands

```bash
# SSH into ECS task (via Systems Manager Session Manager)
aws ecs execute-command \
  --cluster viyapar-cluster \
  --task <task-id> \
  --container viyapar-backend \
  --interactive \
  --command "/bin/bash"

# View ECS logs in real-time
aws logs tail /ecs/viyapar-backend --follow

# Trigger manual deployment
aws ecs update-service \
  --cluster viyapar-cluster \
  --service viyapar-backend \
  --force-new-deployment

# Check ALB performance
aws elbv2 describe-load-balancers --names viyapar-alb

# Monitor auto-scaling activities
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name viyapar-ecs-asg
```

## Support & Escalation

- **GitHub Issues**: For bug reports and feature requests
- **Slack**: For team communication
- **AWS Support**: For infrastructure issues (with Support Plan)
- **Documentation**: See `docs/` directory for detailed guides

## Next Steps

1. Schedule post-deployment review (24 hours)
2. Set up team notifications and monitoring
3. Document any customizations to base deployment
4. Plan backup and disaster recovery drills
5. Establish performance baseline metrics
