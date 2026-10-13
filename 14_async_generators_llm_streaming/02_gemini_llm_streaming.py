"""
===============================================================================
Module 14: Real-time Google Gemini LLM Response Streaming
===============================================================================

CONCEPTS DEMONSTRATED:
1. `client.aio.models.generate_content_stream`.
2. Measuring Time-To-First-Token (TTFT) latency.
3. Real-time streaming output in terminal console via `async for`.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Reads `GEMINI_API_KEY` from environment variables / `.env`.
- If available, calls `generate_content_stream(model="gemini-2.5-flash", contents=prompt)`.
- If key is missing or quota is hit, simulates token streaming with `await asyncio.sleep(0.1)`.
- Loops through token chunks via `async for chunk in response_stream:`.
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


async def simulate_streaming_tokens(text: str):
    """Simulates token streaming via async generator fallback."""
    words = text.split(" ")
    for w in words:
        await asyncio.sleep(0.08)
        yield w + " "


async def stream_gemini_response(prompt: str):
    """Streams response tokens from Google Gemini API in real-time."""
    api_key = os.getenv("GEMINI_API_KEY")

    print(f"Prompt: '{prompt}'")
    print("--- Streaming Gemini Output Tokens ---")
    start_time = time.perf_counter()
    first_token = True

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print("\n[Notice] GEMINI_API_KEY not set. Using simulated streaming with asyncio.sleep()...\n")
        simulated_haiku = "Loop turns endlessly, / Coroutines wake on signal, / Code flows without wait."
        async for chunk in simulate_streaming_tokens(simulated_haiku):
            if first_token:
                print(f"[TTFT] Time To First Token: {time.perf_counter() - start_time:.3f}s\n")
                first_token = False
            print(chunk, end="", flush=True)
    else:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response_stream = await client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt
            )

            async for chunk in response_stream:
                if first_token:
                    ttft = time.perf_counter() - start_time
                    print(f"\n[TTFT] Time To First Token: {ttft:.3f}s\n")
                    first_token = False
                print(chunk.text, end="", flush=True)
        except Exception as exc:
            print(f"\n[Notice] Gemini API unavailable ({exc.__class__.__name__}). Using fallback simulation...\n")
            simulated_haiku = "Silent event loop, / Pausing gently on await, / Waking in good time."
            async for chunk in simulate_streaming_tokens(simulated_haiku):
                print(chunk, end="", flush=True)

    elapsed = time.perf_counter() - start_time
    print(f"\n\n--- Stream Completed in {elapsed:.2f}s ---")


async def main():
    print("=================================================================")
    print("  MODULE 14: REAL-TIME GOOGLE GEMINI TOKEN STREAMING")
    print("=================================================================")
    prompt = "Write a haiku about Python asyncio and event loops."
    await stream_gemini_response(prompt)
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
