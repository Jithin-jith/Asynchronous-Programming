"""
===============================================================================
Module 07: Creating Tasks Concurrently (Real SQLite & Gemini LLM)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Scheduling coroutines concurrently using `asyncio.create_task()`.
2. Background task execution while the main coroutine performs other work.
3. Real-world tasks:
   - Task 1: Asynchronous SQLite query for customer analytics (`aiosqlite`).
   - Task 2: Asynchronous Google Gemini LLM marketing generation (`client.aio`).
   - Task 3: Asynchronous SQLite query for inventory levels (`aiosqlite`).
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Calling `asyncio.create_task(coro)` immediately places `coro` on the event loop ready queue.
- `main()` performs intermediate calculations while background I/O operations execute.
- Awaiting tasks later retrieves their returned values.
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


async def task_query_user_analytics(user_id: int) -> dict:
    """Task 1: Queries user profile and order count from SQLite."""
    print(f"  [Task 1 - DB] Starting customer analytics lookup for User #{user_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT u.name, u.role, COUNT(o.id), COALESCE(SUM(o.total_amount), 0.0)
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.id = ?
            GROUP BY u.id
            """,
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            name, role, count, total = row[0], row[1], row[2], row[3]

    print(f"  [Task 1 - DB] Completed! {name}: {count} orders (${total:.2f})")
    return {"name": name, "role": role, "orders": count, "spent": total}


async def task_generate_gemini_pitch(topic: str, fallback_delay: float = 1.0) -> str:
    """Task 2: Calls Google Gemini LLM to generate an ad copy in the background."""
    print(f"  [Task 2 - LLM] Generating Gemini promotional pitch for '{topic}'...")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Ad] Supercharge your workflow with {topic}!"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Generate a catchy 8-word sales slogan for: {topic}",
        )
        pitch = res.text.strip().replace("\n", " ")
        print("  [Task 2 - LLM] Completed! Gemini slogan generated.")
        return pitch
    except Exception:
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Ad] Experience the next generation of {topic}."


async def task_query_inventory() -> int:
    """Task 3: Queries SQLite to count active product offerings."""
    print("  [Task 3 - DB] Starting inventory stock check...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM products") as cursor:
            count = (await cursor.fetchone())[0]

    print(f"  [Task 3 - DB] Completed! {count} product lines in stock.")
    return count


async def main():
    print("=================================================================")
    print("  MODULE 07: CONCURRENT TASKS WITH REAL SQLITE & GEMINI WORKLOADS")
    print("=================================================================")
    start_time = time.perf_counter()

    # Schedule 3 background tasks on the event loop immediately
    task1 = asyncio.create_task(task_query_user_analytics(1), name="AnalyticsTask")
    task2 = asyncio.create_task(task_generate_gemini_pitch("Cloud AI Solutions"), name="LLMAdTask")
    task3 = asyncio.create_task(task_query_inventory(), name="InventoryTask")

    # Main thread does intermediate work while background tasks run
    print("\n[Main] Tasks dispatched to event loop! Doing local processing...")
    local_calc = sum(x * x for x in range(10_000))
    print(f"[Main] Intermediate calculation done ({local_calc}). Now awaiting task results...\n")

    # Await individual task outputs
    res_analytics = await task1
    res_pitch = await task2
    res_inventory = await task3

    elapsed = time.perf_counter() - start_time

    print("\n---------------- Concurrency Summary ----------------")
    print(f"User Analytics : {res_analytics}")
    print(f"Gemini Ad Copy : '{res_pitch}'")
    print(f"Total Products : {res_inventory}")
    print(f"Total Elapsed  : {elapsed:.2f} seconds")
    print("Notice: All 3 tasks executed concurrently in the background!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
