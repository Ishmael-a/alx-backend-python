import sqlite3
import functools
from datetime import datetime
# import sys, os
import os


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.join(BASE_DIR, "python-generators-0x00"))
# from seed import connect_to_prodev

def init_database():
    """Initialize the database with a users table if it doesn't exist."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Drop users table if it exists
    # cursor.execute('DROP TABLE IF EXISTS users')
    # print("Dropped existing users table (if it existed).")
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if table is empty and add sample data
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert sample users
        sample_users = [
            ("Alice Johnson", "alice@example.com", 28),
            ("Bob Smith", "bob@example.com", 35),
            ("Charlie Brown", "charlie@example.com", 42),
            ("Diana Prince", "diana@example.com", 30),
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            sample_users
        )
        print("Sample users inserted into database.")
    
    conn.commit()
    conn.close()

#### decorator to lof SQL queries
def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function that logs queries before execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'query' in kwargs:
            query = kwargs['query']
        elif args:
            query = args[0]
        else:
            query = "No query provided"

        # Log the query with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Executing SQL Query: {query}")

        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    # conn = connect_to_prodev()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
if __name__ == "__main__":
    init_database()

    users = fetch_all_users(query="SELECT * FROM users")
    print(users)