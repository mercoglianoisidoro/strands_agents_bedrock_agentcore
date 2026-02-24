output "gateway_id" {
  value       = aws_bedrockagentcore_gateway.main.gateway_id
  description = "Gateway ID"
}

output "gateway_arn" {
  value       = aws_bedrockagentcore_gateway.main.gateway_arn
  description = "Gateway ARN"
}

output "gateway_url" {
  value       = aws_bedrockagentcore_gateway.main.gateway_url
  description = "Gateway MCP URL"
}

output "target_id" {
  value       = aws_bedrockagentcore_gateway_target.lambda.target_id
  description = "Target ID"
}
