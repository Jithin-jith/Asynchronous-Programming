"""
===============================================================================
Module 05: Interleaved Await Mechanics & Cooperative Multitasking
===============================================================================

CONCEPTS DEMONSTRATED:
1. Cooperative Context-Switching: How the `await` keyword yields execution control
   back to the asyncio event loop.
2. Interleaved Execution: How two concurrent tasks:
   - Task Alpha (SQLite Database Operations via `aiosqlite`)
   - Task Beta (Google Gemini LLM Generation via `client.aio` with sleep fallback)
   run concurrently on a single OS thread without thread switches.
3. Event Loop Scheduling: The event loop interleaves progress between database
   disk I/O and LLM network I/O.

HOW THIS CODE WORKS:
- `main()` launches Task Alpha and Task Beta concurrently via `asyncio.create_task()`.
- Task Alpha queries `ecommerce.db` for user orders, yields on `await`, then queries revenue.
- Task Beta queries Gemini LLM for product marketing, yields on `await`.
- Execution naturally interleaves on the single thread as each task awaits external I/O.
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


async def task_alpha_database_pipeline() -> str:
    """Task Alpha: Asynchronous SQLite operations interleaved with event loop."""
    print("[Alpha 1 - DB] Starting Task Alpha: Connecting to SQLite for user count...")
    
    # YIELD POINT 1: Yields control back to event loop while connecting to SQLite
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            user_count = (await cursor.fetchone())[0]
            
    print(f"[Alpha 2 - DB] Resumed! Total users in DB: {user_count}. Now fetching orders...")
    
    # YIELD POINT 2: Yields control again while querying orders table
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), SUM(total_amount) FROM orders") as cursor:
            order_row = await cursor.fetchone()
            order_count, total_amount = order_row[0], order_row[1]

    print(f"[Alpha 3 - DB] Finished Task Alpha! Orders: {order_count}, Total: ${total_amount:.2f}")
    return f"DB Summary: {user_count} users, {order_count} orders (${total_amount:.2f})"


async def task_beta_gemini_pipeline(fallback_delay: float = 1.0) -> str:
    """Task Beta: Asynchronous Google Gemini LLM API call interleaved with event loop."""
    print("  [Beta 1 - LLM] Starting Task Beta: Preparing prompt for Google Gemini...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = "Write a catchy 6-word slogan for an AI cloud platform."

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"  [Beta 1 - LLM] No API key. Yielding at await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        print("  [Beta 2 - LLM] Resumed Task Beta after simulated network wait!")
        return "[Simulated Slogan] AI Cloud: Powering Next-Gen Intelligence"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        print("  [Beta 1 - LLM] Sending async HTTP request to Gemini API (YIELDING CONTROL)...")
        
        # YIELD POINT: The coroutine suspends, allowing Task Alpha to execute database queries!
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        print("  [Beta 2 - LLM] Resumed Task Beta! Gemini HTTP response packets received.")
        return res.text.strip().replace("\n", " ")
    except Exception as exc:
        print(f"  [Beta 1 - LLM] Gemini call failed ({exc.__class__.__name__}). Using fallback sleep...")
        await asyncio.sleep(fallback_delay)
        return "[Fallback Slogan] Empowering your cloud with AI."


async def main():
    print("=================================================================")
    print("  MODULE 05: INTERLEAVED AWAIT MECHANICS (SQLite DB vs Gemini LLM)")
    print("=================================================================")
    start_time = time.perf_counter()

    # Create tasks to schedule them concurrently on the event loop
    t_alpha = asyncio.create_task(task_alpha_database_pipeline(), name="DB_Task_Alpha")
    t_beta = asyncio.create_task(task_beta_gemini_pipeline(), name="LLM_Task_Beta")

    # Await both tasks
    alpha_res, beta_res = await asyncio.gather(t_alpha, t_beta)

    duration = time.perf_counter() - start_time

    print("\n---------------- Concurrency Results ----------------")
    print(f"Task Alpha Result: {alpha_res}")
    print(f"Task Beta Result : {beta_res}")
    print(f"Total Duration   : {duration:.2f} seconds")
    print("Notice how Task Alpha (DB) and Task Beta (LLM) cooperatively interleaved")
    print("their execution on the event loop without blocking each other!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
