"""
===============================================================================
Module 09: Async Timeouts with wait_for and asyncio.timeout (Gemini LLM SLA)
===============================================================================

CONCEPTS DEMONSTRATED:
1. `asyncio.wait_for(coro, timeout)`: Enforcing strict latency SLAs.
2. Python 3.11+ `async with asyncio.timeout(delay):` context manager.
3. Real-world scenario: An LLM API request takes longer than the allowed HTTP SLA
   (e.g. 0.5s limit on a multi-second LLM query).
4. Automatic cancellation of the underlying in-flight task upon timeout.
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Section 1: Calls Gemini with a 0.5s timeout via `wait_for`.
- Section 2: Calls Gemini with a 0.5s timeout via `asyncio.timeout()`.
- Both enforce timeout cancellation without leaking socket resources.
===============================================================================
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")


async def slow_gemini_llm_call(prompt: str, simulated_delay: float = 3.0) -> str:
    """Simulates a heavy LLM prompt that takes multiple seconds."""
    print(f"  [LLM Service] Dispatching complex prompt: '{prompt}'...")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        await asyncio.sleep(simulated_delay)
        return "[Simulated LLM Output]"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        # Detailed multi-step reasoning prompt that takes several seconds
        res = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Provide a detailed 500-word comprehensive architectural analysis of distributed event loops.",
        )
        return res.text.strip()
    except asyncio.CancelledError:
        print("  [LLM Service] Task cancelled mid-request due to SLA timeout!")
        raise


async def main():
    print("=================================================================")
    print("  MODULE 09: ASYNC TIMEOUTS & SLA ENFORCEMENT (GEMINI LLM)")
    print("=================================================================")

    # 1. Using asyncio.wait_for() with strict 0.5s timeout
    print("1. Enforcing 0.5s SLA via asyncio.wait_for()...")
    try:
        result = await asyncio.wait_for(
            slow_gemini_llm_call("Deep Architecture Analysis"),
            timeout=0.5
        )
        print(f"Result: {result[:50]}...")
    except TimeoutError:
        print("  -> [TIMEOUT] Exceeded 0.5s SLA! LLM call was automatically cancelled.\n")

    # 2. Using Python 3.11+ asyncio.timeout() context manager
    print("2. Enforcing 0.5s SLA via Python 3.11+ asyncio.timeout()...")
    try:
        async with asyncio.timeout(0.5):
            result = await slow_gemini_llm_call("Deep Architecture Analysis")
            print(f"Result: {result[:50]}...")
    except TimeoutError:
        print("  -> [TIMEOUT] Context manager triggered TimeoutError! Socket closed.\n")

    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
