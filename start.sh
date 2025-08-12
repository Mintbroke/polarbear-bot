#!/usr/bin/env bash
set -euo pipefail

# ---- Start Ollama (local-only) ----
if command -v ollama >/dev/null; then
  export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
  echo "Starting Ollama on $OLLAMA_HOST ..."
  ollama serve &

  echo "Waiting for Ollama..."
  # poll the local API until ready
  for i in {1..60}; do
    curl -fsS "http://127.0.0.1:11434/api/tags" >/dev/null && break || sleep 1
  done

  MODEL="${OLLAMA_START_MODEL:-llama3.2:1b}"
  if ! ollama show "$MODEL" >/dev/null 2>&1; then
    echo "Pulling model: $MODEL"
    ollama pull "$MODEL"
  fi
else
  echo "Ollama not installed; skipping local LLM."
fi

# ---- Start your Python bot/app ----
echo "Starting bot..."
exec python main.py
