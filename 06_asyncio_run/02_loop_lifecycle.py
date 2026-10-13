"""
===============================================================================
Module 06: Loop Lifecycle Under the Hood & Concurrent Task Execution
===============================================================================

CONCEPTS DEMONSTRATED:
1. Low-level Event Loop Management: `asyncio.new_event_loop()`, `set_event_loop()`.
2. Synchronous-to-Asynchronous Execution Bridge: `loop.run_until_complete()`.
3. Resource Cleanup & Teardown: `loop.close()`.
4. Concurrent Task Scheduling: `asyncio.create_task()` running a progress ticker
   concurrently while executing a real-world SQLite & Gemini LLM pipeline.
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

EXECUTION WORKFLOW:
1. `asyncio.new_event_loop()` instantiates a fresh OS-level event loop instance.
2. `asyncio.set_event_loop(loop)` assigns this instance as the current thread's loop.
3. `loop.run_until_complete(database_and_llm_worker())` executes the workload.
4. Inside the worker, a background ticker coroutine reports elapsed progress concurrently
   while SQLite and Google Gemini API requests are executing.
5. A `try...finally` block guarantees `loop.close()` executes to clean up OS resources.
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


async def progress_ticker(stop_event: asyncio.Event):
    """Concurrent ticker reporting elapsed seconds while worker runs."""
    sec = 0
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            break
        except asyncio.TimeoutError:
            sec += 1
            print(f"  [Ticker] Concurrently ticking on loop: {sec}s elapsed...")


async def database_and_llm_worker() -> dict:
    """Worker coroutine performing real SQLite read and Gemini LLM call."""
    print("  [Worker] Starting database read from ecommerce.db...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, price FROM products LIMIT 3") as cursor:
            rows = await cursor.fetchall()
            products_str = ", ".join(f"{r[0]} (${r[1]:.2f})" for r in rows)

    print(f"  [Worker] Retrieved products: {products_str}")

    # Launch background progress ticker
    stop_event = asyncio.Event()
    ticker_task = asyncio.create_task(progress_ticker(stop_event))

    print("  [Worker] Calling Google Gemini LLM for product catalogue highlights...")
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = f"Write a 1-sentence product highlight for these items: {products_str}."

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(2.0)
        llm_output = f"[Simulated Highlight] Top items featured: {products_str}"
    else:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            res = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            llm_output = res.text.strip().replace("\n", " ")
        except Exception:
            await asyncio.sleep(2.0)
            llm_output = f"[Fallback Highlight] Featured catalog: {products_str}"

    # Signal ticker to stop and wait for it
    stop_event.set()
    await ticker_task

    print("  [Worker] Pipeline finished successfully!")
    return {"catalog": products_str, "ai_summary": llm_output}


def main_manual():
    print("=================================================================")
    print("  MODULE 06: MANUAL EVENT LOOP LIFECYCLE (new_event_loop & close)")
    print("=================================================================")

    # 1. Manually instantiate a fresh event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f"[Loop Setup] Instantiated new loop: {type(loop).__name__}")

    try:
        # 2. Run the worker coroutine until complete
        print("[Loop Exec] Calling loop.run_until_complete()...\n")
        start = time.perf_counter()
        result = loop.run_until_complete(database_and_llm_worker())
        elapsed = time.perf_counter() - start

        print(f"\n[Loop Result] Returned payload in {elapsed:.2f}s:")
        print(f"  Catalog   : {result['catalog']}")
        print(f"  AI Summary: {result['ai_summary']}")
    finally:
        # 3. Clean up and close the event loop instance
        print("\n[Loop Teardown] Closing event loop to release OS file & socket handles...")
        loop.close()
        print(f"[Loop Teardown] Is loop closed? {loop.is_closed()}")
        print("=================================================================\n")


if __name__ == "__main__":
    main_manual()
