# Multi-Agent Web Search System

A production-ready multi-agent system implementing the "Agents as Tools" pattern with A2A protocol support. Features a specialized web search agent powered by SearxNG metasearch engine.

## Architecture

```
┌─────────────────────────────────────────┐
│ AWS VPC (10.0.0.0/16)                   │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ AgentCore    │───▶│ EC2          │  │
│  │ Web Search   │HTTP│ SearxNG      │  │
│  │ Agent        │8080│ (Private)    │  │
│  └──────────────┘    └──────────────┘  │
│         ▲                    │          │
│         │                    ▼          │
│         │              NAT Gateway      │
│         │                    │          │
└─────────┼────────────────────┼──────────┘
          │ A2A                │ HTTPS
          │                    ▼
   Orchestrator           Internet
   Agent                  (70+ engines)
```

## Features

### Security
- ✅ **Network isolation**: SearxNG in private subnet
- ✅ **Least privilege IAM**: CloudWatch logs only
- ✅ **Encrypted storage**: EBS volumes encrypted at rest
- ✅ **IMDSv2 enforced**: Secure instance metadata
- ✅ **VPC Flow Logs**: Network traffic monitoring

### Scalability
- ✅ **AgentCore Runtime**: Serverless agent execution
- ✅ **Docker deployment**: Easy updates and rollbacks
- ✅ **Auto-restart**: Container failure recovery

### Observability
- ✅ **CloudWatch Logs**: Centralized logging
- ✅ **VPC Flow Logs**: Network monitoring
- ✅ **Structured logging**: JSON format

## Directory Structure

```
multi-agent/
├── multi_agents/
│   ├── __init__.py
│   ├── remote_entrypoint.py      # AgentCore entrypoint
│   └── web_search/
│       ├── __init__.py
│       ├── agent.py               # Agent creation
│       ├── config.py              # Configuration
│       ├── tools/
│       │   ├── __init__.py
│       │   └── searxng_tool.py   # SearxNG integration
│       └── prompts/
│           └── system_prompt.txt # Agent instructions
├── tests/
│   ├── test_agent.py
│   └── test_searxng_tool.py
├── docs/                          # Design documentation
├── pyproject.toml
└── README.md

infrastructure-multi-agent/
├── main.tf                        # Provider configuration
├── vpc.tf                         # VPC, subnets, NAT
├── ec2_searxng.tf                # EC2 instance
├── security_groups.tf            # Security groups
├── iam.tf                        # IAM roles
├── monitoring.tf                 # CloudWatch, Flow Logs
├── user_data.sh                  # Bootstrap script
├── variables.tf                  # Input variables
├── outputs.tf                    # Outputs
└── terraform.tfvars.example      # Configuration template
```

## Quick Start

### Prerequisites

```bash
# Install dependencies
brew install terraform awscli

# Configure AWS credentials
aws configure

# Install Python dependencies
cd multi-agent
pip install -e .
```

### 1. Deploy Infrastructure

```bash
cd infrastructure-multi-agent

# Configure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your IP

# Deploy
terraform init
terraform apply

# Save SearxNG URL
export SEARXNG_URL=$(terraform output -raw searxng_url)
```

### 2. Test Locally (Optional)

```bash
# Start local SearxNG for testing
cd ../searxng_setup
docker compose up -d

# Test agent locally
cd ../multi-agent
export SEARXNG_URL="http://localhost:8080"
python -c "
from multi_agents.web_search import create_web_search_agent
agent = create_web_search_agent()
print(agent('Search for AWS Bedrock'))
"
```

### 3. Deploy to AgentCore

```bash
cd multi-agent

# Set environment
export SEARXNG_URL=$(cd ../infrastructure-multi-agent && terraform output -raw searxng_url)
export AWS_REGION="us-west-2"

# Deploy
agentcore deploy \
  --name web-search-agent \
  --entrypoint multi_agents.remote_entrypoint:app \
  --environment "SEARXNG_URL=${SEARXNG_URL}" \
  --environment "AWS_REGION=${AWS_REGION}"
```

### 4. Test Deployed Agent

```bash
# Invoke agent
agentcore invoke \
  --agent-name web-search-agent \
  --prompt "Search for Python best practices"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_URL` | `http://localhost:8080` | SearxNG endpoint |
| `MODEL_ID` | `us.amazon.nova-pro-v1:0` | Bedrock model ID |
| `AWS_REGION` | `us-west-2` | AWS region |
| `MAX_RESULTS` | `5` | Max search results |
| `SEARXNG_TIMEOUT` | `10` | Request timeout (seconds) |

### Infrastructure Variables

Edit `infrastructure-multi-agent/terraform.tfvars`:

```hcl
aws_region     = "us-west-2"
instance_type  = "t3.small"
admin_ip_cidr  = "YOUR_IP/32"  # Your IP for SSH
project_name   = "multi-agent-prototype"
```

## Testing

```bash
cd multi-agent

# Run tests (requires SearxNG running)
export SEARXNG_URL="http://localhost:8080"
pytest tests/

# Test specific module
pytest tests/test_searxng_tool.py -v
```

## Cost Estimate

| Component | Monthly Cost |
|-----------|--------------|
| EC2 t3.small (24/7) | ~$15 |
| NAT Gateway | ~$32 |
| EBS 20GB gp3 | ~$2 |
| CloudWatch Logs | ~$1 |
| AgentCore (1000 searches) | ~$10-20 |
| **Total** | **~$60-70/month** |

## Maintenance

### Update SearxNG

```bash
# SSH to EC2 (via Systems Manager)
aws ssm start-session --target $(cd infrastructure-multi-agent && terraform output -raw searxng_instance_id)

# Update container
cd /opt/searxng
docker-compose pull
docker-compose up -d
```

### View Logs

```bash
# CloudWatch logs
aws logs tail /aws/ec2/searxng --follow

# VPC Flow Logs
aws logs tail /aws/vpc/multi-agent-prototype-flow-logs --follow
```

### Destroy Infrastructure

```bash
cd infrastructure-multi-agent
terraform destroy
```

## Security Best Practices

### Network
- SearxNG has no public IP (private subnet only)
- NAT Gateway for outbound traffic only
- Security groups restrict access to VPC CIDR
- VPC Flow Logs enabled for monitoring

### Access Control
- IAM roles follow least privilege principle
- EC2 instance profile: CloudWatch logs only
- SSH access restricted to admin IP
- IMDSv2 enforced on EC2

### Encryption
- EBS volumes encrypted at rest
- CloudWatch logs encrypted (default KMS)
- Secrets should use AWS Secrets Manager

### Monitoring
- CloudWatch Logs for application logs
- VPC Flow Logs for network traffic
- CloudWatch metrics for EC2 health

## Troubleshooting

### SearxNG not responding

```bash
# Check EC2 instance
aws ec2 describe-instances --instance-ids <instance-id>

# Check Docker container
aws ssm start-session --target <instance-id>
docker ps
docker logs searxng
```

### Agent deployment fails

```bash
# Check AgentCore logs
agentcore logs --agent-name web-search-agent

# Verify environment variables
agentcore describe --agent-name web-search-agent
```

### Search timeouts

```bash
# Increase timeout
export SEARXNG_TIMEOUT=20

# Or update agent configuration
agentcore update \
  --agent-name web-search-agent \
  --environment "SEARXNG_TIMEOUT=20"
```

## Development

### Local Development

```bash
# Start local SearxNG
cd searxng_setup
docker compose up -d

# Install in development mode
cd ../multi-agent
pip install -e .

# Run agent locally
python -c "
from multi_agents.web_search import create_web_search_agent
agent = create_web_search_agent()
print(agent('Test search'))
"
```

### Adding New Tools

1. Create tool in `multi_agents/web_search/tools/`
2. Import in `agent.py`
3. Add to agent's tools list
4. Update system prompt if needed
5. Add tests

### Code Style

```bash
# Format code
black multi_agents/

# Lint
ruff check multi_agents/

# Type check
mypy multi_agents/
```

## References

- [Design Documentation](./docs/README.md)
- [Infrastructure Design](./docs/infrastructure-design-secure.md)
- [Implementation Proposal](./docs/multi-agent-web-search-proposal.md)
- [Strands Documentation](https://strandsagents.com)
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [SearxNG Documentation](https://docs.searxng.org/)

## License

See repository root for license information.
