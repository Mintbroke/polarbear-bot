FROM python:3.12-slim

# 1) Install ffmpeg, Opus libs, and build tools for PyNaCl (and any other C extensions)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libopus0 libopus-dev \
      libsodium-dev \
      build-essential \
      libffi-dev \
      python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Copy & install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 3) Copy your bot code
COPY . /app

# 4) Run your bot
CMD ["python", "main.py"]
