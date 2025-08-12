# Base: your Python bot image
FROM python:3.12-slim

WORKDIR /app

# System deps for Discord voice, Postgres headers, build tools, and curl for Ollama install
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libopus0 \
      libopus-dev \
      libsodium-dev \
      libpq-dev \
      build-essential \
      python3-dev \
      curl \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ---- Install Ollama (binary) ----
# This installs the 'ollama' CLI/server into the image
RUN curl -fsSL https://ollama.com/install.sh | sh

# ---- Python deps ----
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- App code ----
COPY . .

# ---- Startup script (runs Ollama + your bot) ----
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Keep Ollama private inside the container
ENV OLLAMA_HOST=127.0.0.1:11434
# Change the default model if you like (small CPU-friendly ones recommended)
ENV OLLAMA_START_MODEL=tinyllama:1.1b

# If you want models to persist across restarts, mount a volume at /root/.ollama
# VOLUME ["/root/.ollama"]

# Entrypoint: boot Ollama, wait, pull model if needed, then run your bot
CMD ["/app/start.sh"]
