"""Configuration for web search agent."""

import os


class WebSearchConfig:
    """Configuration for web search agent."""
    
    model_id = os.getenv("MODEL_ID", "us.amazon.nova-pro-v1:0")
    region_name = os.getenv("AWS_REGION", "us-west-2")
    searxng_url = os.getenv("SEARXNG_URL", "http://localhost:8080")
    searxng_timeout = int(os.getenv("SEARXNG_TIMEOUT", "10"))
    max_results = int(os.getenv("MAX_RESULTS", "5"))
