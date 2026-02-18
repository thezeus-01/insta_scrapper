import time
import random
from instagrapi import Client
from config import IG_USERNAME, IG_PASSWORD, DRY_RUN
import os
from ai_handler import AIHandler

class InstagramBot:
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [3, 7]
        self.ai = AIHandler()
        self.user_dna = "Standard interests: music, travel, tech." # Default fallback
        self.following_ids = set()
        self.follower_ids = set()

    def login(self):
        print(f"Attempting to login as {IG_USERNAME}...")
        try:
            # Check if session exists to avoid re-login bans
            if os.path.exists("session.json"):
                self.cl.load_settings("session.json")
                print("Loaded existing session.")
            
            self.cl.login(IG_USERNAME, IG_PASSWORD)
            self.cl.dump_settings("session.json")
            print("Login successful!")
            
            # Fetch social circles to avoid messaging them
            print("Fetching your following and followers to avoid awkwardness...")
            my_pk = self.cl.user_id
            self.following_ids = set(self.cl.user_following(my_pk).keys())
            self.follower_ids = set(self.cl.user_followers(my_pk).keys())
            print(f"Social filter loaded: skipping {len(self.following_ids)} following and {len(self.follower_ids)} followers.")
            
        except Exception as e:
            print("\n" + "!"*50)
            print("LOGIN FAILED")
            print(f"Error: {e}")
            if "BadPassword" in str(e):
                print("\nPOSSIBLE FIXES:")
                print("1. Double-check your password in the .env file.")
                print("2. Check your phone for a 'This was me' security alert.")
                print("3. Try logging in manually on your phone on the same Wi-Fi.")
            elif "blacklist" in str(e).lower():
                print("\nYOUR IP IS TEMPORARILY BLACKLISTED.")
                print("Wait 15-30 minutes or try switching to a mobile hotspot.")
            print("!"*50 + "\n")
            raise

    def get_profiles_to_check(self, hashtag, count=10):
        """
        Finds profiles using a specific hashtag.
        """
        print(f"Searching for profiles with hashtag #{hashtag}...")
        try:
            medias = self.cl.hashtag_medias_recent(hashtag, amount=count)
            user_ids = [m.user.pk for m in medias]
            return list(set(user_ids))
        except Exception as e:
            print(f"Failed to fetch hashtag #{hashtag}: {e}")
            return []

    def analyze_own_profile(self):
        """
        Analyzes the bot owner's profile to feed into Gemini as 'DNA'.
        """
        print("Analyzing your profile to build 'Matching DNA'...")
        try:
            my_info = self.cl.user_info(self.cl.user_id)
            my_posts = self.cl.user_medias(self.cl.user_id, amount=5)
            my_captions = " | ".join([p.caption_text for p in my_posts if p.caption_text])
            
            self.user_dna = f"Bio: {my_info.biography}\nInterests: {my_captions}"
            print("Profile analyzed successfully.")
        except Exception as e:
            print(f"Failed to analyze own profile: {e}. Using default DNA.")

    def check_and_message(self, user_id):
        """
        Scrapes a profile, analyzes with Gemini, and sends a DM if it meets the criteria.
        """
        if str(user_id) in self.following_ids or str(user_id) in self.follower_ids:
            print(f"Skipping user {user_id}: Already in your following or followers list.")
            return False
            
        try:
            user_info = self.cl.user_info(user_id)
            username = user_info.username
            bio = user_info.biography
            
            # Fetch recent post captions
            posts = self.cl.user_medias(user_id, amount=5)
            captions = " | ".join([p.caption_text for p in posts if p.caption_text])
            
            print(f"Analyzing @{username} with Gemini AI...")
            analysis = self.ai.analyze_profile(username, bio, captions, user_dna=self.user_dna)
            
            if analysis.get("match"):
                print(f"Match found! AI reasoning: {analysis['reasoning']}")
                final_message = self.ai.generate_final_message(analysis["suggested_message"])
                
                print(f"Proposed Message for @{username}:\n---\n{final_message}\n---")
                
                if DRY_RUN:
                    print(f"[DRY RUN] Message not sent to @{username}. Set DRY_RUN = False in config.py to send.")
                else:
                    print(f"SENDING MESSAGE to @{username}...")
                    self.cl.direct_send(final_message, [user_id])
                    time.sleep(random.randint(60, 120)) # Safety delay
                return True
            else:
                print(f"No match for @{username}. Reason: {analysis.get('reasoning', 'Unknown')}")
                return False
                
        except Exception as e:
            print(f"Error processing user {user_id}: {e}")
            return False

def main():
    if not IG_USERNAME or not IG_PASSWORD:
        print("Please set your credentials in the .env file.")
        return

    bot = InstagramBot()
    bot.login()
    bot.analyze_own_profile()
    
    # Example: Check profiles under #coding
    target_hashtag = "travel" # Changed to travel for girls targeting example
    user_ids = bot.get_profiles_to_check(target_hashtag, count=5)
    
    for uid in user_ids:
        bot.check_and_message(uid)
        time.sleep(random.randint(5, 10)) # Sleep between profile checks

if __name__ == "__main__":
    main()
