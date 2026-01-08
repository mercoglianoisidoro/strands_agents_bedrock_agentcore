"""
title: AWS Bedrock AgentCore (Auto-Config)
author: open-webui
version: 1.0

Automatically reads agent configuration from .bedrock_agentcore.yaml.
When you redeploy your agent, this function picks up changes automatically.
"""

import json
import os
import uuid
import hashlib
import logging
import boto3
import yaml
from collections import OrderedDict
from typing import Generator, Iterator, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LRUCache(OrderedDict):
    """Simple LRU cache to prevent unbounded session growth."""
    def __init__(self, max_size: int = 100):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            self.popitem(last=False)


class Pipe:
    class Valves(BaseModel):
        AGENTCORE_CONFIG_PATH: str = Field(
            default=os.path.expanduser("~/workspaces/strands_agents/remote-agentcore/.bedrock_agentcore.yaml"),
            description="Path to .bedrock_agentcore.yaml config file"
        )
        AWS_REGION: str = Field(
            default="us-west-2",
            description="AWS Region"
        )
        MAX_SESSIONS: int = Field(
            default=100,
            description="Maximum number of cached sessions"
        )

    def __init__(self):
        self.type = "manifold"
        self.id = "agentcore-auto"
        self.name = "AgentCore: "
        self.valves = self.Valves()
        self.client = None
        self.sessions = LRUCache(max_size=100)
        self._config_cache = None
        self._config_mtime = 0

    def _load_agentcore_config(self) -> Optional[dict]:
        """Load and cache the agentcore config, reloading if file changed."""
        config_path = self.valves.AGENTCORE_CONFIG_PATH

        if not os.path.exists(config_path):
            logger.warning(f"AgentCore config not found: {config_path}")
            return None

        # Check if file was modified
        current_mtime = os.path.getmtime(config_path)
        if self._config_cache and current_mtime == self._config_mtime:
            return self._config_cache

        # Reload config
        try:
            with open(config_path) as f:
                self._config_cache = yaml.safe_load(f)
                self._config_mtime = current_mtime
                logger.info(f"Loaded agentcore config from {config_path}")
                return self._config_cache
        except Exception as e:
            logger.error(f"Failed to load agentcore config: {e}")
            return None

    def _get_agents_from_config(self) -> list[dict]:
        """Extract agent info from the config file."""
        config = self._load_agentcore_config()
        if not config:
            return []

        agents = []
        for agent_name, agent_config in config.get("agents", {}).items():
            agent_arn = agent_config.get("bedrock_agentcore", {}).get("agent_arn")
            if agent_arn:
                agents.append({
                    "name": agent_name,
                    "arn": agent_arn,
                    "is_default": agent_name == config.get("default_agent")
                })
        return agents

    def get_client(self):
        if not self.client:
            self.client = boto3.client('bedrock-agentcore', region_name=self.valves.AWS_REGION)
        return self.client

    def pipes(self) -> list[dict[str, str]]:
        """Dynamically return available agents from config file."""
        agents = self._get_agents_from_config()
        if not agents:
            return [{"id": "not-configured", "name": "Configure AGENTCORE_CONFIG_PATH"}]

        # Return agents, with default first
        agents.sort(key=lambda x: (not x["is_default"], x["name"]))
        return [{"id": agent["arn"], "name": agent["name"]} for agent in agents]

    def _get_session_id(self, body: dict, messages: list) -> str:
        """Get or create a stable session ID for the conversation."""
        # Prefer chat_id from Open WebUI if available
        chat_id = body.get("chat_id")
        if chat_id:
            return chat_id if len(chat_id) >= 33 else f"{chat_id}-{uuid.uuid4().hex[:16]}"

        # Fall back to deterministic hash of first message
        if messages:
            first_msg = json.dumps(messages[0], sort_keys=True)
            conv_id = hashlib.sha256(first_msg.encode()).hexdigest()[:32]
            if conv_id not in self.sessions:
                self.sessions[conv_id] = f"{conv_id}-{uuid.uuid4().hex[:8]}"
            return self.sessions[conv_id]

        return str(uuid.uuid4())

    def pipe(self, body: dict) -> str | Generator | Iterator:
        # Get agent ARN from the selected model
        # body["model"] format: "agentcore-auto.{arn}" - we need to extract the ARN
        model_id = body.get("model", "")

        # Strip the pipe prefix to get the ARN
        if "." in model_id:
            agent_arn = model_id.split(".", 1)[1]
        else:
            agent_arn = model_id

        # Validate ARN
        if not agent_arn or agent_arn == "not-configured":
            return "Error: No agent configured. Please set AGENTCORE_CONFIG_PATH in Function settings."

        if not agent_arn.startswith("arn:aws:bedrock-agentcore:"):
            return f"Error: Invalid agent ARN: {agent_arn}"

        messages = body.get("messages", [])
        stream = body.get("stream", False)

        # Get session ID
        session_id = self._get_session_id(body, messages)

        # Get last user message
        user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), '')
        if not user_message:
            return "Error: No user message found."

        # Call AgentCore
        try:
            client = self.get_client()
            response = client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps({"prompt": user_message}).encode('utf-8')
            )
        except Exception as e:
            logger.error(f"AgentCore invocation failed: {e}")
            return f"Error calling AgentCore: {str(e)}"

        if stream:
            return self.stream_response(response)
        else:
            return self.non_stream_response(response)

    def stream_response(self, response) -> Generator:
        try:
            for line in response['response'].iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:].strip()
                        if data_str:
                            try:
                                content = json.loads(data_str)
                                if isinstance(content, str):
                                    yield content
                                elif isinstance(content, dict):
                                    yield content.get('text', content.get('response', str(content)))
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse streaming chunk: {e}, data: {data_str[:100]}")
        except Exception as e:
            logger.error(f"Error in stream_response: {e}")
            yield f"Error: {str(e)}"

    def non_stream_response(self, response) -> str:
        content_parts = []
        try:
            for line in response['response'].iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:].strip()
                        if data_str:
                            try:
                                content = json.loads(data_str)
                                if isinstance(content, str):
                                    content_parts.append(content)
                                elif isinstance(content, dict):
                                    content_parts.append(content.get('text', content.get('response', str(content))))
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse chunk: {e}, data: {data_str[:100]}")
        except Exception as e:
            logger.error(f"Error in non_stream_response: {e}")
            return f"Error: {str(e)}"

        return ''.join(content_parts)
