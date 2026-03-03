#!/bin/bash
# Real-time multi-agent log streaming with chronological merge
#
# USAGE:
#   ./stream-logs.sh [output_file]
#
# EXAMPLES:
#   ./stream-logs.sh                    # Stream to multi-agent-logs-live.txt
#   ./stream-logs.sh my-session.txt     # Stream to custom file
#
# Press Ctrl+C to stop streaming
#
# This script streams logs from all 3 agents in real-time:
# - Orchestrator (routing decisions)
# - AWS Investigator (research)
# - Validator (verification)
#
# Logs are displayed on screen AND written to file simultaneously

OUTPUT=${1:-"multi-agent-logs-live.txt"}

# Get current agent ARNs
ORCH_ARN=$(terraform output -raw orchestrator_arn 2>/dev/null | grep -o '[^/]*$')
INV_ARN=$(terraform output -raw aws_investigator_arn 2>/dev/null | grep -o '[^/]*$')
VAL_ARN=$(terraform output -raw validator_arn 2>/dev/null | grep -o '[^/]*$')

echo "🔴 Streaming logs in real-time (Ctrl+C to stop)..."
echo "📝 Writing to: $OUTPUT"
echo "📊 Orchestrator: $ORCH_ARN"
echo "📊 Investigator: $INV_ARN"
echo "📊 Validator: $VAL_ARN"
echo ""

# Clear output file
> "$OUTPUT"

# Stream all three agents in parallel
{
  aws logs tail /aws/bedrock-agentcore/runtimes/dev_orchestrator-${ORCH_ARN}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | sed 's/^/[ORCHESTRATOR] /' &
  
  aws logs tail /aws/bedrock-agentcore/runtimes/dev_aws_investigator-${INV_ARN}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | sed 's/^/[INVESTIGATOR] /' &
  
  aws logs tail /aws/bedrock-agentcore/runtimes/dev_validator-${VAL_ARN}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | sed 's/^/[VALIDATOR] /' &
  
  wait
} | tee "$OUTPUT"
