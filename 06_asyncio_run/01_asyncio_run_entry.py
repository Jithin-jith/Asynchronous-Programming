"""
===============================================================================
Module 06: Standard asyncio.run() Application Entry Point (Real I/O)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Standard application main entry point via `asyncio.run()`.
2. Automatic loop setup, main task execution, and teardown.
3. Real-world application startup pipeline:
   - Initializing SQLite database connection via `aiosqlite`.
   - Running an asynchronous Google Gemini LLM startup diagnostic check.
   - Graceful fallback: If LLM subscription is not available, user can use `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `if __name__ == "__main__":` invokes `asyncio.run(async_main())`.
- `asyncio.run()` creates a fresh loop, runs `async_main()`, closes background tasks,
  and shuts down the loop instance cleanly upon return.
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


async def verify_database_health() -> dict:
    """Queries SQLite database to verify data integrity at startup."""
    print("  [Startup 1/2] Connecting to SQLite database to verify tables...")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            user_count = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM orders") as cursor:
            order_count = (await cursor.fetchone())[0]

    print(f"  [Startup 1/2] Database verified: {user_count} users, {order_count} orders active.")
    return {"users": user_count, "orders": order_count}


async def run_ai_startup_diagnostic(db_stats: dict, fallback_delay: float = 1.0) -> str:
    """Invokes Google Gemini LLM for an application startup health message."""
    print("  [Startup 2/2] Querying Google Gemini LLM for system readiness report...")
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = (
        f"Generate a professional 1-sentence system readiness status message for an e-commerce platform "
        f"with {db_stats['users']} users and {db_stats['orders']} orders loaded."
    )

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"  [Startup 2/2] No API key. Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return f"[Simulated Diagnostic] All systems operational with {db_stats['users']} users."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return res.text.strip().replace("\n", " ")
    except Exception as exc:
        print(f"  [Startup 2/2] Gemini API error ({exc.__class__.__name__}). Using fallback sleep...")
        await asyncio.sleep(fallback_delay)
        return f"[Fallback Diagnostic] System operational with {db_stats['users']} users loaded."


async def async_main() -> str:
    """Root main coroutine representing full application lifecycle."""
    print("[Main Coroutine] Application startup sequence initialized.")
    db_stats = await verify_database_health()
    diagnostic = await run_ai_startup_diagnostic(db_stats)
    print(f"[Main Coroutine] Diagnostic Report: {diagnostic}")
    print("[Main Coroutine] Startup tasks completed successfully.")
    return "SUCCESS_CODE_0"


if __name__ == "__main__":
    print("=================================================================")
    print("  MODULE 06: LAUNCHING APPLICATION VIA asyncio.run() (REAL I/O)")
    print("=================================================================")
    exit_status = asyncio.run(async_main())
    print(f"\nApplication returned exit status: '{exit_status}'")
    print("=================================================================\n")
