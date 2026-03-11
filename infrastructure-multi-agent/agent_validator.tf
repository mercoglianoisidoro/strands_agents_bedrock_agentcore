# Validator Agent
# Evidence verification agent

locals {
  validator_name = "${var.environment}_validator"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "validator" {
  name              = "/aws/bedrock-agentcore/runtimes/${local.validator_name}"
  retention_in_days = 7

  tags = local.default_tags
}

# AgentCore Runtime
resource "aws_bedrockagentcore_agent_runtime" "validator" {
  agent_runtime_name = local.validator_name
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
    AGENT_ENTRYPOINT = "validator_entrypoint"
    MODEL_ID         = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    AWS_REGION       = data.aws_region.current.id
    
    # Lambda executor config
    AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR = "default"
    LAMBDA_FUNCTION_NAME = "strands-agents-aws-executor-${var.environment}"
    
    # OTEL observability configuration
    AGENT_OBSERVABILITY_ENABLED         = "true"
    OTEL_PYTHON_DISTRO                  = "aws_distro"
    OTEL_PYTHON_CONFIGURATOR            = "aws_configurator"
    OTEL_EXPORTER_OTLP_PROTOCOL         = "http/protobuf"
    OTEL_TRACES_EXPORTER                = "otlp"
    OTEL_LOGS_EXPORTER                  = "otlp"
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT  = "https://xray.${data.aws_region.current.name}.amazonaws.com"
    OTEL_EXPORTER_OTLP_LOGS_PROTOCOL    = "http/protobuf"
    OTEL_RESOURCE_ATTRIBUTES            = "service.name=${local.validator_name},aws.log.group.names=/aws/bedrock-agentcore/runtimes/${local.validator_name}"
    OTEL_EXPORTER_OTLP_LOGS_HEADERS     = "x-aws-log-group=/aws/bedrock-agentcore/runtimes/${local.validator_name},x-aws-metric-namespace=bedrock-agentcore"
  }

  tags = local.default_tags

  depends_on = [docker_registry_image.multi_agent]
}
