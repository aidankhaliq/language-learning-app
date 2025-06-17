"""
Database Helper Functions
These functions provide a unified interface for database operations
that work with both SQLite and PostgreSQL
"""

def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query that works with both SQLite and PostgreSQL
    
    Args:
        conn: Database connection (SQLite or PostgreSQL)
        query: SQL query string
        params: Query parameters (tuple or None)
        fetch_one: Whether to fetch one result
        fetch_all: Whether to fetch all results
    
    Returns:
        Query result or None
    """
    try:
        # Check if this is a PostgreSQL connection
        if hasattr(conn, 'cursor') and 'psycopg2' in str(type(conn)):
            # PostgreSQL
            cursor = conn.cursor()
            
            # Convert SQLite-style ? placeholders to PostgreSQL-style %s
            pg_query = query.replace('?', '%s')
            
            # Handle special SQLite syntax
            pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
            pg_query = pg_query.replace('PRAGMA busy_timeout', '-- PRAGMA busy_timeout')
            
            cursor.execute(pg_query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                if result:
                    # Convert to dict-like object for compatibility
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))
                return None
            elif fetch_all:
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in results]
                return []
            else:
                return cursor
                
        else:
            # SQLite
            cursor = conn.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor
                
    except Exception as e:
        print(f"Database query error: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        raise e

def commit_transaction(conn):
    """Commit a database transaction"""
    try:
        conn.commit()
    except Exception as e:
        print(f"Commit error: {e}")
        raise e

def handle_insert_or_replace(conn, table, columns, values, conflict_columns):
    """
    Handle INSERT OR REPLACE for both SQLite and PostgreSQL
    """
    try:
        if hasattr(conn, 'cursor') and 'psycopg2' in str(type(conn)):
            # PostgreSQL - use ON CONFLICT
            placeholders = ', '.join(['%s'] * len(values))
            conflict_cols = ', '.join(conflict_columns)
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col not in conflict_columns])
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)}) 
                VALUES ({placeholders})
                ON CONFLICT ({conflict_cols}) 
                DO UPDATE SET {update_clause}
            """
            
            cursor = conn.cursor()
            cursor.execute(query, values)
            return cursor
        else:
            # SQLite
            placeholders = ', '.join(['?'] * len(values))
            query = f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            return conn.execute(query, values)
            
    except Exception as e:
        print(f"Insert or replace error: {e}")
        raise e 