"""
===============================================================================
Module 02: I/O-Bound Workload Asynchronous Demo (SQLite + Gemini LLM)
===============================================================================

CONCEPTS DEMONSTRATED:
1. I/O-Bound Workloads:
   - Operations that spend >95% of their total wall-clock time waiting for 
     external resources (disk storage, database engines, remote LLM HTTP sockets).
   - The CPU is almost entirely idle during this wait period.
2. Real-World Asynchronous I/O Primitives:
   - `aiosqlite.connect()` for non-blocking local database queries.
   - `client.aio.models.generate_content()` for non-blocking Gemini LLM generation.
   - Graceful fallback: If LLM subscription is not available, user can use `asyncio.sleep()`.
3. Concurrency Latency Overlap:
   - Launching 5 diverse I/O tasks concurrently via `asyncio.gather()` allows the 
     single OS thread to interleave them all, completing in approx the MAX single latency.

HOW THIS CODE WORKS:
- Task 1: Async SQLite query fetching users table.
- Task 2: Async SQLite query fetching products catalogue.
- Task 3: Async SQLite query calculating total revenue from orders.
- Task 4: Async Gemini LLM prompt: Summarize product catalogue.
- Task 5: Async Gemini LLM prompt: Generate inventory restock recommendation.
- All 5 tasks run concurrently on a single thread.
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


async def io_query_users() -> str:
    """I/O Task 1: Asynchronous SQLite query fetching registered users."""
    print("[I/O Task 1 - SQLite] Connecting to database to fetch users...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), GROUP_CONCAT(name, ', ') FROM users") as cursor:
            row = await cursor.fetchone()
            count, names = row[0], row[1]
    print(f"[I/O Task 1 - SQLite] Found {count} users: {names}")
    return f"Users({count}): {names}"


async def io_query_products() -> str:
    """I/O Task 2: Asynchronous SQLite query fetching product catalogue."""
    print("[I/O Task 2 - SQLite] Connecting to database to fetch products...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), AVG(price) FROM products") as cursor:
            row = await cursor.fetchone()
            count, avg_price = row[0], row[1]
    print(f"[I/O Task 2 - SQLite] Found {count} products (Avg Price: ${avg_price:.2f})")
    return f"Products({count}, Avg: ${avg_price:.2f})"


async def io_query_revenue() -> str:
    """I/O Task 3: Asynchronous SQLite query calculating total revenue."""
    print("[I/O Task 3 - SQLite] Connecting to database to aggregate sales revenue...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), SUM(total_amount) FROM orders WHERE status = 'completed'") as cursor:
            row = await cursor.fetchone()
            order_count, total_rev = row[0], row[1]
    print(f"[I/O Task 3 - SQLite] Completed orders: {order_count}, Total Revenue: ${total_rev:.2f}")
    return f"Revenue(${total_rev:.2f} across {order_count} orders)"


async def io_gemini_llm_call(task_name: str, prompt: str, fallback_delay: float = 1.5) -> str:
    """I/O Tasks 4 & 5: Asynchronous Google Gemini LLM API call (Network Socket I/O).
    
    If LLM subscription is not available, uses await asyncio.sleep() to execute code.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"[{task_name}] No API key. Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Response for {task_name}]"

    try:
        from google import genai
        print(f"[{task_name}] Sending async prompt to Gemini API: '{prompt[:45]}...'")
        client = genai.Client(api_key=api_key)
        # NON-BLOCKING await: frees the event loop while waiting for HTTP packets
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        summary = response.text.strip().replace("\n", " ")
        print(f"[{task_name}] Gemini returned response successfully!")
        return f"Gemini Output: {summary[:80]}..."
    except Exception as exc:
        print(f"[{task_name}] Gemini API error ({exc.__class__.__name__}). Falling back to sleep...")
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Fallback for {task_name}]"


async def main():
    print("=================================================================")
    print("  MODULE 02: 5 CONCURRENT REAL-WORLD I/O TASKS (SQLite + Gemini)")
    print("=================================================================")
    start_time = time.perf_counter()

    # Schedule 3 database I/O tasks and 2 Gemini LLM network I/O tasks concurrently
    tasks = [
        io_query_users(),
        io_query_products(),
        io_query_revenue(),
        io_gemini_llm_call("I/O Task 4 - LLM", "Explain why SQLite and Asyncio pair well together in 1 sentence."),
        io_gemini_llm_call("I/O Task 5 - LLM", "Give 3 tips for optimizing LLM API latency in 1 sentence."),
    ]

    # asyncio.gather overlaps all 5 waiting times on the single thread
    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time

    print("\n------------------- Execution Results -------------------")
    for i, res in enumerate(results, start=1):
        print(f" Task {i} Result: {res}")
    print("---------------------------------------------------------")
    print(f"Total Wall-Clock Time: {elapsed:.2f} seconds")
    print("TAKEAWAY: All 3 SQLite disk queries and 2 Gemini network calls ran")
    print("concurrently on a single thread. The event loop overlapped all I/O waits!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
