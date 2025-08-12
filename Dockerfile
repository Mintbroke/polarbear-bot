# Base: your Python bot image
FROM python:3.12-slim

WORKDIR /app

# System deps (Discord voice, Postgres headers, build tools, curl/ca for Ollama)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg libopus0 libopus-dev libsodium-dev libpq-dev \
      build-essential python3-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ---- Install Ollama ----
RUN curl -fsSL https://ollama.com/install.sh | sh

# ---- Python deps ----
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- App code ----
COPY . .

# ---- Startup script ----
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Ollama + app defaults (override in Railway Variables as needed)
ENV OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_MODELS=/data/ollama \
    OLLAMA_NUM_THREADS=2 \
    OLLAMA_NUM_PARALLEL=1 \
    OLLAMA_CONTEXT_LENGTH=512 \
    OLLAMA_KEEP_ALIVE=15m \
    OLLAMA_NO_MMAP=0 \
    OLLAMA_START_MODEL=tinyllama:1.1b-chat-v1.0-q4_K_M \
    OPENAI_BASE_URL=http://127.0.0.1:11434/v1 \
    OPENAI_API_KEY=ollama

CMD ["/app/start.sh"]
