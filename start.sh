#!/usr/bin/env bash
set -euo pipefail

if command -v ollama >/dev/null; then
  echo "Starting Ollama on ${OLLAMA_HOST:-127.0.0.1:11434} ..."
  ollama serve &

  for i in {1..60}; do
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null && break || sleep 1
  done
  MODEL="${OLLAMA_START_MODEL:-qwen2.5:0.5b-instruct}"
  ollama show "$MODEL" >/dev/null 2>&1 || ollama pull "$MODEL"


  # after pulling MODEL in start.sh
   # curl -sS --max-time 600 http://127.0.0.1:11434/api/generate \
   # -H "Content-Type: application/json" \
   # -d '{"model":"'"${MODEL}"'","prompt":"ok","stream":false,
   #     "options":{"use_mmap":true,"num_thread":1,"num_ctx":512,"num_predict":1},
   #     "keep_alive":"30m"}' \
   # >/dev/null || echo "warmup: timed out (non-fatal)"


fi

echo "Starting bot..."
exec python main.py
