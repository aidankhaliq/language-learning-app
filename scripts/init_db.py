# init_db.py - Database initialization for the Language Learning Quiz Application
"""
This module initializes the SQLite database for the application.
It creates all necessary tables and sets up default data if needed.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

def initialize_database():
    """
    Initializes the SQLite database with all required tables.
    Creates default admin user if it doesn't exist.
    """
    print("\n=== Initializing Database ===")
    
    # Determine database path - use persistent storage on Render or local path for development
    if os.path.exists('/data'):
        db_path = '/data/database.db'
        print(f"Using Render persistent storage: {db_path}")
    else:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')
        print(f"Using local database: {db_path}")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database (or create it if it doesn't exist)
    with sqlite3.connect(db_path) as conn:
        # Use Write-Ahead Logging for better concurrency and reliability
        conn.execute('PRAGMA journal_mode=WAL;')  # Helps reduce lock issues
        print("✅ WAL mode enabled!")

        # --- Create Tables ---

        # Users table - stores user account information
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,         -- Username for login
                email TEXT UNIQUE NOT NULL,            -- Email address (also used for login)
                password TEXT NOT NULL,                -- Hashed password
                security_answer TEXT NOT NULL,         -- Answer to security question for account recovery
                is_admin INTEGER DEFAULT 0,            -- Admin flag (1 = admin, 0 = regular user)
                reset_token TEXT,                      -- Token for password reset
                bio TEXT,                              -- User profile bio
                urls TEXT,                             -- Social media links
                profile_picture TEXT,                  -- Profile picture filename
                dark_mode INTEGER DEFAULT 0,           -- UI theme preference
                name TEXT,                             -- Full name
                phone TEXT,                            -- Phone number
                location TEXT,                         -- Location/address
                website TEXT,                          -- Personal website
                avatar TEXT                            -- Selected avatar image
            )
        ''')
        print("✅ Table 'users' created/verified!")

        # Quiz results table - stores detailed quiz results with points tracking
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results_enhanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,              -- User who took the quiz
                language TEXT NOT NULL,                -- Language of the quiz
                difficulty TEXT NOT NULL,              -- Difficulty level
                score INTEGER NOT NULL,                -- Number of correct answers
                total INTEGER NOT NULL,                -- Total number of questions
                percentage REAL NOT NULL,              -- Score percentage
                passed INTEGER DEFAULT 0,              -- Whether the quiz was passed (≥80%)
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                question_details TEXT NOT NULL,        -- JSON with detailed question data
                points_earned INTEGER DEFAULT 0,       -- Base points earned
                streak_bonus INTEGER DEFAULT 0,        -- Bonus points from streaks
                time_bonus INTEGER DEFAULT 0,          -- Bonus points from fast answers
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'quiz_results_enhanced' created/verified!")

        # Legacy quiz results table (kept for backward compatibility)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'quiz_results' (legacy) created/verified!")

        # Badges table - tracks user achievements
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,              -- User who earned the badge
                language TEXT NOT NULL,                -- Language the badge was earned in
                badge_id TEXT NOT NULL,                -- Badge identifier
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, language, badge_id)    -- Prevent duplicate badges
            )
        ''')
        print("✅ Table 'user_badges' created/verified!")

        # Notifications table - stores user notifications
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,              -- User who received the notification
                message TEXT NOT NULL,                 -- Notification message
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,             -- Whether notification has been read
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✅ Table 'notifications' created/verified!")

        # Chat history table - stores user-chatbot interactions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                language TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✅ Table 'chat_history' created/verified!")

        # Chat sessions table - organizes chat messages into sessions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                language TEXT NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'chat_sessions' created/verified!")

        # Chat messages table - stores individual messages in a session
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        print("✅ Table 'chat_messages' created/verified!")

        # Quiz questions table - stores all quiz questions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,  -- Stored as JSON
                answer TEXT NOT NULL,
                question_type TEXT DEFAULT 'multiple_choice',
                points INTEGER DEFAULT 10,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Table 'quiz_questions' created/verified!")

        # --- Ensure Required Columns Exist ---
        # Check and add any missing columns to users table
        for column, definition in [
            ("bio", "TEXT"),
            ("urls", "TEXT"),
            ("dark_mode", "INTEGER DEFAULT 0"),
            ("name", "TEXT"),
            ("phone", "TEXT"),
            ("location", "TEXT"),
            ("website", "TEXT"),
            ("avatar", "TEXT"),
            ("timezone", "TEXT"),
            ("datetime_format", "TEXT")
        ]:
            try:
                conn.execute(f'ALTER TABLE users ADD COLUMN {column} {definition};')
                conn.commit()
                print(f"✅ Column '{column}' added to users table!")
            except sqlite3.OperationalError:
                pass  # Column already exists

        # Ensure the 'is_read' column exists in notifications table
        try:
            conn.execute('ALTER TABLE notifications ADD COLUMN is_read INTEGER DEFAULT 0;')
            conn.commit()
            print("✅ Column 'is_read' added to notifications table!")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # --- Create Default Admin User ---
        try:
            admin_password = generate_password_hash('adminpassword')
            conn.execute(
                "INSERT OR IGNORE INTO users (username, email, password, security_answer, is_admin) VALUES (?, ?, ?, ?, ?)",
                ('admin', 'kishenkish18@gmail.com', admin_password, 'admin', 1)
            )
            conn.commit()
            print("✅ Admin user created/verified!")
        except Exception as e:
            print(f"⚠ Error creating admin user: {e}")

        print("\n✅ Database initialization completed successfully!")

if __name__ == '__main__':
    initialize_database()