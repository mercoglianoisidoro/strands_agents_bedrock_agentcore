# Strands Agents Monorepo

Python monorepo demonstrating showcasing AI agents using the Strands framework and AWS Bedrock Agentcore.

## Content overview:

- **local agents**: Strands-based agents that execute locally
- **remote agentcore**: AWS Bedrock AgentCore agents (AWS cloud-native agent hosting)
- **shared utilities**: Common utilities, configuration classes, terminal interfaces, and reusable tools (e.g., Lambda executor)
- **clients**: Python clients for interacting with local and remote agents
- **web openui integration**: Functions for integrating agents into Open WebUI
- **litellm integration**: LiteLLM proxy configuration for OpenAI-compatible endpoints

The monorepo uses **UV workspace management** with a **shared virtual environment**, ensuring consistent dependencies across all components while maintaining modular development.

## Structure

```
strands_agents_bedrock_agentcore/
├── pyproject.toml                  # Root workspace configuration
├── uv.lock                         # Unified dependency lock file
├── .venv/                          # Shared virtual environment
├── local-agents/                   # Local Strands agents (Claude, Ollama, AWS Investigator)
│   ├── pyproject.toml
│   └── local_agents/
│       ├── claude/                 # Claude agent via Bedrock
│       ├── ollama/                 # Ollama local agent
│       └── aws_investigator/       # AWS infrastructure investigation agent
├── remote-agentcore/               # AWS Bedrock AgentCore deployment
│   ├── pyproject.toml
│   ├── pre-deploy.sh               # Workspace dependency sync
│   └── remote_agents/
│       └── remote_agent.py         # AgentCore entrypoint
├── shared/                         # Shared utilities and configurations
│   ├── pyproject.toml
│   └── strands_shared/
│       ├── config/                 # Base configuration classes
│       ├── terminal/               # Terminal interface
│       └── tools/                  # Custom tools (Lambda executor)
├── agentcore_client/               # Client library for deployed agents
│   ├── pyproject.toml
│   └── strands_agentcore_client/
├── web-openui-integration/         # Open WebUI integration
│   ├── agentcore_function.py       # Manual config
│   └── agentcore_function_auto.py  # Auto config from .bedrock_agentcore.yaml
└── litellm-integration/            # LiteLLM proxy for OpenAI-compatible API
    └── litellm_config.yaml
```

## Python Workspace

This monorepo uses **UV workspace** with a **shared virtual environment**:

- Single `.venv/` at root contains all dependencies from all workspace members
- Unified `uv.lock` ensures consistent versions across components
- Each component has its own `pyproject.toml` for dependency declaration
- Workspace members are automatically discovered and linked

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

## Uses cases

### Run local agents

```bash
source activate-locals.sh
python cli.py

```

or

```bash
local-agents/local_agents
uv run cli.py
```

To show the available agents:

`uv run cli.py --list-agents`,

then run with:

`uv run cli.py AGENT_NAME`,

### Run local "Aws Investigator agent"

In this case you need to provision the lambda from 'infrastructure-lambda' using an aws access with the right permissions:

```bash
cd infrastructure-lambda
terraform init
terraform apply --auto-approve
cd ..

cd local-agents/local_agents/
uv run cli.py aws_investigator
```

Note:

- the local aws credentials are used only to run the agent, not for connecting to the account
- in order for the LLM be able to connect to AWS, you need to provide the credentials directly to the LLM.






### Run remote agents with agentcore command

Use this for development.

```bash

source ./activate-remote.sh
agentcore deploy
cd ..

```

Then connect to is using the client:
```bash
cd agentcore_client/strands_agentcore_client
uv run cli.py

```


To destroy: `agentcore destroy`



### Run remote agents with terraform
You need to provision the agent (it needs the right permissions) and the you can connect to it:

```bash

cd strands_agents/remote-agentcore
bash pre-deploy.sh
cd ../../


cd infrastructure-agentcore
terraform init
terraform apply --auto-approve
cd ..
```

Then connect to is using the client
```bash
cd agentcore_client/strands_agentcore_client

uv run cli.py --agent-arn $(cd ../../infrastructure-agentcore && terraform output -raw runtime_arn)

```

Note: use `uv run cli.py --help` to get more info.

### Run AgentCore Gateway with Terraform

The gateway exposes Lambda functions as MCP tools with built-in authentication.

First, deploy the Lambda function:
```bash
cd infrastructure-lambda
terraform init
terraform apply --auto-approve
cd ..
```

Then deploy the gateway:
```bash
cd infrastructure_gateway
terraform init
terraform apply --auto-approve
cd ..
```

Test the gateway:
```bash
cd infrastructure_gateway

# List available tools
python test_gateway.py

# Call a tool
python test_gateway.py call <access_key> <secret_key> <region> "<aws-cli-command>"

# example (with not existing creds):
python test_gateway.py call AKIAIOSFODNN7EXAMPLE wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY us-east-1 "aws sts get-caller-identity"

```

The gateway uses IAM SigV4 authentication. Your AWS credentials must have `bedrock-agentcore:InvokeGateway` permission.

To destroy:
```bash
cd infrastructure_gateway && terraform destroy --auto-approve
cd ../infrastructure-lambda && terraform destroy --auto-approve
```

## TODO:
[] split lambda for the 2 different scenatios: agent and MCP (the payload is different)