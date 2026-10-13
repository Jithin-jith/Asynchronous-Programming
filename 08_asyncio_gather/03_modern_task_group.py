"""
===============================================================================
Module 08: Modern Python 3.11+ asyncio.TaskGroup (Structured Concurrency)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Structured Concurrency via `async with asyncio.TaskGroup() as tg:`.
2. Automatic cancellation of sibling tasks when any task in the group raises an exception.
3. Catching and inspecting `ExceptionGroup`.
4. Real-world tasks:
   - Task A: SQLite product lookup (succeeds).
   - Task B: Simulated network / database failure (raises error).
   - Task C: Long-running Google Gemini LLM API call (automatically cancelled by TaskGroup!).
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `tg.create_task()` registers coroutines inside the structured context manager.
- If Task B raises an exception, the `TaskGroup` context manager automatically cancels
  Task C to prevent resource leakage or orphaned tasks.
- At context exit, an `ExceptionGroup` containing Task B's error is raised.
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


async def task_a_sqlite():
    """Task A: Fast SQLite read."""
    print("  [Task A - DB] Fetching user count from SQLite...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            count = (await cursor.fetchone())[0]
    print(f"  [Task A - DB] Succeeded! Found {count} users.")


async def task_b_faulty():
    """Task B: Simulated database service failure."""
    await asyncio.sleep(0.05)
    print("  [Task B - DB] Critical connection lost! Raising RuntimeError...")
    raise RuntimeError("Database pool connection timeout on Task B!")


async def task_c_gemini_llm(fallback_delay: float = 2.0):
    """Task C: Longer Gemini LLM call that will be automatically cancelled."""
    print("  [Task C - LLM] Sending prompt to Google Gemini...")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.strip() in ("", "your_api_key_here"):
            await asyncio.sleep(fallback_delay)
            print("  [Task C - LLM] Finished simulated LLM task.")
            return

        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Explain structured concurrency in Python in 10 words.",
        )
        print(f"  [Task C - LLM] Succeeded: {res.text.strip()[:40]}...")
    except asyncio.CancelledError:
        print("  [Task C - LLM] CANCELLED automatically by TaskGroup due to Task B failure!")
        raise


async def main():
    print("=================================================================")
    print("  MODULE 08: MODERN asyncio.TaskGroup STRUCTURED CONCURRENCY")
    print("=================================================================")

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task_a_sqlite(), name="SQLiteRead")
            tg.create_task(task_b_faulty(), name="FaultyService")
            tg.create_task(task_c_gemini_llm(), name="GeminiCall")
    except* RuntimeError as eg:
        print(f"\n[Structured Concurrency] Caught ExceptionGroup: '{eg}'")
        for sub_exc in eg.exceptions:
            print(f"  -> Encapsulated Sub-Exception: {type(sub_exc).__name__}: {sub_exc}")

    print("\nTakeaway: TaskGroup prevented Task C from continuing as an orphaned task!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
