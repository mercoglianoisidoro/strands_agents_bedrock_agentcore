"""Configuration settings for Claude agent."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class ClaudeConfig(BaseConfig):
    """Configuration for Claude agent."""

    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.model_id: str = os.getenv("CLAUDE_MODEL", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
        self.region_name: str = os.getenv("AWS_REGION", "us-west-2")
        aws_profile = os.getenv("AWS_PROFILE")
        self.aws_profile: str | None = aws_profile if aws_profile and aws_profile.strip() else None
