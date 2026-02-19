from groq import Groq
import os
import json
from config import GROQ_API_KEY, GROQ_MODEL, BOT_DISCLOSURE, TARGET_AGE_RANGE, MY_INSTA_ID, MY_INTERESTS

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
        """
        Uses Groq to analyze if a profile matches the criteria.
        """
        interests_str = ", ".join(my_interests) if my_interests else ", ".join(MY_INTERESTS)
        
        prompt = f"""
        Reference Profile (The Guy):
        {user_dna}
        Explicit Interests: {interests_str}

        Target Profile to Analyze:
        Username: {username}
        Bio: {bio}
        Recent Posts Context: {posts_content}

        Task:
        1. **STRICT GENDER FILTER (CRITICAL):** The target MUST be female. If the profile belongs to a male, you MUST set "match": false.
        2. **AGE FILTER:** Target range is 19-23. If age looks 24+, set "match": false. If age is UNKNOWN or NOT MENTIONED, set "match": true (The user will manually filter these).
        3. Analyze their top 3 interests.
        4. Match against: {interests_str}.
        5. **PHASE 2 - CONVINCING ICEBREAKER:**
           - DO NOT mention your own profile or ID.
           - DO NOT mention "my profile" or "my interests".
           - **CONVINCING TONE:** Be charming, observant, and high-value. Avoid being generic or creepy.
           - Comment naturally on a specific detail (e.g., "That view in your 3rd post is insane, is that the Alps?" or "Your style is so unique, where do you get those fits?").
           - Make it a question or a light observation that *demands* a response.
           - MUST be ONE LINE (max 12 words).

        Return ONLY a JSON-like structure:
        {{
            "match": true/false,
            "estimated_age": "range",
            "interests": ["interest1", "interest2"],
            "reasoning": "brief explanation",
            "suggested_message": "A hyper-specific, unique, and natural anonymous icebreaker (max 12 words)."
        }}
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return {"match": False, "reasoning": str(e)}

    def generate_final_message(self, suggestion):
        """
        Keeps the message anonymous for the first contact.
        """
        return suggestion

    def generate_reply(self, incoming_text, history=""):
        """
        Generates a natural reply. If they say 'Hi' or engage, offer the Instagram ID.
        """
        prompt = f"""
        User Response: "{incoming_text}"
        Context/History: {history}
        My Main Instagram ID: {MY_INSTA_ID}

        Task:
        - **STRICT ONE LINE RULE:** Your response MUST be a single line. No multiple sentences.
        - **CONVINCING TONE:** Be high-value, charming, and slightly mysterious.
        - **THE AI WINGMAN PERSONA:** You are an AI built by your friend (the developer) to find him his "best match" or a "cool girl".
        - If they just said "Hi" or seem curious, tell them you're an AI built by your friend to find him a girl, and ASK if they want his main Instagram ID.
        - If they asked "Who is this?" or "Do you have an ID?", give them {MY_INSTA_ID} naturally.
        - Example: "I'm just a custom AI built by my friend to find him a cool girl, want his main ID?"
        - Keep it very friendly and informal directly (ONE LINE ONLY).
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=GROQ_MODEL,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Reply Error: {e}")
            return "Hey! Sorry, just saw this. Are you on Instagram? I can give you my ID if you want."

if __name__ == "__main__":
    # Mock test
    handler = AIHandlerEngine()
    result = handler.analyze_profile(
        "travel_girl_99", 
        "21 | Travel enthusiast | Coffee lover", 
        "Photo of Paris, Photo of a latte art, Gym selfie"
    )
    print(result)
    if result.get("match"):
        print(handler.generate_final_message(result["suggested_message"]))
