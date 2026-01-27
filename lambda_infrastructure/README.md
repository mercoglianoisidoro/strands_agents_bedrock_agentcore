# Lambda Infrastructure

AWS infrastructure for Strands Agents Lambda functions and supporting resources.

## Overview

This Terraform configuration deploys:
- Lambda function for AWS CLI command execution
- S3 bucket for Lambda layers storage
- Lambda layers (jq, AWS CLI)
- IAM roles and policies for Lambda execution
- CloudWatch log groups for debugging

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured
- AWS profile with permissions for:
  - Lambda (create/update functions, layers)
  - S3 (create/manage buckets)
  - IAM (create/manage roles and policies)
  - CloudWatch Logs (create log groups)

## Configuration

Create a `terraform.tfvars` file (use `terraform.tfvars.example` as template):

```hcl
environment = "dev"
region      = "us-west-2"
profile     = "your-aws-profile"
```

## Deployment

```bash
# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply infrastructure
terraform apply

# Destroy infrastructure
terraform destroy
```

## File Structure

```
lambda_infrastructure/
├── main.tf                    # Provider and backend configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── lambda-aws.tf              # Lambda function configuration
├── lambda_layers.tf           # Lambda layers
├── buckets.tf                 # S3 bucket resources
├── lambda_aws_source_code/    # Lambda function source code
│   ├── aws.sh                 # Main Lambda handler
│   └── bootstrap              # Lambda runtime bootstrap
├── lambda-layers-files/       # Pre-built Lambda layers (not in git)
└── provision_and_update_conf.sh  # Deployment helper script
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `environment` | Deployment environment | `dev`, `staging`, `prod` |
| `region` | AWS region | `us-west-2` |
| `profile` | AWS CLI profile | `isipilot-infra-admin` |

## Resources Created

- **Lambda Function:** `strands-agents-aws-executor-{env}`
- **S3 Bucket:** `strands-agents-layers-{env}`
- **IAM Role:** `strands-agents-lambda-exec-{env}`
- **IAM Policy:** `strands-agents-s3-access-{env}`
- **Log Group:** `strands-agents-debug-{env}`
