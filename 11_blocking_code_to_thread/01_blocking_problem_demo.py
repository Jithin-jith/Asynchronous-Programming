"""
===============================================================================
Module 11: The Sync Blocking Problem Demo (Synchronous SQLite in Async Loop)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Impact of synchronous blocking calls (e.g. standard `sqlite3` or `time.sleep`)
   executed directly on the asyncio event loop thread.
2. Event Loop stoppage: All other concurrent coroutines (e.g. heartbeat/websockets)
   freeze completely because the single main thread is held captive.

HOW THIS CODE WORKS:
- A background `heartbeat_task` is scheduled to tick every 0.2s.
- Main coroutine directly invokes `sync_sqlite_heavy_query()` (synchronous `sqlite3`).
- Result: Heartbeat output stops completely until the synchronous database operation finishes!
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
    """Synchronous database query simulating legacy blocking library code."""
    print(f"  [SYNC DB] '{label}' started (BLOCKING MAIN THREAD!)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Complex query + artificial pause simulating large un-indexed table scan
    cursor.execute("SELECT COUNT(*), AVG(price) FROM products")
    row = cursor.fetchone()
    time.sleep(1.0)  # Blocking sleep on the main thread!
    conn.close()
    print(f"  [SYNC DB] '{label}' finished (Products: {row[0]}, Avg: ${row[1]:.2f}).")
    return f"Products: {row[0]}"


async def heartbeat_ticker():
    """Background heartbeat task expected to tick every 0.2s."""
    for i in range(5):
        print(f"  [Heartbeat] Pulse #{i+1}...")
        await asyncio.sleep(0.2)


async def main():
    print("=================================================================")
    print("  MODULE 11: SYNC BLOCKING PROBLEM DEMO (LEGACY SQLITE ON LOOP)")
    print("=================================================================")

    # Start background heartbeat task
    heartbeat = asyncio.create_task(heartbeat_ticker())
    await asyncio.sleep(0.1)

    print("\n[Main] Invoking sync_sqlite_heavy_query DIRECTLY on the event loop thread...")
    print("[Main] Notice: The heartbeat freezes completely during this call!\n")
    
    # ANTI-PATTERN: Calling synchronous blocking function directly on event loop!
    sync_sqlite_heavy_query("Sync-Legacy-Scan")

    print("\n[Main] Blocking call finished. Resuming event loop...")
    await heartbeat
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
