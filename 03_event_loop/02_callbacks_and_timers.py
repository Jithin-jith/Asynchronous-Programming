"""
===============================================================================
Module 03: Scheduling Callbacks & Timers on the Event Loop
===============================================================================

CONCEPTS DEMONSTRATED:
1. `loop.call_soon(callback, *args)`:
   - Schedules a synchronous callback function to execute on the VERY NEXT tick
     of the event loop (e.g. logging DB connection initialization).
2. `loop.call_later(delay, callback, *args)`:
   - Schedules a callback after `delay` relative seconds (e.g. database cache eviction).
3. `loop.call_at(when, callback, *args)`:
   - Schedules a callback at an absolute monotonic timestamp (e.g. LLM rate limit token refill).
4. Running synchronous callbacks alongside real asynchronous SQLite & Gemini operations.

HOW THIS CODE WORKS:
- Schedules three synchronous telemetry/cache callbacks (`call_soon`, `call_later`, `call_at`).
- Concurrently runs an asynchronous database query and an asynchronous Gemini LLM call.
- The event loop seamlessly fires the scheduled callbacks when their timers mature while
  awaiting external I/O responses.
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


def db_telemetry_callback(event_type: str, start_time: float, loop):
    """Synchronous callback executed directly by the event loop during its tick cycle."""
    elapsed = loop.time() - start_time
    print(f"  [Callback: {event_type}] Fired at +{elapsed:.3f}s on event loop!")


async def query_db_task() -> str:
    """Async task querying database while callbacks are queued."""
    print("  [Async Task: DB] Fetching total order count from SQLite...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM orders") as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
    print(f"  [Async Task: DB] Completed! Found {count} orders.")
    return f"{count} orders"


async def query_llm_task(fallback_delay: float = 1.0) -> str:
    """Async task calling Gemini LLM while timer callbacks are in the loop queue."""
    print("  [Async Task: LLM] Querying Google Gemini API...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return "[Simulated Gemini Response]"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Summarize the role of an event loop in 6 words.",
        )
        summary = res.text.strip().replace("\n", " ")
        print(f"  [Async Task: LLM] Completed! Gemini response received.")
        return summary
    except Exception:
        await asyncio.sleep(fallback_delay)
        return "[Simulated Fallback Gemini Response]"


async def main():
    print("=================================================================")
    print("  MODULE 03: EVENT LOOP CALLBACKS & MONOTONIC TIMERS (REAL I/O)")
    print("=================================================================")
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    # 1. loop.call_soon(): Runs on the immediate next iteration tick
    loop.call_soon(db_telemetry_callback, "IMMEDIATE_INIT_LOG", start_time, loop)

    # 2. loop.call_later(): Relative timer (runs after 0.3s)
    loop.call_later(0.3, db_telemetry_callback, "CACHE_EVICTION_0.3s", start_time, loop)

    # 3. loop.call_at(): Absolute timestamp targeting (start_time + 0.6s)
    target_timestamp = start_time + 0.6
    loop.call_at(target_timestamp, db_telemetry_callback, "LLM_RATE_LIMIT_RESET_0.6s", start_time, loop)

    # Run asynchronous tasks concurrently while callbacks trigger
    print("\n[Event Loop] Starting concurrent DB and LLM tasks alongside scheduled timers...")
    db_res, llm_res = await asyncio.gather(query_db_task(), query_llm_task())

    print("\n----------------- Summary of Results -----------------")
    print(f"Database Output: {db_res}")
    print(f"Gemini LLM Note: {llm_res}")
    print(f"Total Duration : {loop.time() - start_time:.3f}s")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
