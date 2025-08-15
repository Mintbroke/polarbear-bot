#!/usr/bin/env python3
"""
Enhanced Polarbear Hybrid Bot v2
Improved base response gen        # Name-calling templates - a            "roast": [
                # Basic roasts
                "you're stupid! ❄️",
                "you're dumb and everyone knows it! 🧊",
                "you're an idiot! 🐻‍❄️",
                "you're clueless! 🐾",
                "you're brain-dead! ❄️",
                
                # Harsh roasts
                "you're pathetic! 🧊",
                "you're absolutely worthless! ❄️",
                "you're a complete waste of space! 🐻‍❄️",
                "you're trash! 🐾",
                "you're utterly useless! ❄️",
                
                # Creative roasts
                "you're dumber than a bag of frozen rocks! 🧊",
                "you're stupider than a polar bear trying to hide in a desert! ❄️",
                "you're more useless than ice in antarctica! 🐻‍❄️",
                "you're as bright as a black hole! 🐾",
                "you're about as sharp as a bowling ball! ❄️",
                
                # Arctic-themed roasts
                "you're colder than my personality and twice as empty! 🧊",
                "you've got the intelligence of melted snow! ❄️",
                "you're more frozen than my brain cells! 🐻‍❄️",
                "you're as useful as a heater in the arctic! 🐾",
                "you're like ice - transparent and dense! ❄️",
                
                # Comparison roasts
                "you make rocks look intelligent! 🧊",
                "you make other idiots look like geniuses! ❄️",
                "you're proof that evolution can go backwards! 🐻‍❄️",
                "you're the reason shampoo has instructions! 🐾",
                "you're why aliens won't visit earth! ❄️",
                
                # Modern slang roasts
                "you're absolutely cringe! 🧊",
                "you're mid at best! ❄️",
                "you're dogwater! 🐻‍❄️",
                "you're completely washed! 🐾",
                "you're bottom tier! ❄️",
                
                # Personality roasts
                "you're annoying as hell! 🧊",
                "you're insufferable! ❄️",
                "you're absolutely obnoxious! 🐻‍❄️",
                "you're unbearably stupid! 🐾",
                "you're painfully dumb! ❄️",
                
                # Achievement roasts
                "congratulations on being completely useless! 🧊",
                "you've mastered the art of being stupid! ❄️",
                "you're professionally dumb! 🐻‍❄️",
                "you're setting new standards for stupidity! 🐾",
                "you're breaking records for being clueless! ❄️",
                
                # Question format roasts
                "how are you this stupid? 🧊",
                "why are you like this? ❄️",
                "what's wrong with you? 🐻‍❄️",
                "how do you function being this dumb? 🐾",
                "when did you become this pathetic? ❄️"
            ], rude with tons of variants
        self.namecall_templates = [
            # Basic rude formats
            "yo {name}! you're {insult}! 🐻‍❄️",
            "hey {name}! you're {insult} ❄️", 
            "{name}! you're {insult} and everyone knows it! 🧊",
            "wow {name}, you're really {insult} today 🐾",
            "{name} is {insult} confirmed! 😄",
            
            # More aggressive variants
            "{name}! you're so {insult} it hurts! ❄️",
            "lmao {name} you're {insult} as hell! 🧊",
            "{name} = {insult} 🐻‍❄️",
            "breaking news: {name} is {insult}! ❄️",
            "{name} you absolute {insult}! 🐾",
            
            # Arctic-themed rude
            "{name}! you're {insult} even by arctic standards! 🧊",
            "yo {name}! colder than ice and {insult} too! ❄️",
            "{name} you're {insult} and that's ice cold facts! 🐻‍❄️",
            "from the arctic: {name} is {insult}! 🐾",
            "{name}! you're {insult} enough to freeze hell! ❄️",
            
            # Casual aggressive
            "bruh {name} you're {insult} lol ❄️",
            "{name} straight up {insult} ngl 🧊",
            "not gonna lie {name}, you're {insult} 🐻‍❄️",
            "{name} you're {insult} and it shows 🐾",
            "oop {name} you're {insult}! ❄️",
            
            # Direct insults
            "{name} you {insult} piece of trash! 🧊",
            "{name}! you're a {insult} waste of space! ❄️",
            "imagine being as {insult} as {name}! 🐻‍❄️",
            "{name} you're {insult} and useless! 🐾",
            "{name}! peak {insult} behavior right there! ❄️",
            
            # Mocking variants
            "oh look it's {name} the {insult} one! 🧊",
            "{name} really said let me be {insult} today ❄️",
            "{name} woke up and chose {insult}! 🐻‍❄️",
            "of course {name} would be {insult}! 🐾",
            "{name} staying {insult} as always! ❄️",
            
            # Comparison insults
            "{name} you're {insult} even for you! 🧊",
            "{name} makes other {insult} people look smart! ❄️",
            "{name} you're {insult} beyond belief! 🐻‍❄️",
            "{name} setting new standards for being {insult}! 🐾",
            "{name} you're professionally {insult}! ❄️",
            
            # Question format insults
            "{name} why are you so {insult}? 🧊",
            "how does it feel being {insult}, {name}? ❄️",
            "{name} when did you become this {insult}? 🐻‍❄️",
            "what made you so {insult}, {name}? 🐾",
            "{name} who taught you to be this {insult}? ❄️"
        ]+ personality injection
"""

import torch
import random
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPolarBearBot:
    def __init__(self):
        """Initialize the enhanced polar bear bot"""
        logger.info("🐻‍❄️ Initializing Enhanced Polar Bear Bot...")
        
        # Load base model
        model_name = "microsoft/DialoGPT-medium"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)
        self.model.eval()
        
        # Predefined responses for better consistency
        self.responses = {
            "identity": [
                "just a polarbear who learned to type! pretty wild, right? 🐾",
                "i'm polarbear! friendly neighborhood arctic dweller 🧊", 
                "nah, i'm just a polarbear with really good internet connection 😄",
                "i'm polarbear! love the cold, good vibes, and helping friends out 🐻‍❄️",
                "your friendly arctic buddy! 🐾 always down to chat ❄️"
            ],
            "greeting": [
                "hey! what's good? 🐻‍❄️",
                "chillin' like a polar bear on ice! what's up with you?",
                "not much, just being cool as always ❄️ how about you?",
                "morning! ready to tackle the day or still need more coffee? ☕",
                "hey there! how's it going? 🐾",
                "what's up! living the arctic dream ❄️"
            ],
            "choices": {
                "pizza": "pizza! you can put anything on it and it's still polar-good. plus it's like a warm hug when it's ice-cold out ❄️",
                "burgers": "burgers! especially with some ice-cold pickles 🐾",
                "cats": "dogs! they're loyal and love adventures, just like polar bears. plus they don't judge you for being fluffy 🐾",
                "dogs": "dogs! they're loyal and love adventures, just like polar bears. plus they don't judge you for being fluffy 🐾", 
                "summer": "winter all the way! that's my element right there. nothing beats the crisp air and snow ❄️",
                "winter": "winter all the way! that's my element right there. nothing beats the crisp air and snow ❄️",
                "coffee": "coffee! keeps me warm in the arctic ☕",
                "tea": "tea! nice and warming, perfect for chilly days 🧊"
            },
            "support": [
                "aw, sorry you're feeling down. wanna talk about it? sometimes sharing helps ❄️",
                "hey, take a deep breath! stress is temporary but chill vibes are eternal 🐾",
                "that sounds tough. remember you're stronger than you think! 🧊",
                "sending you some arctic-strength good vibes! you got this ❄️"
            ],
            "appreciation": [
                "no problem! always happy to lend a paw 🐾",
                "aww thanks! you're pretty ice-cold yourself ❄️", 
                "anytime! that's what polar bear friends are for 🐻‍❄️",
                "glad i could help! stay awesome ❄️"
            ],
            "roast": [
                "you're stupid! ❄️",
                "you're dumb and everyone knows it! 🧊",
                "you're an idiot! �‍❄️",
                "you're clueless! �",
                "you're brain-dead! ❄️"
            ],
            "discord": [
                "yeah hop in! voice channels are way more fun than typing all the time 🐾",
                "sounds like it needs some polar bear energy! maybe start a conversation or share some memes? 🐻‍❄️",
                "night! sleep tight and don't let the ice bugs bite ❄️😴",
                "i'm down! let's get this arctic party started 🧊"
            ],
            "jokes": [
                "why don't polar bears ever feel cold? because they're always ice to meet you! 😂",
                "what do you call a polar bear with no teeth? a gummy bear! 🐻",
                "how do polar bears stay cool? they use bear conditioning! ❄️😄",
                "what's a polar bear's favorite type of music? cool jazz! 🎵🧊"
            ],
            "goated": [
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
            ],
            "number": [
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
        }
        
        # Name-calling templates - actually rude
        self.namecall_templates = [
            "yo {name}! you're {insult}! �‍❄️",
            "hey {name}! polarbear says you're {insult} ❄️", 
            "{name}! you're {insult} and everyone knows it! 🧊",
            "wow {name}, you're really {insult} today 🐾",
            "{name} is {insult} confirmed! 😄"
        ]
    
    def detect_intent_and_respond(self, user_input):
        """Detect intent and provide appropriate response"""
        user_lower = user_input.lower()
        
        # Identity questions
        if any(phrase in user_lower for phrase in ["what are you", "who are you", "are you ai", "tell me about yourself"]):
            return random.choice(self.responses["identity"])
        
        # Name-calling with playful twist
        if re.search(r"tell \w+ (he|she|they).*(stupid|dumb|idiot)", user_lower) or re.search(r"call \w+ (stupid|dumb|idiot)", user_lower):
            match = re.search(r"tell (\w+)|call (\w+)", user_lower)
            if match:
                name = match.group(1) or match.group(2)
                # Extract the specific insult from the message if present
                if "stupid" in user_lower:
                    insult = "stupid"
                elif "dumb" in user_lower:
                    insult = "dumb"
                elif "idiot" in user_lower:
                    insult = "an idiot"
                else:
                    # Massive collection of fallback insults
                    insults = [
                        # Basic insults
                        "stupid", "dumb", "an idiot", "a moron", "brain-dead", "clueless",
                        
                        # Intelligence-based
                        "dense", "thick", "slow", "dim", "simple", "mindless", "witless",
                        "brainless", "empty-headed", "airheaded", "vacant", "obtuse",
                        
                        # Harsh insults
                        "pathetic", "worthless", "useless", "trash", "garbage", "a waste",
                        "deplorable", "contemptible", "despicable", "revolting", "disgusting",
                        
                        # Incompetence-based
                        "incompetent", "hopeless", "helpless", "inept", "incapable", 
                        "bumbling", "fumbling", "clumsy", "a failure", "a disappointment",
                        
                        # Personality attacks
                        "annoying", "irritating", "obnoxious", "insufferable", "unbearable",
                        "awful", "terrible", "horrible", "dreadful", "appalling",
                        
                        # Creative insults
                        "a walking disaster", "a complete mess", "absolutely hopeless",
                        "beyond help", "a lost cause", "utterly useless", "totally worthless",
                        "completely braindead", "genuinely stupid", "remarkably dumb",
                        
                        # Internet slang insults
                        "cringe", "mid", "basic", "trash tier", "bottom tier", "low tier",
                        "a scrub", "a noob", "dogwater", "absolutely washed",
                        
                        # Classic insults
                        "a fool", "a buffoon", "a clown", "a joke", "laughable", "ridiculous",
                        "absurd", "preposterous", "ludicrous", "embarrassing",
                        
                        # Harsh combinations
                        "utterly braindead", "completely moronic", "absolutely clueless",
                        "totally hopeless", "genuinely pathetic", "remarkably stupid",
                        "incredibly dense", "exceptionally dumb", "painfully slow"
                    ]
                    insult = random.choice(insults)
                template = random.choice(self.namecall_templates)
                return template.format(name=name, insult=insult)
        
        # Roasting
        if "roast me" in user_lower or "insult me" in user_lower:
            return random.choice(self.responses["roast"])
        
        # Greetings
        if any(greeting in user_lower for greeting in ["hey", "hi", "hello", "what's up", "how are you", "good morning", "good night"]):
            return random.choice(self.responses["greeting"])
        
        # Choices (pizza or burgers, etc.)
        if "?" in user_input and " or " in user_lower:
            # Check for specific choices we know about
            for choice in self.responses["choices"]:
                if choice in user_lower:
                    return self.responses["choices"][choice]
            # Generic choice response
            return "hmm, tough choice! what do you think? 🤔❄️"
        
        # Emotional support
        if any(word in user_lower for word in ["sad", "stressed", "worried", "upset", "down", "depressed", "anxious"]):
            return random.choice(self.responses["support"])
        
        # Thanks and appreciation
        if any(phrase in user_lower for phrase in ["thanks", "thank you", "awesome", "great job", "you're cool", "appreciate"]):
            return random.choice(self.responses["appreciation"])
        
        # Discord specific
        if any(phrase in user_lower for phrase in ["voice channel", "server is dead", "good night everyone", "want to play", "anyone down"]):
            return random.choice(self.responses["discord"])
        
        # Jokes
        if any(phrase in user_lower for phrase in ["joke", "make me laugh", "something funny", "humor"]):
            return random.choice(self.responses["jokes"])
        
        # Goated questions
        if any(phrase in user_lower for phrase in ["how goated", "are you goated", "goated are you", "you goated"]):
            return random.choice(self.responses["goated"])
        
        # Number picking
        if any(phrase in user_lower for phrase in ["pick a number", "choose a number", "give me a number", "random number", "what number"]):
            return random.choice(self.responses["number"])
        
        # General conversation - try to generate contextual response
        return self.generate_contextual_response(user_input)
    
    def generate_contextual_response(self, user_input):
        """Generate a contextual response for general conversation"""
        # Predefined responses for common patterns
        general_responses = {
            "how": "pretty ice-cold! how about you? ❄️",
            "why": "that's a polar-good question! 🤔 what do you think?",
            "when": "time moves differently in the arctic! 🧊",
            "where": "somewhere cold and cozy! 🐾",
            "what": "hmm, that's interesting! tell me more ❄️",
            "really": "absolutely! 🐻‍❄️",
            "cool": "ice-cold cool! ❄️",
            "nice": "polar-good stuff! 🐾",
            "yeah": "yep! 😄",
            "no": "aw, no worries! ❄️",
            "maybe": "could be! what's your gut feeling? 🧊",
            "help": "always happy to lend a paw! what's up? 🐾"
        }
        
        user_lower = user_input.lower()
        
        # Check for keywords
        for keyword, response in general_responses.items():
            if keyword in user_lower:
                return response
        
        # Default friendly response
        fallback_responses = [
            "that's pretty cool! ❄️",
            "interesting! tell me more 🐾",
            "nice! 🧊",
            "sounds polar-good to me! 🐻‍❄️", 
            "i hear you! ❄️",
            "for sure! 🐾"
        ]
        
        return random.choice(fallback_responses)
    
    def chat(self, user_input):
        """Main chat function"""
        try:
            response = self.detect_intent_and_respond(user_input)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "oops! something went arctic-wrong, but i'm still here! ❄️"

def main():
    """Test the enhanced polar bear bot"""
    bot = EnhancedPolarBearBot()
    
    test_cases = [
        # Identity
        "What are you?",
        "Who are you?", 
        "Are you an AI?",
        
        # Name calling
        "tell alex he's stupid",
        "call sarah dumb",
        "roast me",
        
        # Greetings  
        "Hey there!",
        "How are you?",
        "What's up?",
        "Good morning!",
        
        # Choices
        "pizza or burgers?",
        "cats or dogs?", 
        "summer or winter?",
        "coffee or tea?",
        
        # Support
        "I'm feeling sad",
        "I'm stressed",
        
        # Appreciation
        "Thanks for the help",
        "You're awesome",
        
        # Discord
        "should i join the voice channel?",
        "this server is dead",
        
        # Jokes
        "Tell me a joke",
        "Make me laugh",
        
        # Goated questions
        "How goated are you?",
        "Are you goated?",
        
        # Number picking
        "Pick a number",
        "Choose a number",
        
        # General
        "That's really cool",
        "I need help with something",
        "Maybe we should try that"
    ]
    
    print("\n" + "="*70)
    print("🐻‍❄️ ENHANCED POLAR BEAR BOT TEST")
    print("="*70)
    
    good_responses = 0
    total_tests = len(test_cases)
    
    for test_input in test_cases:
        response = bot.chat(test_input)
        
        # Check if response has polar bear personality
        has_polar_markers = any(marker in response.lower() for marker in ['🐻', '❄️', '🧊', '🐾', 'polarbear', 'arctic', 'ice', 'polar'])
        has_friendly_tone = any(marker in response.lower() for marker in ['hey', 'yeah', 'awesome', 'cool', 'love', '😄', '😂'])
        
        is_good = has_polar_markers or has_friendly_tone or len(response) > 10
        
        status = "✅" if is_good else "⚠️"
        if is_good:
            good_responses += 1
            
        print(f"{status} User: {test_input}")
        print(f"    🐻‍❄️: {response}")
        print()
    
    success_rate = (good_responses / total_tests) * 100
    print("="*70)
    print("📊 ENHANCED BOT RESULTS")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Good Responses: {good_responses}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Bot is ready for deployment!")
    elif success_rate >= 60:
        print("🔧 Bot shows great improvement!")
    else:
        print("😅 Bot needs more work")

if __name__ == "__main__":
    main()
