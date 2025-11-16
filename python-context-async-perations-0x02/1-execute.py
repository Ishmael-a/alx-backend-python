import sqlite3


class ExecuteQuery:
    """
    A reusable context manager that handles database connection,
    query execution, and automatic cleanup.
    """
    
    def __init__(self, db_name, query, params=None):
        """
        Initialize the ExecuteQuery context manager.
        
        Args:
            db_name: The name/path of the SQLite database file
            query: The SQL query to execute
            params: Optional parameters for the query (tuple or list)
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager - opens connection and executes query.
        
        Returns:
            The query results
        """
        # Open database connection
        self.connection = sqlite3.connect(self.db_name)
        print(f"Database connection to '{self.db_name}' opened")
        
        # Create cursor
        self.cursor = self.connection.cursor()
        
        # Execute the query with parameters
        self.cursor.execute(self.query, self.params)
        print(f"Query executed: {self.query}")
        print(f"Parameters: {self.params}")
        
        # Fetch all results
        self.results = self.cursor.fetchall()
        
        # Return the results
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager - closes cursor and connection.
        
        Args:
            exc_type: Exception type (if any exception occurred)
            exc_val: Exception value (if any exception occurred)
            exc_tb: Exception traceback (if any exception occurred)
            
        Returns:
            False to propagate any exceptions that occurred
        """
        # Close cursor if it exists
        if self.cursor:
            self.cursor.close()
            print("Cursor closed")
        
        # Close connection if it exists
        if self.connection:
            self.connection.close()
            print(f"Database connection to '{self.db_name}' closed")
        
        # Return False to propagate exceptions
        return False


# Using the ExecuteQuery context manager
if __name__ == "__main__":
    # Query to find users older than 25
    query = "SELECT * FROM users WHERE age > ?"
    
    # Use the context manager
    with ExecuteQuery('users.db', query, (25,)) as results:
        print("\nQuery Results:")
        print("-" * 70)
        print(f"Found {len(results)} user(s) with age > 25:")
        print("-" * 70)
        
        for row in results:
            print(row)
