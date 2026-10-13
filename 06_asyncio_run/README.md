# Module 06: `asyncio.run()` & The Event Loop Lifecycle

## 📌 Executive Summary
`asyncio.run()` is the standard modern top-level entry point for any asyncio application in Python 3.7+. It encapsulates the entire lifecycle of the event loop: creating a fresh loop instance, setting it as the thread default, executing the root coroutine to completion, cancelling remaining background tasks, and shutting down thread resources cleanly.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 📖 Theoretical Deep Dive

### 1. What `asyncio.run(main())` Automates
Under the hood, `asyncio.run()` performs 6 critical lifecycle phases:
1. **Loop Creation**: `loop = asyncio.new_event_loop()`.
2. **Loop Registration**: `asyncio.set_event_loop(loop)`.
3. **Execution**: `loop.run_until_complete(main())`.
4. **Task Cancellation**: Finds all uncompleted tasks (`asyncio.all_tasks(loop)`), calls `task.cancel()`, and runs the loop until cancellations are processed.
5. **Async Generator Cleanup**: `loop.run_until_complete(loop.shutdown_asyncgens())`.
6. **Teardown**: `loop.close()` and `asyncio.set_event_loop(None)`.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_asyncio_run_entry.py` | SQLite health check + Gemini startup diagnostics | Demonstrates standard top-level application startup with automatic lifecycle teardown. |
| `02_loop_lifecycle.py` | Manual loop management (`new_event_loop`, `run_until_complete`, `close`) | Shows low-level loop control while running a DB & LLM worker alongside a concurrent progress ticker. |
| `03_nested_run_anti_pattern.py` | Real SQLite database query subtask | Explains why calling `asyncio.run()` inside an active async coroutine raises `RuntimeError` and how `await` resolves it. |

---

## 🏃 Expected Console Outputs

### Running `01_asyncio_run_entry.py`:
```text
=================================================================
  MODULE 06: LAUNCHING APPLICATION VIA asyncio.run() (REAL I/O)
=================================================================
[Main Coroutine] Application startup sequence initialized.
  [Startup 1/2] Connecting to SQLite database to verify tables...
  [Startup 1/2] Database verified: 5 users, 5 orders active.
  [Startup 2/2] Querying Google Gemini LLM for system readiness report...
[Main Coroutine] Diagnostic Report: System online and ready.
[Main Coroutine] Startup tasks completed successfully.

Application returned exit status: 'SUCCESS_CODE_0'
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why can you not call `asyncio.run()` inside a FastAPI route or another `async def` function?
   - *Answer*: Because an event loop is already actively running on that thread. Calling `asyncio.run()` attempts to initialize a second event loop on the same thread, raising `RuntimeError: asyncio.run() cannot be called from a running event loop`. Instead, simply `await` the coroutine.
