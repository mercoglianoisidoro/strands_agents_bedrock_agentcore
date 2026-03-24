#!/bin/bash
# Force redeploy all agents with fresh Docker images
# Usage: ./redeploy_forced.sh [agent_name]
#   agent_name: orchestrator, aws_investigator, validator, or "all" (default)

set -e

AGENT=${1:-all}
LOG_FILE="/tmp/tf-redeploy-$(date +%Y%m%d-%H%M%S).log"

echo "🔄 Force redeploying agents..."
echo "📝 Logs: $LOG_FILE"
echo ""

# Taint resources to force recreation
if [ "$AGENT" = "all" ] || [ "$AGENT" = "orchestrator" ]; then
    echo "⚡ Tainting orchestrator..."
    terraform taint aws_bedrockagentcore_agent_runtime.orchestrator 2>/dev/null || true
fi

if [ "$AGENT" = "all" ] || [ "$AGENT" = "aws_investigator" ]; then
    echo "⚡ Tainting aws_investigator..."
    terraform taint aws_bedrockagentcore_agent_runtime.aws_investigator 2>/dev/null || true
fi

if [ "$AGENT" = "all" ] || [ "$AGENT" = "validator" ]; then
    echo "⚡ Tainting validator..."
    terraform taint aws_bedrockagentcore_agent_runtime.validator 2>/dev/null || true
fi

# Always rebuild Docker image
echo "⚡ Tainting Docker image..."
terraform taint docker_image.multi_agent 2>/dev/null || true
terraform taint docker_registry_image.multi_agent 2>/dev/null || true

echo ""
echo "🚀 Starting deployment..."
echo "   This will take 3-5 minutes"
echo ""

# Run terraform apply in background
terraform apply -auto-approve | tee "$LOG_FILE" 2>&1 &
TF_PID=$!

# Show progress
echo "⏳ Deploying (PID: $TF_PID)..."
echo "   Monitor: tail -f $LOG_FILE"
echo ""

# Wait for completion
wait $TF_PID
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 New ARNs:"
    grep -E "aws_investigator_arn|validator_arn|orchestrator_arn" "$LOG_FILE" | tail -3
    echo ""
    echo "📝 Full logs: $LOG_FILE"
else
    echo ""
    echo "❌ Deployment failed!"
    echo "📝 Check logs: $LOG_FILE"
    tail -20 "$LOG_FILE"
    exit 1
fi
