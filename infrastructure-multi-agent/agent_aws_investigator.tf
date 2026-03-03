# AWS Investigator Agent
# Web search and AWS CLI investigation agent

locals {
  aws_investigator_name = "${var.environment}_aws_investigator"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "aws_investigator" {
  name              = "/aws/bedrock-agentcore/runtimes/${local.aws_investigator_name}"
  retention_in_days = 7

  tags = local.default_tags
}

# AgentCore Runtime
resource "aws_bedrockagentcore_agent_runtime" "aws_investigator" {
  agent_runtime_name = local.aws_investigator_name
  role_arn           = aws_iam_role.agentcore_runtime.arn

  agent_runtime_artifact {
    container_configuration {
      container_uri = "${aws_ecr_repository.multi_agent.repository_url}:${var.image_tag}"
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
    AGENT_ENTRYPOINT = "remote_entrypoint"
    MODEL_ID         = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    AWS_REGION       = data.aws_region.current.id
    SEARXNG_URL      = local.searxng_url
    MAX_RESULTS      = "5"
    
    # Lambda executor config
    AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR = "default"
    LAMBDA_FUNCTION_NAME = "strands-agents-aws-executor-${var.environment}"
  }

  tags = local.default_tags

  depends_on = [docker_registry_image.multi_agent]
}
