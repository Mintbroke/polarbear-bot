#!/usr/bin/env python3
"""
Enhanced Polarbear Hybrid Bot v2
Hybrid approach using predefined responses + AI model for enhanced conversations
Optimized for Railway deployment (8GB RAM, 8 vCPU)
"""

import random
import re
import logging
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPolarBearBot:
    def __init__(self):
        """Initialize the enhanced polar bear bot with AI model"""
        logger.info("🐻‍❄️ Initializing Enhanced Polar Bear Bot with AI...")
        
        # Initialize AI model (DialoGPT-medium - better quality for Railway constraints)
        self.model_name = "microsoft/DialoGPT-medium"
        self.use_ai = True
        
        try:
            logger.info("📦 Loading AI model (DialoGPT-medium)...")
            # Use CPU-only to fit in 8GB RAM constraint
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU
                device_map="cpu",
                low_cpu_mem_usage=True
            )
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("✅ AI model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load AI model: {e}")
            logger.info("🔄 Falling back to predefined responses only")
            self.use_ai = False
        
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
                "yo! how's it going? ❄️",
                "what's up! 🐾",
                "hey there! chillin like always 🧊",
                "sup! ready to chat? 🐻‍❄️"
            ],
            "roast": [
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
                "you're like ice - transparent and dense! ❄️"
            ],
            "goated": [
                "i'm absolutely GOATED! 🐐❄️",
                "pretty goated not gonna lie 🐻‍❄️🐐",
                "definitely goated! arctic legend status 🧊🐐",
                "100% goated polar bear energy! 🐾🐐",
                "goated and loving it! ❄️🐐",
                "straight up goated! no cap 🐻‍❄️🐐",
                "absolutely goated in every way! 🧊🐐",
                "goated polar bear vibes only! 🐾🐐",
                "yeah i'm pretty goated tbh ❄️🐐",
                "goated status: confirmed! 🐻‍❄️🐐"
            ],
            "number": [
                "i'm like a solid 8.5/10! 🐻‍❄️",
                "definitely a 9! maybe 9.5 on good days ❄️",
                "solid 8! not perfect but pretty great 🐾",
                "i'd say 7.8/10! room for improvement 🧊",
                "honestly? probably a 9.2! 🐻‍❄️",
                "8.7 seems about right! ❄️",
                "i'm thinking 8.3! pretty decent 🐾",
                "maybe like 8.9? close to perfect! 🧊",
                "7.5! not bad at all 🐻‍❄️",
                "solid 8.1! happy with that ❄️",
                "8.6! definitely above average 🐾",
                "probably 8.4! pretty good stuff 🧊",
                "i'd go with 8.8! almost there! 🐻‍❄️",
                "thinking 7.9! not too shabby ❄️",
                "8.2 sounds right! content with that 🐾"
            ]
        }
        
        # Name-calling templates with personality
        self.namecall_templates = [
            "ugh, {name} you're such a {insult}! ❄️",
            "{name} stop being such a {insult}! 🧊",
            "seriously {name}? you're being a total {insult}! 🐻‍❄️",
            "{name} you absolute {insult}! 🐾",
            "god {name}, you're such a {insult}! ❄️",
            "jesus {name}, quit being a {insult}! 🧊",
            "{name} you're acting like a complete {insult}! 🐻‍❄️",
            "come on {name}, don't be such a {insult}! 🐾",
            "{name} you're being a massive {insult}! ❄️",
            "dude {name}, you're such a {insult}! 🧊",
            "{name} stop acting like a {insult}! 🐻‍❄️",
            "honestly {name}, you're being a real {insult}! 🐾",
            "{name} why are you such a {insult}? ❄️",
            "omg {name} you're being such a {insult}! 🧊",
            "{name} you're literally a {insult}! 🐻‍❄️",
            "bruh {name}, you're acting like a {insult}! 🐾",
            "{name} you're so annoying, such a {insult}! ❄️",
            "{name} quit being a {insult} for once! 🧊",
            "ugh {name}, why are you such a {insult}? 🐻‍❄️",
            "{name} you're the biggest {insult} ever! 🐾",
            "seriously {name}? stop being a {insult}! ❄️",
            "{name} you're acting like such a {insult}! 🧊",
            "god damn {name}, you're a real {insult}! 🐻‍❄️",
            "{name} you're being a total {insult} right now! 🐾",
            "jesus christ {name}, you're such a {insult}! ❄️",
            "{name} why do you have to be such a {insult}? 🧊",
            "dude {name}, quit being a {insult}! 🐻‍❄️",
            "{name} you're literally the worst {insult}! 🐾",
            "omfg {name}, you're such a {insult}! ❄️",
            "{name} you're acting like a complete {insult}! 🧊",
            "come on {name}, stop being a {insult}! 🐻‍❄️",
            "{name} you're being such an annoying {insult}! 🐾",
            "ugh {name}, you're the most annoying {insult}! ❄️",
            "{name} you're such a pathetic {insult}! 🧊",
            "god {name}, you're being a real {insult}! 🐻‍❄️",
            "{name} you're acting like a stupid {insult}! 🐾",
            "seriously {name}? you're such a {insult}! ❄️",
            "{name} you're being the worst {insult}! 🧊"
        ]
        
        # Insult words for name-calling
        self.insults = [
            "idiot", "moron", "dummy", "dumbass", "fool", "clown", "loser", 
            "dipshit", "jackass", "asshole", "dickhead", "prick", "douche",
            "turd", "shit", "bitch", "bastard", "freak", "weirdo", "creep",
            "nerd", "geek", "dork", "scrub", "noob", "trash", "garbage",
            "waste", "failure", "disappointment", "disgrace", "joke", "meme",
            "peasant", "pleb", "casual", "normie", "basic", "lame", "cringe",
            "sus", "sussy", "imposter", "impostor", "simp", "incel", "virgin",
            "beta", "cuck", "cuckold", "snowflake", "karen", "boomer", "zoomer",
            "millennial", "Gen Z", "Gen Alpha", "skibidi", "ohio", "sigma", "alpha"
        ]
        
        logger.info("✅ Enhanced Polar Bear Bot initialized!")
    
    def detect_intent(self, message):
        """Detect the intent of the user's message"""
        message_lower = message.lower()
        
        # Identity questions
        if any(phrase in message_lower for phrase in ["who are you", "what are you", "are you ai", "are you a bot", "tell me about yourself"]):
            return "identity"
        
        # Greetings
        if any(phrase in message_lower for phrase in ["hello", "hi", "hey", "sup", "what's up", "whats up", "yo"]):
            return "greeting"
            
        # Roast requests
        if any(phrase in message_lower for phrase in ["roast me", "insult me", "be mean", "be rude", "make fun"]):
            return "roast"
            
        # Goated questions
        if any(phrase in message_lower for phrase in ["how goated", "are you goated", "goated are you"]):
            return "goated"
            
        # Number questions
        if any(phrase in message_lower for phrase in ["pick a number", "choose a number", "what number", "give me a number"]):
            return "number"
            
        # Name-calling (if message contains curse words or aggressive tone)
        if any(word in message_lower for word in ["fuck", "shit", "damn", "stupid", "idiot", "dumb", "hate", "suck"]):
            return "namecall"
        
        return "general"
    
    def extract_name(self, message):
        """Extract name from message for name-calling"""
        # Look for patterns like "you're stupid, john" or "john you're dumb"
        patterns = [
            r'(?:you\'re.*?),\s*([a-zA-Z]+)',  # "you're stupid, john"
            r'([a-zA-Z]+)\s+(?:you\'re|you)',  # "john you're"
            r'(?:hey|hi)\s+([a-zA-Z]+)',       # "hey john"
            r'([a-zA-Z]+)\s+(?:is|are)',       # "john is"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "buddy"  # default name
    
    def generate_namecall_response(self, message):
        """Generate a name-calling response"""
        name = self.extract_name(message)
        template = random.choice(self.namecall_templates)
        insult = random.choice(self.insults)
        
        return template.format(name=name, insult=insult)
    
    def generate_ai_response(self, message):
        """Generate AI response with polar bear personality"""
        if not self.use_ai:
            return None
            
        try:
            # Inject polar bear personality into the prompt
            polar_prompt = f"polarbear (friendly arctic bot): {message.lower()}"
            
            # Tokenize input
            inputs = self.tokenizer.encode(polar_prompt, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 50,  # Keep responses concise
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=2
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the bot's response (after the prompt)
            if "polarbear (friendly arctic bot):" in response:
                response = response.split("polarbear (friendly arctic bot):")[-1].strip()
            
            # Add polar bear personality touches
            if response and len(response) > 5:
                # Add emojis occasionally
                if random.random() < 0.7:
                    emojis = ["🐻‍❄️", "❄️", "🧊", "🐾"]
                    response += f" {random.choice(emojis)}"
                
                # Ensure lowercase casual style
                response = response.lower().strip()
                
                # Remove any weird artifacts
                response = re.sub(r'[^\w\s!?.,\'\"🐻‍❄️❄️🧊🐾]', '', response)
                
                return response
                
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            
        return None
    
    def chat(self, message):
        """Main chat function with hybrid AI + predefined approach"""
        try:
            intent = self.detect_intent(message)
            logger.info(f"Detected intent: {intent}")
            
            # Use predefined responses for specific intents
            if intent == "namecall":
                response = self.generate_namecall_response(message)
            elif intent in self.responses:
                response = random.choice(self.responses[intent])
            else:
                # Try AI model for general conversation
                print("Generating using ai: ")
                response = self.generate_ai_response(message)
                
                # Fallback to predefined if AI fails or gives poor response
                if not response or len(response.strip()) < 3:
                    print("no response from ai...")
                    response = random.choice([
                        "that's pretty cool! ❄️",
                        "nice! keeping it chill 🐻‍❄️",
                        "sounds good to me! 🐾",
                        "word! staying frosty 🧊",
                        "totally! arctic vibes ❄️",
                        "for sure! chillin as always 🐻‍❄️",
                        "absolutely! keeping it icy 🐾",
                        "yeah! polar bear energy 🧊"
                    ])
            
            logger.info(f"Generated response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "sorry, my brain is a bit frozen right now... ❄️"

    def __del__(self):
        """Cleanup when bot is destroyed"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                # Clear model from memory
                del self.model
                del self.tokenizer
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        except:
            pass
        logger.info("🐻‍❄️ Enhanced Polar Bear Bot shutting down...")
