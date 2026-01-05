"""CLI entry point for local agents.

Provides command-line interface to start different types of local agents
(Claude, Ollama) with terminal interaction capabilities.
"""

import asyncio
import logging
import sys
import argparse
import importlib
from pathlib import Path

from local_agents.agent_wrapper import AgentWrapper
from strands_shared.terminal import Terminal


def discover_agents():
    """Dynamically discover agent types from directory structure."""
    agents = {}
    agents_dir = Path(__file__).parent

    for agent_path in agents_dir.iterdir():
        if agent_path.is_dir() and agent_path.name not in ['__pycache__', 'shared']:
            agent_name = agent_path.name
            agent_module_path = f"local_agents.{agent_name}.agent"

            try:
                module = importlib.import_module(agent_module_path)
                create_fn = getattr(module, f"create_agent__{agent_name}", None)

                if create_fn:
                    agents[agent_name] = {
                        "name": agent_name.replace("_", " ").title(),
                        "description": f"{agent_name.replace('_', ' ').title()} agent",
                        "create_fn": create_fn
                    }
            except (ImportError, AttributeError):
                continue

    return agents


# Agent types will be discovered in main() after logging is configured
AGENT_TYPES = {}


def list_agents():
    """Display available agent types."""
    print("Available agent types:\n")
    for agent_type, info in AGENT_TYPES.items():
        print(f"  {agent_type:20} - {info['description']}")
    print()


def create_agent(agent_type: str):
    """Create agent based on type with feedback.

    Args:
        agent_type: Type of agent to create

    Returns:
        Created agent instance

    Raises:
        SystemExit: If unknown agent type is specified.
    """
    if agent_type not in AGENT_TYPES:
        print(f"Unknown agent type: {agent_type}")
        print("\nUse --list-agents to see available types")
        sys.exit(1)

    info = AGENT_TYPES[agent_type]
    print(f"Creating {info['name']} agent...")
    return info['create_fn']()


async def main():
    """Main CLI entry point for starting local agents.

    Accepts agent type as first command line argument.

    The agent is wrapped for message capture and connected to a terminal
    interface for interactive use.

    Raises:
        SystemExit: If unknown agent type is specified.
    """
    parser = argparse.ArgumentParser(
        description="Local Strands agents CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "agent_type",
        nargs="?",
        default="claude",
        help="Type of agent to create (default: claude)"
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List available agent types and exit"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set logging level (default: WARNING)"
    )

    args = parser.parse_args()

    # Handle --list-agents
    if args.list_agents:
        list_agents()
        return

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(levelname)s - %(name)s - %(message)s'
    )

    # Discover agents after logging is configured
    global AGENT_TYPES
    AGENT_TYPES = discover_agents()
    logging.debug(f"Discovered agent types: {AGENT_TYPES}")

    # Create agent with feedback
    agent = create_agent(args.agent_type)

    # Wrap agent for message capture and start terminal interface
    wrapped_agent = AgentWrapper(agent)
    terminal = Terminal(wrapped_agent)

    await terminal.start()


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
        import sys
        sys.exit(1)
