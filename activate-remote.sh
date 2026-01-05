#!/bin/bash
# Activate the workspace virtual environment and sync dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
cd "$SCRIPT_DIR/remote-agentcore"

# Sync workspace dependencies for deployment
./pre-deploy.sh
