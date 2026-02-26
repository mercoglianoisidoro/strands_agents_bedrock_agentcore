
import boto3
import json
import yaml
import os
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


def get_agent_arn_from_config(config_path: Optional[str] = None) -> str:
    """Read agent ARN from agentcore config file.

    Args:
        config_path: Path to .bedrock_agentcore.yaml file. If None, looks for it in common locations.

    Returns:
        Agent ARN string

    Raises:
        FileNotFoundError: If config file not found
        KeyError: If ARN not found in config
    """
    if config_path is None:
        # Look in common locations
        search_paths = [
            Path.cwd() / ".bedrock_agentcore.yaml",
            Path.cwd().parent / "remote-agentcore" / ".bedrock_agentcore.yaml",
            Path(__file__).parent.parent.parent / "remote-agentcore" / ".bedrock_agentcore.yaml"
        ]
        
        config_path = None
        for path in search_paths:
            if path.exists():
                config_path = path
                break
                
        if config_path is None:
            raise FileNotFoundError(f"AgentCore config not found in: {[str(p) for p in search_paths]}")
    else:
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"AgentCore config not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    default_agent = config.get('default_agent')
    if not default_agent:
        raise KeyError("No default_agent specified in config")

    agent_config = config.get('agents', {}).get(default_agent, {})
    agent_arn = agent_config.get('bedrock_agentcore', {}).get('agent_arn')

    if not agent_arn:
        raise KeyError(f"No agent_arn found for agent: {default_agent}")

    return agent_arn



class remote_agent_client:
    def __init__(self, agent_arn: Optional[str] = None, config_path: Optional[str] = None, log_session: bool = False):
        """Initialize remote agent client.

        Args:
            agent_arn: Agent ARN. If None, reads from agentcore config.
            config_path: Path to .bedrock_agentcore.yaml. If None, uses current dir.
            log_session: Whether to log session ID to stdout.
        """
        if agent_arn is None:
            agent_arn = get_agent_arn_from_config(config_path)

        self.agent_arn = agent_arn
        self.client = boto3.client('bedrock-agentcore')
        
        # Generate session ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_id = f"session-{timestamp}-{str(hash(self))[-9:]}"
        
        if log_session:
            print(f"Session ID: {self.session_id}")


    def __call__(self, *args: Any, **kwds: Any) -> Any:
        prompt = args[0] if args else ""
        return self.call_agent(self.agent_arn, self.session_id, prompt)


    def call_agent(self, agent_arn, session_id, prompt) -> str:

        # Initialize the Bedrock AgentCore client
        agent_core_client = boto3.client('bedrock-agentcore')

        # Prepare the payload
        payload = json.dumps({"prompt": prompt}).encode()

        # Invoke the agent
        response = agent_core_client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=payload
        )

        # Process and print the response
        if "text/event-stream" in response.get("contentType", ""):
            # Handle streaming response
            content = []
            for line in response["response"].iter_lines(chunk_size=10):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        line = line[6:]
                        try:
                            # Parse JSON and extract the actual text
                            parsed = json.loads(line)
                            # Extract text from dict if it's a dict
                            if isinstance(parsed, dict):
                                text = parsed.get('data', parsed.get('text', str(parsed)))
                                content.append(text)
                            else:
                                content.append(str(parsed))
                        except json.JSONDecodeError:
                            # If not JSON, use as-is
                            content.append(line)
            result = ''.join(content)
            return result

        elif response.get("contentType") == "application/json":
            # Handle standard JSON response
            content = []
            for chunk in response.get("response", []):
                content.append(chunk.decode('utf-8'))
            result = json.loads(''.join(content))
            return str(result)

        else:
            # Return raw response for other content types
            return str(response)

