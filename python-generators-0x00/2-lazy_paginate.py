import seed

def paginate_users(page_size, offset):
    """Fetch a single page of users."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily loads paginated data from the users database.
    Fetches one page at a time, yielding each page only when needed.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break  # stop when no more data
        yield page  # yield the current page of users
        offset += page_size  # move to the next page
