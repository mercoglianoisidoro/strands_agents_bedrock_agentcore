"""Local Strands agents."""

from local_agents.claude.agent import create_agent__claude
from local_agents.ollama.agent import create_agent__ollama
from local_agents.aws_investigator.agent import create_agent__aws_investigator
from local_agents.agent_wrapper import AgentWrapper

__version__ = "0.1.0"

__all__ = [
    "create_agent__claude",
    "create_agent__ollama",
    "create_agent__aws_investigator",
    "AgentWrapper",
]
