#!/bin/bash
set -e

# Use opentelemetry-instrument if OTEL is enabled
if [ "${AGENT_OBSERVABILITY_ENABLED}" = "true" ]; then
    exec opentelemetry-instrument python -m uvicorn ${AGENT_ENTRYPOINT}:app --host 0.0.0.0 --port 8080
else
    exec python -m uvicorn ${AGENT_ENTRYPOINT}:app --host 0.0.0.0 --port 8080
fi
