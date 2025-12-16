# Strands Shared

Shared utilities for Strands agents - common code used across local and remote agent implementations.

## Contents

### config/
Base configuration classes for agent setup:
- `BaseConfig`: Common configuration with environment loading, logging setup, and system prompt management

### tools/
Reusable custom tools for agents

### terminal/
Terminal interface utilities for interactive agent sessions:
- `Terminal`: Minimal terminal interface for agent interaction with markdown support

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

