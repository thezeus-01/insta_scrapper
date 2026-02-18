from db_manager import DatabaseManager
import sys

def main():
    db = DatabaseManager()
    if len(sys.argv) < 2:
        print("Usage: python remove_profile.py <username>")
        return

    username = sys.argv[1]
    db.remove_match(username)
    print(f"Removed @{username} from potential matches. They will be ignored in Phase 2.")

if __name__ == "__main__":
    main()
