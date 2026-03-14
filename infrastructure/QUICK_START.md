# Viyapar Infrastructure - Quick Reference

## Quick Start Deployment (15 minutes)

### Prerequisites Checklist
- [ ] AWS account with programmatic access
- [ ] Docker installed and running
- [ ] Terraform installed (v1.0+)
- [ ] AWS CLI configured
- [ ] GitHub account with CI/CD secrets access

### 1. Clone and Setup (2 min)

```bash
git clone https://github.com/your-org/viyapar.git
cd viyapar/infrastructure/terraform

# Create S3 state bucket (first time only)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3api create-bucket --bucket viyapar-terraform-state-${ACCOUNT_ID}
aws s3api put-bucket-versioning --bucket viyapar-terraform-state-${ACCOUNT_ID} \
  --versioning-configuration Status=Enabled

# Update terraform.tf backend bucket name
sed -i "s/viyapar-terraform-state-XXXX/viyapar-terraform-state-${ACCOUNT_ID}/" terraform.tf
```

### 2. Create Configuration (3 min)

```bash
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# - domain_name: your-production-domain.com
# - docker_image_url: docker.io/your-username/viyapar-backend
# - database_password: strong random password
# - jwt_secret_key: openssl rand -base64 32

vim terraform.tfvars
```

### 3. Build and Push Docker Image (4 min)

```bash
cd ../../backend

# Build
docker build -t viyapar-backend:latest .

# Tag and push
docker tag viyapar-backend:latest your-username/viyapar-backend:latest
docker push your-username/viyapar-backend:latest

cd ../infrastructure/terraform
```

### 4. Deploy Infrastructure (6 min)

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Save outputs
terraform output -json > deployment_outputs.json
```

### 5. Post-Deployment (1 min)

```bash
# Run database migrations (manual step)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
DATABASE_URL="postgresql://admin:PASSWORD@${RDS_ENDPOINT}/viyapar_prod" alembic upgrade head

# Add GitHub Actions secrets (manual step via GitHub UI)
```

## Project Structure

```
infrastructure/
├── terraform/
│   ├── terraform.tf          # Provider config, backend, outputs
│   ├── variables.tf          # Variable definitions
│   ├── terraform.tfvars.example  # Example values
│   ├── vpc.tf                # VPC, subnets, security groups
│   ├── rds_ecs.tf            # RDS, ECS, ElastiCache, IAM, S3
│   └── alb_ecs_service.tf    # ALB, listener, ECS service, auto-scaling
├── docker-compose.yml        # Local development orchestration
├── nginx/
│   └── nginx.conf            # Production reverse proxy config
├── PRODUCTION_DEPLOYMENT_GUIDE.md
└── QUICK_START.md (this file)
```

## Key Files Overview

| File | Purpose | Notes |
|------|---------|-------|
| `backend/Dockerfile` | FastAPI container image | Multi-stage, ~500MB |
| `docker-compose.yml` | Local dev services | PostgreSQL, Redis, backend, Nginx |
| `nginx/nginx.conf` | Reverse proxy & SSL | Production-ready |
| `terraform/vpc.tf` | VPC & networking | 2-AZ, public/private subnets |
| `terraform/rds_ecs.tf` | Database & compute | RDS multi-AZ, ECS Fargate, ElastiCache |
| `terraform/alb_ecs_service.tf` | Load balancer & orchestration | ALB, target groups, auto-scaling |

## AWS Resources Created

### Compute
- **ECS Fargate Cluster**: Serverless containerization
  - Capacity providers: FARGATE (100%), FARGATE_SPOT (fallback)
  - Auto-scaling: 2-10 tasks based on CPU (70%) and memory (80%)
  - Multi-AZ deployment for high availability

### Database & Cache
- **RDS PostgreSQL 15**: Multi-AZ, encrypted, 30-day backups
- **ElastiCache Redis 7**: Multi-AZ with auth token, TLS encryption, slow-log monitoring

### Networking
- **VPC**: 10.0.0.0/16 with 2 public and 2 private subnets across 2 AZs
- **ALB**: Application Load Balancer with SSL/TLS (ACM certificates)
- **Route53**: DNS records and domain management
- **NAT Gateway**: Private subnet internet access

### Storage & Secrets
- **S3 Bucket**: File uploads (versioned, encrypted, access-controlled)
- **AWS Secrets Manager**: Credential rotation (DB password, Redis password, JWT secret)
- **CloudWatch Logs**: Container logs (7-day retention), Redis slow logs

### Security
- **Security Groups**: ALB → ECS → RDS/Redis (least privilege)
- **IAM Roles**: Task execution role (pull secrets/logs), task role (S3 access)
- **ACM Certificates**: Automatic SSL/TLS provisioning and renewal

## Common Commands

### Infrastructure Management

```bash
# Plan changes (dry-run)
terraform plan

# Apply changes
terraform apply

# Destroy infrastructure (WARNING: deletes everything)
terraform destroy

# Show current state
terraform show

# Refresh state
terraform refresh

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```

### Monitoring & Debugging

```bash
# Get CloudWatch logs
aws logs tail /ecs/viyapar-backend --follow

# Describe ECS tasks
aws ecs list-tasks --cluster viyapar-prod
aws ecs describe-tasks --cluster viyapar-prod --tasks <task-arn>

# SSH into ECS task
aws ecs execute-command --cluster viyapar-prod \
  --task <task-id> \
  --container viyapar-backend \
  --interactive --command /bin/bash

# Check RDS status
aws rds describe-db-instances --db-instance-identifier viyapar-postgres

# View ALB health
aws elbv2 describe-target-health --target-group-arn <arn>
```

### Deployments

```bash
# Force new ECS deployment
aws ecs update-service \
  --cluster viyapar-prod \
  --service viyapar-backend \
  --force-new-deployment

# Manually scale tasks
aws ecs update-service \
  --cluster viyapar-prod \
  --task-definition viyapar-backend:5 \
  --desired-count 4
```

## Environment Variables

### Required for Terraform

```bash
# AWS credentials (via ~/.aws/credentials or environment variables)
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Or use IAM role for local development
```

### Application Configuration (in terraform.tfvars)

```hcl
aws_region         = "us-east-1"
domain_name        = "api.viyapar.com"
docker_image_url   = "docker.io/myorg/viyapar-backend"
docker_image_tag   = "latest"

# Database
db_instance_class       = "db.t3.small"
db_allocated_storage    = 20

# ECS
ecs_task_cpu            = "512"
ecs_task_memory         = "1024"
ecs_desired_count       = 2

# Secrets
jwt_secret_key         = "openssl-generated-32-byte-key"
database_password      = "strong-random-password"

# SMTP
smtp_host              = "smtp.gmail.com"
smtp_user              = "noreply@viyapar.com"
smtp_password          = "app-specific-password"

# Application
backend_allowed_origins = ["https://app.viyapar.com"]
```

## Cost Estimation

### Monthly Breakdown (Standard Setup)

| Service | Quantity | Unit Price | Monthly |
|---------|----------|-----------|---------|
| ALB | 1 | $16.20 | $16.20 |
| ECS (Fargate) | 2 tasks × 730 hrs | $0.04375/hr | ~$64 |
| RDS (t3.small) | 1 | $0.026/hr | ~$19 |
| ElastiCache (t3.micro) | 2 nodes | $0.017/hr | ~$25 |
| NAT Gateway | 2 | $32/month | $64 |
| Data Transfer | ~100GB | $0.09/GB | ~$9 |
| S3 | Standard | ~$10 | $10 |
| **Total** | | | **~$207** |

### Cost Optimization

```hcl
# Development (minimal)
ecs_desired_count = 1
db_instance_class = "db.t3.micro"
redis_node_type = "cache.t3.micro"

# Scale only for traffic
# Use auto-scaling to reduce 4am-7am instance count
```

## Troubleshooting

### State Conflicts

```bash
# If "resource already exists" error:
terraform refresh
terraform plan

# If state is corrupted:
terraform state pull > backup.tfstate  # Save backup
terraform state show  # Review
```

### Deployment Failed

```bash
# Check what went wrong
terraform apply -auto-approve -lock=false

# Roll back manually
terraform destroy -auto-approve
# Fix configuration and redeploy
```

### Container Won't Start

```bash
# Check task definition
aws ecs describe-task-definition --task-definition viyapar-backend

# Check logs
aws logs tail /ecs/viyapar-backend --follow

# Check container image
docker pull <image> && docker run --rm <image> /app/health
```

### Database Connection Issues

```bash
# Test RDS connectivity
psql -h <rds-endpoint> -U admin -d viyapar_prod

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxx
```

## Security Checklist

- [ ] Enable CloudTrail logging
- [ ] Enable S3 access logging
- [ ] Configure CloudWatch alarms
- [ ] Set up AWS Config rules
- [ ] Enable GuardDuty
- [ ] Rotate secrets regularly
- [ ] Review IAM policies (least privilege)
- [ ] Enable MFA on AWS account
- [ ] Configure backup retention
- [ ] Test disaster recovery procedure

## Additional Resources

- [Viyapar Documentation](../../reporting_system.md)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Production](https://fastapi.tiangolo.com/deployment/concepts/)

## Support

- **Issues**: Report via GitHub Issues
- **Security**: Report to security@viyapar.com
- **Documentation**: See `infrastructure/PRODUCTION_DEPLOYMENT_GUIDE.md`
