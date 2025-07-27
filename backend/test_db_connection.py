#!/usr/bin/env python3
"""
Database connection test script
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.config import settings
from urllib.parse import quote_plus
import psycopg2


def test_database_connection():
    """Test database connection with detailed error reporting"""
    print("🔍 Testing database connection...")
    print(f"   Host: {settings.DB_HOST}")
    print(f"   Port: {settings.DB_PORT}")
    print(f"   Database: {settings.DB_NAME}")
    print(f"   User: {settings.DB_USER}")
    print(f"   Password: {'*' * len(settings.DB_PASSWORD)}")

    # Test the constructed URL
    print(f"\n📝 Database URL: {settings.DATABASE_URL}")

    try:
        # Try direct psycopg2 connection
        print("\n🔌 Testing direct psycopg2 connection...")
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
        )
        print("✅ Direct connection successful!")

        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL version: {version[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Direct connection failed: {e}")

        # Try with different connection parameters
        print("\n🔄 Trying alternative connection methods...")

        # Try with URL encoded password
        try:
            encoded_password = quote_plus(settings.DB_PASSWORD)
            print("🔐 Trying with URL-encoded password...")
            conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=encoded_password,
            )
            print("✅ Connection with encoded password successful!")
            conn.close()
        except Exception as e2:
            print(f"❌ Encoded password connection failed: {e2}")

        # Try with connection string
        try:
            print("🔗 Trying with connection string...")
            conn_string = f"host={settings.DB_HOST} port={settings.DB_PORT} dbname={settings.DB_NAME} user={settings.DB_USER} password={settings.DB_PASSWORD}"
            conn = psycopg2.connect(conn_string)
            print("✅ Connection string method successful!")
            conn.close()
        except Exception as e3:
            print(f"❌ Connection string method failed: {e3}")


if __name__ == "__main__":
    test_database_connection()
