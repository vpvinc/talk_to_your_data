"""
Simple database connection test
"""
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv


def test_database_connection():
    """Test connection to PostgreSQL database"""
    
    # Load .env from project root
    env_file = Path(__file__).parent.parent / ".env"
    load_dotenv(env_file)
    
    # Get credentials
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")
    
    # Connect
    conn = psycopg2.connect(
        host=db_host,
        port=int(db_port),
        database=db_name,
        user=db_user,
        password=db_pass,
        connect_timeout=10
    )
    
    # Test with a simple query
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        result = cur.fetchone()
    
    conn.close()
    
    assert result == (1,), "Database connection test failed"


if __name__ == "__main__":
    test_database_connection()
    print("✓ Database connection successful!")
