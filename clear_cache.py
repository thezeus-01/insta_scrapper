from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

def clear_browser_cache():
    print("Initializing browser to clear cache...")
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run headless for speed
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Clearing cache and cookies...")
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    clear_browser_cache()
    # Also delete session.json if it exists (used by bot.py)
    if os.path.exists("session.json"):
        print("Deleting session.json...")
        os.remove("session.json")
        print("Done!")
