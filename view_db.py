import sqlite3
from tabulate import tabulate # You might need to install this, or I'll use simple print

def view_matches():
    db_path = "profiles.db"
    if not sqlite3.os.path.exists(db_path):
        print("Database not found! Run the bot first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, reasoning, status, conversation_state FROM potential_matches")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No profiles found in database yet.")
    else:
        headers = ["ID", "Username", "AI Reasoning", "Initial Msg", "Conv State"]
        # Using simple formatting if tabulate isn't there
        print("\n=== SAVED PROFILES IN DATABASE ===\n")
        
        # Simple table formatting
        row_format = "{:<4} {:<15} {:<40} {:<12} {:<15}"
        print(row_format.format(*headers))
        print("-" * 90)
        for row in rows:
            # Truncate reasoning for better view
            reason = (row[2][:37] + '...') if len(row[2]) > 37 else row[2]
            print(row_format.format(row[0], row[1], reason, row[3], row[4]))
        
        print(f"\nTotal: {len(rows)} profiles.")

if __name__ == "__main__":
    view_matches()
