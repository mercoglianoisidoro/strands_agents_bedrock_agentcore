# AgentCore Client

Client library for interacting with deployed Bedrock AgentCore agents.

## Features

- Auto-discovery of agent ARN from `.bedrock_agentcore.yaml`
- Support for streaming and JSON responses
- Session management

## Usage

```python
from strands_agentcore_client import remote_agent_client

# Auto-read ARN from config
client = remote_agent_client()

# Or specify ARN explicitly
client = remote_agent_client("arn:aws:bedrock-agentcore:...")

# Use the client
response = client("Hello, agent!")
```