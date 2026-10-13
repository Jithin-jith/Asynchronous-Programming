"""
===============================================================================
Module 15: FastAPI Main Async Application (SQLite + Gemini Streaming)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Native `async def` FastAPI route handlers with `aiosqlite` integration.
2. `FastAPI.BackgroundTasks` post-response background logging into SQLite.
3. Real-time Server-Sent Events (SSE) token streaming from Google Gemini via `StreamingResponse`.
4. Graceful fallback: If LLM subscription is not available, uses `asyncio.sleep()`.

HOW THIS CODE WORKS:
- `/api/products`: Async route querying `ecommerce.db` and scheduling a background audit log.
- `/api/stream`: Streams real-time tokens from Gemini LLM or simulated tokens in SSE format.
===============================================================================
"""

import os
import sys
import asyncio
import aiosqlite
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "ecommerce.db"
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="FastAPI Async Architecture Masterclass")


async def log_audit_to_db(endpoint: str):
    """Background worker task executed after HTTP response payload is returned to client."""
    print(f"  [Background Worker] Writing audit log for '{endpoint}' to SQLite...")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO ai_logs (prompt, response, model) VALUES (?, ?, ?)",
            (f"FastAPI Audit: {endpoint}", "HTTP 200 Delivered", "fastapi-runtime")
        )
        await db.commit()
    print(f"  [Background Worker] Audit log saved successfully for '{endpoint}'.")


@app.get("/")
async def root():
    return {
        "message": "FastAPI Async Architecture Engine Running",
        "database": "ecommerce.db",
        "status": "online"
    }


@app.get("/api/products")
async def get_products(background_tasks: BackgroundTasks):
    """Async non-blocking endpoint querying SQLite products."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, category, price FROM products") as cursor:
            rows = await cursor.fetchall()
            products = [{"id": r[0], "name": r[1], "category": r[2], "price": r[3]} for r in rows]

    # Schedule non-blocking background task to run after response delivery
    background_tasks.add_task(log_audit_to_db, "GET /api/products")
    return {"total": len(products), "products": products}


async def gemini_token_stream_generator():
    """Async generator yielding Server-Sent Event (SSE) formatted text chunks from Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = "Explain in 3 short bullet points why FastAPI async endpoints scale well."

    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        tokens = [
            "data: 1. Non-blocking I/O frees worker threads.\n\n",
            "data: 2. Single thread handles thousands of connections.\n\n",
            "data: 3. Seamless async database and AI integration.\n\n",
        ]
        for token in tokens:
            await asyncio.sleep(0.15)
            yield token
    else:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response_stream = await client.aio.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt
            )
            async for chunk in response_stream:
                # SSE format: data: <payload>\n\n
                clean_chunk = chunk.text.replace("\n", " ")
                yield f"data: {clean_chunk}\n\n"
        except Exception:
            yield "data: [Fallback] FastAPI async architecture enables high concurrency.\n\n"


@app.get("/api/stream")
async def stream_tokens():
    """Server-Sent Events (SSE) streaming response endpoint."""
    return StreamingResponse(gemini_token_stream_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
