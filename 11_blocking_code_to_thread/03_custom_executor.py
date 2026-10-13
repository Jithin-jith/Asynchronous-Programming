"""
===============================================================================
Module 11: Custom ThreadPoolExecutor with loop.run_in_executor (Real SQLite)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `ThreadPoolExecutor(max_workers=2)`.
2. `loop.run_in_executor(executor, sync_func, *args)`.
3. Controlling maximum thread concurrency for legacy synchronous database operations.

HOW THIS CODE WORKS:
- Configures a custom `ThreadPoolExecutor` bounded to exactly 2 worker threads.
- Submits 4 blocking synchronous SQLite queries.
- Exactly 2 tasks run concurrently at any time; remaining 2 wait in the executor queue.
===============================================================================
"""

import sys
import time
import asyncio
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


def blocking_sqlite_table_audit(worker_id: int, table_name: str) -> dict:
    """Synchronous database audit function run inside custom thread pool."""
    print(f"  [Worker {worker_id}] Auditing table '{table_name}' on worker thread...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    time.sleep(0.4)  # Simulate complex table scan
    conn.close()
    print(f"  [Worker {worker_id}] Finished '{table_name}': {count} rows.")
    return {"worker_id": worker_id, "table": table_name, "count": count}


async def main():
    print("=================================================================")
    print("  MODULE 11: CUSTOM ThreadPoolExecutor (max_workers=2) (SQLITE)")
    print("=================================================================")
    loop = asyncio.get_running_loop()

    tables = ["users", "products", "orders", "ai_logs"]

    # Create bounded thread pool with exactly 2 threads
    with ThreadPoolExecutor(max_workers=2) as executor:
        print("[Main] Submitting 4 table audits to bounded 2-thread pool...\n")
        futures = [
            loop.run_in_executor(executor, blocking_sqlite_table_audit, idx + 1, table)
            for idx, table in enumerate(tables)
        ]
        results = await asyncio.gather(*futures)

    print("\n---------------- Audit Results ----------------")
    for r in results:
        print(f"  * Table: {r['table']:<10} -> {r['count']} rows (Worker #{r['worker_id']})")
    print("-----------------------------------------------")
    print("Takeaway: ThreadPoolExecutor bounded thread concurrency to 2 workers!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
