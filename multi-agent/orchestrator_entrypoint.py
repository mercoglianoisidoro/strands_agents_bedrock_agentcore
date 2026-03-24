"""
Orchestrator Agent Entrypoint - Root Wrapper

This is the ROOT-LEVEL entrypoint file that Docker/AgentCore looks for.
It simply imports and exposes the actual app from the multi_agents package.

Pattern: Same as remote_entrypoint.py and validator_entrypoint.py
Purpose: Allows Docker to find the app at the root level while keeping
         the actual implementation organized in multi_agents/

Flow: Docker → orchestrator_entrypoint.py (this file) 
             → multi_agents/orchestrator_entrypoint.py (actual implementation)
"""

from multi_agents.orchestrator_entrypoint import app

__all__ = ["app"]
