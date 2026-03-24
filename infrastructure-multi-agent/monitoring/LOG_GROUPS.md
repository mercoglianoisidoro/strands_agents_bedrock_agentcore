# CloudWatch Log Groups - Multi-Agent System

## Overview

This document explains all CloudWatch Log Groups used by the multi-agent system, how they're created, what they contain, and how to use them.

---

## Agent Runtime Log Groups

### 1. Orchestrator Log Group
**Name**: `/aws/bedrock-agentcore/runtimes/dev_orchestrator-<RUNTIME_ID>-DEFAULT`

**Created by**: AWS Bedrock AgentCore automatically when agent is first invoked

**Contains**:
- User queries received by orchestrator
- Tool calls to sub-agents (call_aws_investigator, call_validator)
- Agent reasoning and decision-making logs
- Final responses to users
- OTEL telemetry data (trace IDs, span IDs, session IDs)

**Log Streams**:
- `otel-rt-logs` - OpenTelemetry instrumentation logs
- `2026/03/09/[runtime-logs]<UUID>` - Individual invocation logs

**Terraform Configuration**: `agent_orchestrator.tf`
```hcl
resource "aws_cloudwatch_log_group" "orchestrator" {
  name              = "/aws/bedrock-agentcore/runtimes/${aws_bedrock_agentcore_agent_runtime.orchestrator.id}-DEFAULT"
  retention_in_days = 7
}
```

**Key Fields**:
- `traceId` - Unique identifier for entire conversation
- `attributes["session.id"]` - Session identifier for A2A calls
- `body.input.messages` - User input
- `body.message.tool_calls` - Sub-agent invocations
- `body.output.messages` - Agent responses

---

### 2. AWS Investigator Log Group
**Name**: `/aws/bedrock-agentcore/runtimes/dev_aws_investigator-<RUNTIME_ID>-DEFAULT`

**Created by**: AWS Bedrock AgentCore automatically when agent is first invoked

**Contains**:
- Queries received from orchestrator
- Web search activity
- Web page fetching (fetch_webpage tool)
- Research results
- OTEL telemetry data

**Log Streams**: Same pattern as orchestrator

**Terraform Configuration**: `agent_aws_investigator.tf`
```hcl
resource "aws_cloudwatch_log_group" "aws_investigator" {
  name              = "/aws/bedrock-agentcore/runtimes/${aws_bedrock_agentcore_agent_runtime.aws_investigator.id}-DEFAULT"
  retention_in_days = 7
}
```

**Key Fields**:
- `body.content[0].toolUse.name` - Tool being used (web_search, fetch_webpage)
- `body.content[0].text` - Agent reasoning and responses
- Linked to orchestrator via `session.id`

---

### 3. Validator Log Group
**Name**: `/aws/bedrock-agentcore/runtimes/dev_validator-<RUNTIME_ID>-DEFAULT`

**Created by**: AWS Bedrock AgentCore automatically when agent is first invoked

**Contains**:
- Validation requests from orchestrator
- Evidence verification activity
- Claim validation results
- OTEL telemetry data

**Log Streams**: Same pattern as orchestrator

**Terraform Configuration**: `agent_validator.tf`
```hcl
resource "aws_cloudwatch_log_group" "validator" {
  name              = "/aws/bedrock-agentcore/runtimes/${aws_bedrock_agentcore_agent_runtime.validator.id}-DEFAULT"
  retention_in_days = 7
}
```

**Key Fields**:
- `body.content[0].text` - Validation claims and results
- Linked to orchestrator via `session.id`

---

## Conversation Logging

### 7. Conversations Log Group
**Name**: `/aws/bedrock-agentcore/conversations`

**Created by**: Terraform (`observability.tf`)

**Contains**: 
- Structured A2A conversation flow logs
- User queries to orchestrator
- Orchestrator → Investigator calls and responses
- Orchestrator → Validator calls and responses
- Final responses to users
- Error logs for failed A2A calls

**Purpose**: Dedicated log group for tracing complete conversation flow between orchestrator and sub-agents in human-readable format.

**Terraform Configuration**:
```hcl
resource "aws_cloudwatch_log_group" "conversations" {
  name              = "/aws/bedrock-agentcore/conversations"
  retention_in_days = 7
}
```

**Log Format**: JSON with fields:
- `timestamp` - ISO 8601 timestamp
- `session_id` - Session identifier
- `event` - Event type (user_query, a2a_call, a2a_response, a2a_error, final_response)
- `agent` - Agent identifier (user, orchestrator→investigator, investigator→orchestrator, etc.)
- `content` - Full message content

**Example Log Entry**:
```json
{
  "timestamp": "2026-03-11 15:05:24",
  "session_id": "session-20260311-160508-279967733",
  "event": "a2a_call",
  "agent": "orchestrator→investigator",
  "content": "What causes CloudWatch log group 'aws/spans' error?"
}
```

**Monitoring Scripts**:
- `monitoring/list-conversations.sh` - List recent conversations
- `monitoring/show-conversation.sh <session-id>` - Show complete conversation
- `monitoring/download-conversations.sh [minutes] [output.md]` - Export to markdown
- `monitoring/tail-conversations.sh` - Real-time tail

**Usage**:
```bash
cd infrastructure-multi-agent/monitoring

# List recent conversations
./list-conversations.sh 60

# Show specific conversation
./show-conversation.sh session-20260311-160508-279967733

# Download last 2 hours to markdown
./download-conversations.sh 120 conversations.md

# Real-time monitoring
./tail-conversations.sh
```

---

## OTEL Observability Log Groups

### 4. X-Ray Spans Log Group
**Name**: `/aws/spans`

**Created by**: Terraform (`agent_shared.tf`)

**Contains**: X-Ray trace spans exported to CloudWatch Logs (when Transaction Search is enabled)

**Terraform Configuration**:
```hcl
resource "aws_cloudwatch_log_group" "xray_spans" {
  name              = "/aws/spans"
  retention_in_days = 7
}
```

**Status**: Currently empty (spans not propagating - known limitation of preview feature)

---

### 5. Default Spans Log Group
**Name**: `/aws/spans/default`

**Created by**: Terraform (`agent_shared.tf`)

**Contains**: Default destination for X-Ray spans

**Terraform Configuration**:
```hcl
resource "aws_cloudwatch_log_group" "xray_spans_default" {
  name              = "/aws/spans/default"
  retention_in_days = 7
}
```

**Status**: Currently empty (spans not propagating)

---

### 6. Application Signals Log Group
**Name**: `/aws/application-signals/data`

**Created by**: Terraform (`agent_shared.tf`)

**Contains**: AWS Application Signals telemetry data

**Terraform Configuration**:
```hcl
resource "aws_cloudwatch_log_group" "application_signals" {
  name              = "/aws/spans/default"
  retention_in_days = 7
}
```

**Status**: Currently empty

---

## Log Group Permissions

All agents have permissions to write to their respective log groups via IAM policies in `agent_shared.tf`:

```hcl
resource "aws_iam_policy" "agent_cloudwatch_logs" {
  name = "${var.environment}_agent_cloudwatch_logs"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock-agentcore/conversations*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/spans*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/application-signals/*"
        ]
      }
    ]
  })
}
```

---

## How Logs Are Generated

### 1. Agent Invocation Flow
```
User → Orchestrator → CloudWatch Log Group
                   ↓
              Sub-Agent (Investigator/Validator) → CloudWatch Log Group
```

### 2. OTEL Instrumentation
Configured via environment variables in Terraform:

```hcl
environment_variables = {
  AGENT_OBSERVABILITY_ENABLED         = "true"
  OTEL_PYTHON_DISTRO                  = "aws_distro"
  OTEL_PYTHON_CONFIGURATOR            = "aws_configurator"
  OTEL_EXPORTER_OTLP_PROTOCOL         = "http/protobuf"
  OTEL_TRACES_EXPORTER                = "otlp"
  OTEL_EXPORTER_OTLP_TRACES_ENDPOINT  = "https://xray.us-west-2.amazonaws.com/v1/traces"
  OTEL_EXPORTER_OTLP_TRACES_PROTOCOL  = "http/protobuf"
  OTEL_RESOURCE_ATTRIBUTES            = "service.name=${agent_name}"
}
```

### 3. Agent Entrypoint
Agents start with OTEL instrumentation (`start.sh`):

```bash
if [ "${AGENT_OBSERVABILITY_ENABLED}" = "true" ]; then
    exec opentelemetry-instrument python -m uvicorn ${AGENT_ENTRYPOINT}:app --host 0.0.0.0 --port 8080
else
    exec python -m uvicorn ${AGENT_ENTRYPOINT}:app --host 0.0.0.0 --port 8080
fi
```

---

## Querying Logs

### Using AWS CLI

**Get recent logs**:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/dev_orchestrator-<ID>-DEFAULT \
  --region us-west-2 \
  --since 30m \
  --follow
```

**Filter by trace ID**:
```bash
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/dev_orchestrator-<ID>-DEFAULT \
  --region us-west-2 \
  --filter-pattern "69aebe0150c386a51602ecb75e260045"
```

**Filter by session ID**:
```bash
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/dev_aws_investigator-<ID>-DEFAULT \
  --region us-west-2 \
  --filter-pattern "session-20260309-111832-276050174"
```

### Using CloudWatch Logs Insights

**Basic query**:
```
fields @timestamp, @message
| filter @message like /traceId/
| sort @timestamp desc
| limit 100
```

**Extract trace and session IDs**:
```
fields @timestamp
| filter @message like /traceId/
| parse @message '"traceId":"*"' as traceId
| parse @message '"session.id":"*"' as sessionId
| display @timestamp, traceId, sessionId
| sort @timestamp desc
```

### Using Traceability Scripts

**List all traces**:
```bash
cd infrastructure-multi-agent
./list-traces.sh 60  # Last 60 minutes
```

**Show complete conversation**:
```bash
./show-trace.sh <trace-id>
```

**Show A2A communication**:
```bash
./a2a-trace.sh 30  # Last 30 minutes
```

**Real-time streaming**:
```bash
./stream-logs.sh orchestrator
```

See `TRACEABILITY.md` for complete documentation.

---

## Log Retention

**Current Setting**: 7 days for all log groups

**Configured in**: Each agent's Terraform file

**To change**:
```hcl
resource "aws_cloudwatch_log_group" "orchestrator" {
  name              = "/aws/bedrock-agentcore/runtimes/${aws_bedrock_agentcore_agent_runtime.orchestrator.id}-DEFAULT"
  retention_in_days = 30  # Change to desired days
}
```

**Options**: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653, or never expire (0)

---

## Clearing Logs

**Empty all log groups** (preserves groups):
```bash
cd infrastructure-multi-agent

# Get agent IDs
ORCH_ID=$(terraform output -raw orchestrator_arn | grep -o "[^/]*$")
INV_ID=$(terraform output -raw aws_investigator_arn | grep -o "[^/]*$")
VAL_ID=$(terraform output -raw validator_arn | grep -o "[^/]*$")

# Delete all log streams
for log_group in \
  "/aws/bedrock-agentcore/runtimes/${ORCH_ID}-DEFAULT" \
  "/aws/bedrock-agentcore/runtimes/${INV_ID}-DEFAULT" \
  "/aws/bedrock-agentcore/runtimes/${VAL_ID}-DEFAULT" \
  "/aws/bedrock-agentcore/conversations" \
  "/aws/spans" \
  "/aws/spans/default" \
  "/aws/application-signals/data"; do
  
  aws logs describe-log-streams \
    --log-group-name "$log_group" \
    --region us-west-2 \
    --query 'logStreams[].logStreamName' \
    --output text \
    | tr '\t' '\n' \
    | while read stream; do
        [ -n "$stream" ] && aws logs delete-log-stream \
          --log-group-name "$log_group" \
          --log-stream-name "$stream" \
          --region us-west-2 2>/dev/null
      done
done
```

---

## Troubleshooting

### No logs appearing
1. Check agent is deployed: `terraform output`
2. Verify log group exists: `aws logs describe-log-groups --region us-west-2`
3. Check IAM permissions in `agent_shared.tf`
4. Invoke agent and wait 10-30 seconds for logs to propagate

### Logs from wrong session appearing
- Session IDs can persist across multiple invocations
- Use trace ID for precise filtering
- Clear logs if needed (see above)

### OTEL logs empty
- `/aws/spans` and `/aws/spans/default` are expected to be empty
- This is a known limitation of CloudWatch GenAI Observability preview
- Use agent runtime logs instead

### Can't find trace ID
- Trace IDs only generated for orchestrator invocations
- Direct sub-agent calls don't create traces
- Use `./list-traces.sh` to find available traces

---

## Cost Considerations

**CloudWatch Logs Pricing** (us-west-2):
- Ingestion: $0.50 per GB
- Storage: $0.03 per GB/month
- Insights queries: $0.005 per GB scanned

**Typical Usage**:
- ~1-2 MB per agent invocation
- 7-day retention = minimal storage costs
- Estimated: $1-5/month for moderate usage

**Cost Optimization**:
- Reduce retention period if not needed
- Use filter patterns to reduce query costs
- Delete old log streams periodically

---

## Related Documentation

- `TRACEABILITY.md` - Complete guide to tracing scripts
- `/docs/a2a-debugging-guide.md` - A2A debugging strategies
- `/docs/observability-issues-analysis.md` - CloudWatch GenAI Observability analysis
- `/docs/otel-implementation-complete.md` - OTEL implementation details
