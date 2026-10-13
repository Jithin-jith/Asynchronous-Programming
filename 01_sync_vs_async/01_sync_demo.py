"""
===============================================================================
Module 01: Synchronous Execution Demo (Sequential & Blocking)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Sequential execution flow (Line-by-line processing).
2. Thread blocking during real-world I/O:
   - Synchronous SQLite database queries via Python's standard `sqlite3` module.
   - Synchronous HTTP network calls to Google Gemini LLM (with fallback to sleep).
3. Cumulative total latency calculation: Total Time = sum(Individual Latencies).

HOW THIS CODE WORKS:
- `fetch_user_and_generate_summary_sync(user_id)`:
  1. Opens a synchronous connection to `ecommerce.db` and queries user & order stats.
  2. Calls Google Gemini LLM synchronously to generate a personalized customer note.
     (Note: If LLM subscription is not available, falls back to time.sleep() simulation).
- The `main()` loop calls `fetch_user_and_generate_summary_sync` for 3 users sequentially.
- Because each call halts the thread, User 2 cannot start until User 1 finishes,
  and User 3 cannot start until User 2 finishes.

EXPECTED OUTPUT:
- User 1 starts -> queries SQLite -> queries LLM -> completes
- User 2 starts -> queries SQLite -> queries LLM -> completes
- User 3 starts -> queries SQLite -> queries LLM -> completes
- Total execution time: Sum of all latencies (Sequential).
===============================================================================
"""

import os
import sys
import time
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in sys.path to locate ecommerce.db and .env
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")


def query_user_from_db_sync(user_id: int) -> dict:
    """Connects to SQLite database synchronously and queries user details and orders."""
    print(f"[SYNC DB] Opening connection to {DB_PATH.name} for User #{user_id}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.id, u.name, u.email, u.role, u.status, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = ?
        GROUP BY u.id
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "status": row[4],
            "order_count": row[5]
        }
    return {"id": user_id, "name": f"User_{user_id}", "status": "unknown", "order_count": 0}


def generate_llm_insight_sync(user_data: dict, fallback_delay: float = 1.0) -> str:
    """Calls Google Gemini LLM synchronously to generate a customer summary note.
    
    If LLM subscription is not available, uses time.sleep() to execute code.
    """
    prompt = (
        f"Generate a friendly 1-sentence welcome summary for customer {user_data['name']} "
        f"who has role '{user_data['role']}' and {user_data['order_count']} orders."
    )
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        print(f"[SYNC LLM] No API key found. Falling back to time.sleep({fallback_delay}s)...")
        time.sleep(fallback_delay)
        return f"[Simulated Note] Welcome {user_data['name']}! Thank you for being a valued {user_data['role']}."

    try:
        from google import genai
        print(f"[SYNC LLM] Sending prompt to Google Gemini for {user_data['name']} (BLOCKING thread)...")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"[SYNC LLM] Gemini call failed ({exc.__class__.__name__}). Falling back to time.sleep({fallback_delay}s)...")
        time.sleep(fallback_delay)
        return f"[Fallback Note] Welcome {user_data['name']}, active {user_data['role']} member."


def fetch_user_and_generate_summary_sync(user_id: int) -> dict:
    """Orchestrates sequential synchronous operations: SQLite Query -> LLM Call."""
    print(f"\n[SYNC Worker] >>> Starting pipeline for User #{user_id}...")
    t0 = time.perf_counter()

    # Step 1: Synchronous Database Query
    user_data = query_user_from_db_sync(user_id)
    print(f"[SYNC DB] Retrieved: {user_data['name']} ({user_data['role']}, {user_data['order_count']} orders)")

    # Step 2: Synchronous Gemini LLM Call (blocks the thread)
    note = generate_llm_insight_sync(user_data, fallback_delay=1.0)
    user_data["ai_note"] = note

    duration = time.perf_counter() - t0
    print(f"[SYNC Worker] <<< Completed User #{user_id} in {duration:.2f}s")
    return user_data


def main():
    """Main execution entry point demonstrating sequential blocking execution."""
    print("=================================================================")
    print("  MODULE 01: SYNCHRONOUS EXECUTION DEMO (SQLite + Gemini LLM)")
    print("=================================================================")
    start_time = time.perf_counter()

    users = []
    # Sequential Loop: Each iteration MUST complete before the next iteration can start.
    for user_id in range(1, 4):
        profile = fetch_user_and_generate_summary_sync(user_id)
        users.append(profile)

    total_time = time.perf_counter() - start_time

    print("\n---------------- Synchronous Summary ----------------")
    for u in users:
        print(f" * User #{u['id']} ({u['name']}): {u['ai_note']}")
    print("-----------------------------------------------------")
    print(f"Total Processed     : {len(users)} users")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print("Observation: Total time equals the SUM of all database queries and LLM requests.")
    print("             Because each step blocked the thread, subsequent users had to wait.")
    print("=================================================================\n")


if __name__ == "__main__":
    main()
