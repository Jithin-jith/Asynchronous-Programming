"""
===============================================================================
Module 16: Graceful Event Loop Shutdown & SQLite Buffer Flush
===============================================================================

CONCEPTS DEMONSTRATED:
1. Graceful task cancellation upon application shutdown request.
2. `try...finally` resource cleanup and pending buffer flush to SQLite `ecommerce.db`.
3. Ensuring zero data loss when terminating async daemons or background workers.

HOW THIS CODE WORKS:
- Background worker buffers audit events in memory.
- Upon receiving a shutdown / cancellation signal, catches `CancelledError`.
- Flushes remaining buffered items directly into SQLite `ecommerce.db` before closing.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


async def background_sqlite_telemetry_worker():
    """Background telemetry worker that flushes buffer to SQLite on shutdown."""
    buffer = ["metric_cpu_load=45%", "metric_memory_used=62%", "metric_active_conn=128"]
    print("  [Telemetry] Worker running... Holding 3 telemetry metrics in memory buffer.")

    try:
        while True:
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        print("\n  [Telemetry] Received shutdown signal! Flushing memory buffer to SQLite...")
        async with aiosqlite.connect(DB_PATH) as db:
            for item in buffer:
                await db.execute(
                    "INSERT INTO ai_logs (prompt, response, model) VALUES (?, ?, ?)",
                    ("Telemetry Shutdown Flush", item, "telemetry-worker")
                )
            await db.commit()
        print(f"  [Telemetry] Successfully flushed {len(buffer)} records to ecommerce.db!")
        print("  [Telemetry] Clean worker shutdown complete.")
        raise


async def main():
    print("=================================================================")
    print("  MODULE 16: GRACEFUL EVENT LOOP SHUTDOWN & SQLITE FLUSH")
    print("=================================================================")

    # Spawn long-running background worker
    worker = asyncio.create_task(background_sqlite_telemetry_worker(), name="TelemetryDaemon")

    # Let worker run for 0.4s
    await asyncio.sleep(0.4)

    # Initiate graceful shutdown
    print("\n[Shutdown Manager] SIGINT / Stop signal received! Initiating shutdown...")
    worker.cancel()

    try:
        await worker
    except asyncio.CancelledError:
        print("[Shutdown Manager] Confirmed: Worker caught cancel and flushed buffer cleanly.")

    print("\nApplication shutdown safely with ZERO data loss!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
