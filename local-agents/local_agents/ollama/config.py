"""Configuration settings for Ollama agent."""

import os
from pathlib import Path
from strands_shared.config import BaseConfig


class OllamaConfig(BaseConfig):
    """Configuration for Ollama agent."""
    
    def __init__(self) -> None:
        super().__init__(Path(__file__).parent)
        self.host: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_id: str = os.getenv("OLLAMA_MODEL", "granite4:latest")
