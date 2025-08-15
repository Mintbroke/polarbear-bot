# 🚀 Polar Bear Bot - Deployment Guide

## 🛠️ Prerequisites

1. **Discord Bot Token**: Get from [Discord Developer Portal](https://discord.com/developers/applications)
2. **Bot Permissions**: Make sure your bot has:
   - Read Messages
   - Send Messages
   - Use Slash Commands
   - Message Content Intent (enabled in Developer Portal)

## 🌐 Deployment Options

### Option 1: Railway (Recommended)

1. **Connect Repository**:
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Deploy polar bear bot"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub"
   - Select your `polarbear-bot` repository
   - Railway will automatically detect the `railway.toml` config

3. **Set Environment Variables**:
   - Go to your Railway project settings
   - Add variable: `DISCORD_BOT_TOKEN` = `your_discord_token_here`

4. **Deploy**:
   - Railway will automatically build and deploy using the Dockerfile
   - Check logs to ensure bot starts successfully

### Option 2: Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variable**:
   ```bash
   # Windows
   set DISCORD_BOT_TOKEN=your_token_here
   
   # Linux/Mac
   export DISCORD_BOT_TOKEN=your_token_here
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```

### Option 3: Docker

1. **Build Image**:
   ```bash
   docker build -t polarbear-bot .
   ```

2. **Run Container**:
   ```bash
   docker run -e DISCORD_BOT_TOKEN=your_token_here polarbear-bot
   ```

### Option 4: Fly.io

1. **Install Fly CLI**:
   ```bash
   # Follow instructions at https://fly.io/docs/hands-on/install-flyctl/
   ```

2. **Deploy**:
   ```bash
   fly deploy
   ```

3. **Set Environment Variables**:
   ```bash
   fly secrets set DISCORD_BOT_TOKEN=your_token_here
   ```

### Option 5: Heroku

1. **Create Heroku App**:
   ```bash
   heroku create your-polarbear-bot
   ```

2. **Set Environment Variables**:
   ```bash
   heroku config:set DISCORD_BOT_TOKEN=your_token_here
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🔧 Environment Variables

Required:
- `DISCORD_BOT_TOKEN` - Your Discord bot token

Optional:
- `PORT` - Port for web interface (default: 8000)

## 📋 Post-Deployment Checklist

1. ✅ Bot appears online in Discord
2. ✅ Responds to mentions: `@PolarBear hello`
3. ✅ Commands work: `!pb help`
4. ✅ Name-calling works: `tell alex he's stupid`
5. ✅ Goated responses: `how goated are you`
6. ✅ Number picking: `pick a number`

## 🐛 Troubleshooting

### Bot Not Starting
- Check Discord token is correct
- Verify Message Content Intent is enabled
- Check deployment logs for errors

### Bot Not Responding
- Ensure bot has proper permissions in your Discord server
- Check if bot is mentioned correctly
- Verify bot is online (green status)

### Commands Not Working
- Make sure bot has "Use Slash Commands" permission
- Try mentioning the bot instead: `@PolarBear hello`

## 📊 Bot Features

Once deployed, your bot supports:

- **Identity**: "What are you?" → Arctic polar bear personality
- **Name-calling**: "tell alex he's stupid" → Genuinely rude responses
- **Goated**: "how goated are you?" → 10+ goated responses
- **Numbers**: "pick a number" → 15+ creative number responses
- **General chat**: Greetings, choices, support, jokes
- **Commands**: `!pb help`, `!pb roast`, `!pb joke`, etc.

## 🎉 Success!

Your Polar Bear bot should now be deployed and ready to spread Arctic vibes! 🐻‍❄️❄️

For support, check the logs and ensure all environment variables are set correctly.
