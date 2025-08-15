@echo off
REM Windows batch script for Polar Bear Bot

echo 🐻‍❄️ Starting Polar Bear Discord Bot...

REM Check if Discord token is set
if "%DISCORD_BOT_TOKEN%"=="" (
    echo ❌ Error: DISCORD_BOT_TOKEN environment variable not set!
    echo Please set it with: set DISCORD_BOT_TOKEN=your_token_here
    exit /b 1
)

REM Check if dependencies are installed
python -c "import discord" 2>nul
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Start the bot
echo 🚀 Launching bot...
python main.py
