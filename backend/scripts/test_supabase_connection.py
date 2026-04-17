#!/usr/bin/env python3
"""
Test script to verify Supabase database connection.
Run this before starting the backend server.
"""

import os
import sys
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    """Test database connection to Supabase."""

    database_url = os.getenv("DATABASE_URL")

    print("=" * 60)
    print("SUPABASE DATABASE CONNECTION TEST")
    print("=" * 60)

    # Mask the password in the URL for display
    if "@" in database_url:
        parts = database_url.split("@")
        user_part = parts[0].split("://")[1]
        masked_user = user_part.split(":")[0] + ":***@"
        masked_url = parts[0].split("://")[0] + "://" + masked_user + parts[1]
        print(f"\n📡 Database URL: {masked_url}")
    else:
        print(f"\n📡 Database URL: {database_url}")

    print(f"\n🔍 Testing connection...")

    try:
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )

        # Create session factory
        async_session_maker = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Test connection
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()

            print(f"✅ Connected successfully!")
            print(f"\n📊 PostgreSQL Version:")
            print(f"   {version[:100]}...")

            # Test table count
            result = await session.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """))
            table_count = result.scalar()
            print(f"\n📋 Public Tables: {table_count}")

            # List tables
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"\n📁 Available Tables:")
                for table in tables:
                    print(f"   - {table}")

        # Dispose engine
        await engine.dispose()

        print("\n" + "=" * 60)
        print("✅ CONNECTION TEST PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {type(e).__name__}: {e}")
        print("\n" + "=" * 60)
        print("❌ CONNECTION TEST FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_supabase_connection())
    sys.exit(0 if success else 1)
