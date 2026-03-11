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
    Delegate investigation tasks to AWS Investigator agent.
    
    Uses PERSISTENT session to maintain context across calls. This means:
    - Investigator remembers previously fetched web pages
    - No re-fetching of same URLs
    - Can build on previous research
    - Multi-turn conversations work naturally
    
    Use this when you need to:
    - Search the web for AWS information
    - Execute AWS CLI commands
    - Investigate AWS services, pricing, or features
    - Follow up on previous investigations
    
    Args:
        query: The investigation request to send to AWS Investigator
        
    Returns:
        The investigation results from AWS Investigator
    """
    agent_arn = os.getenv("AWS_INVESTIGATOR_ARN")
    if not agent_arn:
        return "Error: AWS_INVESTIGATOR_ARN environment variable not set"
    
    # Get persistent session for this worker
    session_id = _get_worker_session("investigator")
    
    try:
        from botocore.config import Config
        config = Config(read_timeout=180)  # 3 minutes max per A2A call
        region = os.getenv("AWS_REGION", "us-west-2")
        client = boto3.client("bedrock-agentcore", region_name=region, config=config)

        log_event(session_id, "a2a_call", "orchestrator→investigator", query)

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
        return f"Error calling AWS Investigator: {str(e)}"


@tool
def call_validator(claim: str, evidence_source: str) -> str:
    """
    Delegate verification tasks to Validator agent.
    
    Uses PERSISTENT session to maintain verification context. Validator will:
    - Fetch URLs independently (not relying on Investigator's cache)
    - Re-execute AWS commands with provided credentials
    - Build verification history over multiple checks
    
    IMPORTANT: Pass URL references, NOT content. Web pages are too large
    for context windows. Validator will fetch independently for true verification.
    
    Use this when you need to:
    - Verify claims made by AWS Investigator
    - Re-check evidence sources (URLs, AWS commands)
    - Validate information accuracy
    - Independent fact-checking
    
    Args:
        claim: The claim to verify
        evidence_source: The evidence source (URL or AWS command) - NOT content!
        
    Returns:
        The verification results from Validator
    """
    agent_arn = os.getenv("VALIDATOR_ARN")
    if not agent_arn:
        return "Error: VALIDATOR_ARN environment variable not set"
    
    # Get persistent session for this worker
    session_id = _get_worker_session("validator")
    
    verification_request = f"""Verify: {claim}
Evidence Source: {evidence_source}

Fetch and analyze the source independently to verify the claim."""
    
    try:
        from botocore.config import Config
        config = Config(read_timeout=180)  # 3 minutes max per A2A call
        region = os.getenv("AWS_REGION", "us-west-2")
        client = boto3.client("bedrock-agentcore", region_name=region, config=config)

        log_event(session_id, "a2a_call", "orchestrator→validator", verification_request)

        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": verification_request}).encode()
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
        return f"Error calling Validator: {str(e)}"
