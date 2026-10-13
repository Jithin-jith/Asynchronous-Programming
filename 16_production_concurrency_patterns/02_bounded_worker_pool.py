"""
===============================================================================
Module 16: Bounded Async Worker Pool Pattern (Real SQLite Workload)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Fixed worker task allocation (`num_workers=3`).
2. Bounded input queue providing backpressure.
3. Decoupling batch ingestion from execution rate.
4. Clean queue draining and graceful teardown.

HOW THIS CODE WORKS:
- `BoundedWorkerPool` spawns exactly 3 background worker tasks.
- Submits product audit tasks loaded from `ecommerce.db`.
- Backpressure: If the queue reaches capacity, `submit_job()` pauses until workers consume.
===============================================================================
"""

import sys
import random
import asyncio
import aiosqlite
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


class BoundedWorkerPool:
    """Production-grade bounded worker pool manager."""

    def __init__(self, num_workers: int, queue_capacity: int):
        self.num_workers = num_workers
        self.queue = asyncio.Queue(maxsize=queue_capacity)
        self.workers = []
        self._running = False

    async def _worker_loop(self, worker_id: int):
        """Worker loop reading jobs from queue indefinitely."""
        while self._running:
            try:
                task_id, payload = await self.queue.get()
                print(f"  [Worker #{worker_id}] Auditing Product #{task_id} ({payload})...")
                await asyncio.sleep(random.uniform(0.1, 0.25))
                print(f"  [Worker #{worker_id}] Product #{task_id} Audit Completed.")
                self.queue.task_done()
            except asyncio.CancelledError:
                break

    async def start(self):
        """Starts worker tasks."""
        self._running = True
        self.workers = [
            asyncio.create_task(self._worker_loop(i + 1))
            for i in range(self.num_workers)
        ]
        print(f"[WorkerPool] Started {self.num_workers} background worker tasks.")

    async def submit_job(self, task_id: int, payload: str):
        """Submits job to queue. Applies backpressure if queue is at max capacity."""
        await self.queue.put((task_id, payload))

    async def shutdown(self):
        """Drains remaining queue jobs and shuts down worker pool cleanly."""
        print("[WorkerPool] Draining queue...")
        await self.queue.join()
        print("[WorkerPool] All jobs completed! Cancelling worker tasks...")
        self._running = False
        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        print("[WorkerPool] Pool shutdown successfully.")


async def main():
    print("=================================================================")
    print("  MODULE 16: BOUNDED ASYNC WORKER POOL (SQLITE AUDIT)")
    print("=================================================================")

    # Initialize pool with 3 workers and max queue capacity of 4
    pool = BoundedWorkerPool(num_workers=3, queue_capacity=4)
    await pool.start()

    # Load real product records from SQLite to feed the worker pool
    print("\n[Main] Loading products from ecommerce.db...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name FROM products") as cursor:
            products = await cursor.fetchall()

    print(f"[Main] Submitting {len(products)} product audit jobs to worker pool...")
    for p_id, p_name in products:
        await pool.submit_job(p_id, p_name)

    print("\n[Main] All jobs submitted. Initiating clean pool shutdown...")
    await pool.shutdown()
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
