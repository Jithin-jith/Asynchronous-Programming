"""
===============================================================================
Module 08: Exception Handling in gather() (`return_exceptions=True`)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `return_exceptions=False` (default, fail-fast) vs `return_exceptions=True` (resilient).
2. Safe batch exception handling across database queries and LLM requests.
3. Real-world scenario: An API gateway queries 3 backends concurrently:
   - Request 1: Valid SQLite user query.
   - Request 2: Faulty SQLite query targeting a non-existent table (raises OperationalError).
   - Request 3: Valid Google Gemini LLM API call.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Setting `return_exceptions=True` prevents a single failing operation from crashing
  the entire batch.
- The caught `Exception` object is placed inside the returned list at the failing index.
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


async def valid_db_query(user_id: int) -> dict:
    """Valid SQLite query."""
    print(f"  [Task 1 - DB] Querying User #{user_id}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, email FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
    return {"user": row[0], "email": row[1]}


async def faulty_db_query() -> dict:
    """Faulty SQLite query intentionally referencing a non-existent table."""
    print("  [Task 2 - DB] Executing query on non-existent table...")
    async with aiosqlite.connect(DB_PATH) as db:
        # Intentionally malformed table name
        async with db.execute("SELECT * FROM non_existent_table") as cursor:
            await cursor.fetchall()
    return {"status": "unreachable"}


async def valid_llm_query(fallback_delay: float = 1.0) -> str:
    """Valid Gemini LLM query."""
    print("  [Task 3 - LLM] Sending prompt to Google Gemini...")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        return "[Simulated Gemini Insight]"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'Resilient Concurrency' in 2 words.",
        )
        return res.text.strip().replace("\n", " ")
    except Exception:
        await asyncio.sleep(fallback_delay)
        return "[Fallback LLM Insight]"


async def main():
    print("=================================================================")
    print("  MODULE 08: gather() WITH return_exceptions=True (REAL I/O)")
    print("=================================================================")

    # return_exceptions=True captures exceptions directly into results list
    results = await asyncio.gather(
        valid_db_query(1),
        faulty_db_query(),
        valid_llm_query(),
        return_exceptions=True
    )

    print("\n---------------- Batch Inspection Results ----------------")
    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            print(f" Position [{idx}]: [CAUGHT EXCEPTION] -> {type(res).__name__}: {res}")
        else:
            print(f" Position [{idx}]: [SUCCESS VALUE]    -> {res}")
    print("----------------------------------------------------------")
    print("Takeaway: Position [1] failed without cancelling Task 0 or Task 2!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
