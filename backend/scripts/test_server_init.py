#!/usr/bin/env python3
"""
Diagnostic script to trace database connection timeout issues.
This mimics exactly how the server initializes connections.
"""

import os
import sys
import asyncio
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.core.config import settings
from app.core.database import db_manager
from sqlalchemy import text

# Load environment variables
load_dotenv()

async def test_server_initialization():
    """
    Test the exact initialization path that the server uses.
    This should reveal where the timeout occurs.
    """

    print("=" * 70)
    print("DATABASE CONNECTION DIAGNOSTIC - SERVER INITIALIZATION PATH")
    print("=" * 70)

    # Show the database URL (masked)
    database_url = settings.DATABASE_URL
    if "@" in database_url:
        parts = database_url.split("@")
        user_part = parts[0].split("://")[1]
        masked_user = user_part.split(":")[0] + ":***@"
        masked_url = parts[0].split("://")[0] + "://" + masked_user + parts[1]
        print(f"\n📡 Database URL: {masked_url}")
    else:
        print(f"\n📡 Database URL: {database_url}")

    print(f"\n📋 Configuration:")
    print(f"   USE_DATABASE: {settings.USE_DATABASE}")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   Pool size: 3 (was 5)")
    print(f"   Max overflow: 2 (was 10)")
    print(f"   Connection timeout: 60s (was 30s)")
    print(f"   Pool recycle: 1200s (20 minutes)")

    # Test 1: Lifespan initialization path
    print(f"\n{'='*70}")
    print("TEST 1: Lifespan Manager Initialization Path")
    print(f"{'='*70}")
    print("This mimics: db_manager.init_engine(echo=settings.is_development)")

    try:
        start_time = time.time()
        engine = db_manager.init_engine(echo=settings.is_development)
        elapsed = time.time() - start_time
        print(f"✅ Engine created in {elapsed:.2f} seconds")
        print(f"   Engine class: {type(engine).__name__}")
        print(f"   Pool class: {type(engine.pool).__name__}")
    except Exception as e:
        print(f"❌ FAILED to create engine: {type(e).__name__}: {e}")
        return False

    # Test 2: Session creation via db_manager.get_session()
    print(f"\n{'='*70}")
    print("TEST 2: Session Creation via db_manager.get_session()")
    print(f"{'='*70}")
    print("This mimics: async with db_manager.get_session() as db:")

    try:
        start_time = time.time()
        async with db_manager.get_session() as db:
            elapsed = time.time() - start_time
            print(f"✅ Session created in {elapsed:.2f} seconds")

            # Try to execute a query
            start_time = time.time()
            result = await db.execute(text("SELECT 1"))
            elapsed = time.time() - start_time
            print(f"✅ Query executed in {elapsed:.2f} seconds")
            print(f"   Result: {result.scalar()}")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        print(f"\n📋 Full traceback:")
        traceback.print_exc()
        return False

    # Test 3: Multiple rapid connections (pooler stress test)
    print(f"\n{'='*70}")
    print("TEST 3: Multiple Rapid Connections (Pooler Stress)")
    print(f"{'='*70}")

    try:
        for i in range(5):
            start_time = time.time()
            async with db_manager.get_session() as db:
                result = await db.execute(text("SELECT 1"))
            elapsed = time.time() - start_time
            status = "✅" if elapsed < 5 else "⚠️"
            print(f"   {status} Connection {i+1}: {elapsed:.2f}s")
    except Exception as e:
        print(f"❌ FAILED on connection: {type(e).__name__}: {e}")
        return False

    # Test 4: Simulate idle period then reconnect
    print(f"\n{'='*70}")
    print("TEST 4: Idle Period then Reconnect")
    print(f"{'='*70}")
    print("Waiting 3 seconds (simulating delayed request)...")

    await asyncio.sleep(3)

    try:
        start_time = time.time()
        async with db_manager.get_session() as db:
            result = await db.execute(text("SELECT version()"))
            elapsed = time.time() - start_time
            version = result.scalar()
            print(f"✅ Reconnected after idle in {elapsed:.2f} seconds")
            print(f"   PostgreSQL: {version[:60]}...")
    except Exception as e:
        print(f"❌ FAILED after idle: {type(e).__name__}: {e}")
        return False

    # Cleanup
    print(f"\n{'='*70}")
    print("CLEANUP: Closing database connections")
    print(f"{'='*70}")

    try:
        await db_manager.close()
        print(f"✅ Connections closed")
    except Exception as e:
        print(f"⚠️ Close warning: {e}")

    print(f"\n{'='*70}")
    print("✅ ALL TESTS PASSED")
    print(f"{'='*70}")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_server_initialization())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
