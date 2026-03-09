"""Configuration for orchestrator agent."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class OrchestratorConfig(BaseConfig):
    """Configuration for orchestrator agent."""

    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.model_id: str = os.getenv("MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
        self.region_name: str = os.getenv("AWS_REGION", "us-west-2")
