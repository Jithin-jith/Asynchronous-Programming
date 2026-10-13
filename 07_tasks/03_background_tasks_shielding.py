"""
===============================================================================
Module 07: Background Task References & Task Shielding (Real SQLite Tx)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Retaining strong references to background tasks to prevent Garbage Collection (GC).
2. Shielding critical operations from outer cancellation via `asyncio.shield()`.
3. Real-world scenario: An order payment/confirmation must commit to SQLite
   even if the caller's HTTP request connection disconnects or times out.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `background_tasks.add(task)` maintains a strong set reference so the task isn't GC'd.
- `asyncio.shield(task)` wraps the task in a protective shield.
- Cancelling the outer shielded wrapper raises `CancelledError` locally, but the
  inner critical SQLite transaction task continues executing to safe commit!
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

background_tasks = set()


async def critical_order_transaction(user_id: int, product_name: str, amount: float) -> str:
    """Critical transaction that MUST complete and commit to SQLite even if outer context is cancelled."""
    print("  [Critical DB Tx] Starting order write to SQLite...")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO orders (user_id, product_name, quantity, total_amount, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, product_name, 1, amount, "completed")
        )
        await db.commit()
        
    print(f"  [Critical DB Tx] Order for '{product_name}' (${amount:.2f}) committed safely!")
    return f"ORDER_COMMITTED_{product_name.replace(' ', '_').upper()}"


async def main():
    print("=================================================================")
    print("  MODULE 07: TASK SHIELDING & GC PROTECTION (CRITICAL SQLITE TX)")
    print("=================================================================")

    # 1. Best practice for background tasks: prevent premature garbage collection
    critical_task = asyncio.create_task(
        critical_order_transaction(1, "Async Shield License", 149.00),
        name="CriticalOrderCommitTask"
    )
    background_tasks.add(critical_task)
    critical_task.add_done_callback(background_tasks.discard)

    # 2. Shield the critical task from outer cancellation
    shielded_wrapper = asyncio.shield(critical_task)

    # Simulate client disconnect after 0.001s: cancel the outer shielded task
    await asyncio.sleep(0.001)
    print("\n[Main Web Handler] Client connection disconnected! Cancelling outer request...")
    shielded_wrapper.cancel()

    try:
        await shielded_wrapper
    except asyncio.CancelledError:
        print("[Main Web Handler] Caught CancelledError on outer request wrapper!")

    # 3. CRITICAL OBSERVATION: The inner database write continues and finishes!
    await critical_task
    print(f"\n[Result] Did critical SQLite transaction survive? {critical_task.done()}")
    print(f"[Result] Inner Transaction Result: '{critical_task.result()}'")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
