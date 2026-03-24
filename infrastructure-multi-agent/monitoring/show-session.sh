#!/bin/bash
# show-session.sh - Show conversation by session ID

SESSION_ID=$1
REGION="us-west-2"

if [ -z "$SESSION_ID" ]; then
  echo "Usage: ./show-session.sh <session-id>"
  echo ""
  echo "Get session IDs with: ./list-sessions.sh"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

ORCH_ID=$(terraform output -raw orchestrator_arn 2>/dev/null | grep -o "[^/]*$")
INV_ID=$(terraform output -raw aws_investigator_arn 2>/dev/null | grep -o "[^/]*$")
VAL_ID=$(terraform output -raw validator_arn 2>/dev/null | grep -o "[^/]*$")

echo "=== Session: $SESSION_ID ==="
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📤 ORCHESTRATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/${ORCH_ID}-DEFAULT" \
  --region $REGION \
  --filter-pattern "$SESSION_ID" \
  | jq -r '.events[] | 
    .timestamp as $ts |
    .message as $msg |
    ($ts / 1000 | strftime("%H:%M:%S")) + " | " +
    (try ($msg | fromjson | .message) catch ($msg | .[0:100]))'

echo ""
echo "🔍 INVESTIGATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
INV_COUNT=$(aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/${INV_ID}-DEFAULT" \
  --region $REGION \
  --filter-pattern "$SESSION_ID" \
  | jq '.events | length')

if [ "$INV_COUNT" -gt 0 ]; then
  aws logs filter-log-events \
    --log-group-name "/aws/bedrock-agentcore/runtimes/${INV_ID}-DEFAULT" \
    --region $REGION \
    --filter-pattern "$SESSION_ID" \
    | jq -r '.events[] | 
      .timestamp as $ts |
      .message as $msg |
      ($ts / 1000 | strftime("%H:%M:%S")) + " | " +
      (try ($msg | fromjson | .message) catch ($msg | .[0:100]))' \
    | head -20
else
  echo "  (No investigator activity)"
fi

echo ""
echo "✅ VALIDATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
VAL_COUNT=$(aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/${VAL_ID}-DEFAULT" \
  --region $REGION \
  --filter-pattern "$SESSION_ID" \
  | jq '.events | length')

if [ "$VAL_COUNT" -gt 0 ]; then
  aws logs filter-log-events \
    --log-group-name "/aws/bedrock-agentcore/runtimes/${VAL_ID}-DEFAULT" \
    --region $REGION \
    --filter-pattern "$SESSION_ID" \
    | jq -r '.events[] | 
      .timestamp as $ts |
      .message as $msg |
      ($ts / 1000 | strftime("%H:%M:%S")) + " | " +
      (try ($msg | fromjson | .message) catch ($msg | .[0:100]))' \
    | head -20
else
  echo "  (No validator activity)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
