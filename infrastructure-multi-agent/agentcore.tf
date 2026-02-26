# Get VPC and subnet from infrastructure outputs (same state file)
locals {
  searxng_url        = "http://${aws_instance.searxng.private_ip}:8080"
  private_subnet_id  = aws_subnet.searxng_private.id
  security_group_id  = aws_security_group.searxng.id
}

# Get ECR authorization token
data "aws_ecr_authorization_token" "token" {}

# ECR Repository for web search agent
resource "aws_ecr_repository" "web_search_agent" {
  name                 = "${var.environment}_${var.agent_name}"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }

  tags = merge(local.default_tags, {
    Name = "${var.environment}_${var.agent_name}_ecr"
  })
}

# Build and push Docker image
resource "docker_image" "web_search_agent" {
  name = "${aws_ecr_repository.web_search_agent.repository_url}:${var.image_tag}"

  build {
    context    = "${path.module}/${var.docker_build_context}"
    dockerfile = "Dockerfile"
    platform   = "linux/arm64"
    no_cache   = true
  }

  triggers = {
    always_rebuild = timestamp()
  }
}

resource "docker_registry_image" "web_search_agent" {
  name          = docker_image.web_search_agent.name
  keep_remotely = false

  triggers = {
    always_push = timestamp()
  }

  depends_on = [docker_image.web_search_agent]
}

# IAM role for AgentCore Runtime
resource "aws_iam_role" "agentcore_runtime" {
  name = "${var.environment}_${var.iam_role_name_prefix}role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "bedrock-agentcore.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.default_tags
}

# IAM policy for AgentCore Runtime
resource "aws_iam_role_policy" "agentcore_runtime" {
  name = "agentcore-runtime-policy"
  role = aws_iam_role.agentcore_runtime.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:${data.aws_caller_identity.current.account_id}:inference-profile/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock-agentcore/*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = aws_ecr_repository.web_search_agent.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "agentcore_runtime" {
  name              = "/aws/bedrock-agentcore/runtimes/${var.environment}_${var.agent_name}"
  retention_in_days = 7

  tags = local.default_tags
}

# AgentCore Runtime
resource "aws_bedrockagentcore_agent_runtime" "web_search" {
  agent_runtime_name = "${var.environment}_${var.agent_name}"
  role_arn           = aws_iam_role.agentcore_runtime.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = "${aws_ecr_repository.web_search_agent.repository_url}:${var.image_tag}"
    }
  }

  network_configuration {
    network_mode = "VPC"
    
    network_mode_config {
      subnets         = [local.private_subnet_id]
      security_groups = [local.security_group_id]
    }
  }

  environment_variables = {
    MODEL_ID     = var.model_id
    AWS_REGION   = data.aws_region.current.id
    SEARXNG_URL  = local.searxng_url  # Back to private SearxNG
    MAX_RESULTS  = "5"
  }

  tags = local.default_tags

  depends_on = [docker_registry_image.web_search_agent]
}
