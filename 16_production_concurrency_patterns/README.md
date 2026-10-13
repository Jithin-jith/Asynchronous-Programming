# Module 16: Production Concurrency Patterns

## 📌 Executive Summary
Writing asynchronous code that executes successfully in isolation is different from deploying resilient, production-grade distributed architectures. This module synthesizes advanced operational patterns: **Exponential Backoff with Full Jitter** for API calls (Google Gemini LLM), **Bounded Worker Pools** with backpressure for SQLite audits, **Circuit Breakers** for fast failure recovery, and **Graceful Shutdown** with buffer flushing into SQLite.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_retry_with_backoff.py` | Google Gemini API call with exponential backoff + full jitter | Decorator catching transient network/quota errors and retrying with randomized delay. |
| `02_bounded_worker_pool.py` | SQLite products batch audit with fixed 3-worker pool | Implements backpressure via bounded `asyncio.Queue` to prevent memory blowups under load. |
| `03_circuit_breaker.py` | Fast-failing external outages (`CLOSED` $\to$ `OPEN` $\to$ `HALF-OPEN`) | Shields services from cascading failures by fast-rejecting requests during downtime. |
| `04_graceful_shutdown.py` | Signal cancellation + memory buffer flush to SQLite | Guarantees zero data loss during process termination by saving pending records in `finally:`. |

---

## 🏃 Expected Console Outputs

### Running `01_retry_with_backoff.py`:
```text
=================================================================
  MODULE 16: EXPONENTIAL BACKOFF WITH JITTER (GOOGLE GEMINI)
=================================================================
Prompt: 'Explain in one sentence why retry with exponential backoff is essential.'

--- Gemini Output ---
Retry with exponential backoff prevents thundering herds and allows transient service blips to recover gracefully.
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why is adding randomized "jitter" crucial in exponential backoff algorithms?
   - *Answer*: Without jitter, hundreds of failed client requests would retry at the exact same synchronized intervals ($2^1, 2^2, 2^3$), hitting the recovering server with synchronized waves of traffic ("thundering herd" problem). Full jitter spreads retry times across a randomized window.
