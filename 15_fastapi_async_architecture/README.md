# Module 15: FastAPI Asynchronous Architecture

## 📌 Executive Summary
FastAPI is natively built on top of Starlette and `asyncio`, offering asynchronous non-blocking routing, background tasks, and Server-Sent Events (SSE) token streaming. This module covers thread allocation rules (`async def` on Event Loop vs `def` in ThreadPool), dependency injection with **SQLite** (`aiosqlite`), and streaming **Google Gemini LLM tokens** via `StreamingResponse`.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `main.py` | FastAPI app with SQLite product catalog + Gemini SSE token streaming | Demonstrates non-blocking routes, background tasks, and streaming AI tokens. |
| `01_async_vs_sync_endpoints.py` | `/sync-blocking` (sqlite3 on worker thread) vs `/async-non-blocking` (aiosqlite on loop) | Proves thread allocation differences using `threading.current_thread().name`. |
| `02_background_tasks_db.py` | Order creation with `aiosqlite` dependency + background audit task | Demonstrates `Depends(get_db_connection)` yield pattern and `BackgroundTasks`. |

---

## 🏃 Running the FastAPI Application

```bash
uvicorn 15_fastapi_async_architecture.main:app --reload --port 8000
```
- Open documentation: `http://127.0.0.1:8000/docs`
- Stream Gemini tokens: `curl -N http://127.0.0.1:8000/api/stream`
