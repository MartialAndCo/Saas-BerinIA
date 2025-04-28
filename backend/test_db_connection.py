import psycopg2
from app.core.config import settings
import re

def test_connection():
    try:
        # Parse the database URL
        url = settings.DATABASE_URL
        print(f"Original URL: {url}")
        
        # Use regex to parse the URL more reliably
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)', url)
        if not match:
            print(f"Failed to parse URL: {url}")
            return
        
        username = match.group(1)
        password = match.group(2)
        host = match.group(3)
        port = match.group(4) or '5432'
        database = match.group(5)
        
        if '?' in database:
            database = database.split('?')[0]
        
        print(f"Connecting to: host={host}, port={port}, dbname={database}, user={username}")
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=password
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a simple query
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print(f"Query result: {result}")
        
        # List all tables in the database
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        print("Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Try to create a test table
        cur.execute("CREATE TABLE IF NOT EXISTS test_table (id serial PRIMARY KEY, name varchar);")
        conn.commit()
        print("Test table created successfully")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        print("Database connection test successful!")
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    test_connection() 