"""
title: AWS Bedrock AgentCore
author: open-webui
version: 1.1
"""

import json
import uuid
import hashlib
import logging
import boto3
from collections import OrderedDict
from typing import Generator, Iterator
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
        AGENT_ARN: str = Field(
            default="",
            description="AgentCore Runtime ARN (required)"
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
        self.id = "agentcore"
        self.name = "AgentCore: "
        self.valves = self.Valves()
        self.client = None
        self.sessions = LRUCache(max_size=100)

    def get_client(self):
        if not self.client:
            self.client = boto3.client('bedrock-agentcore', region_name=self.valves.AWS_REGION)
        return self.client

    def pipes(self) -> list[dict[str, str]]:
        return [{"id": "test-agent", "name": "IsiRemoteAgent"}]

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
        # Validate configuration
        if not self.valves.AGENT_ARN:
            return "Error: AGENT_ARN is not configured. Please set it in the Function settings."

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
                agentRuntimeArn=self.valves.AGENT_ARN,
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
                                    # Handle potential structured responses
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
