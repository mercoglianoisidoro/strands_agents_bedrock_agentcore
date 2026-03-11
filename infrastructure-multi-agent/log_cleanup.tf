# Automatic cleanup of AgentCore-generated DEFAULT log groups
# These are created automatically by AWS when runtimes start

resource "null_resource" "cleanup_default_log_groups" {
  triggers = {
    region              = var.aws_region
    orchestrator_id     = try(aws_bedrockagentcore_agent_runtime.orchestrator.agent_runtime_id, "")
    aws_investigator_id = try(aws_bedrockagentcore_agent_runtime.aws_investigator.agent_runtime_id, "")
    validator_id        = try(aws_bedrockagentcore_agent_runtime.validator.agent_runtime_id, "")
  }

  # Clean up old DEFAULT log groups when runtimes are destroyed
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      echo "Cleaning up AgentCore DEFAULT log groups..."
      aws logs describe-log-groups \
        --region ${self.triggers.region} \
        --log-group-name-prefix "/aws/bedrock-agentcore/runtimes/" \
        --query 'logGroups[?contains(logGroupName, `-DEFAULT`)].logGroupName' \
        --output text 2>/dev/null | tr '\t' '\n' | while read log_group; do
        if [ -n "$log_group" ]; then
          echo "Deleting: $log_group"
          aws logs delete-log-group --log-group-name "$log_group" --region ${self.triggers.region} 2>/dev/null || true
        fi
      done
    EOT
  }

  depends_on = [
    aws_bedrockagentcore_agent_runtime.orchestrator,
    aws_bedrockagentcore_agent_runtime.aws_investigator,
    aws_bedrockagentcore_agent_runtime.validator
  ]
}
