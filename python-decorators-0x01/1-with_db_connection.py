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


@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    print(f"Fetched user with ID {user_id}.")
    return cursor.fetchone() 

#### Fetch user by ID with automatic connection handling 
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)