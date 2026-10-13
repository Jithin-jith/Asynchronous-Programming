"""
===============================================================================
Module 13: Async Queue Producer-Consumer Pattern (SQLite + Gemini)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `asyncio.Queue(maxsize)`.
2. Multi-producer, multi-consumer asynchronous processing pipeline.
3. Decoupling SQLite data ingestion from Google Gemini LLM processing.
4. `queue.put()`, `queue.get()`, `queue.task_done()`, `queue.join()`.
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Producer: Fetches orders from `ecommerce.db` and pushes tasks into bounded queue.
- Consumers (Worker Pool of 2): Dequeue jobs, call Gemini LLM to draft order receipts,
  and mark tasks as done with `queue.task_done()`.
- `queue.join()`: Safely blocks until every queued order is fully processed.
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


async def order_producer(queue: asyncio.Queue):
    """Pulls orders from SQLite and feeds them into the processing queue."""
    print("[Producer] Connecting to ecommerce.db to load orders...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, user_id, product_name, total_amount FROM orders LIMIT 4") as cursor:
            orders = await cursor.fetchall()

    for o in orders:
        order_item = {"order_id": o[0], "user_id": o[1], "product": o[2], "amount": o[3]}
        print(f"  [Producer] Queuing Order #{order_item['order_id']} ({order_item['product']})...")
        await queue.put(order_item)
        await asyncio.sleep(0.05)

    print("[Producer] All orders enqueued successfully!")


async def ai_receipt_consumer(consumer_id: int, queue: asyncio.Queue, fallback_delay: float = 0.5):
    """Background consumer worker processing orders from queue via Gemini LLM."""
    api_key = os.getenv("GEMINI_API_KEY")
    while True:
        order = await queue.get()
        print(f"    [Consumer #{consumer_id}] Processing Order #{order['order_id']} ({order['product']})...")

        if not api_key or api_key.strip() in ("", "your_api_key_here"):
            await asyncio.sleep(fallback_delay)
            receipt = f"[Simulated Receipt] Thank you for ordering {order['product']} (${order['amount']:.2f})."
        else:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                res = await client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Generate a friendly 1-sentence receipt for buying {order['product']} (${order['amount']:.2f}).",
                )
                receipt = res.text.strip().replace("\n", " ")
            except Exception:
                await asyncio.sleep(fallback_delay)
                receipt = f"[Fallback Receipt] Order #{order['order_id']} confirmed."

        print(f"    [Consumer #{consumer_id}] Finished Order #{order['order_id']}: '{receipt}'")
        queue.task_done()


async def main():
    print("=================================================================")
    print("  MODULE 13: ASYNC QUEUE PRODUCER-CONSUMER (SQLITE -> GEMINI)")
    print("=================================================================")
    queue = asyncio.Queue(maxsize=10)

    # Start 2 worker consumers
    consumers = [
        asyncio.create_task(ai_receipt_consumer(1, queue)),
        asyncio.create_task(ai_receipt_consumer(2, queue)),
    ]

    # Run producer to load orders
    await order_producer(queue)

    print("\n[Main] Waiting for queue to drain...")
    await queue.join()  # Blocks until all items have task_done() acknowledged

    # Cancel consumer workers cleanly
    for c in consumers:
        c.cancel()

    print("[Main] All queue items processed. Consumers cleanly stopped!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
