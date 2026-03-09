"""A2A tools for orchestrator agent."""

import json
import os
import boto3
from strands import tool


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
        Persistent session ID for the worker agent
    """
    cache_key = f"{parent_session_id or 'default'}-{worker_name}"
    
    if cache_key not in _worker_sessions:
        if parent_session_id:
            _worker_sessions[cache_key] = f"{parent_session_id}-{worker_name}"
        else:
            _worker_sessions[cache_key] = f"orch-{worker_name}"
    
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
        client = boto3.client("bedrock-agentcore", config=config)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": query}).encode()
        )
        
        # Parse streaming response
        result = []
        for event in response.get("eventStream", []):
            if "chunk" in event:
                chunk_data = event["chunk"].get("bytes", b"")
                result.append(chunk_data.decode("utf-8"))
        
        return "".join(result) if result else "No response from AWS Investigator"
    
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
        client = boto3.client("bedrock-agentcore", config=config)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": verification_request}).encode()
        )
        
        # Parse streaming response
        result = []
        for event in response.get("eventStream", []):
            if "chunk" in event:
                chunk_data = event["chunk"].get("bytes", b"")
                result.append(chunk_data.decode("utf-8"))
        
        return "".join(result) if result else "No response from Validator"
    
    except Exception as e:
        return f"Error calling Validator: {str(e)}"
