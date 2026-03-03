# Orchestrator Agent
# Coordinates AWS Investigator and Validator via A2A protocol

locals {
  orchestrator_name = "${var.environment}_orchestrator_v2"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "orchestrator" {
  name              = "/aws/bedrock-agentcore/runtimes/${local.orchestrator_name}"
  retention_in_days = 7

  tags = local.default_tags
}

# AgentCore Runtime
resource "aws_bedrockagentcore_agent_runtime" "orchestrator" {
  agent_runtime_name = local.orchestrator_name
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
    AGENT_ENTRYPOINT = "orchestrator_entrypoint"
    MODEL_ID         = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    AWS_REGION       = data.aws_region.current.id
    
    # Worker agent ARNs for A2A communication
    AWS_INVESTIGATOR_ARN = aws_bedrockagentcore_agent_runtime.aws_investigator.agent_runtime_arn
    VALIDATOR_ARN        = aws_bedrockagentcore_agent_runtime.validator.agent_runtime_arn
  }

  tags = local.default_tags

  depends_on = [
    aws_bedrockagentcore_agent_runtime.aws_investigator,
    aws_bedrockagentcore_agent_runtime.validator
  ]
}
