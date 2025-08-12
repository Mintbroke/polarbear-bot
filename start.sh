#!/usr/bin/env bash
set -euo pipefail

if command -v ollama >/dev/null; then
  echo "Starting Ollama on ${OLLAMA_HOST:-127.0.0.1:11434} ..."
  ollama serve &

  for i in {1..60}; do
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null && break || sleep 1
  done
  MODEL="${OLLAMA_START_MODEL:-smollm:135m}"
  ollama show "$MODEL" >/dev/null 2>&1 || ollama pull "$MODEL"

  # after pulling MODEL in start.sh
curl -sS --max-time 120 "http://127.0.0.1:11434/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer ollama" \
  -d '{"model":"'"${MODEL}"'","messages":[{"role":"user","content":"ok"}],"max_tokens":1,"stream":false}' \
  >/dev/null || echo "warmup: timed out (non-fatal)"


fi

echo "Starting bot..."
exec python main.py
