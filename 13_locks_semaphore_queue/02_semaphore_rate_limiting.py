"""
===============================================================================
Module 13: Rate Limiting with asyncio.Semaphore (Google Gemini LLM)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `asyncio.Semaphore(value)`: Bounding concurrent in-flight requests.
2. Restricting concurrent Gemini LLM API calls to prevent HTTP 429 Too Many Requests.
3. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Instantiates `api_semaphore = asyncio.Semaphore(2)` (Max 2 concurrent calls).
- Dispatches 6 concurrent user prompt requests.
- `async with api_semaphore:` ensures at most 2 requests call Gemini simultaneously.
- Remaining requests wait cooperatively in the queue until slots are released.
===============================================================================
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# Limit concurrent Gemini LLM API requests to 2
api_semaphore = asyncio.Semaphore(2)
active_concurrent_calls = 0


async def rate_limited_gemini_call(req_id: int, fallback_delay: float = 1.0) -> str:
    """Sends a prompt to Gemini governed strictly by the semaphore limit."""
    global active_concurrent_calls

    print(f"[Req #{req_id}] Waiting for an available Semaphore slot...")
    async with api_semaphore:
        active_concurrent_calls += 1
        print(f"  --> [ACQUIRED] [Req #{req_id}] In Flight! (Active Concurrent: {active_concurrent_calls}/2)")
        t0 = time.perf_counter()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.strip() in ("", "your_api_key_here"):
            await asyncio.sleep(fallback_delay)
            res_text = f"Simulated Response #{req_id}"
        else:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                res = await client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Say 'Request #{req_id} approved' in 3 words.",
                )
                res_text = res.text.strip().replace("\n", " ")
            except Exception:
                await asyncio.sleep(fallback_delay)
                res_text = f"Fallback Response #{req_id}"

        active_concurrent_calls -= 1
        duration = time.perf_counter() - t0
        print(f"  <-- [RELEASED] [Req #{req_id}] Finished in {duration:.2f}s! Released Semaphore slot.")
        return res_text


async def main():
    print("=================================================================")
    print("  MODULE 13: RATE LIMITING 6 REQUESTS TO MAX 2 CONCURRENT (GEMINI)")
    print("=================================================================")
    start_time = time.perf_counter()

    tasks = [rate_limited_gemini_call(i) for i in range(1, 7)]
    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time
    print(f"\n[SUMMARY] All {len(results)} rate-limited requests completed in {elapsed:.2f}s!")
    print(f"Sample Results: {results[:3]}")
    print("Takeaway: Semaphore prevented API rate limit spikes by bounding concurrency to 2!")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
