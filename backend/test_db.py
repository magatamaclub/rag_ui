#!/usr/bin/env python3
"""
Simple database connection test for RAG UI Backend.
"""

import sys
import psycopg2
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


def test_connection():
    """Test database connection with detailed error reporting."""
    print("🔧 Database Connection Test")
    print(f"Host: {settings.DB_HOST}")
    print(f"Port: {settings.DB_PORT}")
    print(f"Database: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")
    print()

    try:
        # Try to connect using individual parameters
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            connect_timeout=10,
        )

        print("✅ Database connection successful!")

        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        if version:
            print(f"PostgreSQL version: {version[0][:50]}...")

        # Check existing tables
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()

        if tables:
            print(f"Existing tables: {[t[0] for t in tables]}")
        else:
            print("No tables found - database initialization needed")

        cursor.close()
        conn.close()

        return True

    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
