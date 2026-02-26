"""Web search agent implementation."""

from strands import Agent
from strands.models import BedrockModel
from strands_shared.tools import lambda_aws_cli_executor
from .tools.searxng_tool import web_search
from .tools.fetch_content_tool import fetch_webpage
from .config import WebSearchConfig


def create_web_search_agent() -> Agent:
    """Create web search agent with SearxNG and AWS tools."""
    
    config = WebSearchConfig()
    
    # Setup logging (skip if colorlog not available)
    try:
        config.setup_logging()
    except ImportError:
        pass
    
    # Load system prompt
    system_prompt = config.load_system_prompt()
    
    # Create model
    model = BedrockModel(
        model_id=config.model_id,
        region_name=config.region_name
    )
    
    # Create agent with AWS capability
    return Agent(
        model=model,
        tools=[web_search, fetch_webpage, lambda_aws_cli_executor],
        system_prompt=system_prompt
    )
