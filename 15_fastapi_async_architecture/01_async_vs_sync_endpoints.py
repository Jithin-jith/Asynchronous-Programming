"""
===============================================================================
Module 15: Concurrency Breakdown - async def vs def Endpoints (Real SQLite)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Thread allocation differences between `async def` and standard `def` routes.
2. `threading.current_thread().name`.
3. Integrating SQLite queries in both sync and async FastAPI routes.

HOW THIS CODE WORKS:
- `/sync-blocking`: Defined with standard `def`. FastAPI delegates it to a worker thread pool.
  Inside, it executes synchronous `sqlite3` without blocking the main event loop.
- `/async-non-blocking`: Defined with `async def`. FastAPI executes it directly on the main
  event loop thread using `aiosqlite`.
===============================================================================
"""

import sys
import time
import asyncio
import sqlite3
import threading
import aiosqlite
from pathlib import Path
from fastapi import FastAPI

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"

app = FastAPI()


@app.get("/sync-blocking")
def sync_endpoint():
    """Standard 'def' route: FastAPI automatically runs this on a background worker thread."""
    thread_name = threading.current_thread().name
    print(f"[SYNC ROUTE] Executing on Thread: {thread_name}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    time.sleep(0.3)  # Safe: blocks only this worker thread, NOT the main event loop
    conn.close()

    return {"route": "def (sync)", "thread": thread_name, "products": count}


@app.get("/async-non-blocking")
async def async_endpoint():
    """Native 'async def' route: Executes directly on main Event Loop thread."""
    thread_name = threading.current_thread().name
    print(f"[ASYNC ROUTE] Executing on Thread: {thread_name}")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM products") as cursor:
            count = (await cursor.fetchone())[0]

    await asyncio.sleep(0.1)  # Non-blocking yield to main event loop
    return {"route": "async def", "thread": thread_name, "products": count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
