"""
Quick fix to add execute method to PostgreSQL connections
This allows existing code to work without major changes
"""

def patch_postgresql_connection():
    """Add execute method to PostgreSQL connections for compatibility"""
    try:
        import psycopg2.extensions
        import psycopg2.extras
        
        # Don't patch if already patched
        if hasattr(psycopg2.extensions.connection, '_execute_patched'):
            return
        
        # Store original methods if they exist
        original_methods = {}
        
        # Create a custom cursor class that returns dict-like results
        class PostgreSQLCursor:
            def __init__(self, connection, query, params):
                self.connection = connection
                self.cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                
                # Convert SQLite-style placeholders to PostgreSQL-style
                pg_query = query.replace('?', '%s')
                
                # Handle special SQLite syntax
                pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
                pg_query = pg_query.replace('PRAGMA busy_timeout', '-- PRAGMA busy_timeout')
                
                # Handle SQLite-specific queries
                if 'sqlite_master' in pg_query:
                    pg_query = pg_query.replace('sqlite_master', 'information_schema.tables')
                    pg_query = pg_query.replace("name FROM information_schema.tables WHERE type='table'", 
                                              "table_name FROM information_schema.tables WHERE table_schema='public'")
                
                try:
                    self.cursor.execute(pg_query, params or ())
                except Exception as e:
                    print(f"Query execution error: {e}")
                    print(f"Original Query: {query}")
                    print(f"Converted Query: {pg_query}")
                    print(f"Params: {params}")
                    raise e
            
            def fetchone(self):
                """Fetch one result"""
                result = self.cursor.fetchone()
                return dict(result) if result else None
            
            def fetchall(self):
                """Fetch all results"""
                results = self.cursor.fetchall()
                return [dict(result) for result in results] if results else []
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.cursor.close()
        
        def execute_method(self, query, params=None):
            """Execute method for PostgreSQL connection compatibility"""
            return PostgreSQLCursor(self, query, params)
        
        def commit_method(self):
            """Commit method that handles both SQLite and PostgreSQL"""
            try:
                return self._original_commit()
            except Exception as e:
                print(f"Commit error: {e}")
                raise e
        
        # Store original commit method if it exists
        if hasattr(psycopg2.extensions.connection, 'commit'):
            psycopg2.extensions.connection._original_commit = psycopg2.extensions.connection.commit
            psycopg2.extensions.connection.commit = commit_method
        
        # Add the execute method to PostgreSQL connection class
        psycopg2.extensions.connection.execute = execute_method
        psycopg2.extensions.connection._execute_patched = True
        
        print("✅ PostgreSQL connection patched for compatibility")
        
    except ImportError:
        print("ℹ️ psycopg2 not available - patch not needed")
    except Exception as e:
        print(f"⚠️ Could not patch PostgreSQL connection: {e}")
        import traceback
        print(f"⚠️ Traceback: {traceback.format_exc()}")

# Apply the patch when this module is imported
if __name__ != '__main__':
    patch_postgresql_connection()
else:
    print("Quick fix module loaded directly - not applying patch") 