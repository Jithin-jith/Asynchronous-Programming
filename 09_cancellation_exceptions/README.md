# Module 09: Cancellation, Timeouts & Exception Handling

## 📌 Executive Summary
Production asynchronous applications must anticipate network latency, service timeouts, and partial failures. This module demonstrates task cancellation semantics, enforcing strict HTTP response SLAs with `asyncio.wait_for()` and Python 3.11+ `asyncio.timeout()`, and handling concurrent error groups via `except*` using **SQLite operations** and **Google Gemini LLM calls**.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_task_cancellation.py` | Multi-step SQLite audit stream with manual cancellation | Catches `asyncio.CancelledError`, releases database connection in `finally:`, and re-raises. |
| `02_timeouts_wait_for.py` | Strict 0.5s SLA timeout on heavy Google Gemini prompt | Enforces timeouts using `wait_for` and `asyncio.timeout()`, automatically cancelling pending sockets. |
| `03_exception_handling_and_groups.py` | SQLite `OperationalError` + LLM parameter `ValueError` | Filters multiple concurrent errors from `ExceptionGroup` using Python 3.11+ `except*`. |

---

## 🏃 Expected Console Outputs

### Running `02_timeouts_wait_for.py`:
```text
=================================================================
  MODULE 09: ASYNC TIMEOUTS & SLA ENFORCEMENT (GEMINI LLM)
=================================================================
1. Enforcing 0.5s SLA via asyncio.wait_for()...
  [LLM Service] Dispatching complex prompt: 'Deep Architecture Analysis'...
  -> [TIMEOUT] Exceeded 0.5s SLA! LLM call was automatically cancelled.

2. Enforcing 0.5s SLA via Python 3.11+ asyncio.timeout()...
  [LLM Service] Dispatching complex prompt: 'Deep Architecture Analysis'...
  -> [TIMEOUT] Context manager triggered TimeoutError! Socket closed.
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why is it mandatory to re-raise `asyncio.CancelledError` inside an `except asyncio.CancelledError:` block?
   - *Answer*: If you suppress `CancelledError` without re-raising it, the task signals to the event loop that it completed successfully instead of being cancelled, breaking task management and structured concurrency contracts.
