# Module 02: I/O-Bound vs CPU-Bound Asynchronous Architecture

## 📌 Executive Summary
This module demonstrates why asynchronous concurrency is tailored specifically for **I/O-Bound workloads** (disk I/O with SQLite, network sockets with Google Gemini LLM) and acts as an anti-pattern when incorrectly applied to **CPU-Bound workloads** (pure mathematical computations, data transformations, encryption).

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 📖 Theoretical Deep Dive

### 1. I/O-Bound Operations (Where `asyncio` Shines)
An operation is I/O-bound when the execution speed is limited by external I/O devices (disk storage, database server engines, remote LLM HTTP API endpoints).
- In `01_io_bound_demo.py`, 5 distinct I/O operations are orchestrated concurrently:
  1. SQLite queries fetching users, products, and order revenue via `aiosqlite`.
  2. Google Gemini LLM text generation prompts via `client.aio.models.generate_content`.
- **Key Insight**: Over 95% of wall-clock time is spent waiting on external devices. The CPU thread is completely idle during this wait and can handle other ready tasks.

```
I/O Concurrency Timeline (Single OS Thread):
SQLite Users:    [Query]... (disk wait) ................... [Return Result]
SQLite Products: [Query]... (disk wait) ............. [Return Result]
SQLite Revenue:  [Query]... (disk wait) ....... [Return Result]
Gemini LLM 1:    [HTTP Send]............ (network wait) ................... [Return Result]
Gemini LLM 2:    [HTTP Send]............ (network wait) ................... [Return Result]
Loop Dispatcher: [========================= Event Loop =========================]

Total Duration ≈ Max(All I/O Latencies)
```

---

### 2. CPU-Bound Operations (The `async def` Anti-Pattern)
An operation is CPU-bound when the bottleneck is CPU instruction execution speed (crunching math, matrix multiplication, image filtering).
- In `02_cpu_bound_demo.py`, wrapping a 15-million iteration sum-of-squares function in `async def` does **NOT** achieve concurrency because there are no `await` yield points.
- The single Python thread is held captive, freezing the event loop.
- **Solution**: In `03_benchmarks.py`, CPU-bound tasks are offloaded to separate worker processes via `concurrent.futures.ProcessPoolExecutor`, bypassing Python's GIL.

---

## 💻 Script-by-Script Breakdown

| Script | Workload Type | Key Libraries / Concepts | Execution Outcome |
|---|---|---|---|
| `01_io_bound_demo.py` | **I/O-Bound** | `aiosqlite`, Google Gemini LLM (`google-genai`), `asyncio.gather` | 5 concurrent DB & LLM tasks finish in ~max delay (~7-8s) on a single thread. |
| `02_cpu_bound_demo.py` | **CPU-Bound Anti-Pattern** | Heavy math loop inside `async def` | Freezes the event loop; tasks run sequentially ($T_{total} = T_1 + T_2 + T_3 + T_4$). |
| `03_benchmarks.py` | **CPU Multiprocessing** | `ProcessPoolExecutor`, `loop.run_in_executor` | Offloads CPU tasks across CPU cores, achieving multi-core speedup. |

---

## 🏃 Expected Console Outputs

### Running `01_io_bound_demo.py`:
```text
=================================================================
  MODULE 02: 5 CONCURRENT REAL-WORLD I/O TASKS (SQLite + Gemini)
=================================================================
[I/O Task 1 - SQLite] Connecting to database to fetch users...
[I/O Task 2 - SQLite] Connecting to database to fetch products...
[I/O Task 3 - SQLite] Connecting to database to aggregate sales revenue...
[I/O Task 4 - LLM] Sending async prompt to Gemini API: 'Explain why SQLite and Asyncio pair well...'
[I/O Task 5 - LLM] Sending async prompt to Gemini API: 'Give 3 tips for optimizing LLM API...'
...
Total Wall-Clock Time: 7.71 seconds
TAKEAWAY: All 3 SQLite disk queries and 2 Gemini network calls ran
concurrently on a single thread. The event loop overlapped all I/O waits!
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why does `asyncio.gather()` achieve near $N\times$ speedup for SQLite and Gemini LLM calls, but $0\times$ speedup for sum-of-squares math?
   - *Answer*: SQLite and Gemini calls spend their time waiting for disk/network sockets, yielding CPU control via `await`. Sum-of-squares calculation continuously occupies CPU execution units without yielding, locking the single-threaded event loop.

2. **Practice Task**: If an LLM subscription or API key is not set, observe how `01_io_bound_demo.py` uses `await asyncio.sleep()` fallback to simulate the network latency.
