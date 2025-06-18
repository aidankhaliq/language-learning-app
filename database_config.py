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
    Get database connection with bulletproof error handling and compatibility
    Returns: (connection, db_type)
    """
    try:
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
                    password=config['password'],
                    connect_timeout=30,
                    options='-c statement_timeout=30000'  # 30 second timeout
                )
                # Use RealDictCursor for dict-like row access
                conn.cursor_factory = psycopg2.extras.RealDictCursor
                
                # Test the connection
                with conn.cursor() as test_cursor:
                    test_cursor.execute("SELECT 1")
                    test_cursor.fetchone()
                
                print(f"✅ PostgreSQL connected successfully")
                print(f"📊 Database connection type: postgresql")
                return BulletproofConnection(conn, 'postgresql')
                
            except ImportError:
                print("❌ psycopg2 not installed, falling back to SQLite")
                return get_sqlite_connection()
            except Exception as e:
                print(f"❌ PostgreSQL connection failed: {e}")
                # CRITICAL: DO NOT FALL BACK TO SQLITE IN PRODUCTION!
                # This causes data to be split between databases
                if os.getenv('DATABASE_URL'):
                    print("🚨 CRITICAL: In production environment - PostgreSQL failure is FATAL!")
                    print("🚨 Data would be lost if we fall back to SQLite!")
                    raise Exception(f"Production PostgreSQL connection failed: {e}")
                else:
                    print("⚠️ Development mode: Falling back to SQLite")
                    return get_sqlite_connection()
        else:
            return get_sqlite_connection()
            
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        # CRITICAL: DO NOT FALL BACK TO SQLITE IN PRODUCTION!
        if os.getenv('DATABASE_URL'):
            print("🚨 CRITICAL: In production environment - Database failure is FATAL!")
            raise Exception(f"Production database configuration failed: {e}")
        else:
            print("⚠️ Development mode: Falling back to SQLite")
            return get_sqlite_connection()

def get_sqlite_connection():
    """Get SQLite connection with bulletproof wrapper"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
        print(f"🔵 SQLITE MODE: Using local database: {db_path}")
        
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA busy_timeout = 30000')
        conn.execute('PRAGMA journal_mode = WAL')
        conn.execute('PRAGMA synchronous = FULL')
        
        # Test the connection
        conn.execute('SELECT 1').fetchone()
        
        return BulletproofConnection(conn, 'sqlite')
        
    except Exception as e:
        print(f"❌ SQLite connection error: {e}")
        # Create in-memory database as last resort
        print("⚠️ FALLBACK: Using in-memory database (data will be lost!)")
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        return BulletproofConnection(conn, 'sqlite')

def create_tables(conn, db_type=None):
    """
    Create database tables with appropriate syntax for the database type
    """
    # If db_type is not provided, get it from the connection wrapper
    if db_type is None:
        db_type = conn.db_type if hasattr(conn, 'db_type') else 'sqlite'
    
    if db_type == 'postgresql':
        create_postgresql_tables(conn)
    else:
        create_sqlite_tables(conn)

def create_postgresql_tables(conn):
    """Create tables for PostgreSQL using bulletproof wrapper"""
    try:
        # Users table
        conn.execute('''
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
        conn.execute('''
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
        
        # Notifications table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Chat sessions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id INTEGER NOT NULL,
                language VARCHAR(100) NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat messages table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        
        # Quiz results enhanced table
        conn.execute('''
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
        
        # Study list table
        conn.execute('''
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
        
        # User progress table
        conn.execute('''
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
        conn.execute('''
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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                achievement_type VARCHAR(100) NOT NULL,
                achievement_name VARCHAR(255),
                description TEXT,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Account activity table
        conn.execute('''
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
        conn.execute('''
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
        
        try:
            # Check if admin user exists
            result = conn.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('admin@example.com',)).fetchone()
            admin_exists = (result and result[0] > 0) if result else False
            
            if not admin_exists:
                from werkzeug.security import generate_password_hash
                print("🔑 Creating admin user...")
                conn.execute('''
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
            else:
                print("ℹ️ Admin user already exists")
                
            # Verify admin user exists and has correct privileges
            admin_check = conn.execute("SELECT id, username, is_admin FROM users WHERE email = %s", ('admin@example.com',)).fetchone()
            if admin_check:
                admin_id = admin_check[0] if isinstance(admin_check, (list, tuple)) else admin_check['id']
                admin_username = admin_check[1] if isinstance(admin_check, (list, tuple)) else admin_check['username']
                is_admin_flag = admin_check[2] if isinstance(admin_check, (list, tuple)) else admin_check['is_admin']
                print(f"✅ Admin verification: ID={admin_id}, Username={admin_username}, IsAdmin={is_admin_flag}")
                if not is_admin_flag:
                    print("⚠️ Admin user exists but is_admin flag is not set - fixing...")
                    conn.execute("UPDATE users SET is_admin = 1 WHERE email = %s", ('admin@example.com',))
                    print("✅ Admin privileges fixed")
            else:
                print("❌ Admin user verification failed")
                
        except Exception as e:
            print(f"⚠️ Admin user creation error: {e}")
            import traceback
            print(f"⚠️ Full traceback: {traceback.format_exc()}")
        
        conn.commit()
        print("✅ PostgreSQL tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating PostgreSQL tables: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise

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
            achievement_name TEXT,
            description TEXT,
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

class BulletproofConnection:
    """
    A bulletproof database connection wrapper that handles all compatibility issues
    """
    
    def __init__(self, raw_conn, db_type):
        self.raw_conn = raw_conn
        self.db_type = db_type
        self._closed = False
    
    def execute(self, query, params=None):
        """Execute query with full compatibility and error handling"""
        if self._closed:
            raise Exception("Cannot execute on closed connection")
        
        try:
            if self.db_type == 'postgresql':
                return self._execute_postgresql(query, params)
            else:
                return self._execute_sqlite(query, params)
        except Exception as e:
            print(f"Database query error: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Params: {params}")
            raise e
    
    def _execute_postgresql(self, query, params):
        """Execute PostgreSQL query with conversion"""
        # Convert SQLite syntax to PostgreSQL
        pg_query = self._convert_query_syntax(query)
        pg_params = params or ()
        
        try:
            cursor = self.raw_conn.cursor()
            cursor.execute(pg_query, pg_params)
            return BulletproofResult(cursor, 'postgresql')
        except Exception as e:
            print(f"PostgreSQL query error: {e}")
            print(f"Query: {query} -> {pg_query}")
            print(f"Params: {params}")
            raise e
    
    def _execute_sqlite(self, query, params):
        """Execute SQLite query"""
        try:
            cursor = self.raw_conn.execute(query, params or ())
            return BulletproofResult(cursor, 'sqlite')
        except Exception as e:
            print(f"SQLite query error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise e
    
    def _convert_query_syntax(self, query):
        """Convert SQLite syntax to PostgreSQL"""
        pg_query = query.replace('?', '%s')
        
        # Handle INSERT OR IGNORE - Convert to PostgreSQL ON CONFLICT syntax
        if 'INSERT OR IGNORE' in pg_query:
            # Extract the table name and columns from the INSERT statement
            if 'study_list' in pg_query and '(user_id, word' in pg_query:
                # For study_list table, use unique constraint on user_id + word
                pg_query = pg_query.replace('INSERT OR IGNORE', 'INSERT')
                pg_query += ' ON CONFLICT (user_id, word) DO NOTHING'
            else:
                # Generic fallback for other tables
                pg_query = pg_query.replace('INSERT OR IGNORE', 'INSERT')
                pg_query += ' ON CONFLICT DO NOTHING'
        
        # Handle INSERT OR REPLACE
        if 'INSERT OR REPLACE' in pg_query:
            pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
        
        # Handle PRAGMA statements (ignore them for PostgreSQL)
        if pg_query.strip().startswith('PRAGMA'):
            return 'SELECT 1'  # Harmless query
        
        # Handle SQLite-specific queries
        if 'sqlite_master' in pg_query:
            pg_query = pg_query.replace('sqlite_master', 'information_schema.tables')
            pg_query = pg_query.replace(
                "name FROM information_schema.tables WHERE type='table'",
                "table_name FROM information_schema.tables WHERE table_schema='public'"
            )
        
        return pg_query
    
    def commit(self):
        """Commit transaction"""
        if not self._closed:
            try:
                self.raw_conn.commit()
            except Exception as e:
                print(f"Commit error: {e}")
                raise
    
    def rollback(self):
        """Rollback transaction"""
        if not self._closed:
            try:
                self.raw_conn.rollback()
            except Exception as e:
                print(f"Rollback error: {e}")
                pass  # Don't raise on rollback errors
    
    def close(self):
        """Close connection"""
        if not self._closed:
            try:
                self.raw_conn.close()
                self._closed = True
            except Exception as e:
                print(f"Close error: {e}")
                pass  # Don't raise on close errors
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except:
                self.rollback()
                raise
        self.close()


class BulletproofResult:
    """
    Bulletproof result wrapper that handles all access patterns safely
    """
    
    def __init__(self, cursor, db_type):
        self.cursor = cursor
        self.db_type = db_type
    
    def fetchone(self):
        """Fetch one result with safe access"""
        try:
            result = self.cursor.fetchone()
            if result is None:
                return None
            
            if self.db_type == 'postgresql':
                # PostgreSQL with RealDictCursor returns dict-like objects
                return dict(result) if result else None
            else:
                # SQLite with row_factory returns Row objects (dict-like)
                return result
        except Exception as e:
            print(f"fetchone error: {e}")
            return None
    
    def fetchall(self):
        """Fetch all results with safe access"""
        try:
            results = self.cursor.fetchall()
            if not results:
                return []
            
            if self.db_type == 'postgresql':
                return [dict(result) for result in results]
            else:
                return results
        except Exception as e:
            print(f"fetchall error: {e}")
            return [] 

def safe_dict_get(data, key, default=None):
    """
    Safely get value from dictionary-like object
    Works with dicts, sqlite Row objects, and other dict-like objects
    """
    if data is None:
        return default
    
    try:
        # Try dictionary access first
        if hasattr(data, '__getitem__'):
            return data[key] if key in data else default
        # Try attribute access as fallback
        elif hasattr(data, key):
            return getattr(data, key)
        else:
            return default
    except (KeyError, TypeError, AttributeError):
        return default


def safe_fetchone(cursor_result):
    """
    Safely fetch one result with error handling
    """
    try:
        if hasattr(cursor_result, 'fetchone'):
            return cursor_result.fetchone()
        else:
            return cursor_result
    except Exception as e:
        print(f"fetchone error: {e}")
        return None


def safe_fetchall(cursor_result):
    """
    Safely fetch all results with error handling
    """
    try:
        if hasattr(cursor_result, 'fetchall'):
            return cursor_result.fetchall()
        else:
            return [cursor_result] if cursor_result else []
    except Exception as e:
        print(f"fetchall error: {e}")
        return []


def execute_safe_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a query with full error handling and automatic connection management
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or list)
        fetch_one: Return single result
        fetch_all: Return all results
    
    Returns:
        Query result or None/[] on error
    """
    try:
        with get_db_connection() as conn:
            result = conn.execute(query, params)
            
            if fetch_one:
                return result.fetchone()
            elif fetch_all:
                return result.fetchall()
            else:
                return result
                
    except Exception as e:
        print(f"❌ Query execution error: {e}")
        print(f"Query: {query}")
        if params:
            print(f"Params: {params}")
        
        if fetch_one:
            return None
        elif fetch_all:
            return []
        else:
            return None


def get_safe_db_connection():
    """
    Get database connection with comprehensive error handling
    """
    try:
        return get_db_connection()
    except Exception as e:
        print(f"❌ Critical database connection error: {e}")
        print("🔄 Attempting emergency SQLite fallback...")
        
        try:
            # Emergency in-memory SQLite as absolute last resort
            import sqlite3
            conn = sqlite3.connect(':memory:')
            conn.row_factory = sqlite3.Row
            return BulletproofConnection(conn, 'sqlite')
        except Exception as fallback_error:
            print(f"❌ Even SQLite fallback failed: {fallback_error}")
            raise Exception("Complete database failure - unable to establish any connection")


def safe_function_call(func, *args, **kwargs):
    """
    Safely call a function with error handling
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"❌ Function call error in {func.__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def ensure_table_exists(table_name, create_statement):
    """
    Ensure a table exists, create if it doesn't
    """
    try:
        with get_safe_db_connection() as conn:
            # Check if table exists
            if conn.db_type == 'postgresql':
                check_query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """
            else:
                check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            
            result = conn.execute(check_query, (table_name,)).fetchone()
            
            if not result or not result[0]:
                print(f"📋 Creating missing table: {table_name}")
                conn.execute(create_statement)
                conn.commit()
                print(f"✅ Table {table_name} created successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Error ensuring table {table_name} exists: {e}")
        return False


def get_database_type():
    """
    Get the current database type being used
    """
    try:
        with get_safe_db_connection() as conn:
            return conn.db_type
    except:
        return 'sqlite'  # Default fallback 

def safe_add_column(table_name, column_name, column_definition):
    """
    Safely add a column to a table if it doesn't exist
    Works for both SQLite and PostgreSQL
    """
    try:
        with get_db_connection() as conn:
            db_type = conn.db_type
            
            # Check if column exists
            if db_type == 'postgresql':
                result = conn.execute('''
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s
                ''', (table_name, column_name)).fetchone()
            else:
                # SQLite - use PRAGMA table_info
                result = conn.execute(f'PRAGMA table_info({table_name})').fetchall()
                result = [row for row in result if row['name'] == column_name]
            
            if not result:
                # Column doesn't exist, add it
                alter_query = f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}'
                conn.execute(alter_query)
                print(f"✅ Added column {column_name} to {table_name}")
                return True
            else:
                print(f"ℹ️ Column {column_name} already exists in {table_name}")
                return False
                
    except Exception as e:
        print(f"❌ Error adding column {column_name} to {table_name}: {e}")
        return False

def ensure_achievements_table_columns():
    """
    Ensure achievements table has all required columns for compatibility
    """
    try:
        with get_db_connection() as conn:
            # Add missing columns if they don't exist
            safe_add_column('achievements', 'achievement_name', 'VARCHAR(255)')
            safe_add_column('achievements', 'description', 'TEXT')
            
            # For existing records without achievement_name/description, populate them
            conn.execute('''
                UPDATE achievements 
                SET achievement_name = achievement_type,
                    description = 'Achievement: ' || achievement_type
                WHERE achievement_name IS NULL OR achievement_name = ''
            ''')
            
            print("✅ Achievements table columns ensured")
    except Exception as e:
        print(f"❌ Error ensuring achievements table columns: {e}")

def ensure_study_list_table_columns():
    """
    Ensure study_list table has all required columns for compatibility
    """
    try:
        with get_db_connection() as conn:
            # Add language column if it doesn't exist
            safe_add_column('study_list', 'language', 'VARCHAR(100) DEFAULT \'english\'')
            
            # Update existing records to have default language
            conn.execute('''
                UPDATE study_list 
                SET language = 'english'
                WHERE language IS NULL OR language = ''
            ''')
            
            print("✅ Study list table columns ensured")
    except Exception as e:
        print(f"❌ Error ensuring study list table columns: {e}")

def ensure_all_table_compatibility():
    """
    Ensure all tables have required columns for database compatibility
    """
    ensure_achievements_table_columns()
    ensure_study_list_table_columns()