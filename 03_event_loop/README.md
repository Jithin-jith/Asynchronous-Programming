# Module 03: The Asyncio Event Loop

## 📌 Executive Summary
The **Event Loop** is the core reactive engine powering all asynchronous Python applications. It manages task execution queues, processes OS-level I/O signals via system multiplexers (`epoll`, `kqueue`, IOCP), handles callback scheduling (`call_soon`, `call_later`, `call_at`), and maintains high-precision monotonic clocks. Understanding how the event loop operates under the hood is essential for writing efficient, non-blocking Python systems.

---

## 📖 Theoretical Deep Dive

### 1. The Event Loop Architecture & Cycle

```text
+-------------------------------------------------------------------------+
|                        EVENT LOOP ITERATION CYCLE                       |
|                                                                         |
|  1. SELECT PHASE: Query OS Multiplexer (epoll/kqueue/IOCP) for ready    |
|     socket read/write file descriptors.                                 |
|                                                                         |
|  2. TIMER PHASE: Check priority min-heap (`_scheduled`) for expired    |
|     `call_later` and `call_at` callback timers.                         |
|                                                                         |
|  3. EXECUTION PHASE: Execute all pending callbacks in `_ready` FIFO     |
|     queue and step coroutine frames (`Task.__step()`).                  |
|                                                                         |
|  4. IDLE PHASE: Block/sleep until the next scheduled timer expires or   |
|     an OS socket I/O interrupt occurs.                                  |
+-------------------------------------------------------------------------+
```

### 2. Internal Queues & Data Structures
- **Ready Queue (`loop._ready`)**: A FIFO `collections.deque` containing callbacks ready to run on the very next iteration tick. Populated by `loop.call_soon()`.
- **Scheduled Timer Heap (`loop._scheduled`)**: A min-heap array of `TimerHandle` objects sorted by absolute monotonic execution time (`when`). Populated by `loop.call_later()` and `loop.call_at()`.

---

## 🔬 Under the Hood: Operating System Multiplexers

Behind Python's `asyncio` abstraction layer are native OS kernel multiplexing mechanisms:

```text
+---------------------+-------------------+---------------------------------------------+
| Operating System    | Multiplexer Engine| CPython Implementation                      |
+---------------------+-------------------+---------------------------------------------+
| Linux Kernel        | epoll             | _UnixSelectorEventLoop (epollselector)      |
| macOS / FreeBSD     | kqueue            | _UnixSelectorEventLoop (KqueueSelector)     |
| Windows (Default)   | IOCP (Proactor)   | ProactorEventLoop (IocpProactor)            |
| Windows (Fallback)  | select            | _WindowsSelectorEventLoop (SelectSelector)  |
+---------------------+-------------------+---------------------------------------------+
```

1. **Linux `epoll`**: Monitors millions of file descriptors in $O(1)$ constant time efficiency using kernel event notification buffers.
2. **macOS / BSD `kqueue`**: Highly optimized kernel event interface for monitoring socket descriptors, signals, timers, and file system modifications.
3. **Windows IOCP (Input/Output Completion Ports)**: Asynchronous I/O model used by `ProactorEventLoop`. Instead of polling readiness, the OS kernel completes the I/O operation in the background and posts a completion packet to a queue.

---

## 💻 Script-by-Script Breakdown & Line-by-Line Guide

### 1. [`01_event_loop_basics.py`](file:Asynchronous-Programming/03_event_loop/01_event_loop_basics.py)
* **Goal**: Inspect active event loop properties, check running state, and observe monotonic clock progression.
* **Key Concept**: `asyncio.get_running_loop()` retrieves the active loop; `loop.time()` provides a non-decreasing monotonic clock source (`time.monotonic()`).

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L25** | `asyncio.get_running_loop()` | Obtains reference to active thread's loop instance. Raises `RuntimeError` if called outside an async coroutine context. |
| **L28-L29** | `loop.is_running()`, `loop.is_closed()` | Queries loop state flags. `is_running()` returns `True`; `is_closed()` returns `False`. |
| **L32-L33** | `loop.time()`, `time.perf_counter()` | Reads high-resolution monotonic timestamps. Unaffected by system clock NTP updates. |
| **L39** | `await asyncio.sleep(0.5)` | **Yield Point**: Suspends coroutine for 0.5s, allowing the loop timer queue to advance. |
| **L42** | `end_loop_time - start_loop_time` | Calculates exact clock progression delta (~0.500s). |
| **L47** | `asyncio.run(inspect_event_loop())` | Initializes new loop, runs coroutine, and closes loop upon completion. |

---

### 2. [`02_callbacks_and_timers.py`](file:Asynchronous-Programming/03_event_loop/02_callbacks_and_timers.py)
* **Goal**: Schedule synchronous non-async callbacks directly onto the event loop using `call_soon`, `call_later`, and `call_at`.
* **Key Concept**: Standard `def` functions can be scheduled directly onto loop queues without defining `async def` coroutines.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L22-L37** | `def sync_callback(...)` | Synchronous callback function invoked by the loop during callback/timer execution phases. |
| **L46** | `loop.call_soon(...)` | Pushes callback to `_ready` FIFO queue. Executes on the **very next iteration tick**. |
| **L49** | `loop.call_later(1.0, ...)` | Inserts callback into `_scheduled` min-heap targeting relative delay of +1.0s. |
| **L52** | `loop.call_later(0.5, ...)` | Inserts callback into `_scheduled` min-heap targeting relative delay of +0.5s. |
| **L56-L59** | `loop.call_at(target, ...)` | Inserts callback into `_scheduled` min-heap targeting absolute timestamp `start_time + 1.5s`. |
| **L65** | `await asyncio.sleep(2.0)` | Keeps event loop active for 2.0s so all scheduled timers can expire and execute. |

---

### 3. [`03_under_the_hood_selector.py`](file:Asynchronous-Programming/03_event_loop/03_under_the_hood_selector.py)
* **Goal**: Inspect active OS multiplexer backend (`epoll`, `kqueue`, or `IOCP`) and event loop policy.
* **Key Concept**: Introspecting `loop._selector` or `type(loop)` reveals low-level kernel driver bindings.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L23** | `asyncio.get_event_loop_policy()` | Queries default loop policy instance for current OS platform. |
| **L28** | `loop = asyncio.new_event_loop()` | Instantiates temporary event loop instance for low-level property inspection. |
| **L34-L38** | `hasattr(loop, "_selector")` | Checks if loop relies on a Selector backend (`_selector`) or Windows IOCP (`ProactorEventLoop`). |
| **L40** | `loop.close()` | Explicitly releases system resources associated with temporary loop instance. |

---

## 🏃 Expected Console Outputs

### 1. `01_event_loop_basics.py` Output:
```text
=== Inspecting Event Loop Instance & Clock ===
Running Event Loop Instance: <_UnixSelectorEventLoop running=True closed=False debug=False>
Is Loop Running?           : True
Is Loop Closed?            : False
Loop Monotonic Clock Time  : 14205.1234
System Perf Counter        : 14205.1235
Loop Clock after 0.5s sleep: 14205.6239 (Delta: 0.5005s)
```

### 2. `02_callbacks_and_timers.py` Output:
```text
=== Direct Callback Scheduling on Event Loop ===
All callbacks registered on event loop queues. Keeping loop alive for 2.0s...
 -> Callback 'Immediate (call_soon)' executed at +0.000s from start!
 -> Callback 'Delayed 0.5s (call_later)' executed at +0.501s from start!
 -> Callback 'Delayed 1.0s (call_later)' executed at +1.002s from start!
 -> Callback 'Absolute 1.5s (call_at)' executed at +1.501s from start!
Execution complete!
```

### 3. `03_under_the_hood_selector.py` Output (Windows / Linux):
```text
=== Event Loop OS Multiplexer Inspection ===
Operating System Platform: win32
Active Event Loop Policy : WindowsProactorEventLoopPolicy
Event Loop Class         : ProactorEventLoop
OS Multiplexer Backend   : Windows Proactor (IOCP - I/O Completion Ports)
```

---

## ❓ Exercises & Practical Knowledge Checks

1. **Question**: What is the key difference between `time.time()` and `loop.time()`?
   - **Answer**: `time.time()` reads system wall-clock time which can jump forward or backward due to NTP synchronization or manual user adjustment. `loop.time()` uses `time.monotonic()` which is guaranteed to be strictly non-decreasing, ensuring accurate timer calculations.

2. **Practice Task**: Use `loop.call_later(1.0, callback)` to schedule a synchronous function that prints a message after 1 second without using `await asyncio.sleep()`.

