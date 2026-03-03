# Shared resources for all agents

# Locals for networking (reference existing VPC resources)
locals {
  searxng_url        = "http://${aws_instance.searxng.private_ip}:8080"
  private_subnet_id  = aws_subnet.searxng_private.id
  security_group_id  = aws_security_group.searxng.id
}

# Get ECR authorization token
data "aws_ecr_authorization_token" "token" {}

# ECR Repository (shared by all agents - same codebase)
resource "aws_ecr_repository" "multi_agent" {
  name                 = "${var.environment}_multi_agent"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }

  tags = merge(local.default_tags, {
    Name = "${var.environment}_multi_agent_ecr"
  })
}

# Build and push Docker image (once for all agents)
resource "null_resource" "pre_deploy" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command     = "./pre-deploy.sh"
    working_dir = "${path.module}/../multi-agent"
  }
}

resource "docker_image" "multi_agent" {
  name = "${aws_ecr_repository.multi_agent.repository_url}:${var.image_tag}"

  build {
    context    = "${path.module}/../multi-agent"
    dockerfile = "Dockerfile"
    platform   = "linux/arm64"
    no_cache   = true
  }

  triggers = {
    always_rebuild = timestamp()
  }
  
  depends_on = [null_resource.pre_deploy]
}

resource "docker_registry_image" "multi_agent" {
  name          = docker_image.multi_agent.name
  keep_remotely = false

  triggers = {
    always_push = timestamp()
  }

  depends_on = [docker_image.multi_agent]
}

# IAM role for AgentCore Runtime (shared by all agents)
resource "aws_iam_role" "agentcore_runtime" {
  name = "${var.environment}_multi_agent_runtime_role"
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
        Resource = aws_ecr_repository.multi_agent.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["lambda:InvokeFunction"]
        Resource = "arn:aws:lambda:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:function:strands-agents-aws-executor-*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:InvokeAgentRuntime"
        ]
        Resource = "arn:aws:bedrock-agentcore:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:agent-runtime/*"
      }
    ]
  })
}
