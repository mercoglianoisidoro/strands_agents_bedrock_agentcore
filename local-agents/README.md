# Local Agents

Local agent implementations built with the Strands agents framework. These agents run on your local machine and can be accessed via CLI using the terminal component from `strands_shared`.

## Overview

This package provides three pre-configured agent implementations for different use cases:
- **Claude**: Cloud-based general-purpose agent via AWS Bedrock
- **Ollama**: Fully offline local agent for privacy-sensitive work
- **AWS Investigator**: Specialized agent for AWS infrastructure troubleshooting

All agents share the same terminal interface and configuration patterns, making it easy to switch between them based on your needs.

## Available Agents

### Claude
**Purpose:** General-purpose development assistant powered by AWS Bedrock.

Uses Claude 3.5 Haiku (configurable) for fast, cost-effective interactions. Ideal for everyday development tasks, code generation, and AWS-related questions.

**Tools:**
- File operations (read, write)
- HTTP requests
- Environment variable access
- Current time utilities

**Best for:** General development, AWS interactions, code assistance

---

### Ollama
**Purpose:** Fully offline local agent for privacy-sensitive or air-gapped environments.

Runs entirely on your machine using Ollama with Granite4 (configurable). No data leaves your computer, making it suitable for sensitive codebases or offline work.

**Tools:**
- File operations (read, write)
- HTTP requests
- AWS CLI commands (local execution)
- Current time utilities

**Best for:** Offline development, privacy-sensitive work, local testing

---

### AWS Investigator
**Purpose:** Specialized agent for AWS infrastructure investigation and troubleshooting.

Combines Claude's intelligence with AWS-specific tools, including remote AWS CLI execution via Lambda. Designed for diagnosing infrastructure issues, analyzing configurations, and automating AWS operations.

**Tools:**
- All Claude tools (file ops, HTTP, environment, time)
- Lambda AWS CLI executor (remote cross-account execution)
- MCP clients:
  - AWS Documentation (awslabs.aws-documentation-mcp-server)
  - Browser automation (for AWS Console inspection)

**Best for:** AWS troubleshooting, infrastructure analysis, cross-account operations

**Note:** Requires Lambda function deployment for remote AWS CLI execution. Lambda code is still missing.

## Installation

### 1. Install Workspace Packages

This package is part of the strands_agents_bedrock_agentcore workspace. Install from workspace root:

```bash
# Install all workspace packages
uv sync --all-packages
```

This installs `local-agents` along with its dependencies (`strands-shared`, `strands-agents`, etc.) into the shared `.venv/`.

### 2. Install Ollama (Optional)

If you plan to use the Ollama agent, install Ollama:

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

**Start Ollama and pull a model:**
```bash
# Start Ollama server
ollama serve

# In another terminal, pull the model
ollama pull granite4
```

## Quick Start

```bash
# Activate workspace environment
source .venv/bin/activate

# Run default agent (Claude)
python -m local_agents

# Or run specific agent
python -m local_agents claude
python -m local_agents ollama
python -m local_agents aws_investigator
```

The terminal interface will start, and you can begin chatting with the agent immediately.

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

Each agent requires environment variables configured in its `.env` file. Copy the `.env.example` file to `.env` and customize for your environment.

### Claude Agent

**Location:** `local_agents/claude/.env`

```bash
LOG_LEVEL=INFO                # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_COLORS=true               # Enable colored log output
CLAUDE_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0  # Bedrock model ID
AWS_REGION=us-west-2          # AWS region for Bedrock
SYSTEM_PROMPT_PATH=system_prompt.md  # Path to system prompt file
```

**Prerequisites:**
- AWS credentials configured (via `~/.aws/credentials` or environment variables)
- Access to AWS Bedrock in the specified region

---

### Ollama Agent

**Location:** `local_agents/ollama/.env`

```bash
LOG_LEVEL=INFO                # Logging level
LOG_COLORS=true               # Enable colored log output
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL
OLLAMA_MODEL=granite4:latest  # Ollama model name
SYSTEM_PROMPT_PATH=system_prompt.md  # Path to system prompt file
```

**Prerequisites:**
- Ollama installed and running locally (`ollama serve`)
- Model pulled (`ollama pull granite4`)

---

### AWS Investigator

**Location:** `local_agents/aws_investigator/.env`

```bash
LOG_LEVEL=INFO                # Logging level
LOG_COLORS=true               # Enable colored log output
CLAUDE_MODEL=us.anthropic.claude-3-5-haiku-20241022-v1:0  # Bedrock model ID
AWS_REGION=us-west-2          # AWS region for Bedrock
SYSTEM_PROMPT_PATH=system_prompt.md  # Path to system prompt file
AWS_PROFILE_LAMBDA_AWS_CLI_EXECUTOR=your-profile  # AWS profile for Lambda executor
```

**Prerequisites:**
- AWS credentials configured with Bedrock access
- Lambda function deployed for AWS CLI executor (see `strands_shared.tools`)
- AWS profile with permissions to invoke the Lambda function
- MCP servers installed (`uvx awslabs.aws-documentation-mcp-server@latest`)

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

## Development

This package is part of the strands_agents_bedrock_agentcore monorepo workspace. See the [workspace README](../README.md) for general setup instructions.

### Type Checking

The package includes a `py.typed` marker for full type checking support:
```bash
mypy local_agents
```

### Adding New Agents

To add a new agent implementation:

1. **Create agent directory:**
   ```bash
   mkdir local_agents/your_agent
   ```

2. **Add required files:**
   - `agent.py` - Agent creation function (`create_agent__your_agent()`)
   - `config.py` - Configuration class extending `BaseConfig`
   - `.env.example` - Example environment variables
   - `system_prompt.md` - Agent system prompt

3. **Register in CLI:**
   Edit `local_agents/cli.py` and add to `AGENT_TYPES` dictionary:
   ```python
   AGENT_TYPES = {
       # ... existing agents
       "your_agent": create_agent__your_agent,
   }
   ```

4. **Export creation function:**
   Edit `local_agents/__init__.py`:
   ```python
   from local_agents.your_agent.agent import create_agent__your_agent

   __all__ = [
       # ... existing exports
       "create_agent__your_agent",
   ]
   ```

5. **Test:**
   ```bash
   python -m local_agents your_agent
   ```
