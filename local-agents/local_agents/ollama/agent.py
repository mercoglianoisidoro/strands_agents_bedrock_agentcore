"""Ollama Agent implementation."""

import logging
from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools import current_time, file_read, use_aws, http_request, file_write
# from strands_shared.tools import lambda_aws_cli_executor
from .config import OllamaConfig

logger = logging.getLogger(__name__)


def create_agent__ollama() -> Agent:
    """Create and configure Ollama agent.
    
    Returns:
        Configured Ollama agent instance
        
    Raises:
        ValueError: If configuration is invalid or agent creation fails
    """
    try:
        config = OllamaConfig()
    except Exception as e:
        raise ValueError(f"Failed to load Ollama configuration: {e}") from e

    try:
        # Setup logging
        config.setup_logging()

        # Load system prompt
        system_prompt = config.load_system_prompt()

        # Create Ollama model with parameters optimized to prevent loops
        model = OllamaModel(
            host=config.host,
            model_id=config.model_id,
            # temperature=0.0,  # Zero temperature for deterministic responses
        # top_p=0.95,       # Higher top_p for better reasoning
        # max_tokens=4096   # More tokens for complete responses
        )

        logger.info(f"Ollama model configured: host={config.host}, model_id={config.model_id}")

        # Enable debug logging for model interactions
        # logging.getLogger("strands").setLevel(logging.DEBUG)
        # logging.getLogger("strands.models.ollama").setLevel(logging.DEBUG)
        # logging.getLogger("strands.agent").setLevel(logging.DEBUG)


        # Define tools
        tools = [use_aws, current_time, file_read, file_write, http_request]
        logger.info(f"Ollama agent tools: {[tool.__name__ for tool in tools]}")

        # Create agent with max iterations to prevent infinite loops
        return Agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            # max_iterations=3  # Limit to 3 tool calls to prevent loops
        )
    except Exception as e:
        raise ValueError(f"Failed to create Ollama agent: {e}") from e
