"""
seed.py
Sets up the MySQL database ALX_prodev, creates the user_data table,
and inserts data from a CSV file using a generator for efficient streaming.
"""


import mysql.connector
from mysql.connector import Error
import csv
import uuid


# function to connect to db
def connect_db():
    """Establish a connection to the MySQL database."""
    try: 
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ishmael204@sql!",
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

def create_database(connection):
    """Create the ALX_prodev if it does not already exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("Database ALX_prodev created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="ishmael204@sql!",
            database="ALX_prodev"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None
    

def create_table(connection):
    """Create the user_data if it does not exist."""
    try:
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX(user_id)
        );
        """
        cursor.execute(query)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")


def row_generator(csv_file):
    """
        Generator that yields one row at a time from a CSV file.
        Each yield returns a tuple: (uuid, name, email, age)
    """
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (
                str(uuid.uuid4()),
                row['name'],
                row['email'],
                row['age']
            )


def insert_data(connection, data_source, from_file=True):
    """Insert data from the CSV into the user_data table."""
    try:
        cursor = connection.cursor()
        query = "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
        count = 0
        if from_file:
            import csv
            with open(data_source, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                # next(reader)  # Skip header row
                for row in reader:
                    data = (
                        str(uuid.uuid4()),
                        row['name'],
                        row['email'],
                        row['age']
                    )
                    cursor.execute(query, data)
                    count += 1
        else:
            # New behaviour: insert from in-memory rows
            for row in data_source:
                cursor.execute(query, row)
                count += 1
                if count % 1000 == 0:  # Progress update every 1000 rows
                    print(f"   Inserted {count} rows...")

        connection.commit()
        print(f"Data inserted successfully ({count} rows total)")
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()


        