# Python Generators - 0x00

## Project Overview

This project focuses on using Python generators to efficiently handle large datasets from a MySQL database. Generators allow for memory-efficient data processing by yielding data one item at a time instead of loading entire datasets into memory.


## Project Structure

```
python-generators-0x00/
├── README.md
├── seed.py
├── user_data.csv
├── 0-stream_users.py
├── 1-batch_processing.py
├── 2-lazy_paginate.py
└── 4-stream_ages.py
```

## Database Setup

The project uses a MySQL database called `ALX_prodev` with a table `user_data` containing:
- `user_id` (Primary Key, UUID, Indexed)
- `name` (VARCHAR, NOT NULL)
- `email` (VARCHAR, NOT NULL)
- `age` (DECIMAL, NOT NULL)

## Tasks

### 0. Getting Started with Python Generators
**File:** `seed.py`

Set up the MySQL database and seed it with sample data.

**Functions:**
- `connect_db()` - Connects to the MySQL database server
- `create_database(connection)` - Creates the database ALX_prodev if it doesn't exist
- `connect_to_prodev()` - Connects to the ALX_prodev database
- `create_table(connection)` - Creates the user_data table if it doesn't exist
- `insert_data(connection, data)` - Inserts data from CSV file

**Usage:**
```bash
./0-main.py
```

---

### 1. Generator That Streams Rows from SQL Database
**File:** `0-stream_users.py`

Create a generator function that streams rows from the database one by one.

**Prototype:**
```python
def stream_users()
```

**Features:**
- Uses `yield` to stream data
- Memory-efficient (doesn't load entire dataset)
- Proper connection and cursor management
- Only uses 1 loop

**Usage:**
```bash
./1-main.py
```

**Example Output:**
```python
{'user_id': '00234e50-...', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-...', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
```

---

### 2. Batch Processing Large Data
**File:** `1-batch_processing.py`

Fetch and process data in batches to filter users over the age of 25.

**Prototypes:**
```python
def stream_users_in_batches(batch_size)
def batch_processing(batch_size)
```

**Features:**
- Processes data in configurable batch sizes
- Filters users with age > 25
- Uses no more than 3 loops
- Memory-efficient batch processing

**Usage:**
```bash
./2-main.py | head -n 5
```

**Example Output:**
```python
{'user_id': '00234e50-...', 'name': 'Dan Altenwerth Jr.', 'email': 'Molly59@gmail.com', 'age': 67}
{'user_id': '006bfede-...', 'name': 'Glenda Wisozk', 'email': 'Miriam21@gmail.com', 'age': 119}
...
```

---

### 3. Lazy Loading Paginated Data
**File:** `2-lazy_paginate.py`

Simulate fetching paginated data using lazy loading - only fetch the next page when needed.

**Prototypes:**
```python
def paginate_users(page_size, offset)
def lazy_paginate(page_size)
```

**Features:**
- Lazy evaluation - pages loaded only when needed
- Uses LIMIT and OFFSET for pagination
- Only uses 1 loop
- Memory-efficient pagination

**Usage:**
```bash
python 3-main.py | head -n 7
```

---

### 4. Memory-Efficient Aggregation with Generators
**File:** `4-stream_ages.py`

Calculate the average age of users without loading the entire dataset into memory.

**Features:**
- Streams ages one at a time using generators
- Calculates average without SQL AVERAGE function
- Uses no more than 2 loops
- Memory-efficient aggregation

**Usage:**
```bash
./4-main.py
```

**Example Output:**
```
Average age of users: 65.4
```

---

## Key Concepts

### What are Generators?
Generators are functions that return an iterator that yields items one at a time. They use the `yield` keyword instead of `return`.

**Benefits:**
- Memory efficient - generate items on-the-fly
- Lazy evaluation - compute values only when needed
- Can represent infinite sequences
- Better performance for large datasets



### Why Use Generators for Database Operations?

1. **Memory Efficiency**: Don't load entire dataset into memory
2. **Performance**: Start processing data immediately
3. **Scalability**: Handle datasets larger than available RAM
4. **Resource Management**: Better control over database connections

## Best Practices

1. **Always close database connections** in a `finally` block
2. **Use `dictionary=True`** for readable cursor results
3. **Handle exceptions** properly to avoid resource leaks
4. **Use generators** for large datasets to save memory
5. **Process in batches** for balance between memory and performance
6. **Implement pagination** for user-facing applications

## Common Pitfalls

1. **Unread results error**: Occurs when generator is not fully consumed
2. **Memory leaks**: Forgetting to close cursors and connections
3. **Buffered cursors**: Using `buffered=True` loads all results into memory
4. **Type errors**: Forgetting `dictionary=True` returns tuples, not dicts

## Testing

Each task includes a main file for testing:
- `0-main.py` - Tests database setup
- `1-main.py` - Tests streaming users
- `2-main.py` - Tests batch processing
- `3-main.py` - Tests lazy pagination
- `4-main.py` - Tests age aggregation

Run tests with:
```bash
./X-main.py
```

Or with output limiting:
```bash
./X-main.py | head -n 10
```