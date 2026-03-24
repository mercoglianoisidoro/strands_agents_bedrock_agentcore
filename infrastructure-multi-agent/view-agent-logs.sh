#!/bin/bash
# View multi-agent orchestration logs

SESSION_ID=${1:-""}
SINCE=${2:-"30m"}

echo "=== ORCHESTRATOR LOGS ==="
aws logs tail /aws/bedrock-agentcore/runtimes/dev_orchestrator \
  --region us-west-2 \
  --since $SINCE \
  --format short \
  --filter-pattern "$SESSION_ID"

echo ""
echo "=== AWS INVESTIGATOR LOGS ==="
aws logs tail /aws/bedrock-agentcore/runtimes/dev_aws_investigator \
  --region us-west-2 \
  --since $SINCE \
  --format short \
  --filter-pattern "$SESSION_ID"

echo ""
echo "=== VALIDATOR LOGS ==="
aws logs tail /aws/bedrock-agentcore/runtimes/dev_validator \
  --region us-west-2 \
  --since $SINCE \
  --format short \
  --filter-pattern "$SESSION_ID"
