# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Discord voice, PostgreSQL client headers, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libopus0 \
      libopus-dev \
      libsodium-dev \
      libpq-dev \
      build-essential \
      python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run the bot
CMD ["python3", "main.py"]
