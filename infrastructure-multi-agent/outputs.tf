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

# Multi-Agent Outputs
output "aws_investigator_arn" {
  description = "ARN of the AWS Investigator agent runtime"
  value       = aws_bedrockagentcore_agent_runtime.aws_investigator.agent_runtime_arn
}

output "validator_arn" {
  description = "ARN of the Validator agent runtime"
  value       = aws_bedrockagentcore_agent_runtime.validator.agent_runtime_arn
}

output "orchestrator_arn" {
  description = "ARN of the Orchestrator agent runtime"
  value       = aws_bedrockagentcore_agent_runtime.orchestrator.agent_runtime_arn
}

output "ecr_repository_url" {
  description = "ECR repository URL for all agents"
  value       = aws_ecr_repository.multi_agent.repository_url
}

output "test_commands" {
  description = "Commands to test the deployed agents"
  value = <<-EOT
    # Test AWS Investigator
    cd agentcore_client/strands_agentcore_client
    uv run cli.py --agent-arn ${aws_bedrockagentcore_agent_runtime.aws_investigator.agent_runtime_arn}
    
    # Test Validator
    uv run cli.py --agent-arn ${aws_bedrockagentcore_agent_runtime.validator.agent_runtime_arn}
    
    # Test Orchestrator (recommended - coordinates both agents)
    uv run cli.py --agent-arn ${aws_bedrockagentcore_agent_runtime.orchestrator.agent_runtime_arn}
  EOT
}
