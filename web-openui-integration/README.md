# Open WebUI Integration for AWS Bedrock AgentCore

This directory contains the integration between Open WebUI and AWS Bedrock AgentCore agents, allowing you to interact with your AgentCore agents through a chat interface.

## What is This?

This integration creates a custom "model" in Open WebUI that connects to your AWS Bedrock AgentCore agent. When you chat with this model, your messages are sent to the AgentCore agent, and responses are streamed back in real-time.

### Key Features
- ✅ Native Open WebUI integration (no separate proxy needed)
- ✅ Conversation memory (maintains session context)
- ✅ Streaming responses
- ✅ Configurable via UI (change agent ARN without code changes)
- ✅ Works with any AgentCore agent
- ✅ Auto-config option: reads from `.bedrock_agentcore.yaml` (no manual ARN updates)

## Architecture

```
User → Open WebUI (Function) → AWS Bedrock AgentCore → Agentcore Agent
```

The function runs inside Open WebUI's process and uses boto3 to call the AgentCore API directly.

## Prerequisites

1. **Python 3.11+** installed
2. **AWS credentials** configured (via `~/.aws/credentials` or environment variables)
3. **AWS Bedrock AgentCore agent** deployed and accessible
4. **Permissions**: Your AWS credentials need `bedrock-agentcore:InvokeAgentRuntime` permission

## Installation

### Step 1: Install Open WebUI

```bash
pip install open-webui
```

### Step 2: Install Dependencies

```bash
pip install boto3 pyyaml
```

> **Note:** `pyyaml` is only required for `agentcore_function_auto.py` (auto-config version)

### Step 3: Start Open WebUI

```bash
open-webui serve
```

Open WebUI will start on `http://localhost:8080`

### Step 4: Create an Account

1. Open `http://localhost:8080` in your browser
2. Create an account (first user becomes admin)
3. Log in

### Step 5: Add the AgentCore Function

#### Option A: Via Workspace (if Functions is enabled)
1. Click **Workspace** in the top menu
2. Click **Functions** in the sidebar
3. Click the **"+"** button (top right)
4. Copy the entire content of `agentcore_function.py`
5. Paste it into the editor
6. Click **Save**
7. **Toggle the function ON** (enable it)

#### Option B: Via Admin Panel (if Functions not in Workspace)
1. Click your **profile icon** (top right)
2. Go to **Admin Panel**
3. Navigate to **Settings** → **Functions**
4. Click the **"+"** button
5. Copy the entire content of `agentcore_function.py`
6. Paste it into the editor
7. Click **Save**
8. **Toggle the function ON** (enable it)

### Step 6: Configure the Agent ARN (Optional)

If your agent ARN is different:

1. In the Functions page, click on the **AgentCore** function
2. Click the **⚙️ Settings** icon
3. Update the **AGENT_ARN** field with your agent's ARN
4. Update **AWS_REGION** if needed
5. Click **Save**

### Step 7: Start Chatting

1. Go to the main chat interface
2. Click the **model selector** dropdown
3. Select **"IsiRemoteAgent"** (or your agent name)
4. Start chatting!

## How It Works

### Session Management
The function maintains conversation context by:
- Creating a unique session ID for each conversation
- Reusing the same session ID for follow-up messages
- Allowing the agent to remember previous interactions

### Message Flow
1. User sends a message in Open WebUI
2. Function extracts the last user message
3. Function calls AgentCore's `invoke_agent_runtime` API
4. AgentCore processes the request and streams back chunks
5. Function parses the streaming response
6. User sees the response in real-time

### Streaming
The function supports both streaming and non-streaming modes:
- **Streaming**: Responses appear word-by-word as the agent generates them
- **Non-streaming**: Complete response appears at once


## Advanced Usage

### Multiple Agents
To add multiple AgentCore agents:

1. Modify the `pipes()` method to return multiple agents:
```python
def pipes(self) -> list[dict[str, str]]:
    return [
        {"id": "agent-1", "name": "Customer Support Agent"},
        {"id": "agent-2", "name": "Technical Agent"}
    ]
```

2. Update `pipe()` to route to different ARNs based on the selected model

### Custom Agent Names
Change the agent name in the `pipes()` method:
```python
{"id": "test-agent", "name": "Your Custom Name"}
```

## Files

| File | Description |
|------|-------------|
| `agentcore_function.py` | Manual config - Set ARN via Open WebUI Function settings |
| `agentcore_function_auto.py` | Auto config - Reads ARN from `.bedrock_agentcore.yaml` automatically |
| `README.md` | This documentation |

## Choosing a Version

### `agentcore_function.py` (Manual Config)

Best for:
- Simple setups with one agent
- Stable ARNs that don't change often
- Users who prefer UI configuration

Configuration:
1. Upload to Open WebUI → Functions
2. Set `AGENT_ARN` in Function settings
3. Set `AWS_REGION` if needed

### `agentcore_function_auto.py` (Auto Config)

Best for:
- Frequent agent redeployments
- Multiple agents defined in config
- CI/CD workflows

Features:
- Reads agents from `.bedrock_agentcore.yaml`
- Hot-reloads when config file changes
- Lists all agents defined in config
- Default agent appears first in dropdown

Configuration:
1. Upload to Open WebUI → Functions
2. Set `AGENTCORE_CONFIG_PATH` to your `.bedrock_agentcore.yaml` file
3. After `agentcore deploy`, agents update automatically

```
# Example workflow with auto config
agentcore deploy          # Updates .bedrock_agentcore.yaml
# Open WebUI automatically picks up new agent ARN on next request
```
