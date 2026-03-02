"""AgentCore entrypoint for validator agent."""

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
        logger.info("Creating validator agent instance")
        try:
            from multi_agents.validator import create_validator_agent
            _agent = create_validator_agent()
            logger.info("Validator agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create validator agent: {e}", exc_info=True)
            raise RuntimeError(f"Validator agent initialization failed: {e}") from e
    return _agent


@app.entrypoint
async def invoke(payload, context):
    """Validator agent entrypoint."""
    try:
        if not isinstance(payload, dict):
            yield "Error: Invalid payload format"
            return

        user_message = payload.get("prompt", "Hello!")
        logger.info(f"Processing validation request: {user_message[:50]}...")

        agent = get_agent()
        stream = agent.stream_async(user_message)

        async for event in stream:
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]

        logger.info("Validation completed successfully")
    except Exception as e:
        logger.error(f"Error processing validation request: {e}", exc_info=True)
        yield f"Error: {str(e)}"


if __name__ == "__main__":
    app.run()
