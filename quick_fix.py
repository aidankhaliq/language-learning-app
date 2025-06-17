"""
Quick fix to add execute method to PostgreSQL connections
This allows existing code to work without major changes
"""

def patch_postgresql_connection():
    """Add execute method to PostgreSQL connections for compatibility"""
    try:
        import psycopg2.extensions
        
        def execute_method(self, query, params=None):
            """Execute method for PostgreSQL connection compatibility"""
            cursor = self.cursor()
            
            # Convert SQLite-style placeholders to PostgreSQL-style
            pg_query = query.replace('?', '%s')
            
            # Handle special SQLite syntax
            pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
            pg_query = pg_query.replace('PRAGMA busy_timeout', '-- PRAGMA busy_timeout')
            
            cursor.execute(pg_query, params or ())
            return cursor
        
        # Add the execute method to PostgreSQL connection class
        psycopg2.extensions.connection.execute = execute_method
        print("✅ PostgreSQL connection patched for compatibility")
        
    except ImportError:
        print("ℹ️ psycopg2 not available - patch not needed")
    except Exception as e:
        print(f"⚠️ Could not patch PostgreSQL connection: {e}")

# Apply the patch when this module is imported
patch_postgresql_connection() 