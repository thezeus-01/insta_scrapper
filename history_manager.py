import json
import os

class HistoryManager:
    def __init__(self, filename="sent_history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def is_messaged(self, username):
        return username in self.history

    def add_to_history(self, username, message):
        from datetime import datetime
        self.history[username] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        }
        self.save_history()

    def save_history(self):
        with open(self.filename, 'w') as f:
            json.dump(self.history, f, indent=4)
