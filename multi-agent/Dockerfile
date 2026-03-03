FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Copy workspace dependencies first
COPY strands_shared/ ./strands_shared/

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY multi_agents/ ./multi_agents/
COPY *_entrypoint.py ./

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV AGENT_ENTRYPOINT=remote_entrypoint

CMD ["/app/start.sh"]
