resource "aws_iam_role" "gateway" {
  name = "${local.gateway_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AmazonBedrockAgentCoreGatewayBasePolicyProd"
      Effect = "Allow"
      Principal = {
        Service = "bedrock-agentcore.amazonaws.com"
      }
      Action = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:bedrock-agentcore:${var.region}:${data.aws_caller_identity.current.account_id}:gateway/${local.gateway_name}-*"
        }
      }
    }]
  })

  tags = local.default_tags
}

resource "aws_iam_role_policy" "gateway_lambda" {
  name = "${local.gateway_name}-lambda-invoke"
  role = aws_iam_role.gateway.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = var.lambda_arn
    }]
  })
}

resource "aws_bedrockagentcore_gateway" "main" {
  name            = local.gateway_name
  protocol_type   = "MCP"
  authorizer_type = "AWS_IAM"
  role_arn        = aws_iam_role.gateway.arn
  exception_level = "DEBUG"

  tags = local.default_tags
}

resource "aws_bedrockagentcore_gateway_target" "lambda" {
  gateway_identifier = aws_bedrockagentcore_gateway.main.gateway_id
  name               = "LambdaAWSExecutor"

  target_configuration {
    mcp {
      lambda {
        lambda_arn = var.lambda_arn

        tool_schema {
          inline_payload {
            name        = "AWS"
            description = "Execute AWS CLI commands to retrieve information from AWS infrastructure"

            input_schema {
              type = "object"

              property {
                name        = "AWS_ACCESS_KEY_ID"
                type        = "string"
                description = "AWS_ACCESS_KEY_ID to connect to the AWS account"
                required    = true
              }

              property {
                name        = "AWS_SECRET_ACCESS_KEY"
                type        = "string"
                description = "AWS_SECRET_ACCESS_KEY to connect to the AWS account"
                required    = true
              }

              property {
                name        = "AWS_SESSION_TOKEN"
                type        = "string"
                description = "AWS_SESSION_TOKEN to connect to the AWS account. Optional"
                required    = false
              }

              property {
                name        = "REGION"
                type        = "string"
                description = "AWS region. Example: eu-west-1, us-west-2"
                required    = true
              }

              property {
                name        = "bash_command"
                type        = "string"
                description = "AWS CLI command to run. Always include '--output text'"
                required    = true
              }
            }
          }
        }
      }
    }
  }

  credential_provider_configuration {
    gateway_iam_role {}
  }
}
