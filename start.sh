#!/bin/bash
# Simple start script for Polar Bear Bot

echo "🐻‍❄️ Starting Polar Bear Discord Bot..."

# Check if Discord token is set
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "❌ Error: DISCORD_BOT_TOKEN environment variable not set!"
    echo "Please set it with: export DISCORD_BOT_TOKEN='your_token_here'"
    exit 1
fi

# Check if dependencies are installed
if ! python -c "import discord" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the bot
echo "🚀 Launching bot..."
python main.py
