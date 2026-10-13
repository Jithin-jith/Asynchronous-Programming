# Module 13: Synchronization Primitives (Lock, Semaphore, Queue)

## 📌 Executive Summary
Concurrency introduces shared-state coordination challenges: race conditions on mutable data, API rate limits (HTTP 429), and decoupled workload balancing. This module covers `asyncio.Lock` for atomic critical sections, `asyncio.Semaphore` for **Google Gemini LLM rate limiting**, and `asyncio.Queue` for an asynchronous **SQLite-to-Gemini Producer-Consumer pipeline**.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_async_lock.py` | Concurrent inventory stock purchases | Eliminates race conditions across `await` points using `async with lock:`. |
| `02_semaphore_rate_limiting.py` | Google Gemini LLM API calls bounded to 2 concurrent | Prevents HTTP 429 quota exhaustion using `async with semaphore:`. |
| `03_async_queue_producer_consumer.py` | SQLite orders producer $\to$ Gemini receipt consumer | Decouples data ingestion from AI processing using an asynchronous bounded queue. |

---

## 🏃 Expected Console Outputs

### Running `02_semaphore_rate_limiting.py`:
```text
=================================================================
  MODULE 13: RATE LIMITING 6 REQUESTS TO MAX 2 CONCURRENT (GEMINI)
=================================================================
[Req #1] Waiting for an available Semaphore slot...
  --> [ACQUIRED] [Req #1] In Flight! (Active Concurrent: 1/2)
[Req #2] Waiting for an available Semaphore slot...
  --> [ACQUIRED] [Req #2] In Flight! (Active Concurrent: 2/2)
[Req #3] Waiting for an available Semaphore slot...
  <-- [RELEASED] [Req #1] Finished! Released Semaphore slot.
  --> [ACQUIRED] [Req #3] In Flight! (Active Concurrent: 2/2)
...
Takeaway: Semaphore prevented API rate limit spikes by bounding concurrency to 2!
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Since Python asyncio runs on a single thread, why is `asyncio.Lock` ever needed?
   - *Answer*: Because a coroutine yields control whenever it hits an `await` expression. If shared state is read before `await` and written after `await`, another concurrent task can interleave and mutate the state in between, causing lost updates or race conditions.
