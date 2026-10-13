"""
===============================================================================
Module 11: Offloading Sync Code with asyncio.to_thread() (Real SQLite)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `asyncio.to_thread(sync_func, *args)`.
2. Offloading legacy synchronous database drivers or blocking code to worker threads.
3. Preventing event loop starvation while running legacy synchronous `sqlite3` calls.

HOW THIS CODE WORKS:
- `asyncio.to_thread(sync_sqlite_heavy_query, "Threaded-Scan")` delegates execution
  to a worker thread from asyncio's default `ThreadPoolExecutor`.
- Result: The main thread event loop remains non-blocking and free!
- The background `heartbeat_ticker` continues pulsing smoothly while the SQLite query executes.
===============================================================================
"""

import sys
import time
import asyncio
import sqlite3
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


def sync_sqlite_heavy_query(label: str) -> str:
    """Synchronous database query executing isolated on a background worker thread."""
    print(f"  [THREAD] '{label}' running on worker thread...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), AVG(price) FROM products")
    row = cursor.fetchone()
    time.sleep(1.0)  # Blocking, but isolated on worker thread!
    conn.close()
    print(f"  [THREAD] '{label}' finished (Products: {row[0]}, Avg: ${row[1]:.2f}).")
    return f"Products: {row[0]}, Avg: ${row[1]:.2f}"


async def heartbeat_ticker():
    """Background heartbeat task expected to tick every 0.2s."""
    for i in range(5):
        print(f"  [Heartbeat] Pulse #{i+1}...")
        await asyncio.sleep(0.2)


async def main():
    print("=================================================================")
    print("  MODULE 11: SOLUTION DEMO: OFFLOADING WITH asyncio.to_thread()")
    print("=================================================================")

    # Start background heartbeat task
    heartbeat = asyncio.create_task(heartbeat_ticker())
    await asyncio.sleep(0.1)

    print("\n[Main] Offloading sync_sqlite_heavy_query to background worker thread...")
    print("[Main] Notice: Heartbeat continues pulsing concurrently without pausing!\n")

    # SOLUTION: Offload sync function to background thread pool (NON-BLOCKING for main loop!)
    result = await asyncio.to_thread(sync_sqlite_heavy_query, "Threaded-Scan")

    await heartbeat
    print(f"\n[Result] Returned from worker thread: '{result}'")
    print("Takeaway: asyncio.to_thread kept the event loop responsive!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
