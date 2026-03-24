"""Structured conversation logger for A2A tracing."""

import json
import os
import time
import boto3
import logging

logger = logging.getLogger(__name__)

_client = None
_log_group = None
_log_stream = None


def _ensure_stream():
    global _client, _log_group, _log_stream
    if _client:
        return

    _log_group = os.getenv("CONVERSATION_LOG_GROUP")
    if not _log_group:
        return

    region = os.getenv("AWS_REGION", "us-west-2")
    _client = boto3.client("logs", region_name=region)
    _log_stream = f"orchestrator-{int(time.time())}"

    try:
        _client.create_log_stream(logGroupName=_log_group, logStreamName=_log_stream)
    except _client.exceptions.ResourceAlreadyExistsException:
        pass
    except Exception as e:
        logger.warning(f"Failed to create log stream: {e}")
        _client = None


def log_event(session_id: str, event_type: str, agent: str, content: str):
    """Log a conversation event."""
    _ensure_stream()
    if not _client:
        return

    event = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "session_id": session_id,
        "event": event_type,
        "agent": agent,
        "content": content
    }

    try:
        _client.put_log_events(
            logGroupName=_log_group,
            logStreamName=_log_stream,
            logEvents=[{"timestamp": int(time.time() * 1000), "message": json.dumps(event)}]
        )
    except Exception as e:
        logger.warning(f"Failed to log conversation event: {e}")
