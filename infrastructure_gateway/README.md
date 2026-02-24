# Strands Agents Gateway Infrastructure

Terraform configuration for AWS Bedrock AgentCore Gateway.

## Prerequisites

- Lambda function already deployed (from infrastructure-lambda)
- Lambda permission for bedrock-agentcore.amazonaws.com

## Usage

```bash
terraform init
terraform plan
terraform apply
```

## Resources Created

- AgentCore Gateway (MCP protocol, AWS IAM auth)
- Gateway Target (Lambda with tool schema)

## Outputs

- `gateway_url`: MCP endpoint URL
- `gateway_id`: Gateway identifier
- `target_id`: Target identifier
