#!/bin/bash
# download-conversations.sh - Download conversation logs to markdown

MINUTES=${1:-30}
OUTPUT=${2:-"conversations-$(date +%Y%m%d-%H%M%S).md"}
REGION="us-west-2"
LOG_GROUP="/aws/bedrock-agentcore/conversations"

echo "Downloading last ${MINUTES} minutes to: $OUTPUT"

{
  echo "# Conversation Logs"
  echo ""
  echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""

  aws logs filter-log-events \
    --log-group-name "$LOG_GROUP" \
    --region $REGION \
    --start-time $(($(date +%s) - MINUTES*60))000 \
    | jq -r '.events[] | .message | fromjson |
      "# \(.timestamp) | \(.agent) | \(.event)\n\n**Session:** `\(.session_id)`\n\n\(.content)\n\n---\n"'
} > "$OUTPUT"

echo "✅ Downloaded $(grep -c '^# ' "$OUTPUT") events"
echo "View: cat $OUTPUT"
