# Multi-Agent Infrastructure Deployment

This Terraform configuration deploys a complete multi-agent system on AWS Bedrock AgentCore with:
- **AWS Investigator**: Web search + AWS CLI investigation (Claude Sonnet 4)
- **Validator**: Independent evidence verification (Claude Haiku 3.5)
- **Orchestrator**: Coordinates both agents via A2A protocol (Claude Sonnet 4)

## Architecture

```
┌─────────────────────────────────────┐
│   Orchestrator Agent                │
│   (Claude Sonnet 4)                 │
│                                     │
│   - Analyzes user queries           │
│   - Routes to specialist agents     │
│   - Calls via A2A protocol          │
│   - Synthesizes responses           │
└──────────────┬──────────────────────┘
               │ A2A (boto3)
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────────┐    ┌─────────────┐
│ AWS Invest. │    │ Validator   │
│ (Sonnet 4)  │    │ (Haiku 3.5) │
│             │    │             │
│ - Web search│    │ - Verifies  │
│ - AWS CLI   │    │   claims    │
│ - SearxNG   │    │ - Re-checks │
└─────────────┘    └─────────────┘
```

## Infrastructure Components

1. **VPC & Networking**
   - Private subnet for agents
   - Security groups
   - NAT Gateway for outbound access

2. **SearxNG EC2 Instance**
   - Private metasearch engine
   - Accessible only from VPC
   - Used by AWS Investigator

3. **ECR Repository**
   - Single repository for all agents
   - Same Docker image, different entrypoints

4. **AgentCore Runtimes** (3 agents)
   - AWS Investigator
   - Validator
   - Orchestrator (with worker ARNs)

5. **IAM Roles & Policies**
   - Bedrock model access
   - ECR pull permissions
   - Lambda executor access
   - A2A invocation permissions

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Terraform** >= 1.0
3. **Docker** for building images
4. **Lambda executor** deployed (for AWS CLI execution)

## Deployment

### 1. Initialize Terraform

```bash
cd infrastructure-multi-agent
terraform init
```

### 2. Review Variables

Check `variables.tf` and create `terraform.tfvars`:

```hcl
environment = "dev"
aws_region  = "us-west-2"
image_tag   = "latest"
```

### 3. Deploy

```bash
terraform plan
terraform apply
```

This will:
1. Create VPC and networking
2. Launch SearxNG EC2 instance
3. Build and push Docker image to ECR
4. Deploy AWS Investigator agent
5. Deploy Validator agent
6. Deploy Orchestrator agent (with worker ARNs)

**Deployment time**: ~10-15 minutes

### 4. Get Agent ARNs

```bash
terraform output orchestrator_arn
terraform output aws_investigator_arn
terraform output validator_arn
```

## Testing

### Test Orchestrator (Recommended)

The orchestrator coordinates both agents:

```bash
cd ../agentcore_client/strands_agentcore_client
export ORCHESTRATOR_ARN=$(cd ../../infrastructure-multi-agent && terraform output -raw orchestrator_arn)
uv run cli.py --agent-arn $ORCHESTRATOR_ARN
```

Example queries:
- "What is AWS Lambda pricing?"
- "Verify that Lambda has 1M free requests per month"
- "List my EC2 instances and verify they're running"

### Test Individual Agents

**AWS Investigator**:
```bash
export AWS_INVESTIGATOR_ARN=$(cd ../../infrastructure-multi-agent && terraform output -raw aws_investigator_arn)
uv run cli.py --agent-arn $AWS_INVESTIGATOR_ARN
```

**Validator**:
```bash
export VALIDATOR_ARN=$(cd ../../infrastructure-multi-agent && terraform output -raw validator_arn)
uv run cli.py --agent-arn $VALIDATOR_ARN
```

## How It Works

### Persistent Worker Sessions

The orchestrator maintains **persistent sessions** with worker agents:
- AWS Investigator remembers fetched web pages (no re-fetching)
- Validator maintains verification history
- Multi-turn conversations work naturally

### A2A Communication

The orchestrator calls workers via boto3:

```python
client = boto3.client("bedrock-agentcore-runtime")
response = client.invoke_agent_runtime(
    agentRuntimeArn=os.getenv("AWS_INVESTIGATOR_ARN"),
    runtimeSessionId=session_id,
    payload=json.dumps({"prompt": query}).encode()
)
```

### Environment Variables

**Orchestrator receives**:
- `AWS_INVESTIGATOR_ARN`: ARN of AWS Investigator agent
- `VALIDATOR_ARN`: ARN of Validator agent

These are automatically set by Terraform during deployment.

## Monitoring

### CloudWatch Logs

Each agent has its own log group:
```bash
/aws/bedrock-agentcore/runtimes/dev_aws_investigator
/aws/bedrock-agentcore/runtimes/dev_validator
/aws/bedrock-agentcore/runtimes/dev_orchestrator
```

View logs:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/dev_orchestrator --follow
```

### Agent Status

Check agent status:
```bash
aws bedrock-agentcore describe-agent-runtime \
  --agent-runtime-arn $(terraform output -raw orchestrator_arn)
```

## Costs

Estimated monthly costs (us-west-2):
- **EC2 (t3.small)**: ~$15/month
- **NAT Gateway**: ~$32/month
- **AgentCore Runtime**: Pay per invocation
- **Bedrock Models**: Pay per token
- **ECR Storage**: ~$1/month

**Total infrastructure**: ~$50/month + usage costs

## Cleanup

```bash
terraform destroy
```

This will remove all resources including:
- AgentCore runtimes
- ECR repository and images
- EC2 instance
- VPC and networking

## Troubleshooting

### Agent fails to start

Check CloudWatch logs:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/dev_orchestrator --follow
```

### A2A calls fail

Verify IAM permissions include:
```json
{
  "Effect": "Allow",
  "Action": ["bedrock-agentcore-runtime:InvokeAgentRuntime"],
  "Resource": "arn:aws:bedrock-agentcore:*:*:agent-runtime/*"
}
```

### SearxNG not accessible

Check security group allows traffic from agent subnet:
```bash
terraform output searxng_security_group_id
```

## Files

- **`agent_shared.tf`**: Shared resources (ECR, IAM, Docker image)
- **`agent_aws_investigator.tf`**: AWS Investigator agent deployment
- **`agent_validator.tf`**: Validator agent deployment
- **`agent_orchestrator.tf`**: Orchestrator agent deployment (depends on workers)
- `vpc.tf`: VPC and networking
- `ec2_searxng.tf`: SearxNG instance
- `iam.tf`: Additional IAM roles
- `security_groups.tf`: Security groups
- `outputs.tf`: Output values
- `variables.tf`: Input variables

## Next Steps

1. **Add monitoring**: CloudWatch dashboards, alarms
2. **Add tests**: Integration tests for orchestration
3. **Production hardening**: Retry logic, rate limiting
4. **Cost optimization**: Reserved instances, spot instances

## References

- [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [A2A Protocol](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-a2a-protocol-contract.html)
- [Multi-Agent Best Practices](../multi-agent/docs/session-management-best-practices.md)
