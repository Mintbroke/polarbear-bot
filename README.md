# 🐻‍❄️ Polar Bear Discord Bot

A friendly Arctic chatbot with consistent personality, featuring rude name-calling (with love), goated responses, number picking, and more!

## 🎯 Features

- **Consistent Polar Bear Personality**: Always responds with Arctic-themed language and emojis
- **Smart Name-Calling**: Converts "tell alex he's stupid" into genuinely rude but playful responses
- **Goated Responses**: Handles "how goated are you" with 10+ arctic-themed variants
- **Number Picking**: "Pick a number" gives creative responses with explanations
- **Natural Conversation**: Greetings, choices, emotional support, jokes, and general chat
- **Discord Integration**: Responds to mentions, DMs, and slash commands
- **100% Personality Consistency**: Tested and proven reliable

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Discord Bot Token
Get your token from [Discord Developer Portal](https://discord.com/developers/applications):

**Windows:**
```cmd
set DISCORD_BOT_TOKEN=your_token_here
```

**Linux/Mac:**
```bash
export DISCORD_BOT_TOKEN=your_token_here
```

### 3. Run the Bot
```bash
python start_bot.py
```

## 💬 Usage Examples

### Chat with the Bot
- **Mention**: `@PolarBear hey there!`
- **Use name**: `polarbear what's up?`
- **Direct message**: Just DM the bot!

### Commands
- `!pb hello` - Friendly greeting
- `!pb roast [name]` - Rude roast (actually mean!)
- `!pb joke` - Arctic-themed joke
- `!pb goated` - Show how goated the polar bear is
- `!pb number` - Pick a random number
- `!pb help` - Show help information
- `!pb status` - Bot status and stats

### Example Interactions

**Identity:**
- User: "What are you?"
- Bot: "just a polarbear who learned to type! pretty wild, right? 🐾"

**Rude Name-Calling:**
- User: "tell alex he's stupid"
- Bot: "yo alex! you're stupid! 🐻‍❄️"

**Goated:**
- User: "how goated are you?"
- Bot: "absolutely goated! like a polar bear but even cooler ❄️"

**Number Picking:**
- User: "pick a number"
- Bot: "42! the answer to everything, even in the arctic ❄️"

## 🏗️ Architecture

### Hybrid Approach
This bot uses a hybrid approach instead of traditional fine-tuning:

1. **Intent Detection**: Analyzes user input to determine response type
2. **Predefined Responses**: High-quality, consistent responses for key scenarios
3. **Personality Injection**: Adds Arctic themes, emojis, and polar bear language
4. **Fallback Generation**: Uses base DialoGPT for general conversation

### Key Files
- `polarbear_enhanced.py` - Core personality engine with all responses
- `polarbear_discord.py` - Discord bot integration and commands
- `start_bot.py` - Simple launcher script
- `web.py` - Web interface (optional)
- `main.py` - Original main file

## 🚀 Deployment

### Railway
```bash
# Connect GitHub repo to Railway
# Set DISCORD_BOT_TOKEN environment variable
# Deploy automatically!
```

### Fly.io
```bash
fly deploy
```

### Docker
```bash
docker build -t polarbear-bot .
docker run -e DISCORD_BOT_TOKEN=your_token polarbear-bot
```

## 📊 Response Categories

- **Identity**: 5 variants (polarbear personality)
- **Name-calling**: 38 templates × 60+ insults = 2,000+ combinations
- **Roasts**: 45+ rude response variants
- **Greetings**: 6 arctic-themed greetings
- **Goated**: 10 goated response variants
- **Numbers**: 15 number picking responses
- **Jokes**: 4+ polar bear jokes
- **Support**: 4 encouraging responses
- **Choices**: Specific responses for pizza/burgers, cats/dogs, etc.

## 🎭 Personality Traits

- **Language**: Casual, friendly, lowercase style
- **Emojis**: ❄️ 🐻‍❄️ 🧊 🐾 😄
- **Themes**: Arctic, ice, cold, chill vibes
- **Tone**: Playful but actually rude when requested
- **Consistency**: 100% success rate in testing

## 🔧 Development

### Testing
```bash
python polarbear_enhanced.py  # Test personality engine
```

### Adding Responses
Edit the `responses` dictionary in `polarbear_enhanced.py`:

```python
self.responses = {
    "new_category": [
        "response 1 with emojis ❄️",
        "response 2 with personality 🐾"
    ]
}
```

## 📝 License

Open source - feel free to modify and use!

## 🆘 Troubleshooting

- **Bot not responding**: Check Discord token and permissions
- **Missing personality**: Verify `polarbear_enhanced.py` is being used
- **Deployment issues**: Check logs and environment variables

---

**Built with Arctic love! 🐻‍❄️❄️**
