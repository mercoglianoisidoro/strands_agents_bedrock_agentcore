"""Configuration for AWS investigator agent."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class AwsInvestigatorConfig(BaseConfig):
    """Configuration for AWS investigator agent."""
    
    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.model_id: str = os.getenv("MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
        self.region_name: str = os.getenv("AWS_REGION", "us-west-2")
        self.searxng_url: str = os.getenv("SEARXNG_URL", "http://localhost:8080")
        self.searxng_timeout: int = int(os.getenv("SEARXNG_TIMEOUT", "10"))
        self.max_results: int = int(os.getenv("MAX_RESULTS", "5"))
