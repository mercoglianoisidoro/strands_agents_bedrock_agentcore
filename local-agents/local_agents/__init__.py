"""Local Strands agents."""

__version__ = "0.1.0"

# Lazy imports to avoid import errors when dependencies are missing
__all__ = [
    "create_agent__claude",
    "create_agent__ollama",
    "create_agent__aws_investigator",
    "AgentWrapper",
]

def __getattr__(name):
    if name == "create_agent__claude":
        from local_agents.claude.agent import create_agent__claude
        return create_agent__claude
    elif name == "create_agent__ollama":
        from local_agents.ollama.agent import create_agent__ollama
        return create_agent__ollama
    elif name == "create_agent__aws_investigator":
        from local_agents.aws_investigator.agent import create_agent__aws_investigator
        return create_agent__aws_investigator
    elif name == "AgentWrapper":
        from local_agents.agent_wrapper import AgentWrapper
        return AgentWrapper
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
