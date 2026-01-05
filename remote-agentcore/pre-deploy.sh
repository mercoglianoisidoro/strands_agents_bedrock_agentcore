#!/bin/bash
# pre-deploy.sh - Package workspace dependencies for agentcore deployment
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📦 Syncing workspace dependencies..."

# Remove old copy/symlink and copy fresh
rm -rf "$SCRIPT_DIR/strands_shared"
cp -r "$WORKSPACE_ROOT/shared/strands_shared" "$SCRIPT_DIR/"

echo "✅ strands_shared synced"
echo "Run 'agentcore deploy' to deploy"
