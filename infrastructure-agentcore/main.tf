terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.18.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ECR Repository
resource "aws_ecr_repository" "agent" {
  name                 = var.agent_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

# Get ECR authorization token
data "aws_ecr_authorization_token" "token" {}

# Docker provider configuration
provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

# Build and push Docker image
resource "docker_image" "agent" {
  name = "${aws_ecr_repository.agent.repository_url}:${var.image_tag}"

  build {
    context    = "${path.module}/../remote-agentcore/remote_agents"
    dockerfile = "Dockerfile"
    platform   = "linux/arm64"
    no_cache   = true  # Force rebuild every time
  }

  triggers = {
    always_rebuild = timestamp()  # Force rebuild on every apply
  }
}

resource "docker_registry_image" "agent" {
  name          = docker_image.agent.name
  keep_remotely = false  # Allow replacement

  triggers = {
    always_push = timestamp()  # Force push on every apply
  }

  depends_on = [docker_image.agent]
}

# IAM role for AgentCore Runtime
resource "aws_iam_role" "agentcore_runtime" {
  name_prefix = "agentcore-runtime-"
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
}

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
        Resource = aws_ecr_repository.agent.arn
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
  name              = "/aws/bedrock-agentcore/runtimes/${var.agent_name}"
  retention_in_days = 7
}

# AgentCore Runtime (Container)
resource "aws_bedrockagentcore_agent_runtime" "main" {
  agent_runtime_name = var.agent_name
  role_arn           = aws_iam_role.agentcore_runtime.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = "${aws_ecr_repository.agent.repository_url}:${var.image_tag}"
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  environment_variables = {
    MODEL_ID   = var.model_id
    AWS_REGION = data.aws_region.current.id
  }

  tags = var.tags

  depends_on = [docker_registry_image.agent]
}
