import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="profiles.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS potential_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                bio TEXT,
                vibe TEXT,
                reasoning TEXT,
                suggested_message TEXT,
                screenshot_path TEXT,
                status TEXT DEFAULT 'pending',
                conversation_state TEXT DEFAULT 'scraped' -- scraped, sent, replied, offered_id, finished
            )
        ''')
        
        # Migration: Add conversation_state column if it doesn't exist
        try:
            cursor.execute("SELECT conversation_state FROM potential_matches LIMIT 1")
        except sqlite3.OperationalError:
            print("Migrating database: Adding 'conversation_state' column...")
            cursor.execute("ALTER TABLE potential_matches ADD COLUMN conversation_state TEXT DEFAULT 'scraped'")
            
        conn.commit()
        conn.close()

    def add_potential_match(self, username, bio, vibe, reasoning, suggested_message, screenshot_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO potential_matches (username, bio, vibe, reasoning, suggested_message, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, bio, vibe, reasoning, suggested_message, screenshot_path))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already exists
            return False
        finally:
            conn.close()

    def get_pending_matches(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM potential_matches WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_as_sent(self, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE potential_matches SET status = 'sent' WHERE username = ?", (username,))
        conn.commit()
        conn.close()

    def update_conversation_state(self, username, state):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE potential_matches SET conversation_state = ? WHERE username = ?", (state, username))
        conn.commit()
        conn.close()

    def get_matches_by_state(self, state):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM potential_matches WHERE conversation_state = ?", (state,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def user_exists(self, username):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM potential_matches WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return row is not None
