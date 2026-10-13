# Module 08: `asyncio.gather()` & Python 3.11+ `TaskGroup`

## 📌 Executive Summary
Concurrent fan-out and join patterns allow multiple coroutines to execute simultaneously on the event loop and aggregate their returned values. This module contrasts legacy unstructured concurrency via `asyncio.gather()` (order preservation, `return_exceptions=True`) against modern structured concurrency via Python 3.11+ `asyncio.TaskGroup` using **SQLite database queries** and **Google Gemini LLM calls**.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_gather_basics.py` | Concurrent SQLite user query + SQLite product query + Gemini LLM call | Demonstrates positional argument order preservation in returned results. |
| `02_gather_return_exceptions.py` | Valid DB query + Faulty DB query (non-existent table) + Gemini LLM call | Shows how `return_exceptions=True` captures exceptions into the results list without aborting valid operations. |
| `03_modern_task_group.py` | Structured `TaskGroup` with DB read, service fault, and long Gemini call | Illustrates structured concurrency: automatically cancels sibling tasks and wraps errors in `ExceptionGroup`. |

---

## 🏃 Expected Console Outputs

### Running `01_gather_basics.py`:
```text
=================================================================
  MODULE 08: asyncio.gather() RESULT ORDER PRESERVATION (REAL I/O)
=================================================================
[Service 1 - DB] Querying User #1...
[Service 2 - DB] Querying Product #2...
[Service 3 - LLM] Requesting summary from Gemini for: 'concurrency'...
[Service 1 - DB] User #1 retrieved successfully!
[Service 2 - DB] Product #2 retrieved successfully!
[Service 3 - LLM] Response received from Google Gemini!

[SUMMARY] All gathered services completed!
Position 0 (User Service)   : {'user_id': 1, 'name': 'Alice Johnson', 'role': 'admin'}
Position 1 (Product Service): {'product_id': 2, 'product_name': 'Vector Database License', 'price': 199.5}
Position 2 (Gemini Service) : 'Concurrency maximizes throughput by overlapping independent tasks.'
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: What is the key advantage of `asyncio.TaskGroup` over `asyncio.gather()`?
   - *Answer*: `TaskGroup` guarantees structured concurrency: if any task raises an exception, all other active tasks in the group are automatically cancelled, eliminating orphaned background tasks.
