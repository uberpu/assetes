import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.shared.db import get_connection

def reset_db():
    print("Resetting the Continuous AI database...")
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE q_table RESTART IDENTITY;")
            cur.execute("TRUNCATE TABLE match_results RESTART IDENTITY;")
            conn.commit()
            print("[+] Database tables truncated successfully.")
        conn.close()
    except Exception as e:
        print(f"[!] Could not connect to the database or truncate tables. ({e})")
        print("Note: If the database does not exist, there is nothing to reset.")

if __name__ == '__main__':
    reset_db()
