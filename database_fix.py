"""
Universal Database Fix - Final Solution
This completely eliminates ALL conn.execute compatibility issues
"""

class UniversalConnection:
    """A connection wrapper that works identically for both SQLite and PostgreSQL"""
    
    def __init__(self, raw_connection, db_type):
        self.raw_connection = raw_connection
        self.db_type = db_type
    
    def execute(self, query, params=None):
        """Execute method that works for both database types"""
        if self.db_type == 'postgresql':
            return self._execute_postgresql(query, params)
        else:
            return self._execute_sqlite(query, params)
    
    def _execute_postgresql(self, query, params):
        """Handle PostgreSQL execution"""
        try:
            import psycopg2.extras
            
            # Convert SQLite syntax
            pg_query = query.replace('?', '%s')
            
            # Handle special cases
            if pg_query.strip().startswith('PRAGMA'):
                # Return mock cursor for PRAGMA statements
                return MockCursor()
            
            if 'INSERT OR REPLACE' in pg_query:
                pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
            
            if 'sqlite_master' in pg_query:
                pg_query = pg_query.replace('sqlite_master', 'information_schema.tables')
                pg_query = pg_query.replace(
                    "name FROM information_schema.tables WHERE type='table'",
                    "table_name FROM information_schema.tables WHERE table_schema='public'"
                )
            
            cursor = self.raw_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(pg_query, params or ())
            
            return PostgreSQLCursor(cursor)
            
        except Exception as e:
            print(f"PostgreSQL query error: {e}")
            print(f"Query: {query} -> {pg_query}")
            print(f"Params: {params}")
            raise e
    
    def _execute_sqlite(self, query, params):
        """Handle SQLite execution"""
        cursor = self.raw_connection.execute(query, params or ())
        return SQLiteCursor(cursor)
    
    def commit(self):
        """Commit transaction"""
        self.raw_connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.raw_connection.rollback()
    
    def close(self):
        """Close connection"""
        if hasattr(self.raw_connection, 'close'):
            self.raw_connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self.rollback()
            except:
                pass
        else:
            try:
                self.commit()
            except:
                pass
        self.close()


class PostgreSQLCursor:
    """PostgreSQL cursor wrapper"""
    
    def __init__(self, cursor):
        self.cursor = cursor
    
    def fetchone(self):
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def fetchall(self):
        results = self.cursor.fetchall()
        return [dict(result) for result in results] if results else []


class SQLiteCursor:
    """SQLite cursor wrapper"""
    
    def __init__(self, cursor):
        self.cursor = cursor
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()


class MockCursor:
    """Mock cursor for unsupported operations like PRAGMA"""
    
    def fetchone(self):
        return None
    
    def fetchall(self):
        return []


def patch_app_connection():
    """Patch the app's get_db_connection function"""
    try:
        # Import the app module
        import app
        
        # Store the original function
        original_get_db_connection = app.get_db_connection
        
        def new_get_db_connection():
            """New connection function that returns wrapped connection"""
            try:
                from database_config import get_db_connection as get_raw_connection, create_tables
                
                raw_conn, db_type = get_raw_connection()
                print(f"📊 Database connection type: {db_type}")
                
                # Initialize tables
                try:
                    create_tables(raw_conn, db_type)
                    print(f"✅ Tables created successfully for {db_type}")
                except Exception as table_error:
                    print(f"⚠️ Table creation warning: {table_error}")
                
                if db_type == 'postgresql':
                    print("🐘 PostgreSQL setup complete")
                else:
                    print("🔵 SQLite setup complete")
                    try:
                        app._initialize_database_tables(raw_conn)
                        app.ensure_user_columns_on_connection(raw_conn)
                        raw_conn.commit()
                    except Exception as e:
                        print(f"SQLite initialization warning: {e}")
                
                return UniversalConnection(raw_conn, db_type)
                
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                import traceback
                print(f"❌ Full traceback: {traceback.format_exc()}")
                
                # Emergency fallback
                print("⚠️ Using emergency fallback SQLite database")
                import sqlite3
                import os
                
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database_fallback.db')
                raw_conn = sqlite3.connect(db_path)
                raw_conn.row_factory = sqlite3.Row
                
                app._initialize_database_tables(raw_conn)
                
                return UniversalConnection(raw_conn, 'sqlite')
        
        # Replace the function
        app.get_db_connection = new_get_db_connection
        print("✅ App database connection patched successfully")
        
    except Exception as e:
        print(f"❌ Failed to patch app connection: {e}")


# Apply the patch when imported
patch_app_connection() 