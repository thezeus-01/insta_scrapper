import os
from dotenv import load_dotenv

load_dotenv()

# Instagram Credentials
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# AI SETTINGS
USE_AI = True  # Set to False to skip AI analysis and follow everyone
AI_PROVIDER = "groq" # Options: "gemini", "groq"
GROQ_MODEL = "llama-3.3-70b-versatile"

# MESSAGING
DEFAULT_MESSAGE = "Hey! Loved your profile. Would love to connect! :)"

# Personal Branding
MY_INSTA_ID = "MENTION YOUR ID " # The ID of the guy behind the bot

# Targeting Criteria
TARGET_AGE_RANGE = (19, 23)
TARGET_GENDER = "female"
GENDER_KEYWORDS = ["girl", "woman", "female", "lady", "her", "she", "queen", "bride", "model"] # Keywords to look for in thumbnails
MAX_POSTS_PER_HASHTAG = 30 # Scrapes this many matches before moving to next hashtag
MAX_SESSION_MATCHES = 300   # Global cap for matches in a single run
TARGET_HASHTAGS = [
    "singlelife", "independentgirl", "selfloveclub", "loveyourself", "girlsnight",
    "livingmybestlife", "hotgirlenergy", "selfcarefirst", "soloqueen", "confidenceiskey",
    "reelsindia", "collegevibes", "latepost", "weekendoutfit", "selfiegirl",
    "travelalone", "coffeeandme", "aestheticgirl", "explorepageindia", "goodvibesonly"
]
MY_INTERESTS = [
    "Fashion", "Travel", "Fitness", "Cooking", "Dancing", 
    "Photography", "Gaming", "Reading", "Music", "Art", 
    "Yoga", "Cafehopping", "Shopping", "Skincare", "Pets"
]

# Bot Disclosure Message
BOT_DISCLOSURE = "PS: This is a bot texting you to find cool people!"

# Message Template (will be override by AI suggestion)
MESSAGE_TEMPLATE = "Hey! I saw your profile and noticed we have similar interests. You are cute!"

# Safety/Matching
MATCH_THRESHOLD = 0.2
DRY_RUN = False  # SET TO False TO ACTUALLY SEND MESSAGES
# Browser Settings
USE_BROWSER = True
HEADLESS = False # Set to True to hide the browser window
USE_EXISTING_BROWSER = True # Set to True to connect to an already running Chrome
REMOTE_DEBUGGING_PORT = 9222 # The port Chrome is running on for debugging

# DELAY SETTINGS (In seconds)
# Speed up Phase 2 (Messaging)
MESSAGE_DELAY_RANGE = (5, 15)  # Delay between messages to different users
ACTION_DELAY_RANGE = (1, 3)    # Delay between internal browser actions (clicks, navigation)
