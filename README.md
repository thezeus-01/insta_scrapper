# Instagram AI Matchmaker Bot 🤖💖

A powerful, high-speed Instagram bot powered by AI to help you find, connect, and chat with matching profiles based on your interests and specified hashtags.

## ✨ Features

- **Smart Scraping (Phase 1)**: Explores hashtags and uses AI (Groq/Gemini) to analyze bios and post vibes to find your perfect match.
- **Automated Messaging (Phase 2)**: High-speed, personalized initial contact messaging from your approved matches database.
- **AI Conversations (Phase 3)**: Automatically handles replies and manages the conversation to offer your Instagram ID.
- **Anti-Detection**: Connects to your **existing** Chrome or Brave browser session to bypass bot detection.
- **Custom Targeting**: Highly configurable hashtag list (20+) and interests (15+).
- **Speed Optimized**: Move through profiles and messages "within seconds" with configurable delay ranges.

## 🛠 Prerequisites

- **Python 3.8+**
- **Chrome** or **Brave Browser**
- **Chromedriver** (Automatically managed by the bot)
- **API Keys**: Groq or Gemini (for AI analysis)

## 🚀 Getting Started

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/insta-ai-bot.git
cd insta-ai-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the `.env.example` and add your credentials:

```env
IG_USERNAME=your_username
IG_PASSWORD=your_password
GROQ_API_KEY=your_groq_api_key
```

Edit `config.py` to customize your interests, hashtags, and speed settings.

### 3. Usage (The "Brave" Way)

To avoid getting banned, the bot uses your **real** browser session.

1. **Close your browser**: Ensure all Brave/Chrome windows are closed.
2. **Launch with Debug Mode**: Run the provided helper script:
   - Double-click `start_brave.bat` (or `start_chrome.bat`).
   - Log in to Instagram manually in that window.
3. **Run the Bot**:
   ```powershell
   python browser_bot.py
   ```
4. **Choose your Phase**:
   - `1`: Scrape new girls from hashtags.
   - `2`: Send initial messages to matches in your DB.
   - `3`: Check for replies and chat.

## ⚙️ Configuration Parameters

| Parameter | Description |
|-----------|-------------|
| `MAX_POSTS_PER_HASHTAG` | Matches to find per hashtag (default: 30) |
| `MAX_SESSION_MATCHES` | Global cap per run (default: 300) |
| `MESSAGE_DELAY_RANGE` | Delay between messages to avoid bans |
| `ACTION_DELAY_RANGE` | Speed of browser clicks and navigation |

## ⚠️ Disclaimer

This tool is for educational purposes only. Automated scraping and messaging may violate Instagram's Terms of Service. Use responsibly and at your own risk.

## 👤 Author
Developed by Mr. Zeus - Empowering connections through AI.
