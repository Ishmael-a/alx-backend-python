import time
import sqlite3 
import functools


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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function if it fails due to exceptions.
    
    Args:
        retries: Number of times to retry the function (default: 3)
        delay: Delay in seconds between retries (default: 2)
        
    Returns:
        The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt < retries:
                try:
                    if attempt > 0:
                        print(f"Success on attempt {attempt + 1}")

                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    if attempt < retries:
                        print(f"Attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"Attempt {attempt} failed: {e}. No more retries left.")

            raise last_exception
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)