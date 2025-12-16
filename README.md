# Strands Agents Monorepo

UV workspace with shared virtual environment for Strands agent components.

## Structure

```
strands_agents/
├── pyproject.toml         # Workspace configuration
├── .venv/                 # Shared virtual environment
├── local-agents/          # Local Strands agents (Claude, Ollama)
│   ├── pyproject.toml
│   └── local_agents/
└── shared/                # Shared utilities and configurations
    ├── pyproject.toml
    └── strands_shared/
```

## Setup

```bash
# Initial setup
uv sync --all-packages --extra dev

# Activate environment
source .venv/bin/activate
```

Or use activation scripts:
```bash
source activate-locals.sh  # Activates and cd to local-agents
source activate-shared.sh  # Activates and cd to shared
```

## Running

```bash
# After activation
python -m local_agents

# Or directly
.venv/bin/python -m local_agents

# With arguments
python -m local_agents aws_investigator
```

## Development

### Adding Dependencies
1. Edit the appropriate `pyproject.toml` file
2. Run `uv sync --all-packages`

### Running Code Directly
```bash
# From package directory (no activation needed)
cd local-agents
python local_agents

# Or with the venv python
.venv/bin/python -m local_agents
```
