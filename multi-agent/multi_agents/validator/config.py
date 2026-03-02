"""Validator agent configuration."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class ValidatorConfig(BaseConfig):
    """Configuration for validator agent."""
    
    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.model_id: str = os.getenv("MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
        self.region_name: str = os.getenv("AWS_REGION", "us-west-2")
