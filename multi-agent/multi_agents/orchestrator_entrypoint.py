"""
Orchestrator Agent Entrypoint - Actual Implementation

This is the ACTUAL entrypoint implementation for the Orchestrator agent.
It creates and manages the orchestrator agent instance with A2A tools.

Architecture:
- BedrockAgentCoreApp: Provides /invocations endpoint on port 8080
- Module-level caching: _agent variable caches the agent instance
- Lazy initialization: Agent created only on first invocation
- A2A Tools: call_aws_investigator, call_validator

Session Management:
- Container-level: Same agent instance reused across invocations
- Worker-level: Persistent sessions maintained for AWS Investigator and Validator

Pattern: Matches remote_entrypoint.py and validator_entrypoint.py for consistency
"""

import logging
import sys
from bedrock_agentcore import BedrockAgentCoreApp

# Force unbuffered output for CloudWatch
sys.stdout = sys.stdout
sys.stderr = sys.stderr

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()
_agent = None  # Module-level cache for agent instance

# Startup log
logger.info("=" * 60)
logger.info("ORCHESTRATOR ENTRYPOINT LOADED")
logger.info("=" * 60)


def get_agent():
    """
    Get or create cached orchestrator agent instance.
    
    This function implements lazy initialization with module-level caching:
    - First call: Creates the orchestrator agent with A2A tools
    - Subsequent calls: Returns the cached instance
    
    Benefits:
    - Agent created only when needed (not at container startup)
    - Same instance reused across all invocations in this container
    - Maintains state and context between requests
    
    Returns:
        Agent: The orchestrator agent instance with A2A tools
        
    Raises:
        RuntimeError: If agent creation fails
    """
    global _agent
    if _agent is None:
        logger.info("=" * 60)
        logger.info("CREATING ORCHESTRATOR AGENT INSTANCE")
        logger.info("=" * 60)
        try:
            from multi_agents.orchestrator import create_orchestrator_agent
            _agent = create_orchestrator_agent()
            logger.info("✅ Orchestrator agent created successfully")
        except Exception as e:
            logger.error(f"❌ FATAL: Agent creation failed - {e}", exc_info=True)
            raise RuntimeError(f"Orchestrator initialization failed: {e}") from e
    return _agent


@app.entrypoint
async def invoke(payload, context):
    """
    Orchestrator agent entrypoint - handles all incoming requests.
    
    This is the main entry point called by AWS Bedrock AgentCore when
    the orchestrator receives a request. It delegates to the cached
    agent instance which routes to specialist agents via A2A protocol.
    
    Flow:
    1. Validate payload format
    2. Extract user prompt
    3. Get cached agent instance
    4. Stream agent response back to caller
    
    Args:
        payload: Request payload with 'prompt' field
        context: AgentCore context (session_id, etc.)
        
    Yields:
        str: Streaming response chunks from the agent
        
    Error Handling:
        - Invalid payload: Returns error message
        - Agent errors: Logs and returns error message
    """
    logger.info("=" * 60)
    logger.info(f"📥 INVOCATION RECEIVED - Session: {context.session_id}")
    logger.info("=" * 60)
    
    try:
        if not isinstance(payload, dict):
            logger.error("❌ Invalid payload format")
            yield "Error: Invalid payload format"
            return

        user_message = payload.get("prompt", "Hello!")
        logger.info(f"📝 Processing: {user_message[:100]}")

        from multi_agents.conversation_logger import log_event
        log_event(context.session_id, "user_query", "user", user_message)

        agent = get_agent()
        stream = agent.stream_async(user_message)

        response_chunks = []
        async for event in stream:
            if "data" in event and isinstance(event["data"], str):
                response_chunks.append(event["data"])
                yield event["data"]

        log_event(context.session_id, "final_response", "orchestrator", "".join(response_chunks))
        logger.info("✅ Request completed successfully")
    except Exception as e:
        logger.error(f"❌ Orchestrator error: {e}", exc_info=True)
        yield f"Error: {str(e)}"


if __name__ == "__main__":
    app.run()
