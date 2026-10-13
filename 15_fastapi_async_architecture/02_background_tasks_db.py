"""
===============================================================================
Module 15: Async Database Session Dependency Injection (Real SQLite)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `Depends(get_db_connection)`.
2. Asynchronous yield dependency pattern for `aiosqlite`.
3. Integrating database sessions with `FastAPI.BackgroundTasks`.
4. Writing background order audits into SQLite `ecommerce.db`.

HOW THIS CODE WORKS:
- `get_db_connection()` yields an `aiosqlite.Connection` per HTTP request.
- Automatically handles closing connection after HTTP response is returned.
- A post-request background task logs completion into `ecommerce.db`.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI, Depends, BackgroundTasks

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"

app = FastAPI()


async def get_db_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """FastAPI Async DB Dependency Injection yielding aiosqlite connection."""
    conn = await aiosqlite.connect(DB_PATH)
    try:
        yield conn
    finally:
        await conn.close()


async def process_post_request_audit(order_id: int):
    """Async background task executed after response payload delivery."""
    print(f"  [Background Worker] Writing post-request audit for order #{order_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO ai_logs (prompt, response, model) VALUES (?, ?, ?)",
            (f"Order #{order_id} Created", "Audit Confirmed", "fastapi-background-worker")
        )
        await db.commit()
    print(f"  [Background Worker] Order #{order_id} audit saved to SQLite!")


@app.post("/orders")
async def create_order(
    user_id: int,
    product_name: str,
    amount: float,
    bg_tasks: BackgroundTasks,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """API endpoint consuming async DB connection and attaching background worker."""
    cursor = await db.execute(
        """
        INSERT INTO orders (user_id, product_name, quantity, total_amount, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, product_name, 1, amount, "completed")
    )
    await db.commit()
    new_order_id = cursor.lastrowid

    # Attach background task to log audit after response returns
    bg_tasks.add_task(process_post_request_audit, new_order_id)
    return {"status": "created", "order_id": new_order_id, "amount": amount}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
