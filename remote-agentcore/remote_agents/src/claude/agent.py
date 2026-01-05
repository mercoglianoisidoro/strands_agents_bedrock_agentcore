"""Claude Agent implementation."""

import logging
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
# from strands_tools import current_time, file_read, use_aws, http_request, file_write, environment
# from strands.tools.mcp import MCPClient
# from strands_shared.tools import lambda_aws_cli_executor
from .config import ClaudeConfig

logger = logging.getLogger(__name__)



def create_agent__claude() -> Agent:
    """Create and configure Claude agent.

    Returns:
        Configured Claude agent instance

    Raises:
        ValueError: If configuration is invalid or agent creation fails
    """
    try:
        config = ClaudeConfig()
    except Exception as e:
        raise ValueError(f"Failed to load Claude configuration: {e}") from e

    try:
        # Setup logging
        config.setup_logging()

        # Load system prompt
        system_prompt = config.load_system_prompt()

        # Create Bedrock model
        model = BedrockModel(
            model_id=config.model_id,
            region_name=config.region_name,

        )
        tools = []
        # tools = [ current_time, file_read, file_write, http_request, environment]
        # Create MCP clients
        # mcp_client_aws_doc = MCPClient(lambda: stdio_client(
        #     StdioServerParameters(
        #         command="uvx",
        #         args=["awslabs.aws-documentation-mcp-server@latest"]
        #     )
        # ))




        # Add MCP tools
        # tools += [mcp_client_aws_doc, mcp_client_browser]



        # Print tool names
        # tool_names = []
        # for tool in tools:
        #     if hasattr(tool, '__name__'):
        #         tool_names.append(tool.__name__)
        #     elif hasattr(tool, 'name'):
        #         tool_names.append(tool.name)
        #     else:
        #         tool_names.append(str(type(tool).__name__))
        # logger.info(f"Claude agent tools: {tool_names}")

        # Create agent
        return Agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt
        )

    except Exception as e:
        raise ValueError(f"Failed to create Claude agent: {e}") from e