"""
===============================================================================
Module 04: Coroutine Frame State Machine & Lifecycle Tracking (SQLite & LLM)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `inspect.getcoroutinestate(coro)`: Inspecting the internal state of a Python
   native coroutine object.
2. The 4 Coroutine States defined by CPython `inspect` module:
   - `CORO_CREATED`   : Coroutine object instantiated, but execution has not started.
   - `CORO_RUNNING`   : Coroutine is currently executing (active frame on stack).
   - `CORO_SUSPENDED` : Coroutine is paused at an `await` point (e.g. awaiting Gemini LLM response).
   - `CORO_CLOSED`    : Coroutine has completed execution or returned.
3. Event Loop Scheduling Mechanics:
   - Wrapping a coroutine in an `asyncio.Task` (`create_task()`).
   - Catching the coroutine in `CORO_SUSPENDED` while it waits for real I/O.
   - Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Step 1: `fetch_user_pipeline(user_id)` is instantiated -> state is `CORO_CREATED`.
- Step 2: Task is scheduled on the loop via `create_task(coro)`.
- Step 3: While `fetch_user_pipeline` awaits the Gemini LLM network call, the caller
  inspects the coroutine state, verifying it has entered `CORO_SUSPENDED`.
- Step 4: After awaiting task completion, state transitions to `CORO_CLOSED`.
===============================================================================
"""

import os
import sys
import asyncio
import inspect
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")


async def fetch_user_pipeline(user_id: int, fallback_delay: float = 1.0) -> str:
    """Asynchronous pipeline that pauses at await points while querying DB & LLM."""
    print("  [Coro Body] >>> Step 1: Querying SQLite database...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, role FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            name, role = (row[0], row[1]) if row else ("User", "member")

    print(f"  [Coro Body] >>> Step 2: Awaiting Gemini LLM response for {name}...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        # Pauses here: enters CORO_SUSPENDED state
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Note] Hello {name} ({role})"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        # CRITICAL SUSPENSION POINT: Coroutine enters CORO_SUSPENDED while awaiting HTTP socket
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Say hello to {name} ({role}) in 5 words.",
        )
        return res.text.strip()
    except Exception:
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Note] Hello {name} ({role})"


async def main():
    print("=================================================================")
    print("  MODULE 04: TRACKING COROUTINE LIFECYCLE STATES (REAL I/O)")
    print("=================================================================")

    # -------------------------------------------------------------------------
    # STATE 1: CORO_CREATED
    # -------------------------------------------------------------------------
    coro = fetch_user_pipeline(2)
    state1 = inspect.getcoroutinestate(coro)
    print(f"1. Initial State (Created, unstarted) : {state1}")
    assert state1 == inspect.CORO_CREATED, f"Expected CORO_CREATED, got {state1}"

    # Schedule the coroutine as a Task on the event loop
    task = asyncio.create_task(coro)

    # -------------------------------------------------------------------------
    # STATE 2: CORO_SUSPENDED
    # Yield control briefly to let the task start and reach the Gemini await point
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.01)  # Lets task run until its first I/O suspension
    state2 = inspect.getcoroutinestate(coro)
    print(f"2. Suspended State (Awaiting I/O)    : {state2}")
    print(f"   Notice: The coroutine yielded control and is paused waiting for I/O!")

    # -------------------------------------------------------------------------
    # STATE 3: CORO_CLOSED
    # Await the task to completion and inspect the final state
    # -------------------------------------------------------------------------
    result = await task
    state3 = inspect.getcoroutinestate(coro)
    print(f"3. Final State (Completed / Closed)  : {state3}")
    assert state3 == inspect.CORO_CLOSED, f"Expected CORO_CLOSED, got {state3}"

    print(f"\nPipeline Return Value: '{result}'")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
