"""
===============================================================================
Module 10: Google Gemini Async LLM Call & SQLite Persistence
===============================================================================

CONCEPTS DEMONSTRATED:
1. `google.genai` SDK `Client` initialization with environment `GEMINI_API_KEY`.
2. Asynchronous LLM generation via `client.aio.models.generate_content`.
3. Non-blocking await for Gemini response payload.
4. Asynchronous persistence of LLM responses into SQLite `ecommerce.db` (`ai_logs` table).
5. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- Retrieves `GEMINI_API_KEY` from environment / `.env`.
- If available, calls Google Gemini API via `client.aio`.
- Persists the generated response into `ecommerce.db` asynchronously via `aiosqlite`.
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


async def log_ai_interaction_to_db(prompt: str, response_text: str, model: str):
    """Asynchronously logs the prompt and LLM response into SQLite ai_logs table."""
    print("  [DB Logger] Saving interaction to ecommerce.db ai_logs table...")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO ai_logs (prompt, response, model)
            VALUES (?, ?, ?)
            """,
            (prompt, response_text, model)
        )
        await db.commit()
    print("  [DB Logger] Successfully logged LLM generation record!")


async def generate_gemini_response(prompt: str, fallback_delay: float = 1.0) -> str:
    """Sends an asynchronous prompt generation request to Google Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"  [Notice] GEMINI_API_KEY not set. Falling back to await asyncio.sleep({fallback_delay}s)...")
        await asyncio.sleep(fallback_delay)
        return "[Simulated Gemini Response] Asynchronous I/O prevents server threads from stalling during LLM generation."

    try:
        from google import genai
        print("[Gemini] Connecting to Gemini API via client.aio...")
        client = genai.Client(api_key=api_key)
        
        # Non-blocking async API call using client.aio
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"  [Notice] Gemini API call error ({exc.__class__.__name__}). Falling back to sleep...")
        await asyncio.sleep(fallback_delay)
        return "[Fallback Response] Asynchronous I/O overlaps waiting times across external services."


async def main():
    print("=================================================================")
    print("  MODULE 10: ASYNC GOOGLE GEMINI API CALL + SQLITE LOGGING")
    print("=================================================================")
    prompt = "Explain why asynchronous I/O is ideal for LLM applications in 2 sentences."
    print(f"Prompt: '{prompt}'\n")

    reply = await generate_gemini_response(prompt)
    print("--- Gemini Response ---")
    print(reply)
    print("-----------------------\n")

    # Persist the output in SQLite
    await log_ai_interaction_to_db(prompt, reply, "gemini-2.5-flash")
    print("=================================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
