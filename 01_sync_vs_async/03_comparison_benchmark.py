"""
===============================================================================
Module 01: Side-by-Side Performance Comparison Benchmark
===============================================================================

CONCEPTS DEMONSTRATED:
1. Benchmarking execution speedup factor: Speedup = Sync Time / Async Time.
2. Real-world I/O workload benchmarking:
   - Synchronous: Sequential SQLite queries (`sqlite3`) and Gemini LLM calls (or fallback sleep).
   - Asynchronous: Concurrent SQLite queries (`aiosqlite`) and Gemini LLM calls via `asyncio.gather()`.
3. Mathematical verification of N-task latency scaling:
   - Sync Time  = Sum(T_1 + T_2 + ... + T_n)
   - Async Time = Max(T_1, T_2, ..., T_n)

BENCHMARK SETUP:
- Tasks: 4 user profiles (User IDs 1 through 4)
- Work per Task: SQLite customer & order lookup + Gemini LLM personalized note
- If LLM subscription is not available, uses fallback simulation sleep so benchmarks
  still execute cleanly and demonstrate concurrency.
===============================================================================
"""

import os
import sys
import time
import asyncio
import sqlite3
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")

USER_IDS = [1, 2, 3, 4]


# -----------------------------------------------------------------------------
# 1. SYNCHRONOUS PIPELINE IMPLEMENTATION
# -----------------------------------------------------------------------------
def sync_worker(user_id: int) -> dict:
    """Executes SQLite query and Gemini LLM call sequentially (blocking)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    name = row[1] if row else f"User_{user_id}"
    role = row[2] if row else "customer"

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip() not in ("", "your_api_key_here"):
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"Write a 5-word greeting for {name} ({role})."
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            result = resp.text.strip()
        except Exception:
            time.sleep(1.0)
            result = f"Hello {name}, welcome back!"
    else:
        time.sleep(1.0)
        result = f"Hello {name}, welcome back!"

    return {"id": user_id, "name": name, "note": result}


def run_sync_benchmark() -> float:
    """Runs all users sequentially."""
    start = time.perf_counter()
    results = [sync_worker(uid) for uid in USER_IDS]
    duration = time.perf_counter() - start
    print(f" -> Synchronous completed {len(results)} users in {duration:.2f}s")
    return duration


# -----------------------------------------------------------------------------
# 2. ASYNCHRONOUS PIPELINE IMPLEMENTATION
# -----------------------------------------------------------------------------
async def async_worker(user_id: int) -> dict:
    """Executes SQLite query and Gemini LLM call concurrently (non-blocking)."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, role FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()

    name = row[1] if row else f"User_{user_id}"
    role = row[2] if row else "customer"

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip() not in ("", "your_api_key_here"):
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"Write a 5-word greeting for {name} ({role})."
            resp = await client.aio.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            result = resp.text.strip()
        except Exception:
            await asyncio.sleep(1.0)
            result = f"Hello {name}, welcome back!"
    else:
        await asyncio.sleep(1.0)
        result = f"Hello {name}, welcome back!"

    return {"id": user_id, "name": name, "note": result}


async def run_async_benchmark() -> float:
    """Runs all users concurrently using asyncio.gather()."""
    start = time.perf_counter()
    tasks = [async_worker(uid) for uid in USER_IDS]
    results = await asyncio.gather(*tasks)
    duration = time.perf_counter() - start
    print(f" -> Asynchronous completed {len(results)} users in {duration:.2f}s")
    return duration


def main():
    print("=================================================================")
    print(f"  BENCHMARK: SYNCHRONOUS VS ASYNCHRONOUS ({len(USER_IDS)} Real SQLite + LLM Tasks)")
    print("=================================================================")

    # 1. Run Synchronous Benchmark
    print("\n1. Executing Synchronous Sequential Pipeline (One by One)...")
    sync_duration = run_sync_benchmark()

    # 2. Run Asynchronous Benchmark
    print("\n2. Executing Asynchronous Concurrent Pipeline (Overlapped)...")
    async_duration = asyncio.run(run_async_benchmark())

    # 3. Calculate Speedup
    speedup = sync_duration / async_duration if async_duration > 0 else 0.0

    print("\n=================================================================")
    print("                      BENCHMARK RESULTS                          ")
    print("=================================================================")
    print(f" Synchronous Total Duration : {sync_duration:.2f} seconds")
    print(f" Asynchronous Total Duration: {async_duration:.2f} seconds")
    print(f" Performance Acceleration  : [SPEEDUP] {speedup:.2f}x Faster!")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
