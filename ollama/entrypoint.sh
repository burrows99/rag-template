#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"

echo "🔗 Connecting to Ollama at: ${OLLAMA_HOST}"

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
  if curl -s "${OLLAMA_HOST}/api/version" > /dev/null 2>&1; then
    echo "✅ Ollama is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ Ollama failed to respond within 60 seconds"
    echo "   Make sure Ollama Desktop app is running"
    exit 1
  fi
  echo "   Ollama not ready yet, retrying in 2 seconds... ($i/30)"
  sleep 2
done

# Only pull models if LLM_PROVIDER is set to ollama
if [ "${LLM_PROVIDER}" = "ollama" ]; then
    # Pull LLM model if specified
    if [ -n "${LLM_MODEL}" ]; then
        # Extract model name (remove provider prefix if present)
        MODEL_NAME="${LLM_MODEL#*/}"
        echo "🔴 Pulling LLM model: ${MODEL_NAME}..."
        
        # Use Ollama API to pull model
        curl -X POST "${OLLAMA_HOST}/api/pull" \
          -H "Content-Type: application/json" \
          -d "{\"name\": \"${MODEL_NAME}\"}" \
          --no-buffer 2>/dev/null | while IFS= read -r line; do
            echo "$line" | grep -q '"status":"success"' && echo "🟢 LLM model ready!" && break
          done
    fi

    # Pull embedding model if specified
    if [ -n "${EMBEDDING_MODEL}" ]; then
        # Extract model name (remove provider prefix if present)
        EMBED_MODEL_NAME="${EMBEDDING_MODEL#*/}"
        echo "🔴 Pulling embedding model: ${EMBED_MODEL_NAME}..."
        
        # Use Ollama API to pull model
        curl -X POST "${OLLAMA_HOST}/api/pull" \
          -H "Content-Type: application/json" \
          -d "{\"name\": \"${EMBED_MODEL_NAME}\"}" \
          --no-buffer 2>/dev/null | while IFS= read -r line; do
            echo "$line" | grep -q '"status":"success"' && echo "🟢 Embedding model ready!" && break
          done
    fi
else
    echo "ℹ️  LLM_PROVIDER is not set to 'ollama', skipping model pulls..."
fi

echo "✅ Model initialization complete!"