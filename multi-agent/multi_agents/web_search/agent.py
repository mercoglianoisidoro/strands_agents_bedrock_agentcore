"""Web search agent implementation."""

from strands import Agent
from strands.models import BedrockModel
from .tools.searxng_tool import web_search
from .tools.fetch_content_tool import fetch_webpage
from .config import WebSearchConfig
from pathlib import Path


def create_web_search_agent() -> Agent:
    """Create web search agent with SearxNG tool."""
    
    config = WebSearchConfig()
    
    # Load system prompt
    prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
    system_prompt = prompt_path.read_text()
    
    # Create model
    model = BedrockModel(
        model_id=config.model_id,
        region_name=config.region_name
    )
    
    # Create agent
    return Agent(
        model=model,
        tools=[web_search, fetch_webpage],
        system_prompt=system_prompt
    )
