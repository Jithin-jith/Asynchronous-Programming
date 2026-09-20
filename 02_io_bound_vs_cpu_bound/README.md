# Module 02: I/O-Bound vs CPU-Bound Workloads

## 📌 Executive Summary
A common misconception in Python asynchronous programming is assuming that wrapping CPU-intensive code in an `async def` function will automatically make it run faster or run in parallel. This module clarifies the fundamental distinction between **I/O-Bound** and **CPU-Bound** workloads, details CPython's **Global Interpreter Lock (GIL)**, demonstrates the single-threaded nature of the `asyncio` event loop, and introduces multi-core offloading strategies using `ProcessPoolExecutor`.

---

## 📖 Theoretical Deep Dive

### 1. Workload Categorization Matrix

```text
                                WORKLOAD TYPE MATRIX
                           /                            \
                          /                              \
                I/O-Bound Tasks                   CPU-Bound Tasks
           (Network, Disk, Databases)        (Math, AI/ML, Parsing)
                      |                                  |
          Spends time waiting for external     Spends time actively utilizing
          devices (Sockets, Disks, APIs).      CPU ALU registers & core caches.
                      |                                  |
               OPTIMAL SOLUTION:                OPTIMAL SOLUTION:
                    asyncio                       Multiprocessing
             (Single-Thread Event Loop)      (ProcessPoolExecutor / C-Ext)
```

#### A. I/O-Bound Tasks
- **Characteristics**: Execution throughput is bottlenecked by external system latency (e.g. HTTP response packet arrival, database query execution, filesystem disk reads).
- **CPU Behavior**: The CPU is ~99% idle during execution, waiting for hardware or network interrupts.
- **Concurrency Strategy**: `asyncio` multiplexes thousands of concurrent requests on a single OS thread using non-blocking OS primitives (e.g., `epoll`, `kqueue`, `select`, IOCP).

#### B. CPU-Bound Tasks
- **Characteristics**: Execution throughput is bottlenecked by raw CPU clock speed and arithmetic processing capacity (e.g., matrix operations, image rendering, cryptographic hashing, parsing massive payloads).
- **CPU Behavior**: A CPU core is pinned at 100% utilization throughout computation.
- **Python's GIL Bottleneck**: In standard CPython, the **Global Interpreter Lock (GIL)** prevents multiple OS threads from executing Python bytecode in parallel on a single process. Because `asyncio` runs on a **single OS thread**, wrapping a CPU-bound function in `async def` does **NOT** parallelize calculation — it locks the main thread and freezes the event loop.

---

## 🔬 Under the Hood: CPython GIL & Execution Architecture

```text
                       CPYTHON GIL CONTEXT SWITCHING
                       
   Thread 1: [=== Holds GIL: Run Bytecode ===] -- (GIL Released) --> [Waiting for GIL]
   Thread 2: [Waiting for GIL] --------------> [Holds GIL: Run Bytecode]
```

- **Pure Asyncio**: Interleaves non-blocking I/O operations on a single thread by yielding control (`await`) during socket/timer waits. It does NOT bypass the GIL.
- **Multiprocessing (`ProcessPoolExecutor`)**: Spawns multiple independent child OS processes, each with its own CPython interpreter instance and GIL. This unlocks true multi-core hardware parallelism (e.g. 4 cores = 4 concurrent Python processes).

---

## 💻 Script-by-Script Breakdown & Line-by-Line Guide

### 1. [`01_io_bound_demo.py`](file:///f:/Projects/Asynchronous-Programming/02_io_bound_vs_cpu_bound/01_io_bound_demo.py)
* **Goal**: Demonstrate how non-blocking cooperative multitasking yields the CPU during I/O waits, overlapping request latencies.
* **Key Concept**: Total execution time equals $\max(t_1, t_2, \dots, t_n)$, NOT $\sum(t_i)$.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L23-L39** | `simulate_io_request` | Simulates a remote HTTP request with `await asyncio.sleep(duration)` non-blocking yield. |
| **L36** | `await asyncio.sleep(duration)` | **Cooperative Yield Point**: Instructs event loop to suspend task and run other coroutines while timer ticks. |
| **L47-L53** | `tasks = [simulate_io_request(...)]` | Instantiates 5 un-awaited coroutine objects with latencies `[1.0s, 0.8s, 1.2s, 0.5s, 1.5s]`. |
| **L56** | `await asyncio.gather(*tasks)` | Schedules all 5 coroutines on the event loop concurrently and waits for completion. |
| **L65** | `asyncio.run(main())` | Initializes event loop, runs `main()`, and cleans up loop resources upon completion. |

---

### 2. [`02_cpu_bound_demo.py`](file:///f:/Projects/Asynchronous-Programming/02_io_bound_vs_cpu_bound/02_cpu_bound_demo.py)
* **Goal**: Demonstrate the **CPU-Bound Anti-Pattern** in pure `asyncio`.
* **Key Concept**: Simply placing `async def` in front of a function containing no `await` expressions will **NOT** make it non-blocking. Execution remains strictly sequential ($T_{\text{total}} = T_1 + T_2 + T_3 + T_4$).

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L44-L65** | `compute_heavy_math(n)` | Synchronous CPU-bound sum-of-squares calculation loop ($N = 15,000,000$). Holds GIL continuously. |
| **L68-L88** | `async_wrapper(n)` | **Anti-Pattern Coroutine**: Wraps `compute_heavy_math` in `async def` without `await`. Blocks main thread upon entry. |
| **L99** | `tasks = [async_wrapper(...) for _ in range(4)]` | Instantiates 4 coroutine objects holding CPU calculations. |
| **L106** | `await asyncio.gather(*tasks)` | Event loop attempts to gather tasks, but Task 1 blocks the main thread for ~2s. Tasks 2, 3, 4 execute sequentially. |
| **L124** | `asyncio.run(main())` | Starts single-threaded event loop execution. |

---

### 3. [`03_benchmarks.py`](file:///f:/Projects/Asynchronous-Programming/02_io_bound_vs_cpu_bound/03_benchmarks.py)
* **Goal**: Benchmark Pure Asyncio (Sequential Main Thread) vs `ProcessPoolExecutor` (Multi-Core Multiprocessing).
* **Key Concept**: Bypassing the GIL by offloading CPU workloads to worker processes via `loop.run_in_executor()`.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L24-L27** | `cpu_work(n)` | Synchronous sum-of-squares computation function submitted to process workers. |
| **L29-L34** | `run_pure_asyncio(counts)` | Runs CPU tasks sequentially on the main thread as a baseline benchmark. |
| **L36-L46** | `run_multiprocessing(counts)` | **Proper Multi-Core Solution**: Offloads CPU work to separate OS child processes. |
| **L39** | `loop = asyncio.get_running_loop()` | Obtains active event loop reference required for executor registration. |
| **L42** | `with ProcessPoolExecutor() as pool:` | Spawns worker process pool (one process per CPU core, each with independent GIL). |
| **L43** | `loop.run_in_executor(pool, cpu_work, c)` | Converts process submission into an awaitable `asyncio.Future` without blocking the main loop. |
| **L44** | `await asyncio.gather(*futures)` | Main thread non-blockingly waits for child process completion signals. |
| **L63** | `speedup = pure_time / mp_time` | Calculates multi-core performance acceleration ratio (~3.0x - 4.0x speedup). |

---

## 🏃 Console Outputs & Benchmarks

### 1. `01_io_bound_demo.py` Output:
```text
=== Simulating 5 Concurrent I/O Network Requests ===
[I/O Task] Request #1 sent to remote server (latency: 1.0s)...
[I/O Task] Request #2 sent to remote server (latency: 0.8s)...
[I/O Task] Request #3 sent to remote server (latency: 1.2s)...
[I/O Task] Request #4 sent to remote server (latency: 0.5s)...
[I/O Task] Request #5 sent to remote server (latency: 1.5s)...
[I/O Task] Request #4 response received after 0.5s!
[I/O Task] Request #2 response received after 0.8s!
[I/O Task] Request #1 response received after 1.0s!
[I/O Task] Request #3 response received after 1.2s!
[I/O Task] Request #5 response received after 1.5s!

[SUMMARY] Successfully processed 5 I/O requests!
[SUMMARY] Total Wall-Clock Time : 1.51 seconds
[SUMMARY] Max Single Delay      : 1.50 seconds
[SUMMARY] Sum of All Delays     : 5.00 seconds
---------------------------------------------------------------------------
TAKEAWAY: Execution completed in ~1.5s (the maximum single delay) instead of
5.0s (the sum) because asyncio overlapped all network waiting times concurrently!
---------------------------------------------------------------------------
```

### 2. `02_cpu_bound_demo.py` Output:
```text
=== Running CPU-Bound Calculations Sequentially in Async Event Loop ===
[CPU Task] Calculating sum of squares for N = 15,000,000...
[CPU Task] Finished calculation for N = 15,000,000
[CPU Task] Calculating sum of squares for N = 15,000,000...
[CPU Task] Finished calculation for N = 15,000,000
[CPU Task] Calculating sum of squares for N = 15,000,000...
[CPU Task] Finished calculation for N = 15,000,000
[CPU Task] Calculating sum of squares for N = 15,000,000...
[CPU Task] Finished calculation for N = 15,000,000

[SUMMARY] Completed 4 CPU-bound tasks in 9.28 seconds!
---------------------------------------------------------------------------
[WARNING] NOTICE THE ANTI-PATTERN:
  1. Even though we used 'asyncio.gather', execution was STRICTLY SEQUENTIAL.
  2. Total time equals the SUM of all 4 task durations (T1 + T2 + T3 + T4).
  3. Reason: asyncio handles single-threaded I/O concurrency, NOT CPU parallelism.
  4. Solution: For CPU-bound tasks, use Multiprocessing (ProcessPoolExecutor)
     to utilize multiple CPU cores and bypass the CPython GIL.
---------------------------------------------------------------------------
```

### 3. `03_benchmarks.py` Output:
```text
=================================================================
   CPU-BOUND BENCHMARK: PURE ASYNCIO vs PROCESS POOL EXECUTOR    
=================================================================

1. Running Pure Asyncio (Main Thread Sequential)...
   Pure Asyncio Duration : 7.2140 seconds

2. Running ProcessPoolExecutor (Multi-Core Parallel)...
   ProcessPool Duration  : 2.1580 seconds

=================================================================
 [SPEEDUP] Multiprocessing Acceleration: 3.34x Faster!
=================================================================
```

---

## ❓ Exercises & Practical Knowledge Checks

1. **Question**: You are building a Web Crawler that downloads 500 web pages over HTTP and processes their text using regex and NLTK parsing (CPU). What is the optimal architecture?
   - **Solution**: Use `httpx.AsyncClient` or `aiohttp` in `asyncio` to fetch all 500 HTML pages concurrently over non-blocking network sockets. Pass each downloaded HTML string to a `ProcessPoolExecutor` via `loop.run_in_executor()` for CPU parsing across multi-core processors.

2. **Practice Task**: Modify `03_benchmarks.py` to test different worker pool sizes (e.g. `max_workers=2` vs `max_workers=4` vs `max_workers=8`). Measure how performance scales with available physical hardware cores on your system.
