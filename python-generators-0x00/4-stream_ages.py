import seed
from mysql.connector import Error

def stream_user_ages(): 
    """
    Generator that streams user ages one by one from the database.
    Fetches rows lazily to avoid loading the entire dataset into memory.
    """
    connection = None
    db_cursor = None
    try:
        connection = seed.connect_to_prodev()
        cursor = connection.cursor(dictionary=True, buffered=False)
        cursor.execute("SELECT age FROM user_data")

        for row in cursor:
            yield row['age']

    except Error as e:
        print(f"Database error streaming user ages: {e}")
    finally:
        if db_cursor is not None:
            try:
                db_cursor.close()
            except Error:
                # Ignore errors from unread results during cursor close
                pass
        
        # Close connection without checking is_connected()
        if connection is not None:
            try:
                connection.close()
            except Error:
                # Ignore any errors during connection close
                pass

            
    

