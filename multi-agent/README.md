# Multi-Agent System

A multi-agent architecture using AWS Bedrock AgentCore with specialized agents coordinated by an orchestrator.

## Architecture

```
┌─────────────────────────────────────┐
│         Orchestrator                │
│   (Coordinates specialized agents)  │
└────────┬──────────────┬─────────────┘
         │              │
         ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│ AWS Investigator │  │    Validator     │
│                  │  │                  │
│ Investigates and │  │ Verifies claims  │
│ provides answers │  │ by re-checking   │
│ with evidence    │  │ evidence sources │
└──────────────────┘  └──────────────────┘
```

## Agents

### 1. AWS Investigator (`aws_investigator`)

**Purpose**: Investigate questions using web search and AWS CLI commands.

**Tools**:
- `web_search` - Search the web using SearxNG
- `fetch_webpage` - Fetch and convert webpages to markdown
- `http_request` - Make HTTP API requests
- `lambda_aws_cli_executor` - Execute AWS CLI commands via Lambda

**Use Cases**:
- "What EC2 instances are running in my account?"
- "What is AWS Lambda pricing?"
- "Search for AWS best practices for S3"

**Output**: Answers with supporting evidence (URLs, commands used)

---

### 2. Validator (`validator`)

**Purpose**: Independently verify claims by re-checking evidence sources.

**Tools**:
- `fetch_webpage` - Re-fetch URLs to verify content
- `http_request` - Re-call APIs to verify data
- `lambda_aws_cli_executor` - Re-run AWS commands to verify state

**Use Cases**:
- Verify: "EC2 instance i-123 is running (evidence: aws ec2 describe-instances)"
- Verify: "Lambda costs $0.20/1M requests (evidence: https://aws.amazon.com/lambda/pricing/)"

**Output**: Verification result (VERIFIED, DISCREPANCY, UNABLE_TO_VERIFY) with details

---

### 3. Orchestrator (`orchestrator`) - *Coming Soon*

**Purpose**: Coordinate aws_investigator and validator using A2A protocol.

**Workflow**:
1. Receive user query
2. Call `aws_investigator` to investigate
3. Call `validator` to verify evidence
4. Synthesize final answer with verification status

---

## Development

### Run Agent Locally

```bash
cd multi-agent

# Install dependencies
uv sync

# Run development server
uv run agentcore dev

# Test in another terminal
uv run agentcore invoke --dev "Your question here"
```

### Deploy to AWS

```bash
cd ../infrastructure-multi-agent
terraform init
terraform apply
```

### Test Deployed Agent

```bash
cd ../agentcore_client/strands_agentcore_client
uv run cli.py --agent-arn <agent-arn>
```

---

## Configuration

### Environment Variables

```bash
MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
AWS_REGION=us-west-2
SEARXNG_URL=http://10.0.1.248:8080  # Private SearxNG instance
```

### Dependencies

**Production** (`requirements.txt`):
- Runtime dependencies only
- Used by Docker/AgentCore

**Development** (`pyproject.toml`):
- All dependencies + test tools
- Used for local development

```bash
# Local dev with tests
uv sync --extra test

# Production
pip install -r requirements.txt
```

---

## Testing

```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_validator.py -v
```

---

## Project Structure

```
multi-agent/
├── multi_agents/
│   ├── aws_investigator/      # Investigation agent
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── system_prompt.md
│   │   └── tools/
│   │       ├── searxng_tool.py
│   │       └── fetch_content_tool.py
│   │
│   ├── validator/             # Verification agent
│   │   ├── agent.py
│   │   ├── config.py
│   │   └── system_prompt.md
│   │
│   ├── orchestrator/          # Coordinator (coming soon)
│   │   └── ...
│   │
│   └── remote_entrypoint.py   # AgentCore entrypoint
│
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── pyproject.toml            # Dev dependencies
├── requirements.txt          # Production dependencies
├── .bedrock_agentcore.yaml   # AgentCore config
└── README.md                 # This file
```

---

## Documentation

- [Orchestrator Implementation Plan](docs/orchestrator-implementation-plan.md)
- [Multi-Agent Architecture Proposal](docs/multi-agent-web-search-proposal.md)

---

## Next Steps

1. ✅ AWS Investigator - Implemented
2. ✅ Validator - Implemented
3. ⬜ Orchestrator - In progress
4. ⬜ Unit tests
5. ⬜ Integration tests
6. ⬜ Production deployment
