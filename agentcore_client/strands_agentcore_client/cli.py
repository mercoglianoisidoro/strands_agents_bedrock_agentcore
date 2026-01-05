"""CLI entry point for remote agent client.

Provides command-line interface to interact with deployed Bedrock AgentCore agents
with terminal interaction capabilities.
"""

import sys
from pathlib import Path

# Add workspace root to path for direct execution
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

import asyncio
import logging
import argparse

from strands_shared.terminal import Terminal
from strands_agentcore_client import remote_agent_client


async def main():
    """Main CLI entry point for remote agent client.
    
    Connects to a deployed Bedrock AgentCore agent and provides
    an interactive terminal interface.
    """
    parser = argparse.ArgumentParser(
        description="Remote AgentCore client CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--agent-arn",
        help="Agent ARN (if not provided, reads from .bedrock_agentcore.yaml)"
    )
    parser.add_argument(
        "--config-path",
        help="Path to .bedrock_agentcore.yaml file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set logging level (default: WARNING)"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(levelname)s - %(name)s - %(message)s'
    )

    try:
        # Create remote agent client
        print("Connecting to remote agent...")
        client = remote_agent_client(
            agent_arn=args.agent_arn,
            config_path=args.config_path,
            log_session=True
        )
        print(f"Connected to agent: {client.agent_arn}")
        
        # Start terminal interface
        terminal = Terminal(client)
        await terminal.start()
        
    except Exception as e:
        print(f"Failed to connect to remote agent: {e}")
        sys.exit(1)


def run_main():
    """Synchronous wrapper to run the async main function."""
    asyncio.run(main())


if __name__ == "__main__":
    try:
        run_main()
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C - message already shown by Terminal
        pass
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)