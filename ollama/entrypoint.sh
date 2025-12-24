#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

# Only pull models if LLM_PROVIDER is set to ollama
if [ "${LLM_PROVIDER}" = "ollama" ]; then
    # Pull LLM model if specified
    if [ -n "${LLM_MODEL}" ]; then
        # Extract model name (remove provider prefix if present)
        MODEL_NAME="${LLM_MODEL#*/}"
        echo "🔴 Pulling LLM model: ${MODEL_NAME}..."
        ollama pull "${MODEL_NAME}"
        echo "🟢 LLM model ready!"
    fi

    # Pull embedding model if specified
    if [ -n "${EMBEDDING_MODEL}" ]; then
        # Extract model name (remove provider prefix if present)
        EMBED_MODEL_NAME="${EMBEDDING_MODEL#*/}"
        echo "🔴 Pulling embedding model: ${EMBED_MODEL_NAME}..."
        ollama pull "${EMBED_MODEL_NAME}"
        echo "🟢 Embedding model ready!"
    fi
else
    echo "ℹ️  LLM_PROVIDER is not set to 'ollama', skipping model pulls..."
fi

# Wait for Ollama process to finish.
wait $pid