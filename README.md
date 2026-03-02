# Strands Agents Monorepo

Python monorepo showcasing AI agents using the Strands framework and AWS Bedrock Agentcore.

## Content overview:

- **local agents**: Strands-based agents that execute locally (Claude, Ollama, AWS Investigator)
- **remote agentcore**: AWS Bedrock AgentCore agents (AWS cloud-native agent hosting)
- **shared utilities**: Common utilities, configuration classes, terminal interfaces, and reusable tools
- **clients**: Python clients for interacting with local and remote agents
- **infrastructure**: Terraform configurations for Lambda, AgentCore, and Gateway deployments
- **documentation**: Comprehensive guides on multi-agent patterns, authentication, and deployment
- **web openui integration**: Functions for integrating agents into Open WebUI
- **litellm integration**: LiteLLM proxy configuration for OpenAI-compatible endpoints
- **searxng setup**: Free web search integration for local agents

The monorepo uses **UV workspace management** with a **shared virtual environment**, ensuring consistent dependencies across all components while maintaining modular development.

## Structure

```
strands_agents/
├── pyproject.toml                  # Root workspace configuration
├── uv.lock                         # Unified dependency lock file
│
├── local-agents/                   # Local Strands agents
│   ├── pyproject.toml
│   └── local_agents/
│       ├── claude/                 # Claude agent via Bedrock
│       ├── ollama/                 # Ollama local agent
│       └── aws_investigator/       # AWS infrastructure investigation agent
│
├── remote-agentcore/               # AWS Bedrock AgentCore deployment
│   ├── pyproject.toml
│   ├── pre-deploy.sh               # Workspace dependency sync
│   └── remote_agents/
│       └── remote_agent.py         # AgentCore entrypoint
│
├── shared/                         # Shared utilities and configurations
│   ├── pyproject.toml
│   └── strands_shared/
│       ├── config/                 # Base configuration classes
│       ├── terminal/               # Terminal interface
│       └── tools/                  # Custom tools (Lambda executor)
│
├── agentcore_client/               # Client library for deployed agents
│   ├── pyproject.toml
│   └── strands_agentcore_client/
│
├── infrastructure-lambda/          # Lambda deployment (Terraform)
│   ├── main.tf
│   ├── lambda.tf
│   └── outputs.tf
│
├── infrastructure-agentcore/       # AgentCore deployment (Terraform)
│   ├── main.tf
│   ├── agentcore.tf
│   └── outputs.tf
│
├── infrastructure_gateway/         # AgentCore Gateway (Terraform)
│   ├── gateway.tf
│   ├── test_gateway.py
│   └── README.md
│
├── web-openui-integration/         # Open WebUI integration
│   ├── agentcore_function.py       # Manual config
│   └── agentcore_function_auto.py  # Auto config from .bedrock_agentcore.yaml
│
└── litellm-integration/            # LiteLLM proxy for OpenAI-compatible API
    └── litellm_config.yaml
```

## Python Workspace

This monorepo uses **UV workspace** with a **shared virtual environment**:

- Single `.venv/` at root contains all dependencies from all workspace members
- Unified `uv.lock` ensures consistent versions across components
- Each component has its own `pyproject.toml` for dependency declaration
- Workspace members are automatically discovered and linked

### Dependency Management Strategy

**Pattern: `pyproject.toml` (development) + `requirements.txt` (production)**

Each workspace package follows this best practice:

1. **`pyproject.toml`**: Development dependencies
   - All production dependencies (for reference)
   - Test dependencies in `[project.optional-dependencies]`
   - Workspace references: `strands-shared = { workspace = true }`
   - Used for local development with `uv sync`

2. **`requirements.txt`**: Production dependencies only
   - Pinned versions for reproducibility
   - No test dependencies (lean Docker images)
   - No workspace references (resolved to actual packages)
   - Used by Docker/production deployments

**Benefits:**
- ✅ Reproducible production builds (pinned `requirements.txt`)
- ✅ Rich development environment (test tools in `pyproject.toml`)
- ✅ Lean Docker images (no test dependencies)
- ✅ Workspace integration (local development uses shared packages)

**Example workflow:**
```bash
# Local development (includes test deps + workspace packages)
cd multi-agent
uv sync --extra test

# Production Docker (only runtime deps)
pip install -r requirements.txt
```

## Installation

**Required first step** - install all workspace packages:

```bash
uv sync --all-packages
```

This installs all workspace members (`local-agents`, `shared`, `remote-agentcore`, `agentcore_client`) and their dependencies into the shared `.venv/`.

## Activate Python Environment

```bash
# Manual activation
source .venv/bin/activate

# Or use convenience scripts
source activate-locals.sh   # Activates and cd to local-agents
source activate-shared.sh   # Activates and cd to shared
source activate-remote.sh   # Activates, cd to remote-agentcore, and runs pre-deploy.sh
```

## Running Code

### From Root Workspace

```bash
# Run module directly (no activation needed)
uv run python -m local_agents

# Or activate first
source .venv/bin/activate
python -m local_agents
```

### From Single Workspace

```bash
# Navigate to component
cd local-agents

# Run with shared venv
../.venv/bin/python -m local_agents

# Or activate and run
source ../.venv/bin/activate
python -m local_agents
```

## Development

### Adding Dependencies

```bash
# Edit the component's pyproject.toml
cd local-agents
# Add dependency to pyproject.toml

# Sync workspace
cd ..
uv sync --all-packages
```

## Use Cases

### 1. Run Local Agents

**Description**: Execute Strands agents locally (Claude, Ollama) without any infrastructure dependencies.

**Dependencies**: None

```
┌─────────────────┐
│  Local Agent    │
│  (Claude/Ollama)│
└─────────────────┘
```

**Usage**:
```bash
source activate-locals.sh
python cli.py

# Or directly
cd local-agents/local_agents
uv run cli.py

# List available agents
uv run cli.py --list-agents

# Run specific agent
uv run cli.py claude
```

---

### 2. Run AWS Investigator Agent (Local)

**Description**: Local agent that executes AWS CLI commands via Lambda for secure AWS operations.

**Dependencies**:
- ✅ Lambda infrastructure (Terraform)

```
┌─────────────────┐      ┌──────────────┐
│ AWS Investigator│─────▶│ Lambda       │
│ Agent (Local)   │      │ (AWS CLI)    │
└─────────────────┘      └──────────────┘
```

**Setup**:
```bash
# 1. Deploy Lambda
cd infrastructure-lambda
terraform init
terraform apply --auto-approve
cd ..

# 2. Run agent
cd local-agents/local_agents/
uv run cli.py aws_investigator
```

**Note**: Local AWS credentials are used only to run the agent. Provide AWS credentials directly to the LLM for AWS operations.

---

### 3. Run Remote Agents (AgentCore CLI)

**Description**: Deploy and run agents on AWS Bedrock AgentCore using the CLI (for development).

**Dependencies**:
- ✅ AWS credentials with AgentCore permissions

```
┌─────────────────┐      ┌──────────────────┐
│ AgentCore CLI   │─────▶│ Bedrock          │
│ (Local)         │      │ AgentCore Runtime│
└─────────────────┘      └──────────────────┘
```

**Usage - test locally**:
```bash
# Deploy
source ./activate-remote.sh
agentcore dev

# Connect with client
uv run agentcore invoke --dev "What is AWS Lambda?"

# Destroy
agentcore destroy
```

**Usage - deploy**:
```bash
# Deploy
source ./activate-remote.sh
agentcore deploy
cd ..

# Connect with client
cd agentcore_client/strands_agentcore_client
uv run cli.py

# Destroy
agentcore destroy
```

---

### 4. Run Remote Agents (Terraform)

**Description**: Deploy agents to AgentCore using Terraform for production deployments.

**Dependencies**:
- ✅ AWS credentials with AgentCore permissions
- ✅ Pre-deployment script execution

```
┌─────────────────┐      ┌──────────────────┐
│ Terraform       │─────▶│ Bedrock          │
│ (Infrastructure)│      │ AgentCore Runtime│
└─────────────────┘      └──────────────────┘
```

**Setup**:
```bash
# 1. Prepare deployment
cd strands_agents/remote-agentcore
bash pre-deploy.sh
cd ../../

# 2. Deploy with Terraform
cd infrastructure-agentcore
terraform init
terraform apply --auto-approve
cd ..

# 3. Connect with client
cd agentcore_client/strands_agentcore_client
uv run cli.py --agent-arn $(cd ../../infrastructure-agentcore && terraform output -raw runtime_arn)
```

**Tip**: Use `uv run cli.py --help` for more options.

---

### 5. Run AgentCore Gateway (MCP Tools)

**Description**: Expose Lambda functions as MCP tools with built-in IAM authentication via AgentCore Gateway.

**Dependencies**:
- ✅ Lambda infrastructure (Terraform)
- ✅ Gateway infrastructure (Terraform)

```
┌─────────────────┐      ┌──────────────┐      ┌──────────────┐
│ MCP Client      │─────▶│ AgentCore    │─────▶│ Lambda       │
│ (Agent)         │      │ Gateway      │      │ (MCP Tools)  │
└─────────────────┘      └──────────────┘      └──────────────┘
```

**Setup**:
```bash
# 1. Deploy Lambda
cd infrastructure-lambda
terraform init
terraform apply --auto-approve
cd ..

# 2. Deploy Gateway
cd infrastructure_gateway
terraform init
terraform apply --auto-approve
cd ..

# 3. Test Gateway
cd infrastructure_gateway

# List tools
python test_gateway.py

# Call a tool
python test_gateway.py call <access_key> <secret_key> <region> "<aws-cli-command>"

# Example
python test_gateway.py call AKIAIOSFODNN7EXAMPLE wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY us-east-1 "aws sts get-caller-identity"
```

**Authentication**: Gateway uses IAM SigV4. Your AWS credentials need `bedrock-agentcore:InvokeGateway` permission.

**Cleanup**:
```bash
cd infrastructure_gateway && terraform destroy --auto-approve
cd ../infrastructure-lambda && terraform destroy --auto-approve
```

---

### 6. Run Multi-Agent System (AgentCore)

**Description**: Deploy and test specialized agents (AWS Investigator, Validator) on AWS Bedrock AgentCore.

**Dependencies**:
- ✅ AWS credentials with AgentCore permissions

**Architecture**:
```
┌─────────────────────────────────────┐
│         Orchestrator                │
│   (Coordinates specialized agents)  │
└────────┬──────────────┬─────────────┘
         │              │
         ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│ AWS Investigator │  │    Validator     │
│                  │  │                  │
│ Investigates and │  │ Verifies claims  │
│ provides answers │  │ by re-checking   │
│ with evidence    │  │ evidence sources │
└──────────────────┘  └──────────────────┘
```

**Test Locally**:
```bash
cd multi-agent

# Test AWS Investigator (default)
uv run agentcore dev
# In another terminal:
uv run agentcore invoke --dev "What EC2 instances are running?"

# Switch to Validator
uv run agentcore configure set-default validator
uv run agentcore dev
# In another terminal:
uv run agentcore invoke --dev "Verify: Python 3.12 was released in 2023. Evidence: https://www.python.org/downloads/"

# Switch back to AWS Investigator
uv run agentcore configure set-default aws_investigator
```

**Deploy to AWS with agentcode sdk**:
```bash
cd multi-agent

# Deploy AWS Investigator
uv run agentcore deploy
export AWS_INVESTIGATOR_ARN=$(uv run agentcore status | grep "Agent ARN" | awk '{print $3}')

# Deploy Validator
uv run agentcore configure set-default validator
uv run agentcore deploy
export VALIDATOR_ARN=$(uv run agentcore status | grep "Agent ARN" | awk '{print $3}')

# Test deployed agents
cd ../agentcore_client/strands_agentcore_client
uv run cli.py --agent-arn $AWS_INVESTIGATOR_ARN
```

**Agents**:
- **AWS Investigator**: Web search + AWS CLI investigation (Claude Sonnet 4)
- **Validator**: Independent evidence verification (Claude Haiku 3.5)
  - Web URLs: Fetches and verifies content
  - AWS commands: Re-executes with provided credentials
- **Orchestrator**: Coordinates agents (coming soon)



## TODO:
[] split lambda for the 2 different scenarios: agent and MCP (the payload is different)