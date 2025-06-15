import sqlite3
import os

def get_db_connection():
    # Get the absolute path to the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def make_user_admin(user_id):
    try:
        with get_db_connection() as conn:
            # First check if the user exists
            user = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user:
                print(f"No user found with ID {user_id}")
                return False
            
            # Update the user to be an admin
            conn.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            conn.commit()
            print(f"Successfully made user {user['username']} (ID: {user_id}) an admin")
            return True
    except Exception as e:
        print(f"Error making user admin: {e}")
        return False

if __name__ == "__main__":
    make_user_admin(5) 