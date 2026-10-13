"""
===============================================================================
Module 14: Async Generators Basics (Streaming SQLite Database Records)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `async def` with `yield` (Async Generator).
2. `AsyncGenerator[YieldType, SendType]`.
3. Consuming database streams asynchronously using `async for`.
4. Low memory consumption: Streams records row-by-row instead of loading all into RAM.

HOW THIS CODE WORKS:
- `stream_products_from_db()` yields product records one at a time from `ecommerce.db`.
- Main coroutine consumes stream using `async for product in stream:`.
===============================================================================
"""

import sys
import asyncio
import aiosqlite
from pathlib import Path
from typing import AsyncGenerator

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"


async def stream_products_from_db() -> AsyncGenerator[dict, None]:
    """Async generator streaming product rows from SQLite one by one."""
    print(f"[DB Stream] Connecting to {DB_PATH.name}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, category, price FROM products") as cursor:
            async for row in cursor:
                await asyncio.sleep(0.1)  # Simulate network cursor pagination
                yield {
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "price": row[3]
                }


async def main():
    print("=================================================================")
    print("  MODULE 14: STREAMING SQLITE RECORDS WITH ASYNC GENERATORS")
    print("=================================================================")

    stream = stream_products_from_db()

    async for item in stream:
        print(f" -> [Stream Received] #{item['id']} {item['name']:<25} | {item['category']:<10} | ${item['price']:.2f}")

    print("\n[DB Stream] All database records streamed successfully!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
