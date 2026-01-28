# Container Deployment for AgentCore

Terraform infrastructure for deploying the remote AgentCore agent as a container.

> **Note**: This directory contains only the **deployment infrastructure**. For information about the agent itself, its functionality, and local development, see the [remote-agentcore README](../remote-agentcore/README.md).

## What This Does

Terraform automates the entire deployment:
1. Creates ECR repository for container images
2. Builds ARM64 Docker image from your agent code
3. Pushes image to ECR
4. Creates IAM role with Bedrock/CloudWatch permissions
5. Deploys AgentCore Runtime with the container

## Prerequisites

- Docker installed and running
- AWS CLI configured with credentials
- Terraform >= 1.0

## Quick Start

```bash
cd infrastructure-agentcore
terraform init
terraform apply
```

## Update Agent Code

After modifying agent code:

```bash
cd infrastructure-agentcore
terraform apply
```

Terraform automatically:
- Rebuilds the Docker image (no cache)
- Pushes new image to ECR
- Updates the AgentCore Runtime

## Architecture

### Directory Structure
```
infrastructure-agentcore/
├── main.tf              # All resources
├── variables.tf         # Configuration
├── outputs.tf           # Runtime ARN, ECR URL, etc.
└── README.md           # This file

remote-agentcore/
├── remote_agents/
│   ├── remote_agent.py      # Agent entrypoint
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Container definition
│   └── strands_shared/     # Synced from workspace
└── pre-deploy.sh           # Dependency sync script
```

### Key Resources

**IAM Role** (`aws_iam_role.agentcore_runtime`)
- Execution role for the agent
- Permissions: Bedrock (all regions), CloudWatch Logs, ECR

**IAM Policy** (`aws_iam_role_policy.agentcore_runtime`)
- Attached to the role
- Grants access to foundation models and inference profiles

**Docker Image** (`docker_image.agent`)
- Built from `../remote-agentcore/remote_agents/`
- Platform: `linux/arm64` (required by AgentCore)
- No cache: Forces rebuild every time

**ECR Push** (`docker_registry_image.agent`)
- Pushes built image to ECR
- Authenticates automatically via AWS provider

**AgentCore Runtime** (`aws_bedrockagentcore_agent_runtime.main`)
- The actual running agent
- Uses the IAM role for AWS API calls
- Pulls container from ECR
- Network mode: PUBLIC

## Configuration

Edit `variables.tf` to customize:
- `agent_name`: Runtime name (default: "remote_agent")
- `image_tag`: Docker tag (default: "latest")
- `log_retention_days`: CloudWatch retention (default: 7)
- `model_id`: Bedrock model to use

## Outputs

After deployment:
```bash
terraform output runtime_arn        # Use for invocations
terraform output ecr_repository_url # Container registry
terraform output execution_role_arn # IAM role ARN
terraform output log_group          # CloudWatch logs
```

## Testing

Invoke the deployed agent:
```bash
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn $(terraform output -raw runtime_arn) \
  --payload '{"prompt":"hello"}' \
  --region us-west-2
```

View logs:
```bash
aws logs tail $(terraform output -raw log_group) --follow --region us-west-2
```

## Cleanup

Remove all resources:
```bash
terraform destroy
```

## Force Rebuild

Terraform always rebuilds (no cache), but to force recreation:
```bash
terraform taint docker_image.agent
terraform apply
```
