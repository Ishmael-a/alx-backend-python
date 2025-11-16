import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        List of all user records
    """
    async with aiosqlite.connect('users.db') as conn:
        async with conn.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print(f"async_fetch_users: Fetched {len(results)} users")
            return results
        

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        List of user records where age > 40
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print(f"async_fetch_older_users: Fetched {len(results)} users older than 40")
            return results
        

async def fetch_concurrently():
    """
    Execute both database queries concurrently using asyncio.gather.
    
    Returns:
        Tuple containing results from both queries (all_users, older_users)
    """
    print("Starting concurrent database queries...\n")
    
    # Execute both queries concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    print("\n" + "="*70)
    print("Concurrent queries completed!")
    print("="*70)
    
    # Display results
    print(f"\nTotal users fetched: {len(all_users)}")
    print(f"Users older than 40: {len(older_users)}")
    
    print("\n--- All Users ---")
    for user in all_users:
        print(user)
    
    print("\n--- Users Older Than 40 ---")
    for user in older_users:
        print(user)
    
    return all_users, older_users


# Run the concurrent fetch
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())