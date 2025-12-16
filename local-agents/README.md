# Local Agents

Local Strands agents for interactive  agents with terminal interface. Includes Claude (AWS Bedrock), Ollama, and AWS Investigator implementations.

## Available Agents

### Claude
AWS Bedrock-based agent using Claude models for general-purpose tasks.
- **Model**: Claude 3.5 Haiku (configurable)
- **Tools**: File operations, HTTP requests, environment access, time utilities
- **Use case**: General development, AWS interactions via Bedrock

### Ollama
Local Ollama-based agent for offline development.
- **Model**: Granite4 (configurable)
- **Tools**: File operations, HTTP requests, AWS CLI, time utilities
- **Use case**: Offline development, local testing

### AWS Investigator
Specialized agent for AWS infrastructure investigation with Lambda executor.

**NOTE:** Lambda code still to be committed.

- **Model**: Claude 3.5 Haiku via Bedrock
- **Tools**: All Claude tools + Lambda AWS CLI executor + MCP clients (AWS docs, browser)
- **Use case**: AWS troubleshooting, infrastructure analysis

## Installation

This package is part of the strands_agents workspace. Install from workspace root:

```bash
# Install all packages
uv sync --all-packages
```

## Usage

### Command Line

```bash
# Activate workspace environment
source .venv/bin/activate

# Run default agent (Claude)
python -m local_agents

# Run specific agent
python -m local_agents claude
python -m local_agents ollama
python -m local_agents aws_investigator

# List available agents
python -m local_agents --list-agents

# Set log level
python -m local_agents claude --log-level DEBUG

# Show help
python -m local_agents --help
```

### Programmatic Usage

```python
from local_agents import (
    create_agent__claude,
    create_agent__ollama,
    create_agent__aws_investigator,
    AgentWrapper
)
from strands_shared.terminal import Terminal

# Create and wrap agent
agent = create_agent__claude()
wrapped = AgentWrapper(agent)

# Start interactive terminal
terminal = Terminal(wrapped)
await terminal.start()
```

## Configuration

Each agent requires environment variables configured in its `.env` file:

### Claude Agent (`local_agents/claude/.env`)
```bash
LOG_LEVEL=INFO
LOG_COLORS=true
CLAUDE_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0
AWS_REGION=us-west-2
SYSTEM_PROMPT_PATH=system_prompt.md
```

### Ollama Agent (`local_agents/ollama/.env`)
```bash
LOG_LEVEL=INFO
LOG_COLORS=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=granite4:latest
SYSTEM_PROMPT_PATH=system_prompt.md
```

### AWS Investigator (`local_agents/aws_investigator/.env`)
```bash
LOG_LEVEL=INFO
LOG_COLORS=true
CLAUDE_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0
AWS_REGION=us-west-2
SYSTEM_PROMPT_PATH=system_prompt.md
AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR=your-aws-profile-name
```

**Note**: Copy `.env.example` files to `.env` and customize for your environment.

## Terminal Interface

The terminal interface supports:
- **Single-line input**: Type and press Enter
- **Multi-line input**: Press Option+Enter (macOS) or Alt+Enter (Windows/Linux) to add newlines
- **Paste support**: Multi-line paste is automatically detected
- **Commands**: Type `exit` or `quit` to end session
- **Interrupts**: Ctrl+C or Ctrl+D for graceful exit

## Dependencies

- `strands-shared`: Shared utilities (workspace dependency)
- `strands-agents`: Core agent framework
- `strands-agents-tools`: Pre-built tools
- `bedrock-agentcore`: AWS Bedrock agent runtime
- `boto3`, `botocore`: AWS SDK
- `mcp`: Model Context Protocol
- `ollama`: Ollama Python client
- `playwright`: Browser automation
- `opencv-python`: Image processing
- `pytesseract`: OCR capabilities
- `numpy`, `pillow`: Image manipulation
- `rich`: Terminal formatting

## Project Structure

```
local-agents/
├── local_agents/
│   ├── __init__.py          # Public API exports
│   ├── cli.py               # CLI entry point
│   ├── agent_wrapper.py     # Agent message capture wrapper
│   ├── py.typed             # Type checking marker
│   ├── claude/              # Claude agent
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── .env.example
│   │   └── system_prompt.md
│   ├── ollama/              # Ollama agent
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── .env.example
│   │   └── system_prompt.md
│   └── aws_investigator/    # AWS Investigator agent
│       ├── agent.py
│       ├── config.py
│       ├── .env.example
│       └── system_prompt.md
├── pyproject.toml
└── README.md
```

## Development

This package is part of the strands_agents monorepo workspace. See the [workspace README](../README.md) for setup instructions.

### Type Checking

The package includes a `py.typed` marker for full type checking support:
```bash
mypy local_agents
```

### Adding New Agents

1. Create new directory under `local_agents/`
2. Add `agent.py`, `config.py`, `.env.example`, `system_prompt.md`
3. Register in `cli.py` `AGENT_TYPES` dictionary
4. Export creation function in `__init__.py`

## Troubleshooting

### "No module named 'strands_shared'"
Ensure the workspace is properly set up:
```bash
cd /path/to/strands_agents
uv sync --all-packages
```

### AWS Credentials Issues
For AWS Investigator, ensure:
- `AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR` is set in `.env`
- The profile exists in `~/.aws/credentials`
- The profile has permissions to invoke the Lambda function

### Logging
Increase log level for debugging:
```bash
python -m local_agents claude --log-level DEBUG
```
