#!/bin/bash

# Viyapar Production Deployment Health Check
# Run this script to verify your deployment status

set -e

echo "========================================="
echo "Viyapar Deployment Health Check"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_count=0
pass_count=0
fail_count=0

check_status() {
    local name=$1
    local status=$2
    
    check_count=$((check_count + 1))
    
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $name"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $name"
        fail_count=$((fail_count + 1))
    fi
}

# 1. Check Prerequisites
echo "1. Checking Prerequisites..."
echo ""

# AWS CLI
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version | cut -d' ' -f1)
    check_status "AWS CLI installed ($AWS_VERSION)" 0
else
    check_status "AWS CLI installed" 1
fi

# Terraform
if command -v terraform &> /dev/null; then
    TF_VERSION=$(terraform version | head -1 | cut -d'v' -f2)
    check_status "Terraform installed (v$TF_VERSION)" 0
else
    check_status "Terraform installed" 1
fi

# Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3)
    check_status "Docker installed ($DOCKER_VERSION)" 0
else
    check_status "Docker installed" 1
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    check_status "Git installed ($GIT_VERSION)" 0
else
    check_status "Git installed" 1
fi

echo ""

# 2. Check AWS Configuration
echo "2. Checking AWS Configuration..."
echo ""

if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    USER=$(aws sts get-caller-identity --query Arn --output text)
    check_status "AWS credentials configured (Account: $ACCOUNT)" 0
    echo "  User: $USER"
else
    check_status "AWS credentials configured" 1
fi

echo ""

# 3. Check Local Docker Setup
echo "3. Checking Local Docker Setup..."
echo ""

if [ -f "docker-compose.yml" ]; then
    check_status "docker-compose.yml exists" 0
    
    # Check if services are running
    if docker-compose ps | grep -q "healthy\|running"; then
        check_status "Docker containers running" 0
        
        # Check backend
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            check_status "Backend service responding (:8000)" 0
        else
            check_status "Backend service responding (:8000)" 1
        fi
        
        # Check Nginx
        if curl -s http://localhost/health > /dev/null 2>&1; then
            check_status "Nginx service responding (:80)" 0
        else
            check_status "Nginx service responding (:80)" 1
        fi
    else
        check_status "Docker containers running" 1
    fi
else
    check_status "docker-compose.yml exists" 1
fi

echo ""

# 4. Check Terraform Configuration
echo "4. Checking Terraform Configuration..."
echo ""

if [ -d "infrastructure/terraform" ]; then
    check_status "Terraform directory exists" 0
    
    if [ -f "infrastructure/terraform/terraform.tf" ]; then
        check_status "terraform.tf exists" 0
    else
        check_status "terraform.tf exists" 1
    fi
    
    if [ -f "infrastructure/terraform/variables.tf" ]; then
        check_status "variables.tf exists" 0
    else
        check_status "variables.tf exists" 1
    fi
    
    if [ -f "infrastructure/terraform/terraform.tfvars" ]; then
        check_status "terraform.tfvars exists" 0
    else
        echo -e "${YELLOW}!${NC} terraform.tfvars not found (copy from terraform.tfvars.example)"
    fi
    
    # Validate Terraform
    cd infrastructure/terraform
    if terraform validate > /dev/null 2>&1; then
        check_status "Terraform configuration valid" 0
    else
        check_status "Terraform configuration valid" 1
        terraform validate
    fi
    cd - > /dev/null
else
    check_status "Terraform directory exists" 1
fi

echo ""

# 5. Check Infrastructure in AWS
echo "5. Checking AWS Infrastructure..."
echo ""

# Check ECS Cluster
CLUSTER_NAME="viyapar-prod"
if aws ecs describe-clusters --clusters $CLUSTER_NAME &> /dev/null; then
    CLUSTER_STATUS=$(aws ecs describe-clusters --clusters $CLUSTER_NAME --query 'clusters[0].status' --output text)
    if [ "$CLUSTER_STATUS" == "ACTIVE" ]; then
        check_status "ECS Cluster running ($CLUSTER_NAME)" 0
        
        # Check services
        SERVICES=$(aws ecs list-services --cluster $CLUSTER_NAME --query 'serviceArns[]' --output text)
        if [ ! -z "$SERVICES" ]; then
            SERVICE_COUNT=$(echo $SERVICES | wc -w)
            SERVICE_STATUS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICES --query 'services[0].status' --output text)
            check_status "ECS Service running (Status: $SERVICE_STATUS)" 0
        fi
    else
        check_status "ECS Cluster running" 1
    fi
else
    check_status "ECS Cluster exists" 1
fi

# Check RDS Instance
DB_INSTANCE="viyapar-postgres"
if aws rds describe-db-instances --db-instance-identifier $DB_INSTANCE &> /dev/null; then
    DB_STATUS=$(aws rds describe-db-instances --db-instance-identifier $DB_INSTANCE --query 'DBInstances[0].DBInstanceStatus' --output text)
    if [ "$DB_STATUS" == "available" ]; then
        check_status "RDS Database running ($DB_INSTANCE)" 0
    else
        check_status "RDS Database running (Status: $DB_STATUS)" 1
    fi
else
    check_status "RDS Database exists" 1
fi

# Check ALB
ALB_NAME="viyapar-alb"
if aws elbv2 describe-load-balancers --names $ALB_NAME &> /dev/null; then
    ALB_STATUS=$(aws elbv2 describe-load-balancers --names $ALB_NAME --query 'LoadBalancers[0].State.Code' --output text)
    if [ "$ALB_STATUS" == "active" ]; then
        check_status "Application Load Balancer running ($ALB_NAME)" 0
        ALB_DNS=$(aws elbv2 describe-load-balancers --names $ALB_NAME --query 'LoadBalancers[0].DNSName' --output text)
        echo "  DNS: $ALB_DNS"
    else
        check_status "Application Load Balancer running" 1
    fi
else
    check_status "Application Load Balancer exists" 1
fi

# Check ElastiCache Redis
if aws elasticache describe-cache-clusters --cache-cluster-id viyapar-redis &> /dev/null; then
    REDIS_STATUS=$(aws elasticache describe-cache-clusters --cache-cluster-id viyapar-redis --query 'CacheClusters[0].CacheClusterStatus' --output text)
    if [ "$REDIS_STATUS" == "available" ]; then
        check_status "ElastiCache Redis running" 0
    else
        check_status "ElastiCache Redis running (Status: $REDIS_STATUS)" 1
    fi
else
    check_status "ElastiCache Redis exists" 1
fi

echo ""

# 6. Check CI/CD Configuration
echo "6. Checking CI/CD Configuration..."
echo ""

if [ -f ".github/workflows/backend.yml" ]; then
    check_status "Backend CI/CD pipeline exists" 0
else
    check_status "Backend CI/CD pipeline exists" 1
fi

if [ -f ".github/workflows/android.yml" ]; then
    check_status "Android CI/CD pipeline exists" 0
else
    check_status "Android CI/CD pipeline exists" 1
fi

if [ -f ".github/GITHUB_ACTIONS_SETUP.md" ]; then
    check_status "GitHub Actions setup guide exists" 0
else
    check_status "GitHub Actions setup guide exists" 1
fi

echo ""

# 7. Check Documentation
echo "7. Checking Documentation..."
echo ""

if [ -f "DEPLOYMENT_COMPLETE.md" ]; then
    check_status "Deployment documentation complete" 0
else
    check_status "Deployment documentation complete" 1
fi

if [ -f "infrastructure/PRODUCTION_DEPLOYMENT_GUIDE.md" ]; then
    check_status "Production deployment guide exists" 0
else
    check_status "Production deployment guide exists" 1
fi

if [ -f "infrastructure/QUICK_START.md" ]; then
    check_status "Quick start guide exists" 0
else
    check_status "Quick start guide exists" 1
fi

echo ""

# Summary
echo "========================================="
echo "Health Check Summary"
echo "========================================="
echo -e "Total Checks: $check_count"
echo -e "${GREEN}Passed: $pass_count${NC}"
if [ $fail_count -gt 0 ]; then
    echo -e "${RED}Failed: $fail_count${NC}"
else
    echo -e "${GREEN}Failed: $fail_count${NC}"
fi
echo "========================================="
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Your deployment is ready.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the items above.${NC}"
    echo ""
    echo "Resources:"
    echo "  - Deployment Guide: infrastructure/PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo "  - Quick Start: infrastructure/QUICK_START.md"
    echo "  - GitHub Setup: .github/GITHUB_ACTIONS_SETUP.md"
    exit 1
fi
