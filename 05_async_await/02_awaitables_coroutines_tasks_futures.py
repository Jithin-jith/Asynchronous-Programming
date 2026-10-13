"""
===============================================================================
Module 05: Awaiting Coroutines, Tasks, and Futures (The 3 Awaitables)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Native Coroutines: `async def` function objects that execute lazily when awaited.
   - Example: Awaiting an asynchronous SQLite query function directly.
2. `asyncio.Task` Objects: Wrappers created via `asyncio.create_task()` that schedule 
   coroutines for concurrent execution on the event loop.
   - Example: Scheduling a Google Gemini LLM API call concurrently as a background Task.
3. `asyncio.Future` Objects: Low-level result containers representing an eventual outcome
   resolved asynchronously (e.g. by database cache events or callback timers).
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Section 1: Awaits a raw coroutine object querying `ecommerce.db` for product details.
- Section 2: Wraps a Google Gemini LLM call into an `asyncio.Task` and awaits it.
- Section 3: Creates an `asyncio.Future`, registers a callback via `loop.call_later()`,
  and awaits the Future until the callback fulfills it with `fut.set_result(...)`.
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


# 1. Native Coroutine Function
async def query_product_coroutine(product_id: int) -> dict:
    """Coroutine querying a product record from SQLite database."""
    print(f"  [Coro] Querying product #{product_id} from {DB_PATH.name}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, price, category FROM products WHERE id = ?", (product_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": product_id, "name": row[0], "price": row[1], "category": row[2]}
    return {"id": product_id, "name": "Unknown", "price": 0.0, "category": "General"}


# 2. Coroutine to be wrapped in an asyncio.Task
async def gemini_task_coroutine(product_name: str, fallback_delay: float = 1.0) -> str:
    """Coroutine calling Google Gemini LLM to generate a marketing tagline."""
    print(f"  [Task] Initiating Gemini LLM call for product '{product_name}'...")
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = f"Write a 4-word sales pitch for '{product_name}'."

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Tagline] Best-in-class {product_name}!"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return res.text.strip().replace("\n", " ")
    except Exception:
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Tagline] Premium {product_name} solution."


# 3. Synchronous callback to resolve a low-level Future
def fulfill_database_cache_future(fut: asyncio.Future, cached_payload: dict):
    """Callback triggered by event loop timer to fulfill a low-level Future."""
    print("  [Callback] Database cache refresh timer triggered! Fulfilling Future container...")
    fut.set_result(cached_payload)


async def main():
    print("=================================================================")
    print("  MODULE 05: THE 3 TYPES OF AWAITABLES IN PYTHON (REAL I/O)")
    print("=================================================================")
    loop = asyncio.get_running_loop()

    # -------------------------------------------------------------------------
    # 1. AWAITING A NATIVE COROUTINE OBJECT (SQLite Query)
    # -------------------------------------------------------------------------
    print("\n1. Awaiting a Native Coroutine Object directly (SQLite query):")
    coro = query_product_coroutine(1)
    print(f"   Instantiated coroutine object: {coro}")
    print(f"   Is awaitable?               : {isinstance(coro, asyncio.Future) is False}")
    product_data = await coro
    print(f"   Awaited Result              : {product_data}")

    # -------------------------------------------------------------------------
    # 2. AWAITING AN asyncio.Task OBJECT (Gemini LLM Call)
    # -------------------------------------------------------------------------
    print("\n2. Awaiting an asyncio.Task Object (Google Gemini LLM):")
    task = asyncio.create_task(
        gemini_task_coroutine(product_data["name"]),
        name="Gemini_Tagline_Task"
    )
    print(f"   Created Task instance: {task}")
    print(f"   Is Task a Future?    : {isinstance(task, asyncio.Future)} (Task is a subclass of Future)")
    tagline = await task
    print(f"   Awaited Task Result  : '{tagline}'")

    # -------------------------------------------------------------------------
    # 3. AWAITING A LOW-LEVEL asyncio.Future OBJECT (Cache Callback)
    # -------------------------------------------------------------------------
    print("\n3. Awaiting a Low-Level asyncio.Future Object (Cache Event):")
    fut = loop.create_future()
    print(f"   Created Future instance : {fut} (State: pending)")

    # Schedule cache fulfillment in 0.2 seconds
    cached_data = {"cache_hit": True, "cached_product": "AI Cloud Server", "cached_ttl": 300}
    loop.call_later(0.2, fulfill_database_cache_future, fut, cached_data)

    print("   Now awaiting Future... Execution pauses until fut.set_result() is called.")
    future_result = await fut
    print(f"   Awaited Future Result   : {future_result}")
    print(f"   Future State After Await: {fut} (State: finished)")

    print("\n=================================================================")
    print("SUMMARY: Coroutines, Tasks, and Futures all implement __await__()")
    print("and can be seamlessly awaited on the asyncio Event Loop!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
