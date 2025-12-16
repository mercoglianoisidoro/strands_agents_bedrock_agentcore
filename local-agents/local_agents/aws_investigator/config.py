"""Configuration settings for AWS Investigator agent."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class AwsInvestigatorConfig(BaseConfig):
    """Configuration for AWS Investigator agent."""

    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.model_id: str = os.environ.get("MODEL_ID", "us.anthropic.claude-3-5-haiku-20241022-v1:0")
        self.region_name: str = os.environ.get("REGION_NAME", "us-west-2")
        aws_profile = os.environ.get("AWS_PROFILE")
        self.aws_profile: str | None = aws_profile if aws_profile and aws_profile.strip() else None
