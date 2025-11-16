import time
import sqlite3 
import functools


query_cache = {}

def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with automatic connection handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connection = sqlite3.connect('users.db')
        print("Database connection opened.")
        try:
            return func(connection, *args, **kwargs)
        finally:
            connection.close()
            print("Database connection closed.")

    return wrapper



def cache_query(func):
    """
    Decorator that caches the results of database queries based on the SQL query string.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with query caching
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'query' in kwargs:
            query = kwargs['query']
        elif args:
            query = args[0]
        else:
            return func(*args, **kwargs)
        
        if query in query_cache:
            print("Fetching result from cache.")
            return query_cache[query]
        
        result = func(*args, **kwargs)
        print("Caching result of the query.")
        query_cache[query] = result
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")