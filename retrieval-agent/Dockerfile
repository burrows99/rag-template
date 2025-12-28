# LangGraph Server Dockerfile
# Source: LangGraph self-hosted deployment
# Docs: https://docs.langchain.com/langsmith/self-hosted
# Python base image for LangGraph runtime

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all application files first
COPY . .

# Install Python dependencies
# langgraph-cli[inmem] is required for running the dev server with in-memory API
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir "langgraph-cli[inmem]"

# Expose LangGraph server port
EXPOSE 2024

# Run LangGraph dev server
# Note: For production, consider using langgraph up or a production ASGI server
CMD ["langgraph", "dev", "--allow-blocking", "--port", "2024", "--host", "0.0.0.0"]
