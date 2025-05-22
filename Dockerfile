FROM python:3.12-slim

# 1) Install ffmpeg + Opus runtime + dev (so the .so symlink exists)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libopus0 libopus-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Install your Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 3) Copy your code
WORKDIR /app
COPY . /app

# 4) Launch your bot
CMD ["python", "main.py"]
