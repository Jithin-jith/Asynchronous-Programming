"""
===============================================================================
Module 08: asyncio.gather() Basics & Order Preservation (Real I/O)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Concurrent Fan-Out and Join via `asyncio.gather(*coroutines)`.
2. Input order preservation: Return values match positional arguments regardless
   of which task finishes first.
3. Real-world tasks:
   - Service 1: Asynchronous SQLite user query (`aiosqlite`).
   - Service 2: Asynchronous SQLite product query (`aiosqlite`).
   - Service 3: Asynchronous Google Gemini LLM marketing generation (`client.aio`).
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Database tasks may finish in ~0.005s, while Gemini LLM takes ~2-4s.
- `asyncio.gather()` returns results matching the INPUT positional order:
  `[user_data, product_data, llm_insight]`.
===============================================================================
"""

import os
import sys
import time
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


async def fetch_user_service(user_id: int) -> dict:
    """Service 1: Queries user profile from SQLite."""
    print(f"[Service 1 - DB] Querying User #{user_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, role FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
    print(f"[Service 1 - DB] User #{user_id} retrieved successfully!")
    return {"user_id": row[0], "name": row[1], "role": row[2]}


async def fetch_product_service(product_id: int) -> dict:
    """Service 2: Queries product details from SQLite."""
    print(f"[Service 2 - DB] Querying Product #{product_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,)) as cursor:
            row = await cursor.fetchone()
    print(f"[Service 2 - DB] Product #{product_id} retrieved successfully!")
    return {"product_id": row[0], "product_name": row[1], "price": row[2]}


async def fetch_gemini_service(topic: str, fallback_delay: float = 1.0) -> str:
    """Service 3: Calls Google Gemini LLM API."""
    print(f"[Service 3 - LLM] Requesting summary from Gemini for: '{topic}'...")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Insight for {topic}]"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Summarize why {topic} is critical in modern software in 1 sentence.",
        )
        print("[Service 3 - LLM] Response received from Google Gemini!")
        return res.text.strip().replace("\n", " ")
    except Exception:
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Insight for {topic}]"


async def main():
    print("=================================================================")
    print("  MODULE 08: asyncio.gather() RESULT ORDER PRESERVATION (REAL I/O)")
    print("=================================================================")
    start_time = time.perf_counter()

    # Pass 3 distinct real-world services to asyncio.gather
    # Positional order: 1 = User Service, 2 = Product Service, 3 = Gemini Service
    user_res, prod_res, llm_res = await asyncio.gather(
        fetch_user_service(1),
        fetch_product_service(2),
        fetch_gemini_service("concurrency"),
    )

    elapsed = time.perf_counter() - start_time

    print(f"\n[SUMMARY] All gathered services completed in {elapsed:.2f}s!")
    print(f"Position 0 (User Service)   : {user_res}")
    print(f"Position 1 (Product Service): {prod_res}")
    print(f"Position 2 (Gemini Service) : '{llm_res}'")
    print("Notice: Results match positional input order, despite differing execution times!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
