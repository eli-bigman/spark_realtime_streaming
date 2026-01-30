import pytest
import psycopg2
import time
import os
from config.settings import settings

@pytest.fixture(scope="module")
def db_connection():
    """Establish a connection to the Postgres database."""
    # Retry logic to wait for DB to be ready
    retries = 10
    conn = None
    while retries > 0:
        try:
            conn = psycopg2.connect(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                dbname=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT
            )
            break
        except Exception as e:
            print(f"Waiting for DB... {e}")
            time.sleep(2)
            retries -= 1
            
    if not conn:
        pytest.fail("Could not connect to Postgres DB")
        
    yield conn
    conn.close()

def test_postgres_connection(db_connection):
    """TC-02: Verify Database connection and schema."""
    cur = db_connection.cursor()
    cur.execute("SELECT 1;")
    assert cur.fetchone()[0] == 1
    cur.close()

def test_table_existence(db_connection):
    """TC-02: Verify 'ecommerce_events' table exists."""
    cur = db_connection.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'ecommerce_events'
        );
    """)
    exists = cur.fetchone()[0]
    cur.close()
    assert exists, "Table 'ecommerce_events' does not exist"

def test_data_ingestion(db_connection):
    """TC-04: Verify data is being ingested into Postgres."""
    cur = db_connection.cursor()
    
    # Wait for data to arrive (timeout 60s)
    timeout = 60
    start_time = time.time()
    row_count = 0
    
    while time.time() - start_time < timeout:
        cur.execute("SELECT count(*) FROM ecommerce_events;")
        row_count = cur.fetchone()[0]
        if row_count > 0:
            break
        time.sleep(5)
        
    assert row_count > 0, "No data found in 'ecommerce_events' table after 60 seconds"
    print(f"Verified ingestion: Found {row_count} rows.")
    cur.close()
