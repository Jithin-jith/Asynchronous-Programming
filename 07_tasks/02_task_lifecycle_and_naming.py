"""
===============================================================================
Module 07: Task Lifecycle, Naming, and Inspection (Real I/O)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Setting custom, human-readable task names (`name="SQLite-OrderAnalytics"`).
2. Inspecting task state transitions: `task.done()`, `task.result()`.
3. Inspecting active loop tasks via `asyncio.all_tasks()`.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Custom task names simplify debugging, tracing, and observability in production.
- `asyncio.all_tasks()` inspects all running tasks currently registered in loop.
- Demonstrates state tracking across an asynchronous SQLite query and a Gemini call.
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


async def sqlite_analytics_worker() -> str:
    """Named Task 1: Asynchronous SQLite query."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), SUM(total_amount) FROM orders") as cursor:
            row = await cursor.fetchone()
            return f"Processed {row[0]} orders totaling ${row[1]:.2f}"


async def gemini_summary_worker(fallback_delay: float = 1.0) -> str:
    """Named Task 2: Asynchronous Gemini LLM call."""
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = "Summarize the importance of task observability in 1 sentence."

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return "[Simulated Insight] Task observability enables real-time system monitoring."

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
        return "[Fallback Insight] Observability ensures healthy async systems."


async def main():
    print("=================================================================")
    print("  MODULE 07: TASK NAMING, LIFECYCLE & ACTIVE TASK INSPECTION")
    print("=================================================================")

    # 1. Schedule tasks with custom names
    t1 = asyncio.create_task(sqlite_analytics_worker(), name="Task-SQLite-Orders")
    t2 = asyncio.create_task(gemini_summary_worker(), name="Task-Gemini-Observability")

    print(f"Task 1 Name : {t1.get_name()} | Initially Done? {t1.done()}")
    print(f"Task 2 Name : {t2.get_name()} | Initially Done? {t2.done()}")

    # 2. Inspect active tasks in event loop
    active_tasks = asyncio.all_tasks()
    print(f"\nActive Tasks in Event Loop ({len(active_tasks)}):")
    for t in active_tasks:
        print(f"  * Task: '{t.get_name()}' (Done: {t.done()})")

    # 3. Await tasks and inspect results
    await asyncio.gather(t1, t2)

    print("\n---------------- Tasks After Completion ----------------")
    print(f"Task 1 Done? {t1.done()} | Result: '{t1.result()}'")
    print(f"Task 2 Done? {t2.done()} | Result: '{t2.result()}'")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
