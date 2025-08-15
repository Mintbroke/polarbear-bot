# Polar Bear Discord Bot - Clean Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg libopus0 libsodium-dev \
      build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for web interface (optional)
EXPOSE 8000

# Run the Discord bot
CMD ["python", "main.py"]
    OLLAMA_START_MODEL=qwen2.5:0.5b-instruct-q4_K_M \
    OPENAI_BASE_URL=http://127.0.0.1:11434/v1 \
    OPENAI_API_KEY=ollama

CMD ["/app/start.sh"]
