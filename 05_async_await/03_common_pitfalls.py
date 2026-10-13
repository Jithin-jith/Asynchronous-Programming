"""
===============================================================================
Module 05: Common Async/Await Pitfalls & Anti-Patterns (Real I/O)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Unawaited Coroutine Warning:
   - Invoking an `async def` function without `await` returns an unstarted coroutine
     object that never executes its body code (e.g. database is never queried!).
2. Awaiting Non-Awaitable Objects:
   - Attempting to `await` primitives (e.g. `int`, `str`, `float` price from SQLite)
     raises `TypeError: object ... can't be used in 'await' expression`.
3. Blocking the Event Loop with Synchronous Code:
   - Calling synchronous `time.sleep()` or blocking synchronous database drivers
     inside a coroutine freezes the event loop, starving all other concurrent tasks.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Pitfall 1: Calls `query_product_unawaited()` without `await`, demonstrating that
  the SQLite database query never runs, then shows the correct `await` syntax.
- Pitfall 2: Evaluates `await price` to demonstrate the expected `TypeError`.
- Pitfall 3: Illustrates how blocking calls stall the loop and provides the solution
  (`asyncio.to_thread` for legacy sync code or native async libraries like `aiosqlite`).
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


async def query_product_demo(product_id: int) -> dict:
    """Async function querying SQLite."""
    print("  [DB Query] This print statement ONLY runs if the coroutine is awaited!")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, price FROM products WHERE id = ?", (product_id,)) as cursor:
            row = await cursor.fetchone()
            return {"name": row[0], "price": row[1]} if row else {"name": "Not found", "price": 0.0}


async def main():
    print("=================================================================")
    print("  MODULE 05: COMMON ASYNC/AWAIT PITFALLS & ANTI-PATTERNS")
    print("=================================================================")

    # -------------------------------------------------------------------------
    # PITFALL 1: FORGETTING TO AWAIT AN ASYNC FUNCTION
    # -------------------------------------------------------------------------
    print("\n1. Calling query_product_demo() WITHOUT 'await':")
    coro_ref = query_product_demo(1)
    print(f"   Stored variable type: {type(coro_ref)}")
    print(f"   Notice: '[DB Query]' was NOT printed! SQLite was never touched.")
    
    # Close explicitly to clean up dormant frame
    coro_ref.close()

    # Correct usage:
    print("\n   [Fix] Now calling WITH 'await':")
    product_result = await query_product_demo(1)
    print(f"   Retrieved Product: {product_result}")

    # -------------------------------------------------------------------------
    # PITFALL 2: ATTEMPTING TO AWAIT A NON-AWAITABLE OBJECT
    # -------------------------------------------------------------------------
    print("\n2. Attempting to await a non-awaitable float primitive (await product['price']):")
    price = product_result["price"]

    async def _invalid_await():
        return await price  # Primitive float cannot be awaited!

    try:
        await _invalid_await()
    except TypeError as exc:
        print(f"   [ERROR] Caught Expected TypeError: {exc}")
        print("   [Fix] Only await Coroutines, Tasks, Futures, or objects with __await__().")

    # -------------------------------------------------------------------------
    # PITFALL 3: BLOCKING THE EVENT LOOP WITH SYNCHRONOUS CODE
    # -------------------------------------------------------------------------
    print("\n3. Blocking the Event Loop (Conceptual Anti-Pattern):")
    print("   [Anti-Pattern] Using synchronous sqlite3 or time.sleep() inside async coroutines.")
    print("                  This blocks the single thread and halts ALL concurrent requests!")
    print("   [Fix A] Use native async libraries (e.g., `aiosqlite`, Google Gemini `client.aio`).")
    print("   [Fix B] For legacy synchronous blocking code, use `await asyncio.to_thread(sync_func)`.")

    print("\n=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
