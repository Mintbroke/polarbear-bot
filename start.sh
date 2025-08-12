#!/usr/bin/env bash
set -euo pipefail

if command -v ollama >/dev/null; then
  echo "Starting Ollama on ${OLLAMA_HOST:-127.0.0.1:11434} ..."
  ollama serve &

  for i in {1..60}; do
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null && break || sleep 1
  done
  MODEL="${OLLAMA_START_MODEL:-llama3.2:1b}"
  ollama show "$MODEL" >/dev/null 2>&1 || ollama pull "$MODEL"
fi

echo "Starting bot..."
exec python main.py
