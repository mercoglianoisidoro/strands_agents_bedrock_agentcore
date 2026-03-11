#!/bin/bash
# list-sessions.sh - List conversations by session ID (workaround for missing traceId)

TIME_WINDOW=${1:-60}  # Minutes to look back (default: 60)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

ORCH_ID=$(terraform output -raw orchestrator_arn 2>/dev/null | grep -o "[^/]*$")
START_TIME=$(($(date +%s) - TIME_WINDOW*60))000

echo "=== Unique Sessions (last ${TIME_WINDOW} minutes) ==="
echo ""

aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/${ORCH_ID}-DEFAULT" \
  --region us-west-2 \
  --start-time $START_TIME \
  | jq -r '.events[] | 
      .timestamp as $ts |
      .message as $msg |
      try (
        $msg | fromjson | 
        select(.sessionId) |
        ($ts / 1000 | strftime("%Y-%m-%d %H:%M:%S")) + " | " + .sessionId
      ) catch empty' \
  | sort -u \
  | column -t -s '|'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Usage: View session with show-session.sh"
echo "  ./show-session.sh <session-id>"
