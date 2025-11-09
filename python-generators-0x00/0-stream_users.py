import seed
from mysql.connector import Error

def stream_users():
    """
    Generator function that connects to the ALX_prodev MySQL database
    and streams user records one by one from the user_data table.
    """

    connection = None
    db_cursor = None

    try:
        connection = seed.connect_to_prodev()
        if connection.is_connected():
            db_cursor = connection.cursor(dictionary=True, buffered=False)

            db_cursor.execute("SELECT * FROM user_data")

            # yield each row as a dictionary
            for row in db_cursor:
                yield row
    except Error as e:
        print(f"Database error: {e}")
    finally:
        # if db_cursor is not None:
        #     db_cursor.close()
         # Close cursor first if it exists
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
    