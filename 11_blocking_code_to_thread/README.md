# Module 11: Offloading Blocking Synchronous Code to Threads

## 📌 Executive Summary
While greenfield code should use non-blocking asynchronous drivers (`aiosqlite`, `httpx`, `client.aio`), production systems inevitably encounter legacy synchronous libraries, synchronous file systems, or blocking database drivers. This module demonstrates the catastrophic impact of executing synchronous code directly inside an event loop and shows how to safely offload it using `asyncio.to_thread()` and custom `ThreadPoolExecutor` instances.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_blocking_problem_demo.py` | Synchronous `sqlite3` table scan on event loop | Demonstrates how calling synchronous database code directly on the loop starves background heartbeat tasks. |
| `02_asyncio_to_thread.py` | Synchronous `sqlite3` offloaded to `asyncio.to_thread` | Delegates synchronous execution to a worker thread pool, keeping the main loop responsive. |
| `03_custom_executor.py` | Bounded `ThreadPoolExecutor(max_workers=2)` for DB audits | Limits concurrent worker threads to protect CPU cores and memory pools from thread bloat. |

---

## 🏃 Expected Console Outputs

### Running `02_asyncio_to_thread.py`:
```text
=================================================================
  MODULE 11: SOLUTION DEMO: OFFLOADING WITH asyncio.to_thread()
=================================================================
  [Heartbeat] Pulse #1...

[Main] Offloading sync_sqlite_heavy_query to background worker thread...
  [THREAD] 'Threaded-Scan' running on worker thread...
  [Heartbeat] Pulse #2...
  [Heartbeat] Pulse #3...
  [Heartbeat] Pulse #4...
  [THREAD] 'Threaded-Scan' finished (Products: 5, Avg: $173.50).
  [Heartbeat] Pulse #5...

[Result] Returned from worker thread: 'Products: 5, Avg: $173.50'
Takeaway: asyncio.to_thread kept the event loop responsive!
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: When should you use `asyncio.to_thread()` versus `loop.run_in_executor()`?
   - *Answer*: Use `asyncio.to_thread()` (Python 3.9+) for simple, one-off synchronous calls using the default thread pool. Use `loop.run_in_executor()` when you need a custom bounded `ThreadPoolExecutor` (e.g. limiting DB connections) or `ProcessPoolExecutor` (for CPU-bound parallelism).
