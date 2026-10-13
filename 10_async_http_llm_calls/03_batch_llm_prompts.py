"""
===============================================================================
Module 10: Batching Multiple Concurrent Gemini LLM Prompts + DB Storage
===============================================================================

CONCEPTS DEMONSTRATED:
1. Concurrent LLM prompt batching.
2. `asyncio.gather(*tasks)` for API parallelization.
3. Concurrent persistence of LLM responses into SQLite `ecommerce.db`.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Defines 3 independent prompts.
- Schedules all 3 prompts concurrently using `asyncio.gather()`.
- Demonstrates massive latency reduction: Total time ≈ Max single request time.
- Asynchronously saves all answers into SQLite `ai_logs` table.
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

PROMPTS = [
    "List 3 key advantages of asyncio in Python.",
    "Summarize what an event loop is in one sentence.",
    "What is the difference between a Task and a Coroutine?",
]


async def ask_gemini_and_save(prompt_id: int, prompt: str, fallback_delay: float = 1.0) -> str:
    """Helper coroutine for requesting prompt generation and saving to SQLite."""
    print(f"  [Prompt #{prompt_id}] Sending to Gemini: '{prompt[:35]}...'")
    start_time = time.perf_counter()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(fallback_delay)
        answer = f"[Simulated Output for Prompt #{prompt_id}]"
    else:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            answer = response.text.strip()
        except Exception as exc:
            print(f"  [Prompt #{prompt_id}] Error ({exc.__class__.__name__}). Using fallback...")
            await asyncio.sleep(fallback_delay)
            answer = f"[Fallback Answer for Prompt #{prompt_id}]"

    elapsed = time.perf_counter() - start_time
    print(f"  [Prompt #{prompt_id}] Finished in {elapsed:.2f}s! Saving to SQLite...")

    # Log to SQLite ai_logs table
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO ai_logs (prompt, response, model) VALUES (?, ?, ?)",
            (prompt, answer[:200], "gemini-2.5-flash")
        )
        await db.commit()

    return f"--- Prompt #{prompt_id} Answer ---\n{answer}\n"


async def main():
    print(f"=== Sending {len(PROMPTS)} Concurrent Prompts to Gemini (Batch Parallelization) ===")
    total_start = time.perf_counter()

    # Schedule all 3 prompts concurrently on the event loop
    tasks = [ask_gemini_and_save(idx + 1, p) for idx, p in enumerate(PROMPTS)]
    answers = await asyncio.gather(*tasks)

    total_elapsed = time.perf_counter() - total_start
    print(f"\n[DONE] All {len(PROMPTS)} LLM responses received & stored in {total_elapsed:.2f}s!\n")
    print("=" * 65)
    for ans in answers:
        print(ans)
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
