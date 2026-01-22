# Strands Agents Monorepo

Python monorepo showcasing:
- Strands agent implementation
- AWS bedrock Agentcore implementations

The monorepo uses UV workspace management with a shared virtual environment.


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
