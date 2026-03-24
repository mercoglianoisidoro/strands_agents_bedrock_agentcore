"""Validator agent implementation."""

from strands import Agent
from strands.models import BedrockModel
from strands_shared.tools import lambda_aws_cli_executor
from strands_tools import http_request
from multi_agents.aws_investigator.tools.fetch_content_tool import fetch_webpage
from .config import ValidatorConfig


def create_validator_agent() -> Agent:
    """Create validator agent for evidence verification."""
    
    config = ValidatorConfig()
    
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
    
    # Create agent with verification tools only
    return Agent(
        model=model,
        tools=[fetch_webpage, http_request, lambda_aws_cli_executor],
        system_prompt=system_prompt
    )
