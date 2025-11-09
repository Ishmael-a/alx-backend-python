
import seed 
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows in batches from the user_data table.
    
    Args:
        batch_size: Number of rows to fetch per batch
        
    Yields:
        List of user dictionaries for each batch
    """
    connection = None
    db_cursor = None

    try:
        connection = seed.connect_to_prodev()
        if connection.is_connected():
            db_cursor = connection.cursor(dictionary=True, buffered=False)
            db_cursor.execute("SELECT * FROM user_data")

            batch = []
            for row in db_cursor:
                batch.append(row)
                if len(batch) == batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if db_cursor is not None:
            try:
                db_cursor.close()
            except Error:
                pass
        
        if connection is not None:
            try:
                connection.close()
            except Error:
                pass



def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size: Number of rows to process per batch
    """
    for batch in stream_users_in_batches(batch_size):
        # for each batch is a user in a batch is over the age of 25
        for user in batch:
            if user['age'] > 25:
                print(user)