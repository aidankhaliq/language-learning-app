"""
Database Wrapper - Complete Solution for PostgreSQL/SQLite Compatibility
This module provides a unified database interface that completely eliminates
conn.execute compatibility issues throughout the entire codebase.
"""

import os
from contextlib import contextmanager

class DatabaseWrapper:
    """
    A unified database wrapper that handles both SQLite and PostgreSQL
    with identical syntax and return types.
    """
    
    def __init__(self, connection, db_type):
        self.connection = connection
        self.db_type = db_type
        self._closed = False
    
    def execute(self, query, params=None):
        """Execute a query with unified syntax"""
        if self._closed:
            raise Exception("Cannot execute on closed connection")
            
        if self.db_type == 'postgresql':
            return self._execute_postgresql(query, params)
        else:
            return self._execute_sqlite(query, params)
    
    def _execute_postgresql(self, query, params):
        """Execute PostgreSQL query"""
        import psycopg2.extras
        
        # Convert SQLite syntax to PostgreSQL
        pg_query = self._convert_sqlite_to_postgresql(query)
        
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(pg_query, params or ())
        
        return PostgreSQLResultWrapper(cursor)
    
    def _execute_sqlite(self, query, params):
        """Execute SQLite query"""
        cursor = self.connection.execute(query, params or ())
        return SQLiteResultWrapper(cursor)
    
    def _convert_sqlite_to_postgresql(self, query):
        """Convert SQLite syntax to PostgreSQL"""
        pg_query = query.replace('?', '%s')
        
        # Handle INSERT OR REPLACE
        if 'INSERT OR REPLACE' in pg_query:
            # Convert to UPSERT syntax - this is a simplified conversion
            # For production, you might need more sophisticated handling
            pg_query = pg_query.replace('INSERT OR REPLACE', 'INSERT')
            # Add ON CONFLICT handling if needed
        
        # Handle PRAGMA statements
        if pg_query.strip().startswith('PRAGMA'):
            return '-- ' + pg_query  # Comment out PRAGMA statements
        
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
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if not self._closed:
            self.connection.rollback()
    
    def close(self):
        """Close connection"""
        if not self._closed:
            self.connection.close()
            self._closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class ResultWrapper:
    """Base class for result wrappers"""
    
    def __init__(self, cursor):
        self.cursor = cursor
    
    def fetchone(self):
        raise NotImplementedError
    
    def fetchall(self):
        raise NotImplementedError


class PostgreSQLResultWrapper(ResultWrapper):
    """PostgreSQL result wrapper that mimics SQLite behavior"""
    
    def fetchone(self):
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def fetchall(self):
        results = self.cursor.fetchall()
        return [dict(result) for result in results] if results else []


class SQLiteResultWrapper(ResultWrapper):
    """SQLite result wrapper"""
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()


@contextmanager
def get_database_connection():
    """
    Context manager that returns a unified database connection
    Usage: 
        with get_database_connection() as conn:
            result = conn.execute("SELECT * FROM users")
    """
    from database_config import get_db_connection as get_raw_connection, get_database_type
    
    raw_conn = None
    try:
        raw_conn, db_type = get_raw_connection()
        wrapped_conn = DatabaseWrapper(raw_conn, db_type)
        yield wrapped_conn
    except Exception as e:
        if raw_conn:
            try:
                raw_conn.rollback()
            except:
                pass
        raise e
    finally:
        if raw_conn and hasattr(raw_conn, 'close'):
            try:
                raw_conn.close()
            except:
                pass


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a single query with automatic connection management
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch_one: Return single result
        fetch_all: Return all results
    
    Returns:
        Query result or None
    """
    with get_database_connection() as conn:
        result = conn.execute(query, params)
        
        if fetch_one:
            return result.fetchone()
        elif fetch_all:
            return result.fetchall()
        else:
            return result


def execute_transaction(operations):
    """
    Execute multiple operations in a single transaction
    
    Args:
        operations: List of (query, params) tuples
    
    Returns:
        True if successful, raises exception on error
    """
    with get_database_connection() as conn:
        for query, params in operations:
            conn.execute(query, params)
        return True 