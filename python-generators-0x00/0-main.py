import io
import uuid
import requests
import csv
import seed


S3_CSV_URL = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20251108%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20251108T151347Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=3f0211852ae27097f5d0fa84cc133796a513bc923344d0d8ac7655627d286b08"

def fetch_csv_from_url(url):
    """Fetch and return CSV content from a public S3 link."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_content = response.text
        print("CSV file fetched successfully from url.")
        return io.StringIO(csv_content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CSV file: {e}")
        return None
    
def csv_row_generator(csv_buffer):
    """
    Generator that yields one row at a time from CSV buffer.
    Each yield returns a tuple: (uuid, name, email, age)
    """
    reader = csv.DictReader(csv_buffer)
    for row in reader:
        yield (
            str(uuid.uuid4()),
            row['name'],
            row['email'],
            row['age']
        )

if __name__ == "__main__":
    # Step 1: Connect to MySQL server and create database
    connection = seed.connect_db()
    if connection:
        seed.create_database(connection)
        connection.close()
        print("Database created successfully")

        # Step 2: Connect to ALX_prodev DB
        connection = seed.connect_to_prodev()
        if connection:
            seed.create_table(connection)

            # Step 3: Fetch CSV directly from the S3 link and insert into DB
            csv_buffer = fetch_csv_from_url(S3_CSV_URL)
            if csv_buffer:
                # Create generator for efficient streaming
                row_gen = csv_row_generator(csv_buffer)
                
                # Convert to list to count rows (or keep as generator for true streaming)
                # rows = list(row_gen)
                # print(f"📦 Inserting {len(rows)} records into DB...")

                print(f"📦 Inserting records into DB (streaming)...")
                
                seed.insert_data(connection, row_gen, from_file=False)
                print("✅ Data insertion completed")

                # Verification: Check if DB and table are populated
                cursor = connection.cursor()
                cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
                result = cursor.fetchone()
                if result:
                    print("✅ Database ALX_prodev is present")

                cursor.execute("SELECT * FROM user_data LIMIT 5;")
                rows = cursor.fetchall()
                print("📊 Sample rows:", rows)

                cursor.close()
                connection.close()
            else:
                print("❌ Failed to fetch CSV data")
                connection.close()
        else:
            print("❌ Failed to connect to ALX_prodev database")
    else:
        print("❌ Failed to connect to MySQL server")
