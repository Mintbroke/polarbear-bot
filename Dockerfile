FROM python:3.12-slim

# 1) Install OS-level build deps, voice libs, and PostgreSQL headers
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      git \
      curl \
      ffmpeg \
      libopus0 libopus-dev \
      libsodium-dev \
      libffi-dev \
      libssl-dev \
      python3-dev \
      libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copy & install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 3) Copy your code
COPY . .

# 4) Start your bot (and web.py if you wrap them, etc.)
CMD ["python", "main.py"]
