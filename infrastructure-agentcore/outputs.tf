output "runtime_id" {
  description = "AgentCore Runtime ID"
  value       = aws_bedrockagentcore_agent_runtime.main.agent_runtime_id
}

output "runtime_arn" {
  description = "AgentCore Runtime ARN"
  value       = aws_bedrockagentcore_agent_runtime.main.agent_runtime_arn
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.agent.repository_url
}

output "image_uri" {
  description = "Full Docker image URI"
  value       = "${aws_ecr_repository.agent.repository_url}:${var.image_tag}"
}

output "log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.agentcore_runtime.name
}

output "execution_role_arn" {
  description = "IAM execution role ARN"
  value       = aws_iam_role.agentcore_runtime.arn
}
