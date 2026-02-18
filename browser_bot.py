import time
import random
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import (
    IG_USERNAME, IG_PASSWORD, GEMINI_API_KEY, GROQ_API_KEY, GROQ_MODEL,
    HEADLESS, DRY_RUN, TARGET_HASHTAGS, MY_INTERESTS, MY_INSTA_ID, USE_AI, DEFAULT_MESSAGE,
    MAX_POSTS_PER_HASHTAG, GENDER_KEYWORDS
)
from history_manager import HistoryManager
from db_manager import DatabaseManager
from matcher import calculate_similarity
from groq import Groq
import re

class AIHandlerEngine:
    def __init__(self):
        print("\n" + "="*50)
        print("MIGRATING AI ENGINE TO GROQ (EXTREME SPEED)")
        print("="*50 + "\n")
        try:
            self.client = Groq(api_key=GROQ_API_KEY)
            print(f"AI System Initialized: Using Groq ({GROQ_MODEL})")
        except Exception as e:
            print(f"CRITICAL: AI Initialization failed: {e}")
            self.client = None

    def analyze_profile(self, username, bio, posts_content, user_dna="", my_interests=None):
        interests_str = ", ".join(my_interests) if my_interests else ", ".join(MY_INTERESTS)
        prompt = f"""
        Reference Profile: {user_dna}
        Interests: {interests_str}
        Target: @{username} | Bio: {bio} | Posts: {posts_content}
        
        Task:
        1. **STRICT GENDER FILTER (CRITICAL):** The target MUST be female. If the profile belongs to a male, you MUST set "match": false.
        2. **AGE FILTER:** Target range is 19-23. 
           - If age is 24+, set "match": false.
           - If age is UNKNOWN or NOT MENTIONED, set "match": true (The user will manually filter these).
        3. Match interests.
        4. Suggested message (Anonymous, no ID).
        
        Return JSON ONLY: {{"match": true/false, "estimated_age": "range or unknown", "gender": "male/female", "reasoning": "...", "suggested_message": "..."}}
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            return {"match": False, "reasoning": str(e)}

    def generate_final_message(self, suggestion): return suggestion
    def generate_reply(self, incoming_text, history=""):
        prompt = f"User said: {incoming_text}\nReply naturally. If they ask who this is or seem interested, offer ID: {MY_INSTA_ID}"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
            )
            return chat_completion.choices[0].message.content.strip()
        except: return "Hey! Follow me on my main ID: " + MY_INSTA_ID

class InstagramBrowserBot:
    def __init__(self):
        chrome_options = Options()
        if HEADLESS: chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.ai = AIHandlerEngine()
        self.history = HistoryManager()
        self.db = DatabaseManager()
        self.user_dna = "Standard interests: music, travel, tech."
        
        if not os.path.exists("scraped_profiles"): os.makedirs("scraped_profiles")

    def is_logged_in(self):
        try:
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            if "login" not in self.driver.current_url:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/')] | //svg[@aria-label='Home']")))
                return True
        except: pass
        return False

    def login(self):
        print("Checking Instagram session...")
        if self.is_logged_in():
            print("Already logged in. Skipping login steps.")
            return

        print("Opening Login Page...")
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        try:
            try:
                continue_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
                continue_btn.click()
                print("Clicked 'Continue as' button.")
                time.sleep(5)
                if self.is_logged_in(): return
            except: pass

            print(f"Attempting auto-login for {IG_USERNAME}...")
            user_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")))
            pass_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            user_input.send_keys(IG_USERNAME)
            pass_input.send_keys(IG_PASSWORD); pass_input.send_keys(Keys.ENTER)
            time.sleep(5)
            try:
                save_info_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save Info')] | //div[contains(text(), 'Save Info')]")))
                save_info_btn.click()
                print("Clicked 'Save Info'.")
                time.sleep(3)
            except: pass
        except Exception as e:
            print(f"Auto-login skipped or fields not found.")

        print("\n--- ACTION REQUIRED ---")
        print("1. Look at the Chrome window.")
        print("2. DO NOT PRESS ENTER until you see your actual Instagram FEED (posts from friends).")
        print(">>> Press Enter here ONLY when you are on the Home Page...")
        input()

    def is_verified(self):
        """Checks if the current profile has a verified blue tick."""
        try:
            # Verified badges usually have aria-label="Verified" or an SVG with that label
            verified_selectors = [
                "//span[@aria-label='Verified']",
                "//span[contains(@class, 'VerificationBadge')]",
                "//svg[@aria-label='Verified']",
                "//header//span[contains(@class, 'x1lliihq')]//svg[@aria-label='Verified']"
            ]
            for s in verified_selectors:
                try:
                    if self.driver.find_elements(By.XPATH, s):
                        return True
                except: continue
        except: pass
        return False

    def scrape_profile_internal(self):
        """Scrapes bio and vibe from the current profile page."""
        try:
            header = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
            bio = header.text
            post_images = self.driver.find_elements(By.TAG_NAME, "img")
            vibe_details = [img.get_attribute("alt") for img in post_images if img.get_attribute("alt")]
            vibe_context = " | ".join(list(set(vibe_details))[:5])
            return bio, vibe_context
        except: return None, None

    def follow_user_internal(self):
        """Follows the user while on their profile page."""
        try:
            selectors = ["//button[contains(., 'Follow')]", "//button//div[contains(text(), 'Follow')]"]
            for s in selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, s)
                    if btn.is_displayed():
                        btn.click()
                        print("Successfully followed!")
                        return
                except: continue
        except: pass

    def simple_filter(self, bio, vibe):
        """Simple keyword filter to skip obvious business/junk profiles without AI."""
        junk_keywords = ["business", "store", "shop", "marketing", "promotion", "agency", "service", "booking", "enterprise", "mom", "married"]
        bio_lower = bio.lower()
        for key in junk_keywords:
            if key in bio_lower:
                return False, f"Bio contains junk keyword: {key}"
        return True, "Passed simple keyword filter."

    def collect_grid_posts(self, hashtag, target_count):
        """Scrolls the grid and collects unique post links, filtering by gender keywords in alt text."""
        print(f"Collecting potential matches from #{hashtag} grid...")
        links = []
        seen_links = set()
        scroll_attempts = 0
        max_scrolls = 15

        while len(links) < target_count * 2 and scroll_attempts < max_scrolls:
            # Find all post/reel anchors
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reels/')]")
            
            for post in posts:
                try:
                    url = post.get_attribute("href")
                    # EXCLUDE global links like /reels/ and /p/
                    # We want /reels/ABC123/ or /p/XYZ789/
                    url_clean = url.strip("/").split("?")[0]
                    if url_clean.endswith("/reels") or url_clean.endswith("/p") or not any(x in url for x in ["/p/", "/reels/"]):
                        continue
                        
                    if url not in seen_links:
                        seen_links.add(url)
                        # Check image alt text for "Pseudo-CV" filtering
                        try:
                            img = post.find_element(By.TAG_NAME, "img")
                            alt_text = img.get_attribute("alt").lower()
                            
                            # Prioritize keywords
                            is_potential_girl = any(word in alt_text for word in GENDER_KEYWORDS)
                            if is_potential_girl:
                                links.append(url)
                                print(f"  [GRID] Potential Girl detected: {url.split('/p/')[-1] if '/p/' in url else url.split('/')[-2]}")
                            elif len(links) < target_count: # If we don't have enough girls, take others too
                                links.append(url)
                        except:
                            if len(links) < target_count: links.append(url)
                except: continue

            if len(links) >= target_count: break
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_attempts += 1
            print(f"  Scrolling grid... (Collected: {len(links)})")

        return list(dict.fromkeys(links))[:target_count*2] # Unique links, limited

    def run_phase_1_scrape(self, hashtags):
        """
        PHASE 1: Grid Collection + Direct Profile Visits.
        """
        self.login()
        
        for hashtag in hashtags:
            print(f"\n--- EXPLORING HASHTAG: #{hashtag} ---")
            self.driver.get(f"https://www.instagram.com/explore/tags/{hashtag}/")
            time.sleep(5)
            
            post_links = self.collect_grid_posts(hashtag, MAX_POSTS_PER_HASHTAG)
            print(f"Found {len(post_links)} links to analyze.")
            
            match_count = 0
            for link in post_links:
                if match_count >= MAX_POSTS_PER_HASHTAG: break
                
                try:
                    print(f"\nAnalyzing Post: {link}")
                    self.driver.get(link)
                    time.sleep(random.uniform(3, 5))
                    
                    # Extract handle from post page
                    try:
                        # Robust selectors for username in header (Post and Reels)
                        handle_selectors = [
                            "//header//a[contains(@href, '/') and @role='link']", # Standard post header
                            "//div[contains(@class, 'x1cy8zhl')]//a[@role='link']", # Reels sidebar name
                            "//span[contains(@class, 'xt0psk2')]//a[@role='link']", # Reel name
                            "//div[contains(@class, 'x1iyjqo2')]//a[@role='link']", # Header Link
                            "//h2//a", # Some headers use H2
                            "(//a[@role='link'])[1]" # Fallback
                        ]
                        name = ""
                        for selector in handle_selectors:
                            try:
                                el = self.driver.find_element(By.XPATH, selector)
                                potential_name = el.text.strip().split("\n")[0].split(" •")[0].split("  ")[0]
                                if potential_name and len(potential_name) > 2:
                                    # Filter common UI text
                                    filtered = re.sub(r'[^a-zA-Z0-9._]', '', potential_name)
                                    if filtered and filtered.lower() not in ["explore", "reels", "direct", "home", "search", "messages", "notifications", "create", "profile", "more", "following", "follow"]:
                                        name = filtered
                                        break
                            except: continue
                    except Exception as e:
                        print(f"  Extraction error for {link}: {e}")
                        continue
                        
                    if not name or name in [IG_USERNAME, "explore", "about"] or self.history.is_messaged(name):
                        print(f"  Skipping @{name} (Already handled or invalid).")
                        continue

                    print(f"Processing Profile: @{name}")
                    
                    # Visit Profile Directly
                    self.driver.get(f"https://www.instagram.com/{name}/")
                    time.sleep(random.uniform(4, 6))
                    
                    # Check for Verified Badge (Skip if verified)
                    if self.is_verified():
                        print(f"  Skipping @{name} (Verified Account - unlikely to reply).")
                        continue

                    # Scrape & Analyze
                    bio, vibe = self.scrape_profile_internal()
                    if bio:
                        if USE_AI:
                            print(f"  AI Analysis for @{name}...")
                            analysis = self.ai.analyze_profile(name, bio, vibe, user_dna=self.user_dna, my_interests=MY_INTERESTS)
                            
                            # CHECK FOR 429 RESOURCE EXHAUSTED OR OTHER API FAILURES
                            reasoning = analysis.get("reasoning", "")
                            if "429" in reasoning or "RESOURCE_EXHAUSTED" in reasoning or "quota" in reasoning.lower():
                                print(f"  !!! AI QUOTA EXCEEDED (429) !!! Falling back to Similarity Matching...")
                                from matcher import calculate_similarity
                                similarity_score, common = calculate_similarity(MY_INTERESTS, f"{bio} {vibe}")
                                is_match = similarity_score >= 0.2
                                reasoning = f"AI Quota Exceeded. Fallback Match: {is_match} (Score: {similarity_score:.2f}, Common: {common})"
                                suggested_message = DEFAULT_MESSAGE
                                print(f"  Fallback Results: Match={is_match}, Score={similarity_score:.2f}")
                            else:
                                is_match = analysis.get("match")
                                suggested_message = analysis.get("suggested_message")
                                print(f"  AI Results: Match={is_match}, Age={analysis.get('estimated_age')}, Gender={analysis.get('gender')}")
                        else:
                            is_match, reasoning = self.simple_filter(bio, vibe)
                            suggested_message = DEFAULT_MESSAGE
                        
                        if is_match:
                            print(f"  MATCH! Following and saving...")
                            self.follow_user_internal() 
                            time.sleep(2)
                            
                            screenshot_path = f"scraped_profiles/{name}.png"
                            self.driver.save_screenshot(screenshot_path)
                            
                            self.db.add_potential_match(
                                username=name, bio=bio, vibe=vibe, reasoning=reasoning,
                                suggested_message=suggested_message, screenshot_path=screenshot_path
                            )
                            match_count += 1
                        else:
                            print(f"  Skip: {reasoning}")
                    
                except Exception as e:
                    print(f"  Error processing {link}: {e}")
                    continue

    def scrape_profile_internal(self):
        """Scrapes bio and vibe from the current profile page."""
        try:
            header = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
            bio = header.text
            post_images = self.driver.find_elements(By.TAG_NAME, "img")
            vibe_details = [img.get_attribute("alt") for img in post_images if img.get_attribute("alt")]
            vibe_context = " | ".join(list(set(vibe_details))[:5])
            return bio, vibe_context
        except: return None, None

    def follow_user_internal(self):
        """Follows the user while on their profile page."""
        try:
            selectors = ["//button[contains(., 'Follow')]", "//button//div[contains(text(), 'Follow')]"]
            for s in selectors:
                try:
                    btn = self.driver.find_element(By.XPATH, s)
                    if btn.is_displayed():
                        btn.click()
                        print("Successfully followed!")
                        return
                except: continue
        except: pass

    def run_phase_2_send(self):
        # ... (rest of the method remains same)
        """
        PHASE 2: Read approved rows from DB and send messages.
        """
        self.login()
        pending = self.db.get_pending_matches()
        print(f"Found {len(pending)} pending profiles in Database.")
        
        for p in pending:
            # p structure from SQLite: (id, username, bio, vibe, reasoning, suggested_message, screenshot_path, status)
            username = p[1]
            message = p[5]
            
            print(f"\nProcessing @{username} from DB Review...")
            print(f"Reasoning: {p[4]}")
            
            if DRY_RUN:
                print(f"[DRY RUN] Would send to @{username}: {message}")
                self.db.mark_as_sent(username) # Mark as handled even in dry run
                continue
            
            sent = self.send_message(username, message)
            if sent:
                self.db.update_conversation_state(username, "sent")
                self.db.mark_as_sent(username)
                time.sleep(random.randint(60, 120)) # Safety delay
            else:
                print(f"Failed to send to @{username}. Keeping as pending.")

    def run_phase_3_replies(self):
        """
        PHASE 3: Check DMs for replies and handle the conversation.
        """
        self.login()
        print("Checking Direct Messages for replies...")
        self.driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(5)
        
        # This is a complex part: Scraping unread messages or checking specific threads.
        # Simplified version: Look for usernames in the inbox that we have messaged.
        
        sent_profiles = self.db.get_matches_by_state("sent")
        offered_profiles = self.db.get_matches_by_state("offered_id")
        to_check = sent_profiles + offered_profiles
        
        print(f"Checking {len(to_check)} profiles for replies...")
        
        for p in to_check:
            username = p[1]
            try:
                # Search for the user in the inbox (using the search box or just finding their name in the sidebar)
                # For simplicity, let's navigate directly to the message thread
                self.driver.get(f"https://www.instagram.com/direct/t/{username}/") # This is a guess, usually IG uses thread IDs but direct URLs sometimes work if handled by IG redirects
                # More robust: Navigate to profile then click Message
                self.driver.get(f"https://www.instagram.com/{username}/")
                time.sleep(2)
                msg_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']")))
                msg_button.click()
                time.sleep(4)
                
                # Check the last message in the thread
                messages = self.driver.find_elements(By.XPATH, "//div[@role='row']")
                if not messages: continue
                
                last_msg_element = messages[-1]
                last_msg_text = last_msg_element.text
                
                # If the last message text doesn't contain our previous message, it's likely a reply
                # Or check alignment/class to see if it's from 'them'
                # Instagram's DM structure is very complex with SVG/Divs. 
                # Let's assume for now we can get the text.
                
                # Simple check: Is the last message from US? (Checking if 'suggested_message' is in last_msg_text)
                if p[5] in last_msg_text:
                    print(f"No reply yet from @{username}.")
                    continue
                
                print(f"New message from @{username}: {last_msg_text}")
                
                # Generate AI reply
                reply = self.ai.generate_reply(last_msg_text, history=f"Bot sent: {p[5]}")
                print(f"AI Response: {reply}")
                
                text_area = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))
                text_area.send_keys(reply)
                text_area.send_keys(Keys.ENTER)
                
                if "ID" in reply or "insta" in reply.lower():
                    self.db.update_conversation_state(username, "offered_id")
                else:
                    self.db.update_conversation_state(username, "replied")
                
                time.sleep(random.randint(5, 10))
                
            except Exception as e:
                print(f"Error checking replies for @{username}: {e}")

    def run(self, hashtags):
        print("\n--- INSTAGRAM BOT ---\n")
        print("1. Phase 1: Scrape & Follow new profiles")
        print("2. Phase 2: Send Initial anonymous messages")
        print("3. Phase 3: Manage Replies & Offer Insta ID")
        choice = input("Select Phase (1/2/3): ")
        
        if choice == '1':
            self.run_phase_1_scrape(hashtags)
        elif choice == '2':
            self.run_phase_2_send()
        elif choice == '3':
            self.run_phase_3_replies()
        else:
            print("Invalid choice.")

    def follow_user(self, username):
        print(f"Attempting to Follow @{username}...")
        try:
            # If we are already on the profile page, just find 'Follow'
            # Otherwise navigate
            if username not in self.driver.current_url:
                self.driver.get(f"https://www.instagram.com/{username}/")
                time.sleep(3)
                
            # More robust selectors for modern Instagram UI
            selectors = [
                "//button[contains(., 'Follow')]",
                "//button//div[contains(text(), 'Follow')]",
                "//div[@role='button'][contains(., 'Follow')]",
                "//button[text()='Follow']"
            ]
            
            follow_btn = None
            for selector in selectors:
                try:
                    follow_btn = self.driver.find_element(By.XPATH, selector)
                    if follow_btn.is_displayed(): break
                except:
                    continue
            
            if follow_btn:
                follow_btn.click()
                print(f"Successfully followed @{username}!")
                time.sleep(2)
            else:
                print(f"Could not find Follow button for @{username}. Maybe already following?")
        except Exception as e:
            print(f"Error trying to follow @{username}: {e}")

    def send_message(self, username, message):
        print(f"Attempting to send message to @{username}...")
        try:
            self.driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(3)
            
            msg_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']")))
            msg_button.click()
            time.sleep(3)
            
            text_area = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']")))
            text_area.send_keys(message)
            text_area.send_keys(Keys.ENTER)
            self.history.add_to_history(username, message)
            print(f"Message sent and saved to history for @{username}!")
            return True
        except Exception as e:
            print(f"Failed to send message via browser: {e}")
            return False

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    bot = InstagramBrowserBot()
    try:
        bot.run(TARGET_HASHTAGS)
    finally:
        bot.close()
