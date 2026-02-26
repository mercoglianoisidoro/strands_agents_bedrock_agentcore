variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type for SearxNG"
  type        = string
  default     = "t3.small"
}

variable "admin_ip_cidr" {
  description = "Admin IP CIDR for SSH access (leave empty to auto-detect)"
  type        = string
  default     = ""
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "multi-agent-prototype"
}

# AgentCore variables
variable "agent_name" {
  description = "Name of the web search agent"
  type        = string
  default     = "web_search_agent"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]{0,47}$", var.agent_name))
    error_message = "Agent name must start with a letter and contain only letters, numbers, and underscores (max 48 chars)."
  }
}

variable "model_id" {
  description = "Bedrock model ID for the agent"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "docker_build_context" {
  description = "Path to Docker build context (multi-agent directory)"
  type        = string
  default     = "../multi-agent"
}

variable "iam_role_name_prefix" {
  description = "Prefix for IAM role name"
  type        = string
  default     = "web-search-agentcore-"
}

