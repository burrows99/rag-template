FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 8000

CMD pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -e . && \
    python -m langgraph_cli dev --host 0.0.0.0 --port 8000 --allow-blocking --no-browser
