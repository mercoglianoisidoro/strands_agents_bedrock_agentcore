# Enable CloudWatch Transaction Search for X-Ray traces
# This allows AgentCore to send OTEL traces and logs to CloudWatch

resource "aws_cloudwatch_log_resource_policy" "xray_transaction_search" {
  policy_name = "TransactionSearchXRayAccess"
  
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "TransactionSearchXRayAccess"
      Effect = "Allow"
      Principal = {
        Service = "xray.amazonaws.com"
      }
      Action = [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = [
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/spans:*",
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:aws/spans:*",
        "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/application-signals/data:*"
      ]
      Condition = {
        ArnLike = {
          "aws:SourceArn" = "arn:aws:xray:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
        }
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

# Create X-Ray spans log groups
resource "aws_cloudwatch_log_group" "xray_spans" {
  name              = "/aws/spans"
  retention_in_days = 7
}

# Conversation log group - structured A2A conversation tracing
resource "aws_cloudwatch_log_group" "conversations" {
  name              = "/aws/bedrock-agentcore/conversations"
  retention_in_days = 7
  tags              = local.default_tags
}

resource "aws_cloudwatch_log_group" "xray_spans_default" {
  name              = "/aws/spans/default"
  retention_in_days = 7
}

# Log group for OTEL traces from X-Ray
resource "aws_cloudwatch_log_group" "xray_otel_traces" {
  name              = "/aws/vendedlogs/xray/traces"
  retention_in_days = 7
}

# Configure X-Ray to send traces to CloudWatch Logs
resource "null_resource" "xray_trace_destination" {
  provisioner "local-exec" {
    command = "aws xray update-trace-segment-destination --region ${data.aws_region.current.name} --destination CloudWatchLogs || true"
  }
  
  depends_on = [
    aws_cloudwatch_log_resource_policy.xray_transaction_search,
    aws_cloudwatch_log_group.xray_spans
  ]
  
  triggers = {
    policy_version = aws_cloudwatch_log_resource_policy.xray_transaction_search.id
  }
}
