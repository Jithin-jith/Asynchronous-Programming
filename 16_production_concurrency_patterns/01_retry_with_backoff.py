"""
===============================================================================
Module 16: Exponential Backoff with Jitter for Async API Calls (Google Gemini)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `async_retry_with_backoff` decorator.
2. Full Jitter formula: `delay = min(max_delay, base_delay * (2 ** attempt)) + jitter`.
3. Handling API rate limits, network blips, and transient service errors.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Decorator wraps `resilient_gemini_call(prompt)`.
- If an exception occurs, calculates exponential delay + randomized jitter and sleeps.
- Retries up to `max_retries` before re-raising.
===============================================================================
"""

import os
import sys
import random
import asyncio
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")


def async_retry_with_backoff(max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 4.0):
    """Decorator implementing exponential backoff with full jitter for async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        print(f"  [FAIL] Max retries ({max_retries}) exceeded. Raising exception...")
                        raise

                    # Exponential backoff formula with randomized full jitter
                    calculated_delay = min(max_delay, base_delay * (2 ** (retries - 1)))
                    jitter = random.uniform(0, calculated_delay)
                    actual_delay = calculated_delay + jitter

                    print(f"  [RETRY #{retries}] Caught '{e}'. Retrying in {actual_delay:.2f}s...")
                    await asyncio.sleep(actual_delay)
        return wrapper
    return decorator


@async_retry_with_backoff(max_retries=3, base_delay=0.5)
async def resilient_gemini_call(prompt: str, fallback_delay: float = 1.0) -> str:
    """Asynchronous Gemini API call protected by retry backoff decorator."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"  [Notice] GEMINI_API_KEY not set. Using fallback sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return "[Simulated Output] Retry with backoff guarantees resilient concurrency."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return res.text.strip().replace("\n", " ")
    except Exception as exc:
        # Raises to trigger exponential backoff retry loop
        raise RuntimeError(f"Gemini API transient failure: {exc}")


async def main():
    print("=================================================================")
    print("  MODULE 16: EXPONENTIAL BACKOFF WITH JITTER (GOOGLE GEMINI)")
    print("=================================================================")
    prompt = "Explain in one sentence why retry with exponential backoff is essential."
    print(f"Prompt: '{prompt}'\n")

    try:
        result = await resilient_gemini_call(prompt)
        print("\n--- Gemini Output ---")
        print(result)
    except Exception as e:
        print(f"\n[ERROR] All retries exhausted: {e}", file=sys.stderr)

    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
