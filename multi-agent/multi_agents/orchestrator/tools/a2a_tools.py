"""A2A tools for orchestrator agent."""

import json
import os
import boto3
import uuid
import logging
from strands import tool
from multi_agents.conversation_logger import log_event

logger = logging.getLogger(__name__)


# Module-level session cache for persistent worker connections
_worker_sessions = {}


def _get_worker_session(worker_name: str, parent_session_id: str = None) -> str:
    """
    Get or create persistent session for worker agent.
    
    Maintains same session across multiple calls to avoid re-fetching web content
    and preserve context. This is critical because:
    - Web pages are too large to pass in context (50KB+ each)
    - Workers need to build up context over multiple interactions
    - Avoids expensive re-fetching of same URLs
    
    Args:
        worker_name: Name of the worker agent
        parent_session_id: Optional parent session for traceability
        
    Returns:
        Persistent session ID for the worker agent (min 33 chars for AWS)
    """
    cache_key = f"{parent_session_id or 'default'}-{worker_name}"
    
    if cache_key not in _worker_sessions:
        # Generate session ID with minimum 33 characters required by AWS
        session_uuid = str(uuid.uuid4())
        if parent_session_id:
            _worker_sessions[cache_key] = f"{parent_session_id}-{worker_name}-{session_uuid}"
        else:
            _worker_sessions[cache_key] = f"orch-{worker_name}-{session_uuid}"
    
    return _worker_sessions[cache_key]


@tool
def call_aws_investigator(query: str) -> str:
    """
    Research AWS questions by searching documentation and web sources.
    
    Use this tool to gather information about AWS services, errors, pricing, 
    features, or troubleshooting steps.
    
    Args:
        query: The AWS question or topic to research
        
    Returns:
        Research findings with sources and documentation links
    """
    agent_arn = os.getenv("AWS_INVESTIGATOR_ARN")
    session_id = _get_worker_session("investigator")
    
    if not agent_arn:
        error_msg = "Error: AWS_INVESTIGATOR_ARN environment variable not set"
        log_event(session_id, "a2a_error", "orchestrator→investigator", error_msg)
        return error_msg
    
    # Log BEFORE attempting the call
    log_event(session_id, "a2a_call", "orchestrator→investigator", query)
    
    try:
        from botocore.config import Config
        config = Config(read_timeout=180)  # 3 minutes max per A2A call
        region = os.getenv("AWS_REGION", "us-west-2")
        client = boto3.client("bedrock-agentcore", region_name=region, config=config)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": query}).encode()
        )
        
        # Parse streaming response
        result = []
        if "text/event-stream" in response.get("contentType", ""):
            for line in response["response"].iter_lines(chunk_size=10):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        # Parse JSON token and extract text
                        try:
                            token = json.loads(line[6:])
                            result.append(token)
                        except:
                            result.append(line[6:])
        elif response.get("contentType") == "application/json":
            for chunk in response.get("response", []):
                result.append(chunk.decode('utf-8'))
        
        response_text = "".join(result) if result else "No response from AWS Investigator"
        log_event(session_id, "a2a_response", "investigator→orchestrator", response_text)
        return response_text
    
    except Exception as e:
        error_msg = f"Error calling AWS Investigator: {str(e)}"
        log_event(session_id, "a2a_error", "orchestrator→investigator", error_msg)
        logger.error(f"Investigator call failed: {e}", exc_info=True)
        return error_msg


@tool
def call_validator(full_answer: str, original_query: str) -> str:
    """
    Validate a complete answer for accuracy and completeness.
    
    REQUIRED: You MUST call this tool before responding to the user.
    
    The validator independently verifies your answer by checking sources,
    re-executing commands, and validating technical accuracy.
    
    Args:
        full_answer: Your COMPLETE draft answer (not a summary)
        original_query: The original user question
        
    Returns:
        "APPROVED" if answer is correct, or "CORRECTIONS: <issues>" if fixes needed
    """
    agent_arn = os.getenv("VALIDATOR_ARN")
    session_id = _get_worker_session("validator")
    
    if not agent_arn:
        error_msg = "Error: VALIDATOR_ARN environment variable not set"
        log_event(session_id, "a2a_error", "orchestrator→validator", error_msg)
        return error_msg
    
    validation_request = f"""Review this complete answer for accuracy and completeness.

Original Question: {original_query}

Complete Answer to Review:
{full_answer}

Instructions:
- Verify key facts by checking sources independently
- Check for completeness (missing important information?)
- Validate technical accuracy
- If everything is correct and complete, respond with: APPROVED
- If corrections needed, respond with: CORRECTIONS: <list specific issues>

Be specific about what needs fixing."""
    
    # Log BEFORE attempting the call
    log_event(session_id, "a2a_call", "orchestrator→validator", validation_request)
    
    try:
        from botocore.config import Config
        config = Config(read_timeout=180)  # 3 minutes max per A2A call
        region = os.getenv("AWS_REGION", "us-west-2")
        client = boto3.client("bedrock-agentcore", region_name=region, config=config)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": validation_request}).encode()
        )
        
        # Parse streaming response
        result = []
        if "text/event-stream" in response.get("contentType", ""):
            for line in response["response"].iter_lines(chunk_size=10):
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        # Parse JSON token and extract text
                        try:
                            token = json.loads(line[6:])
                            result.append(token)
                        except:
                            result.append(line[6:])
        elif response.get("contentType") == "application/json":
            for chunk in response.get("response", []):
                result.append(chunk.decode('utf-8'))
        
        response_text = "".join(result) if result else "No response from Validator"
        log_event(session_id, "a2a_response", "validator→orchestrator", response_text)
        return response_text
    
    except Exception as e:
        error_msg = f"Error calling Validator: {str(e)}"
        log_event(session_id, "a2a_error", "orchestrator→validator", error_msg)
        logger.error(f"Validator call failed: {e}", exc_info=True)
        return error_msg
