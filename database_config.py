"""
Database Configuration Module
Supports both SQLite (local development) and PostgreSQL (production on Render)
"""

import os
import sqlite3
from urllib.parse import urlparse

def get_database_config():
    """
    Determine database configuration based on environment
    Returns: (db_type, connection_params)
    """
    # Check for PostgreSQL DATABASE_URL (Render provides this)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse PostgreSQL URL
        parsed = urlparse(database_url)
        return 'postgresql', {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading slash
            'user': parsed.username,
            'password': parsed.password
        }
    else:
        # Use SQLite for local development
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
        return 'sqlite', {'database': db_path}

def get_db_connection():
    """
    Get database connection based on environment
    """
    db_type, config = get_database_config()
    
    if db_type == 'postgresql':
        try:
            import psycopg2
            import psycopg2.extras
            
            print(f"🐘 POSTGRESQL MODE: Connecting to database...")
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            # Use RealDictCursor for dict-like row access
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            print(f"✅ PostgreSQL connected successfully")
            return conn, 'postgresql'
            
        except ImportError:
            print("❌ psycopg2 not installed, falling back to SQLite")
            return get_sqlite_connection()
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            print("⚠️ Falling back to SQLite")
            return get_sqlite_connection()
    else:
        return get_sqlite_connection()

def get_sqlite_connection():
    """Get SQLite connection"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
    print(f"🔵 SQLITE MODE: Using local database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout = 30000')
    conn.execute('PRAGMA journal_mode = WAL')
    conn.execute('PRAGMA synchronous = FULL')
    
    return conn, 'sqlite'

def create_tables(conn, db_type):
    """
    Create database tables with appropriate syntax for the database type
    """
    if db_type == 'postgresql':
        create_postgresql_tables(conn)
    else:
        create_sqlite_tables(conn)

def create_postgresql_tables(conn):
    """Create tables for PostgreSQL"""
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            reset_token TEXT,
            bio TEXT,
            urls TEXT,
            profile_picture TEXT,
            dark_mode INTEGER DEFAULT 0,
            name TEXT,
            phone TEXT,
            location TEXT,
            website TEXT,
            avatar TEXT,
            timezone TEXT,
            datetime_format TEXT
        )
    ''')
    
    # Quiz questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id SERIAL PRIMARY KEY,
            language VARCHAR(100) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_type VARCHAR(50) DEFAULT 'multiple_choice',
            points INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Other tables...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            language VARCHAR(100) NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results_enhanced (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            language VARCHAR(100) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            question_details TEXT NOT NULL,
            points_earned INTEGER DEFAULT 0,
            streak_bonus INTEGER DEFAULT 0,
            time_bonus INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_list (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            word VARCHAR(255) NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            language VARCHAR(100) DEFAULT 'english',
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, word)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            words_learned INTEGER DEFAULT 0,
            conversation_count INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            daily_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz results table (legacy)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            language VARCHAR(100) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            achievement_type VARCHAR(100) NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Account activity table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            activity_type VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Password resets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create admin user if it doesn't exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('admin@example.com',))
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        from werkzeug.security import generate_password_hash
        print("🔑 Creating admin user...")
        cursor.execute('''
            INSERT INTO users (username, email, password, security_answer, is_admin)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            'admin',
            'admin@example.com', 
            generate_password_hash('admin123'),
            generate_password_hash('admin'),
            1
        ))
        print("✅ Admin user created: admin@example.com / admin123")
    
    conn.commit()
    print("✅ PostgreSQL tables created successfully")

def create_sqlite_tables(conn):
    """Create tables for SQLite (existing implementation)"""
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            security_answer TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            reset_token TEXT,
            bio TEXT,
            urls TEXT,
            profile_picture TEXT,
            dark_mode INTEGER DEFAULT 0,
            name TEXT,
            phone TEXT,
            location TEXT,
            website TEXT,
            avatar TEXT,
            timezone TEXT,
            datetime_format TEXT
        )
    ''')
    
    # Notifications table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Chat sessions table
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
    
    # Chat messages table
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
    
    # Quiz questions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_type TEXT DEFAULT 'multiple_choice',
            points INTEGER DEFAULT 10,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Quiz results enhanced table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results_enhanced (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            question_details TEXT NOT NULL,
            points_earned INTEGER DEFAULT 0,
            streak_bonus INTEGER DEFAULT 0,
            time_bonus INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz results table (legacy)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            language TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            passed INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Study list table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            language TEXT DEFAULT 'english',
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, word)
        )
    ''')
    
    # User progress table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            words_learned INTEGER DEFAULT 0,
            conversation_count INTEGER DEFAULT 0,
            accuracy_rate FLOAT DEFAULT 0.0,
            daily_streak INTEGER DEFAULT 0,
            last_activity_date DATE,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Achievements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_type TEXT NOT NULL,
            earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Account activity table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS account_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Password resets table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    print("✅ SQLite tables created successfully") 