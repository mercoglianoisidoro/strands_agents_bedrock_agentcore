#!/bin/bash
# pre-deploy.sh - Package workspace dependencies for Docker build
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📦 Syncing workspace dependencies..."

# Copy strands_shared into build context
rm -rf "$SCRIPT_DIR/strands_shared"
cp -r "$WORKSPACE_ROOT/shared/strands_shared" "$SCRIPT_DIR/"
echo "✅ strands_shared synced"

echo "✅ Ready for Docker build"
