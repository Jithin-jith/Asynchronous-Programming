"""
===============================================================================
Module 01: Asynchronous Execution Demo (Concurrent & Non-Blocking)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Native Coroutines (`async def`).
2. Non-blocking await points (`await`):
   - Asynchronous SQLite query via `aiosqlite`.
   - Asynchronous Google Gemini LLM API call via `client.aio` (with sleep fallback).
3. Event Loop control transfer: while User 1 waits for the network/database response,
   the event loop concurrently begins User 2 and User 3.
4. Concurrent aggregation with `asyncio.gather()`.

HOW THIS CODE WORKS:
- `fetch_user_and_generate_summary_async(user_id)` is defined with `async def`.
- Inside the coroutine:
  1. `await aiosqlite.connect(...)` queries user & order records non-blockingly.
  2. `await client.aio.models.generate_content(...)` sends the prompt to Gemini.
     (Note: If LLM subscription is not available, falls back to await asyncio.sleep() simulation).
- `asyncio.gather(*tasks)` schedules all 3 coroutines concurrently on the loop.
- All 3 users start, wait, and complete concurrently.

EXPECTED OUTPUT:
- User 1, User 2, and User 3 start almost simultaneously at t=0.0s.
- All 3 database queries and LLM network requests execute concurrently.
- Total execution time ≈ Max(Individual Latencies) rather than the Sum!
===============================================================================
"""

import os
import sys
import time
import asyncio
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path to locate ecommerce.db and .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")


async def query_user_from_db_async(user_id: int) -> dict:
    """Connects to SQLite database asynchronously using aiosqlite."""
    print(f"[ASYNC DB] Non-blocking connect to {DB_PATH.name} for User #{user_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT u.id, u.name, u.email, u.role, u.status, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.id = ?
            GROUP BY u.id
            """,
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "role": row[3],
                    "status": row[4],
                    "order_count": row[5]
                }
    return {"id": user_id, "name": f"User_{user_id}", "status": "unknown", "order_count": 0}


async def generate_llm_insight_async(user_data: dict, fallback_delay: float = 1.0) -> str:
    """Calls Google Gemini LLM asynchronously using client.aio.
    
    If LLM subscription is not available, uses await asyncio.sleep() to execute code.
    """
    prompt = (
        f"Generate a friendly 1-sentence welcome summary for customer {user_data['name']} "
        f"who has role '{user_data['role']}' and {user_data['order_count']} orders."
    )
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"[ASYNC LLM] No API key found. Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Note] Welcome {user_data['name']}! Thank you for being a valued {user_data['role']}."

    try:
        from google import genai
        print(f"[ASYNC LLM] Sending async prompt to Gemini for {user_data['name']} (yielding control)...")
        client = genai.Client(api_key=api_key)
        # CRITICAL POINT: client.aio.models.generate_content is NON-BLOCKING!
        # The 'await' keyword yields control back to the event loop dispatcher.
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"[ASYNC LLM] Gemini call failed ({exc.__class__.__name__}). Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Note] Welcome {user_data['name']}, active {user_data['role']} member."


async def fetch_user_and_generate_summary_async(user_id: int) -> dict:
    """Orchestrates non-blocking concurrent pipeline: Async SQLite Query -> Async LLM Call."""
    print(f"[ASYNC Task] >>> Dispatched pipeline for User #{user_id}...")
    t0 = time.perf_counter()

    # Step 1: Asynchronous Non-Blocking Database Query
    user_data = await query_user_from_db_async(user_id)
    print(f"[ASYNC DB] Retrieved: {user_data['name']} ({user_data['role']}, {user_data['order_count']} orders)")

    # Step 2: Asynchronous Non-Blocking Gemini LLM Call
    note = await generate_llm_insight_async(user_data, fallback_delay=1.0)
    user_data["ai_note"] = note

    duration = time.perf_counter() - t0
    print(f"[ASYNC Task] <<< Completed User #{user_id} in {duration:.2f}s")
    return user_data


async def main():
    """Main asynchronous coroutine entry point."""
    print("=================================================================")
    print("  MODULE 01: ASYNCHRONOUS EXECUTION DEMO (aiosqlite + Gemini LLM)")
    print("=================================================================")
    start_time = time.perf_counter()

    # Create coroutine objects for 3 users (does not execute them yet!)
    coros = [fetch_user_and_generate_summary_async(uid) for uid in range(1, 4)]

    # asyncio.gather schedules all 3 coroutines concurrently on the event loop
    users = await asyncio.gather(*coros)

    total_time = time.perf_counter() - start_time

    print("\n---------------- Asynchronous Summary ---------------")
    for u in users:
        print(f" * User #{u['id']} ({u['name']}): {u['ai_note']}")
    print("-----------------------------------------------------")
    print(f"Total Processed     : {len(users)} users")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print("Observation: Total time is approx the MAX of individual requests, NOT the sum!")
    print("             All 3 SQLite queries and Gemini LLM calls ran CONCURRENTLY.")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
