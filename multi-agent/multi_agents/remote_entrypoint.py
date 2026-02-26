"""AgentCore entrypoint for AWS investigator agent."""

import logging
from bedrock_agentcore import BedrockAgentCoreApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()
_agent = None


def get_agent():
    """Get or create cached agent instance."""
    global _agent
    if _agent is None:
        logger.info("Creating agent instance")
        try:
            from multi_agents.aws_investigator import create_aws_investigator_agent
            _agent = create_aws_investigator_agent()
            logger.info("Agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            raise RuntimeError(f"Agent initialization failed: {e}") from e
    return _agent


@app.entrypoint
async def invoke(payload, context):
    """AWS investigator agent entrypoint."""
    try:
        if not isinstance(payload, dict):
            yield "Error: Invalid payload format"
            return

        user_message = payload.get("prompt", "Hello!")
        logger.info(f"Processing prompt: {user_message[:50]}...")

        agent = get_agent()
        stream = agent.stream_async(user_message)

        async for event in stream:
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]

        logger.info("Request completed successfully")
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        yield f"Error: {str(e)}"


if __name__ == "__main__":
    app.run()
