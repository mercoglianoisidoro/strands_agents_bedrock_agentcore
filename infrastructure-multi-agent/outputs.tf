output "searxng_private_ip" {
  description = "Private IP of SearxNG EC2 instance"
  value       = aws_instance.searxng.private_ip
}

output "searxng_url" {
  description = "SearxNG URL for AgentCore"
  value       = "http://${aws_instance.searxng.private_ip}:8080"
}

output "searxng_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.searxng.id
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.multi_agent.id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = aws_subnet.searxng_private.id
}

output "searxng_security_group_id" {
  description = "SearxNG security group ID"
  value       = aws_security_group.searxng.id
}

output "admin_ip_used" {
  description = "Admin IP CIDR used for SSH access"
  value       = local.admin_ip
}

output "test_search_command" {
  description = "Command to test SearxNG search (run from within VPC or via SSH tunnel)"
  value       = "curl 'http://${aws_instance.searxng.private_ip}:8080/search?q=test&format=json'"
}

output "ssh_command" {
  description = "SSH command to access the instance"
  value       = "aws ssm start-session --target ${aws_instance.searxng.id} --region ${var.aws_region}"
}

output "agent_runtime_arn" {
  description = "ARN of the AgentCore runtime"
  value       = aws_bedrockagentcore_agent_runtime.web_search.agent_runtime_arn
}

output "agent_runtime_id" {
  description = "ID of the AgentCore runtime"
  value       = aws_bedrockagentcore_agent_runtime.web_search.agent_runtime_id
}

output "agent_runtime_name" {
  description = "Name of the AgentCore runtime"
  value       = var.agent_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for the agent"
  value       = aws_ecr_repository.web_search_agent.repository_url
}

output "agent_image_uri" {
  description = "Full Docker image URI"
  value       = "${aws_ecr_repository.web_search_agent.repository_url}:${var.image_tag}"
}

output "test_agent_command" {
  description = "Command to test the agent using agentcore_client"
  value       = "cd agentcore_client/strands_agentcore_client && uv run cli.py --agent-arn ${aws_bedrockagentcore_agent_runtime.web_search.agent_runtime_arn}"
}
