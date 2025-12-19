# Strands Agents Monorepo

Python monorepo for Strands agent components using UV workspace management with a shared virtual environment.

## Structure

```
strands_agents/
├── pyproject.toml         # Root workspace configuration
├── uv.lock                # Unified dependency lock file
├── .venv/                 # Shared virtual environment
├── local-agents/          # Local Strands agents (Claude, Ollama)
│   ├── pyproject.toml
│   └── local_agents/
└── shared/                # Shared utilities and configurations
    ├── pyproject.toml
    └── strands_shared/
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

This installs both workspace members (`local-agents`, `shared`) and all their dependencies into the shared `.venv/`.

## Activate Python Environment

```bash
# Manual activation
source .venv/bin/activate

# Or use convenience scripts
source activate-locals.sh   # Activates and cd to local-agents
source activate-shared.sh   # Activates and cd to shared
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
