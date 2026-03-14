# RDS PostgreSQL Database
resource "aws_db_subnet_group" "main" {
  name       = "viyapar-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "viyapar-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier     = "viyapar-postgres"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  iops                  = 3000
  performance_insights_enabled = true

  db_name  = "viyapar_prod"
  username = "admin"
  password = random_password.db_password.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az               = true
  publicly_accessible    = false
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  skip_final_snapshot       = false
  final_snapshot_identifier = "viyapar-postgres-final-snapshot-${formatdate("YYYY-MM-DD-hhmmss", timestamp())}"

  deletion_protection = true
  copy_tags_to_snapshot = true

  enable_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Name = "viyapar-postgres"
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret" "db_password" {
  name_prefix             = "viyapar/db/"
  rotation_rules {
    automatically_after_days = 30
  }

  tags = {
    Name = "viyapar-db-password"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.postgres.username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = aws_db_instance.postgres.db_name
  })
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/viyapar-backend"
  retention_in_days = 7

  tags = {
    Name = "viyapar-ecs-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "viyapar-prod"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "viyapar-prod-cluster"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "viyapar-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name              = "viyapar-backend"
    image             = "${var.docker_image_url}:${var.docker_image_tag}"
    essential         = true
    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "ENVIRONMENT", value = var.environment },
      { name = "LOG_LEVEL", value = "info" },
      { name = "DEBUG", value = "false" }
    ]

    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.db_password.arn}:password::"
      },
      {
        name      = "JWT_SECRET_KEY"
        valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:jwt_secret::"
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "viyapar-backend-task"
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "viyapar-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_task_execution_role_secrets" {
  name = "viyapar-ecs-task-execution-role-secrets"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn,
          aws_secretsmanager_secret.app_secrets.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task_role" {
  name = "viyapar-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task_role_s3" {
  name = "viyapar-ecs-task-role-s3"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      Resource = "${aws_s3_bucket.uploads.arn}/*"
    }]
  })
}

# Application Secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name_prefix = "viyapar/app/"

  tags = {
    Name = "viyapar-app-secrets"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    jwt_secret = var.jwt_secret_key
  })
}

# S3 for file uploads
resource "aws_s3_bucket" "uploads" {
  bucket = "viyapar-uploads-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "viyapar-uploads"
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ElastiCache Redis Cluster
resource "aws_elasticache_subnet_group" "main" {
  name       = "viyapar-cache-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "viyapar-cache-subnet-group"
  }
}

resource "random_password" "redis_password" {
  length  = 32
  special = true
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "viyapar-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  
  # Enable Multi-AZ
  automatic_failover_enabled = true
  
  # Encryption
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_password.result
  
  # Networking
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  
  # Backups
  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"
  
  # Maintenance
  maintenance_window = "mon:04:00-mon:06:00"
  
  # Logging
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
    enabled          = true
  }

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_engine_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "engine-log"
    enabled          = true
  }

  tags = {
    Name = "viyapar-redis"
  }
}

resource "aws_secretsmanager_secret" "redis_password" {
  name_prefix = "viyapar/redis/"

  tags = {
    Name = "viyapar-redis-password"
  }
}

resource "aws_secretsmanager_secret_version" "redis_password" {
  secret_id = aws_secretsmanager_secret.redis_password.id
  secret_string = jsonencode({
    password = random_password.redis_password.result
    host     = aws_elasticache_cluster.redis.cache_nodes[0].address
    port     = aws_elasticache_cluster.redis.port
  })
}

resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/viyapar-redis/slow-log"
  retention_in_days = 7

  tags = {
    Name = "viyapar-redis-slow-log"
  }
}

resource "aws_cloudwatch_log_group" "redis_engine_log" {
  name              = "/aws/elasticache/viyapar-redis/engine-log"
  retention_in_days = 7

  tags = {
    Name = "viyapar-redis-engine-log"
  }
}

data "aws_caller_identity" "current" {}
