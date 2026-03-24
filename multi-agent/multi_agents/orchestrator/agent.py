"""Orchestrator agent implementation."""

from strands import Agent
from strands.models import BedrockModel

from .config import OrchestratorConfig
from .tools import call_aws_investigator, call_validator


def create_orchestrator_agent() -> Agent:
    """Create and configure the orchestrator agent."""
    config = OrchestratorConfig()
    
    return Agent(
        model=BedrockModel(model_id=config.model_id),
        tools=[call_aws_investigator, call_validator],
        system_prompt=config.load_system_prompt(),
    )
