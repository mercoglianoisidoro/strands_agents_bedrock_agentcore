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

# Create .bedrock_agentcore.yaml from template if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.bedrock_agentcore.yaml" ]; then
    cp "$SCRIPT_DIR/.bedrock_agentcore-template.yaml" "$SCRIPT_DIR/.bedrock_agentcore.yaml"
    echo "✅ .bedrock_agentcore.yaml created from template"
fi


echo "Run 'agentcore deploy' to deploy"

