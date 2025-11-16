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

def transactional(func):
    """
    Decorator that manages database transactions.
    Automatically commits on success or rolls back on error.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function with automatic transaction handling
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            conn.commit()
            print("Transaction committed successfully")

            return func(conn, *args, **kwargs)
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise

    return wrapper


# - Decorators are applied bottom-up
#  - `@transactional` is applied first (receives the connection)
#   - `@with_db_connection` is applied second (manages the connection)

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    print(f"Fetched user with ID {user_id}.")
    user = cursor.fetchone() 
    print(user)

#### Update user's email with automatic transaction handling 
if __name__ == "__main__":
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')