# Strands Shared

Shared utilities for Strands agents - common code used across local and remote agent implementations.

## Contents

### config/
**Purpose:** Standardize configuration management across all agent implementations.

Provides a base configuration class that handles environment variable loading, logging setup, and system prompt management. This ensures consistent configuration patterns whether agents run locally or in remote environments like AWS Lambda.

**Key Component:**
- `BaseConfig`: Foundation for agent configuration with built-in support for `.env` files, colored logging, and markdown-based system prompts

**Why it exists:** Eliminates configuration boilerplate and ensures all agents follow the same setup patterns, making it easier to maintain and deploy agents across different environments.

---

### tools/
**Purpose:** Extend agent capabilities with reusable custom tools.

Contains specialized tools that agents can use to interact with external systems. Currently focused on AWS infrastructure operations through secure, isolated execution environments.

**Key Component:**
- `lambda_aws_cli_executor`: Enables agents to execute AWS CLI commands remotely via Lambda, allowing safe cross-account operations and infrastructure investigation without exposing credentials

**PLEASE NOTE**: the lambda creation is still missing in this repository


**Why it exists:** Agents need to interact with AWS infrastructure in a secure, auditable way. This tool provides that capability while maintaining security boundaries and enabling complex AWS automation workflows.

---

### terminal/
**Purpose:** Provide interactive terminal interfaces for local agent development and testing.

Offers a rich terminal experience with markdown rendering, streaming responses, and multi-line input support. Designed for developers working with agents locally before deployment.

**Key Component:**
- `Terminal`: Interactive CLI interface that wraps agents with user-friendly input/output handling, including colored output, markdown formatting, and graceful error handling

**Why it exists:** Developers need an easy way to interact with agents during development. This provides a polished terminal experience without requiring each agent to implement its own CLI interface.

## Installation

This package is part of the workspace. Install from the repository root:

```bash
uv sync
```

## Usage Examples

### Using BaseConfig

```python
from pathlib import Path
from strands_shared.config import BaseConfig

# Initialize config with directory containing .env file
config = BaseConfig(Path(__file__).parent)

# Load system prompt
system_prompt = config.load_system_prompt()
# Or with custom filename
system_prompt = config.load_system_prompt("custom_prompt.md")

# Setup logging
config.setup_logging("my_agent")
```

**Environment variables (.env file):**
```bash
LOG_LEVEL=INFO
LOG_COLORS=true
SYSTEM_PROMPT_PATH=custom_prompt.md  # Optional
```

### Using Terminal Interface

```python
import asyncio
from strands_shared.terminal import Terminal
from strands import Agent

# Create your agent
agent = Agent(model=your_model, tools=your_tools)

# Wrap with terminal interface
terminal = Terminal(
    agent,
    use_markdown=True,      # Enable markdown rendering
    show_streaming=True     # Show streaming output
)

# Start interactive session
asyncio.run(terminal.start())

# Or with initial message
asyncio.run(terminal.start("Hello, how can you help me?"))
```

### Complete Example

```python
from pathlib import Path
from strands import Agent
from strands.models import BedrockModel
from strands_shared.config import BaseConfig
from strands_shared.terminal import Terminal
import asyncio

# Setup configuration
config = BaseConfig(Path(__file__).parent)
config.setup_logging()

# Load system prompt
system_prompt = config.load_system_prompt()

# Create agent
model = BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0")
agent = Agent(
    model=model,
    tools=[],  # Add your tools here
    system_prompt=system_prompt
)

# Interactive terminal
terminal = Terminal(agent)
asyncio.run(terminal.start())
```

## Dependencies

- `python-dotenv`: Environment variable management
- `colorlog`: Colored logging output
- `pydantic`: Data validation
- `colorama`: Cross-platform colored terminal text
- `strands-agents`: Core agent framework (for tools)
- `boto3`: AWS SDK (for tools)

