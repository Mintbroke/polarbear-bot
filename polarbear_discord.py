#!/usr/bin/env python3
"""
Polarbear Discord Bot - Production Ready
Hybrid approach with consistent polar bear personality
"""

import discord
import random
import re
import logging
from discord.ext import commands

# Import our enhanced polar bear personality
from polarbear_enhanced import EnhancedPolarBearBot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolarBearDiscordBot(commands.Bot):
    def __init__(self):
        # Discord bot setup with necessary intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!pb ',
            intents=intents,
            help_command=None
        )
        
        # Initialize our polar bear personality bot
        self.polar_bot = EnhancedPolarBearBot()
        logger.info("🐻‍❄️ Polar Bear Discord Bot initialized!")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'🎉 {self.user} has connected to Discord!')
        logger.info(f'🧊 Polar Bear is ready to chat!')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.playing, 
            name="in the arctic! 🐻‍❄️"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message):
        """Handle all messages"""
        # Don't respond to self
        if message.author == self.user:
            return
        
        # Don't respond to other bots
        if message.author.bot:
            return
        
        # Check if bot is mentioned or message starts with bot name
        mentioned = self.user in message.mentions
        starts_with_name = message.content.lower().startswith(('polarbear', 'polar bear', 'pb'))
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        # Respond if mentioned, name used, or in DM
        if mentioned or starts_with_name or is_dm:
            await self.respond_to_message(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def respond_to_message(self, message):
        """Generate and send polar bear response"""
        try:
            # Clean the message content
            content = message.content
            
            # Remove bot mention
            if self.user in message.mentions:
                content = content.replace(f'<@{self.user.id}>', '').strip()
                content = content.replace(f'<@!{self.user.id}>', '').strip()
            
            # Remove name prefixes
            content = re.sub(r'^(polarbear|polar bear|pb)\s*', '', content, flags=re.IGNORECASE).strip()
            
            # Handle empty content
            if not content:
                content = "hello!"
            
            # Generate response using our polar bear bot
            response = self.polar_bot.chat(content)
            
            # Send response
            await message.channel.send(response)
            
        except Exception as e:
            logger.error(f"Error responding to message: {e}")
            await message.channel.send("oops! something went arctic-wrong, but i'm still here! ❄️")
    
    @commands.command(name='hello')
    async def hello_command(self, ctx):
        """Say hello"""
        greetings = [
            "hey there! what's good? 🐻‍❄️",
            "hello! chillin' like a polar bear on ice! ❄️", 
            "hi! ready for some arctic vibes? 🧊",
            "hey! what's up? 🐾"
        ]
        await ctx.send(random.choice(greetings))
    
    @commands.command(name='roast')
    async def roast_command(self, ctx, *, target=None):
        """Roast someone (actually rude)"""
        if target:
            # Clean target name
            target = target.strip('@').strip()
            roasts = [
                # Basic roasts
                f"yo {target}! you're stupid! 🐻‍❄️",
                f"hey {target}! you're dumb ❄️",
                f"{target}! you're an idiot and everyone knows it! 🧊",
                f"wow {target}, you're really clueless today 🐾",
                
                # Harsh roasts
                f"{target} you're pathetic! ❄️",
                f"{target}! you're absolutely worthless! 🧊",
                f"{target} you're a complete waste of space! 🐻‍❄️",
                f"{target}! you're trash! 🐾",
                
                # Creative roasts
                f"{target} you're dumber than a bag of frozen rocks! 🧊",
                f"{target}! you're stupider than a polar bear in a desert! ❄️",
                f"{target} you're more useless than ice in antarctica! 🐻‍❄️",
                f"{target}! you're as bright as a black hole! 🐾",
                
                # Modern roasts
                f"{target} you're absolutely cringe! ❄️",
                f"{target}! you're mid at best! 🧊",
                f"{target} you're dogwater! 🐻‍❄️",
                f"{target}! you're completely washed! 🐾",
                
                # Question roasts
                f"{target} how are you this stupid? ❄️",
                f"{target}! why are you like this? 🧊",
                f"{target} what's wrong with you? �‍❄️",
                f"{target}! when did you become this pathetic? �🐾"
            ]
            await ctx.send(random.choice(roasts))
        else:
            self_roasts = [
                "you're stupid! ❄️",
                "you're an idiot! 🧊", 
                "you're pathetic! 🐻‍❄️",
                "you're absolutely worthless! 🐾",
                "you're cringe! ❄️",
                "you're dogwater! 🧊",
                "how are you this dumb? 🐻‍❄️"
            ]
            await ctx.send(random.choice(self_roasts))
    
    @commands.command(name='joke')
    async def joke_command(self, ctx):
        """Tell a polar bear joke"""
        jokes = [
            "why don't polar bears ever feel cold? because they're always ice to meet you! 😂",
            "what do you call a polar bear with no teeth? a gummy bear! 🐻",
            "how do polar bears stay cool? they use bear conditioning! ❄️😄",
            "what's a polar bear's favorite type of music? cool jazz! 🎵🧊"
        ]
        await ctx.send(random.choice(jokes))
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        help_text = """
🐻‍❄️ **Polar Bear Bot Help** 
        
**How to chat with me:**
• Mention me: `@PolarBear hello!`
• Use my name: `polarbear what's up?`
• DM me directly!

**Commands:**
• `!pb hello` - Say hello
• `!pb roast [name]` - Playful roast
• `!pb joke` - Polar bear joke
• `!pb goated` - Show how goated I am
• `!pb number` - Pick a random number
• `!pb status` - Bot status
• `!pb help` - This help

**I love to:**
• Chat about anything! ❄️
• Give friendly "insults" (with love!)
• Share arctic wisdom 🧊
• Spread good vibes 🐾
• Be absolutely goated 🐻‍❄️

Just talk to me naturally - i'm here to chill and chat! 🐻‍❄️
        """
        await ctx.send(help_text)
    
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Show bot status"""
        status_text = f"""
🐻‍❄️ **Polar Bear Status**

• **Servers:** {len(self.guilds)}
• **Users:** {len(set(self.get_all_members()))}
• **Arctic Level:** Maximum Chill ❄️
• **Mood:** Polar-good! 🧊
• **Temperature:** Ice cold! 🐾

Ready to chat and spread good vibes! 🐻‍❄️
        """
        await ctx.send(status_text)
    
    @commands.command(name='goated')
    async def goated_command(self, ctx):
        """Show how goated the polar bear is"""
        goated_responses = [
            "i'm maximum goated! arctic-level goat status 🐻‍❄️",
            "absolutely goated! like a polar bear but even cooler ❄️",
            "i'm so goated it's not even fair! 🧊",
            "peak goated energy! even other goats are jealous 🐾",
            "beyond goated! i'm whatever comes after goated ❄️",
            "certified goat! got the arctic seal of approval 🐻‍❄️",
            "stupidly goated! like embarrassingly goated 🧊",
            "i'm the goat of being goated! meta-goated 🐾",
            "goated to the max! breaking the goat scale ❄️",
            "so goated that being goated got redefined around me 🐻‍❄️"
        ]
        await ctx.send(random.choice(goated_responses))
    
    @commands.command(name='number')
    async def number_command(self, ctx):
        """Pick a random number"""
        number_responses = [
            "42! the answer to everything, even in the arctic ❄️",
            "69! nice 😄",
            "420! blaze it... with ice! 🧊",
            "7! lucky arctic number 🐾",
            "21! blackjack baby! 🐻‍❄️",
            "8! infinity sideways, like me chillin' ❄️",
            "13! unlucky for everyone except polar bears 🧊",
            "100! going full arctic power 🐾",
            "3.14! pi but make it polar ❄️",
            "0! absolute zero, just like the arctic 🐻‍❄️",
            "1337! elite polar bear status 🧊",
            "666! devil may care but polar bears chill ❄️",
            "24! hours in a day, all spent being cool 🐾",
            "365! days of arctic vibes 🐻‍❄️",
            "2025! current year, still goated ❄️"
        ]
        await ctx.send(random.choice(number_responses))

def main():
    """Main function to run the bot"""
    import os
    
    # Get token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set your Discord bot token:")
        print("export DISCORD_BOT_TOKEN='your_token_here'")
        return
    
    # Create and run bot
    bot = PolarBearDiscordBot()
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Error: Invalid Discord bot token!")
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    main()
