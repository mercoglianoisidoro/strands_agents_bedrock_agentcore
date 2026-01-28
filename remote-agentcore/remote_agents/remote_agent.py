"""Run Claude agent."""
import logging
from bedrock_agentcore import BedrockAgentCoreApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

# Cache agent instance
_agent = None

def get_agent():
    """Get or create cached agent instance."""
    global _agent
    if _agent is None:
        logger.info("Creating agent instance")
        from src.claude.agent import create_agent__claude
        _agent = create_agent__claude()
    return _agent

@app.entrypoint
async def invoke(payload, context):
    """Your AI agent function"""
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
