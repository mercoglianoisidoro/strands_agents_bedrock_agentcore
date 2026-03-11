#!/bin/bash
# Real-time multi-agent log streaming with color-coded output
#
# USAGE:
#   ./stream-logs.sh [output_file] [--json]
#
# EXAMPLES:
#   ./stream-logs.sh                    # Stream to multi-agent-logs-live.txt
#   ./stream-logs.sh my-session.txt     # Stream to custom file
#   ./stream-logs.sh --json             # Pretty-print JSON logs
#
# Press Ctrl+C to stop streaming
#
# This script streams logs from all 3 agents in real-time:
# - Orchestrator (blue) - routing decisions
# - AWS Investigator (green) - research
# - Validator (yellow) - verification
#
# Logs are displayed on screen AND written to file simultaneously

# Parse arguments
OUTPUT="multi-agent-logs-live.txt"
PRETTY_JSON=false

for arg in "$@"; do
  case $arg in
    --json)
      PRETTY_JSON=true
      ;;
    *)
      OUTPUT="$arg"
      ;;
  esac
done

# Get current agent runtime IDs (go to parent directory for terraform)
cd "$(dirname "$0")/.."
ORCH_ID=$(terraform output -raw orchestrator_arn 2>/dev/null | grep -o '[^/]*$')
INV_ID=$(terraform output -raw aws_investigator_arn 2>/dev/null | grep -o '[^/]*$')
VAL_ID=$(terraform output -raw validator_arn 2>/dev/null | grep -o '[^/]*$')
cd - > /dev/null

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
GRAY='\033[0;90m'
RESET='\033[0m'

echo -e "${BLUE}🔴 Streaming logs in real-time (Ctrl+C to stop)...${RESET}"
echo -e "${GRAY}📝 Writing to: $OUTPUT${RESET}"
echo -e "${BLUE}📊 Orchestrator: $ORCH_ID${RESET}"
echo -e "${GREEN}📊 Investigator: $INV_ID${RESET}"
echo -e "${YELLOW}📊 Validator: $VAL_ID${RESET}"
echo ""

# Clear output file
> "$OUTPUT"

# Pretty-print function for JSON logs
pretty_print() {
  local prefix="$1"
  while IFS= read -r line; do
    # Extract timestamp and message
    timestamp=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}')
    content=$(echo "$line" | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} //')
    
    # Check if content is JSON
    if echo "$content" | jq -e . >/dev/null 2>&1; then
      # Extract key fields
      body=$(echo "$content" | jq -r '.body // empty' 2>/dev/null)
      severity=$(echo "$content" | jq -r '.severityText // empty' 2>/dev/null)
      scope=$(echo "$content" | jq -r '.scope.name // empty' 2>/dev/null | sed 's/.*\.//')
      
      # Handle different body types
      if [ -n "$body" ]; then
        # Check if body is an object with nested content
        if echo "$body" | jq -e '.content // .message.content' >/dev/null 2>&1; then
          text=$(echo "$body" | jq -r '.content[0].text // .message.content[0].text // empty' 2>/dev/null)
          if [ -n "$text" ]; then
            echo -e "${prefix}${GRAY}${timestamp}${RESET} ${severity:+[$severity]} ${scope:+{$scope}} $text"
          else
            echo -e "${prefix}${GRAY}${timestamp}${RESET} ${severity:+[$severity]} ${scope:+{$scope}} [complex message]"
          fi
        else
          # Simple string body
          echo -e "${prefix}${GRAY}${timestamp}${RESET} ${severity:+[$severity]} ${scope:+{$scope}} $body"
        fi
      else
        echo -e "${prefix}${GRAY}${timestamp}${RESET} ${severity:+[$severity]} ${scope:+{$scope}} [no body]"
      fi
    else
      # Plain text log
      echo -e "${prefix}${GRAY}${timestamp}${RESET} $content"
    fi
  done
}

# Stream all three agents in parallel with smart formatting
{
  aws logs tail /aws/bedrock-agentcore/runtimes/${ORCH_ID}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | pretty_print "$(echo -e ${BLUE})[ORCH]$(echo -e ${RESET}) " &
  
  aws logs tail /aws/bedrock-agentcore/runtimes/${INV_ID}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | pretty_print "$(echo -e ${GREEN})[INVE]$(echo -e ${RESET}) " &
  
  aws logs tail /aws/bedrock-agentcore/runtimes/${VAL_ID}-DEFAULT \
    --region us-west-2 \
    --follow \
    --format short 2>/dev/null | pretty_print "$(echo -e ${YELLOW})[VALD]$(echo -e ${RESET}) " &
  
  wait
} | tee -a "$OUTPUT"
