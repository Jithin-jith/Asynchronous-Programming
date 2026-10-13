"""
===============================================================================
Module 09: Task Cancellation & Graceful Cleanup (Real SQLite & LLM Stream)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Triggering cancellation via `task.cancel()`.
2. Catching `asyncio.CancelledError`.
3. Resource release and database cleanup inside `finally:` blocks.
4. Mandatory re-raising of `CancelledError`.
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `stream_database_and_ai_audit()` runs a multi-step audit processing database rows.
- The caller simulates a cancellation signal after a short delay.
- The worker catches `CancelledError`, releases open database resources, and re-raises.
===============================================================================
"""

import os
import sys
import asyncio
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")


async def stream_database_and_ai_audit():
    """Multi-step database audit that must handle cancellation gracefully."""
    print("  [Audit Worker] Connecting to SQLite to begin batch audit...")
    db = await aiosqlite.connect(DB_PATH)
    try:
        cursor = await db.execute("SELECT id, name FROM users")
        users = await cursor.fetchall()
        print(f"Retrieved {len(users)} users from DB")
        for user_id, user_name in users:
            print(f"  [Audit Worker] Auditing User #{user_id} ({user_name})...")
            # Simulating non-blocking audit step
            await asyncio.sleep(0.3)
            
    except asyncio.CancelledError:
        print("  [Audit Worker] CANCELLED! Rolling back uncommitted audit states...")
        raise  # Mandatory re-raise!
    finally:
        print("  [Audit Worker] Finally block: Closing SQLite database connection cleanly...")
        await db.close()
        print("  [Audit Worker] DB connection closed successfully.")


async def main():
    print("=================================================================")
    print("  MODULE 09: TASK CANCELLATION & CLEANUP (REAL SQLITE AUDIT)")
    print("=================================================================")

    audit_task = asyncio.create_task(stream_database_and_ai_audit())

    # Let audit run for 0.4 seconds (processes first 1-2 users)
    await asyncio.sleep(0.4)

    print("\n[Main Controller] User requested CANCEL! Calling audit_task.cancel()...")
    audit_task.cancel()

    try:
        await audit_task
    except asyncio.CancelledError:
        print("[Main Controller] Confirmed: Caught CancelledError at task join!")

    print(f"\nFinal Task State - Is task cancelled? {audit_task.cancelled()}")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
