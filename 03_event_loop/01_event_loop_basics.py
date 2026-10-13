"""
===============================================================================
Module 03: Event Loop Basics & Clock Inspection with Real I/O (SQLite & Gemini)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Event Loop Retrieval (`asyncio.get_running_loop()`):
   - Safely retrieves the active event loop running on the current OS thread.
   - Raises `RuntimeError` if called outside an active coroutine execution context.
2. Event Loop Operational State:
   - `loop.is_running()`: Returns `True` while executing coroutines.
   - `loop.is_closed()`: Returns `True` if the loop instance has been destroyed.
3. Internal Monotonic Clock (`loop.time()`):
   - Independent of system wall-clock changes.
   - Tracks time progression as real SQLite queries and Google Gemini LLM calls execute.
   - Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `inspect_event_loop()` retrieves the running loop and prints its properties.
- Measures `loop.time()` before and after:
  1. An asynchronous SQLite query to `ecommerce.db`.
  2. An asynchronous Google Gemini LLM API call.
- Proves how the event loop's internal clock advances across real database and network events.
===============================================================================
"""

import os
import sys
import time
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


async def async_db_operation() -> str:
    """Asynchronous SQLite query tracking loop time."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, email FROM users WHERE role = 'admin'") as cursor:
            row = await cursor.fetchone()
            return f"Admin: {row[0]} ({row[1]})" if row else "Admin not found"


async def async_gemini_operation(fallback_delay: float = 1.0) -> str:
    """Asynchronous Gemini LLM call tracking loop time (with fallback sleep)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return "[Simulated Gemini Output]"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Define 'Event Loop' in 10 words.",
        )
        return res.text.strip().replace("\n", " ")
    except Exception:
        await asyncio.sleep(fallback_delay)
        return "[Simulated Fallback Gemini Output]"


async def inspect_event_loop():
    """Retrieves and inspects properties of the active event loop during real I/O."""
    loop = asyncio.get_running_loop()

    print(f"Running Event Loop Instance: {loop.__class__.__name__}")
    print(f"Is Loop Running?           : {loop.is_running()}")
    print(f"Is Loop Closed?            : {loop.is_closed()}")

    t_start = loop.time()
    perf_start = time.perf_counter()
    print(f"\nInitial Monotonic Clock    : {t_start:.4f}s")
    print(f"Initial System Perf Counter: {perf_start:.4f}s")

    # Step 1: Real SQLite I/O on Event Loop
    print("\n[Step 1] Executing asynchronous SQLite query...")
    db_result = await async_db_operation()
    t_after_db = loop.time()
    print(f"  -> DB Result: {db_result}")
    print(f"  -> Loop Monotonic Clock after DB: {t_after_db:.4f}s (Delta: {t_after_db - t_start:.4f}s)")

    # Step 2: Real Google Gemini LLM I/O on Event Loop
    print("\n[Step 2] Executing asynchronous Google Gemini LLM call...")
    llm_result = await async_gemini_operation()
    t_after_llm = loop.time()
    print(f"  -> LLM Result: {llm_result}")
    print(f"  -> Loop Monotonic Clock after LLM: {t_after_llm:.4f}s (Delta: {t_after_llm - t_after_db:.4f}s)")

    print(f"\nTotal Loop Time Elapsed: {t_after_llm - t_start:.4f}s")


def main():
    print("=================================================================")
    print("  MODULE 03: EVENT LOOP INSPECTION WITH REAL SQLITE & GEMINI I/O")
    print("=================================================================")
    asyncio.run(inspect_event_loop())
    print("=================================================================\n")


if __name__ == "__main__":
    main()
