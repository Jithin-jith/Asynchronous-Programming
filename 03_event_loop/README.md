# Module 03: The Event Loop & Operating System Multiplexers

## 📌 Executive Summary
The **Event Loop** is the central orchestrator of `asyncio`. It maintains execution queues, coordinates monotonic clocks, fires scheduled callbacks, and interfaces directly with OS kernel multiplexers (`epoll`, `kqueue`, Windows `IOCP`) to monitor **SQLite file I/O** and **Google Gemini LLM network sockets** without polling or thread freezing.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 📖 Theoretical Deep Dive

### 1. Loop Clock Progression Across Real I/O
The event loop maintains an internal high-resolution monotonic clock (`loop.time()`) guaranteed never to jump backwards due to NTP updates or clock shifts.
- In `01_event_loop_basics.py`, we execute an asynchronous SQLite query via `aiosqlite` and an asynchronous Google Gemini LLM API call.
- Measuring `loop.time()` demonstrates how the internal loop clock advances across real disk and network delays.

```
Event Loop Monotonic Timeline:
Start (t=0.000s) ---> [aiosqlite query (~0.001s)] ---> [Gemini LLM API (~6.0s)] ---> Finish (t=6.001s)
```

---

### 2. Timers and Callbacks alongside Real Concurrency
In `02_callbacks_and_timers.py`, synchronous callbacks are registered directly on the loop:
- `loop.call_soon()`: Immediate execution on the very next loop tick (e.g. initialization logging).
- `loop.call_later()`: Relative delay (e.g. database cache eviction).
- `loop.call_at()`: Absolute monotonic timestamp (e.g. LLM rate limit token refill).
- Crucially, these callbacks fire smoothly on schedule *while* the event loop is concurrently awaiting an SQLite query and Gemini LLM response.

---

### 3. OS-Level Multiplexers Under the Hood
In `03_under_the_hood_selector.py`, we inspect the operating system multiplexer powering the event loop:
- **Linux**: `epoll`
- **macOS / BSD**: `kqueue`
- **Windows**: `IOCP` (`ProactorEventLoop`)
These low-level kernel APIs allow the operating system to notify Python the instant network packets arrive from Google Gemini or when SQLite finishes writing bytes to disk.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_event_loop_basics.py` | Asynchronous SQLite admin lookup + Gemini LLM definition | Inspects `loop.is_running()`, `loop.time()` across real database and AI network delays. |
| `02_callbacks_and_timers.py` | Database telemetry callbacks + Async DB order query + Gemini call | Shows how `call_soon`, `call_later`, and `call_at` fire during concurrent I/O. |
| `03_under_the_hood_selector.py` | OS multiplexer inspection (`epoll`, `kqueue`, `IOCP`) | Reveals how the kernel wakes async coroutines when DB/LLM packets arrive. |

---

## 🏃 Expected Console Outputs

### Running `01_event_loop_basics.py`:
```text
=================================================================
  MODULE 03: EVENT LOOP INSPECTION WITH REAL SQLITE & GEMINI I/O
=================================================================
Running Event Loop Instance: ProactorEventLoop
Is Loop Running?           : True
Is Loop Closed?            : False

[Step 1] Executing asynchronous SQLite query...
  -> DB Result: Admin: Alice Johnson (alice@example.com)
  -> Loop Monotonic Clock after DB: 1826224.4370s (Delta: 0.0000s)

[Step 2] Executing asynchronous Google Gemini LLM call...
  -> LLM Result: Continuously executes queued tasks, managing asynchronous, non-blocking operations.
  -> Loop Monotonic Clock after LLM: 1826230.5150s (Delta: 6.0780s)
Total Loop Time Elapsed: 6.0780s
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why does `loop.time()` use a monotonic clock instead of system wall-clock time (`time.time()`)?
   - *Answer*: Monotonic clocks are guaranteed never to jump backwards (e.g. during daylight saving changes or NTP sync), ensuring timers in `loop.call_later()` never trigger prematurely or hang indefinitely.

2. **Practice Task**: If no `GEMINI_API_KEY` is provided in `.env`, verify that `01_event_loop_basics.py` falls back to `asyncio.sleep()` cleanly.
