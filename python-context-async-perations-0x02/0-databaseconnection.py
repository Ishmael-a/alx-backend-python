import sqlite3


class DatabaseConnection:
    """
    A class-based context manager for handling database connections.
    Automatically opens and closes database connections using the with statement.
    """
    
    def __init__(self, db_name):
        """
        Initialize the DatabaseConnection with a database name.
        
        Args:
            db_name: The name/path of the SQLite database file
        """
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        Opens the database connection.
        
        Returns:
            The database connection object
        """
        self.connection = sqlite3.connect(self.db_name)
        print("Database connection opened.")
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.
        Closes the database connection.
        
        Args:
            exc_type: The exception type (if any)
            exc_value: The exception value (if any)
            traceback: The traceback object (if any)
        """
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
        
        # Return False to propagate exceptions, True to suppress them
        return False
    

if __name__ == "__main__":
    # Use the DatabaseConnection context manager
    with DatabaseConnection('users.db') as conn:
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute("SELECT * FROM users")
        
        # Fetch and print all results
        results = cursor.fetchall()
        
        print("\nQuery Results:")
        print("-" * 50)
        for row in results:
            print(row)
        
        # Close the cursor
        cursor.close()