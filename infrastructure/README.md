# Viyapar Infrastructure & Deployment

Complete production infrastructure setup for Viyapar with containerized services, cloud deployment, and CI/CD pipelines.

## Overview

This directory contains the complete infrastructure configuration for deploying Viyapar in production:

- **Backend**: FastAPI application containerized with Docker, reverse-proxied with Nginx
- **Database**: PostgreSQL with multi-AZ failover and automated backups
- **Cache**: ElastiCache Redis with encryption and monitoring
- **Orchestration**: AWS ECS Fargate for serverless container management
- **Load Balancing**: Application Load Balancer with SSL/TLS and auto-scaling
- **Infrastructure as Code**: Terraform configurations for reproducible deployments
- **CI/CD**: GitHub Actions pipelines for automated testing and deployment

## Quick Start (15 minutes)

```bash
# 1. Clone and navigate
cd infrastructure/terraform

# 2. Create S3 state bucket (first time only)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3api create-bucket --bucket viyapar-terraform-state-${ACCOUNT_ID}

# 3. Configure Terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Update with your values

# 4. Deploy infrastructure
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 5. Run database migrations
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
cd ../../backend
DATABASE_URL="postgresql://admin:PASSWORD@${RDS_ENDPOINT}/viyapar_prod" \
  alembic upgrade head
```

See [QUICK_START.md](./QUICK_START.md) for detailed instructions.

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── terraform.tf                    # Provider, backend, outputs
│   ├── terraform.tfvars.example        # Configuration template
│   ├── terraform.tfvars               # (create from example, add to .gitignore)
│   ├── variables.tf                   # Variable definitions
│   ├── vpc.tf                         # VPC, subnets, security groups
│   ├── rds_ecs.tf                     # RDS, ECS, ElastiCache, IAM, S3
│   └── alb_ecs_service.tf             # ALB, listeners, service, scaling
├── nginx/
│   └── nginx.conf                     # Reverse proxy & SSL configuration
├── docker-compose.yml                 # Local dev orchestration
├── health-check.sh                    # Deployment verification script
├── PRODUCTION_DEPLOYMENT_GUIDE.md    # Complete deployment instructions
├── QUICK_START.md                     # 15-minute setup guide
└── README.md                          # This file
```

## Files Overview

### Terraform Configuration

| File | Purpose | Resources |
|------|---------|-----------|
| **terraform.tf** | Provider setup, backend, outputs | AWS provider, CloudWatch logs, outputs |
| **variables.tf** | Variable definitions | All configurable parameters |
| **vpc.tf** | Networking foundation | VPC, subnets, IGW, NAT, security groups |
| **rds_ecs.tf** | Database & compute | RDS, ECS, ElastiCache, IAM, S3, Secrets |
| **alb_ecs_service.tf** | Load balancing & routing | ALB, listeners, Route53, ECS service, scaling |

**Total Resources**: ~30 AWS resources created and managed by Terraform

### Docker & Container Files

| File | Purpose |
|------|---------|
| **Dockerfile** | Multi-stage FastAPI image (~500MB) |
| **docker-compose.yml** | Local dev orchestration (PostgreSQL, Redis, backend, Nginx) |
| **nginx/nginx.conf** | Production reverse proxy with SSL/TLS, rate limiting, compression |

### Documentation

| Document | Purpose |
|----------|---------|
| **QUICK_START.md** | 15-minute deployment guide |
| **PRODUCTION_DEPLOYMENT_GUIDE.md** | Comprehensive deployment instructions |
| **health-check.sh** | Automated verification script |

## Architecture

### AWS Infrastructure

```
Internet
  ↓ HTTPS
┌──────────────────────────────┐
│ Route53 DNS                  │
└────────────┬─────────────────┘
             ↓
┌──────────────────────────────┐
│ Application Load Balancer    │
│ (Multi-AZ, ACM Certificates)│
└────────────┬─────────────────┘
             ↓
     ┌───────┴────────┐
     ↓                ↓
┌─────────────┐  ┌─────────────┐
│ ECS Fargate │  │ ECS Fargate │
│ Task (AZ-1) │  │ Task (AZ-2) │
└──┬──────┬───┘  └──┬──────┬───┘
   │      │         │      │
   ↓      ↓         ↓      ↓
RDS PostgreSQL   ElastiCache Redis   S3 Uploads
(Multi-AZ)       (Multi-AZ)          (Encrypted)
```

**Features:**
- ✅ Multi-AZ deployment for high availability
- ✅ Auto-scaling (2-10 tasks based on CPU/memory)
- ✅ Encryption in transit and at rest
- ✅ Automated backups and disaster recovery
- ✅ Comprehensive monitoring and logging
- ✅ Security groups with least-privilege access

### Local Development Setup

```
docker-compose.yml orchestrates:
  - PostgreSQL 15 (port 5432)
  - Redis 7 (port 6379)
  - FastAPI Backend (port 8000)
  - Nginx Reverse Proxy (port 80/443)

All services on bridge network with health checks
```

## Deployment Workflow

### Manual Deployment

1. **Build Docker Image**
   ```bash
   docker build -t viyapar-backend:latest backend/
   docker push your-username/viyapar-backend:latest
   ```

2. **Deploy Infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform apply -var-file=terraform.tfvars
   ```

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

### Automated CI/CD (GitHub Actions)

1. **Push to main branch** → Triggers workflows
2. **Backend Workflow:**
   - Run pytest tests
   - Build Docker image
   - Push to Docker Hub
   - Deploy to ECS (blue-green)
   - Notify on Slack

3. **Android Workflow:**
   - ESLint + TypeScript checks
   - Build APK (preview)
   - Build AAB (production)
   - Submit to Google Play Store

## Configuration

### Environment Variables

Copy and configure `.env`:
```bash
cp ../.env.example .env
```

**Required Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - Authentication secret
- `SMTP_*` - Email configuration

### Terraform Configuration

Copy and configure `terraform.tfvars`:
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

**Key Variables:**
- `domain_name` - Your production domain
- `docker_image_url` - Docker Hub image repository
- `database_password` - RDS master password
- `jwt_secret_key` - Application secret key

### GitHub Actions Secrets

See [.github/GITHUB_ACTIONS_SETUP.md](../.github/GITHUB_ACTIONS_SETUP.md) for complete setup:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- `ECS_CLUSTER_NAME`, `ECS_SERVICE_NAME`
- `EAS_TOKEN`, `EXPO_EMAIL`
- `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`

## Key Features

### Security
- ✅ Nginx rate limiting (100 r/s general, 10 r/s auth)
- ✅ SSL/TLS encryption (ACM certificates)
- ✅ Security groups with least-privilege access
- ✅ Secrets Manager for credential rotation
- ✅ S3 bucket encryption and access controls
- ✅ Non-root container users

### Reliability
- ✅ Multi-AZ deployment (all components)
- ✅ RDS automated failover and backups
- ✅ ECS auto-scaling and health checks
- ✅ ALB health checks and connection draining
- ✅ CloudWatch monitoring and logs

### Performance
- ✅ Nginx gzip compression
- ✅ Redis caching layer
- ✅ S3 bucket for static uploads
- ✅ Connection pooling and optimization
- ✅ ECS task CPU/memory tuning

### Observability
- ✅ CloudWatch Logs (7-day retention)
- ✅ Container Insights for ECS metrics
- ✅ ElastiCache slow-log monitoring
- ✅ RDS performance insights
- ✅ Application health endpoints

## Cost Optimization

### Monthly Estimate (Standard Setup)
| Component | Cost |
|-----------|------|
| ALB | $16 |
| ECS (2 tasks) | $64 |
| RDS (t3.small) | $19 |
| ElastiCache (2 nodes) | $25 |
| NAT Gateway (2) | $64 |
| Data Transfer | $9 |
| S3 | $10 |
| **Total** | **~$207** |

### Optimization Strategies
- Use smaller instances in development
- Schedule scaling down during off-peak hours
- Set up auto-scaling based on metrics
- Use S3 lifecycle policies for old uploads
- Consolidate CloudWatch logs

## Health Check

Verify deployment readiness:
```bash
bash health-check.sh
```

This script checks:
- AWS CLI and credentials
- Terraform configuration
- Docker setup and services
- AWS infrastructure status
- CI/CD pipeline configuration
- Documentation completeness

## Troubleshooting

### Common Issues

**Terraform state lock:**
```bash
terraform force-unlock <LOCK_ID>
```

**ECS tasks not starting:**
```bash
aws logs tail /ecs/viyapar-backend --follow
aws ecs describe-task-definition --task-definition viyapar-backend
```

**Database connection failing:**
```bash
# Test connectivity
psql -h <rds-endpoint> -U admin -d viyapar_prod

# Check security group
aws ec2 describe-security-groups --group-ids sg-xxx
```

**ALB not routing to tasks:**
```bash
aws elbv2 describe-target-health --target-group-arn <arn>
```

See [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md) for comprehensive troubleshooting.

## Monitoring & Maintenance

### Daily Checks
```bash
# ECS service status
aws ecs describe-services --cluster viyapar-prod --services viyapar-backend

# Recent errors
aws logs filter-log-events --log-group-name /ecs/viyapar-backend \
  --filter-pattern "ERROR"
```

### Weekly Tasks
- Review CloudWatch metrics
- Check backup status
- Monitor cost trends
- Review security group rules

### Monthly Tasks
- Update Docker base image
- Rotate secrets
- Test disaster recovery
- Review and apply Terraform changes

## Deployment Checklist

Before going to production:
- [ ] Database migrations tested
- [ ] GitHub Actions secrets configured
- [ ] Docker image built and pushed
- [ ] Terraform plan reviewed
- [ ] SSL certificate provisioned
- [ ] Monitoring alerts configured
- [ ] Team trained on procedures
- [ ] Runbook documented
- [ ] DR procedure tested
- [ ] Load testing completed

## Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)

## Support

- **Issues**: GitHub Issues
- **Security**: security@viyapar.com
- **Documentation**: See docs in this directory
- **AWS Support**: Available with AWS support plan

## Next Steps

1. **Read** [QUICK_START.md](./QUICK_START.md) for step-by-step deployment
2. **Configure** `terraform.tfvars` with your values
3. **Deploy** infrastructure using Terraform
4. **Setup** GitHub Actions secrets
5. **Test** with a test deployment
6. **Monitor** with CloudWatch and alerts
7. **Document** any customizations

---

**Version:** 1.0  
**Last Updated:** March 2026  
**Status:** ✅ Production Ready
