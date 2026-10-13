"""
===============================================================================
Module 06: Nested asyncio.run() Anti-Pattern (Real Database Example)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `RuntimeError: asyncio.run() cannot be called from a running event loop`.
2. Common real-world scenario: An async endpoint or worker function tries to invoke
   `asyncio.run()` to call a database query helper.
3. Proper resolution: Simply `await` the async database coroutine directly.

HOW THIS CODE WORKS:
- `query_database_subtask()`: An async coroutine querying `ecommerce.db` via `aiosqlite`.
- `bad_caller()`: Erroneously invokes `asyncio.run(query_database_subtask())` while
  already running inside an active event loop -> throws `RuntimeError`.
- `good_caller()`: Correctly awaits `await query_database_subtask()`.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


async def query_database_subtask():
    """Async child coroutine querying SQLite database."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, email FROM users WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            return f"User: {row[0]} ({row[1]})" if row else "User not found"


async def bad_caller():
    """ANTI-PATTERN: Attempting to call asyncio.run() inside an active coroutine."""
    print("1. [Anti-Pattern] Invoking asyncio.run(query_database_subtask()) from inside loop...")
    try:
        # FATAL ERROR: Cannot nest asyncio.run inside an active running event loop!
        res = asyncio.run(query_database_subtask())
        print(f"   Unexpected Success: {res}")
    except RuntimeError as e:
        print(f"   [ERROR] Caught Expected RuntimeError: {e}")
        print("   Explanation: The event loop is ALREADY running on this thread.")
        print("   Calling asyncio.run() tries to create another event loop on the same thread.")


async def good_caller():
    """CORRECT PATTERN: Simply await child coroutine directly."""
    print("\n2. [Correct Approach] Simply using 'await query_database_subtask()'...")
    res = await query_database_subtask()
    print(f"   [OK] Retrieved Result: '{res}'")


async def main():
    print("=================================================================")
    print("  MODULE 06: NESTED asyncio.run() ANTI-PATTERN (SQLITE)")
    print("=================================================================")
    await bad_caller()
    await good_caller()
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
