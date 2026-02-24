variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "agent_name" {
  description = "Name of the AgentCore runtime (letters, numbers, underscores only)"
  type        = string
  default     = "remote_agent"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]{0,47}$", var.agent_name))
    error_message = "Agent name must start with a letter and contain only letters, numbers, and underscores (max 48 chars)."
  }
}

variable "model_id" {
  description = "Bedrock model ID"
  type        = string
  default     = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "docker_build_context" {
  description = "Path to Docker build context"
  type        = string
  default     = "../remote-agentcore/remote_agents"
}

variable "iam_role_name_prefix" {
  description = "Prefix for IAM role name"
  type        = string
  default     = "agentcore-runtime-"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
