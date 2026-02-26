FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY multi_agents/ ./multi_agents/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "-m", "multi_agents.remote_entrypoint"]
