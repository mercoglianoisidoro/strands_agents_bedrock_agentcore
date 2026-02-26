"""AgentCore entrypoint for web search agent."""

from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
_agent = None


def get_agent():
    """Get or create cached agent instance."""
    global _agent
    if _agent is None:
        from multi_agents.web_search import create_web_search_agent
        _agent = create_web_search_agent()
    return _agent


@app.entrypoint
async def invoke(payload, context):
    """Web search agent entrypoint."""
    user_message = payload.get("prompt", "")
    agent = get_agent()
    
    async for event in agent.stream_async(user_message):
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]


if __name__ == "__main__":
    app.run()
