#!/usr/bin/env bash
set -euo pipefail

# Start Ollama bound to localhost (not exposed publicly)
echo "Starting Ollama on ${OLLAMA_HOST:-127.0.0.1:11434} ..."
ollama serve &

# Wait for Ollama API to be ready
until curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null; do
  sleep 1
done
echo "Ollama is up."

# Ensure the default model exists; pull if missing
MODEL="${OLLAMA_START_MODEL:-llama3.2:1b}"
if ! ollama show "$MODEL" >/dev/null 2>&1; then
  echo "Pulling model: $MODEL"
  ollama pull "$MODEL"
fi

# Finally, run your bot
echo "Starting Python bot..."
exec python3 main.py
