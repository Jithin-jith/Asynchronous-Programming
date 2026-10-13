"""
===============================================================================
Module 04: Native Coroutines with `async def` (SQLite + Gemini LLM)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Defining native coroutines via `async def`.
2. Lazy evaluation:
   - Calling an `async def` function does NOT execute any code inside its body!
   - It does not open a database connection or send any HTTP requests to Gemini.
   - It only returns a dormant coroutine object in memory.
3. Executing coroutine objects via `asyncio.run()`.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `fetch_user_and_generate_ai_greeting(user_id)`:
  - Connects to `ecommerce.db` asynchronously via `aiosqlite`.
  - Generates a personalized greeting using Google Gemini LLM.
- Calling `coro_obj = fetch_user_and_generate_ai_greeting(1)` returns the coroutine object.
- We inspect `type(coro_obj)` and verify nothing has executed yet.
- Finally, `asyncio.run(coro_obj)` binds the coroutine to the event loop and executes it.
===============================================================================
"""

import os
import sys
import asyncio
import inspect
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")


async def fetch_user_and_generate_ai_greeting(user_id: int, fallback_delay: float = 1.0) -> str:
    """Native coroutine that queries SQLite and calls Google Gemini LLM."""
    print(f"\n  [Coro Body] >>> Coroutine execution STARTED for User #{user_id}!")
    
    # 1. Asynchronous SQLite Query
    print(f"  [Coro Body] Querying {DB_PATH.name}...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, role FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            name, role = (row[0], row[1]) if row else ("Valued Customer", "member")
    print(f"  [Coro Body] Retrieved user: {name} ({role})")

    # 2. Asynchronous Gemini LLM Call
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"  [Coro Body] No API key. Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return f"[Simulated AI Greeting] Welcome back, {name} ({role})!"

    try:
        from google import genai
        print(f"  [Coro Body] Calling Google Gemini API for personalized greeting...")
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Generate a warm, professional 1-sentence welcome greeting for {name}, an esteemed {role}.",
        )
        return res.text.strip()
    except Exception as exc:
        print(f"  [Coro Body] Gemini error ({exc.__class__.__name__}). Using fallback sleep...")
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Greeting] Welcome {name}, esteemed {role}."


def main():
    print("=================================================================")
    print("  MODULE 04: NATIVE COROUTINES & LAZY EVALUATION (REAL I/O)")
    print("=================================================================")
    
    # STEP 1: Calling the async def function does NOT execute its body code!
    print("Step 1: Invoking 'fetch_user_and_generate_ai_greeting(1)'...")
    coro_obj = fetch_user_and_generate_ai_greeting(1)

    print(f"  -> Type of returned object : {type(coro_obj)}")
    print(f"  -> Is it a coroutine object?: {asyncio.iscoroutine(coro_obj)}")
    print(f"  -> Inspect iscoroutine()    : {inspect.iscoroutine(coro_obj)}")
    print("  -> NOTICE: '[Coro Body] >>>' has NOT been printed! No database or Gemini calls happened yet.\n")

    # STEP 2: Execute the coroutine object with asyncio.run()
    print("Step 2: Now executing coroutine object with asyncio.run(coro_obj)...")
    result = asyncio.run(coro_obj)
    
    print("\n---------------- Final Returned Result ----------------")
    print(f"  {result}")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
