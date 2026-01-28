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

# Clean agentcore cache to prevent bloated deployments
rm -rf "$SCRIPT_DIR/remote_agents/.bedrock_agentcore"
echo "✅ .bedrock_agentcore cache cleaned"

# Create .bedrock_agentcore.yaml from template if it doesn't exist

if [ ! -f "$SCRIPT_DIR/.bedrock_agentcore.yaml" ]; then
    # cp "$SCRIPT_DIR/.bedrock_agentcore-template.yaml" "$SCRIPT_DIR/.bedrock_agentcore.yaml"
    # echo "✅ .bedrock_agentcore.yaml created from template"

    agentcore configure \
    --entrypoint remote_agents/remote_agent.py \
    --name test_agent \
    --deployment-type direct_code_deploy \
    --runtime PYTHON_3_10 \
    --disable-memory \
    --non-interactive

    echo "✅ .bedrock_agentcore.yaml created using 'agentcore configure'"

fi


echo "Run 'agentcore deploy' to deploy"

