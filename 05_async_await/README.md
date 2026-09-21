# Module 05: `async` and `await` Deep Dive

## 📌 Executive Summary
`async` and `await` are the core keywords that enable asynchronous control flow in modern Python. This module breaks down the definition of an **Awaitable**, explains how the `await` operator yields control to the event loop, compares the 3 major awaitable types (Coroutines, Tasks, Futures), and details common syntax pitfalls and anti-patterns to avoid.

---

## 💡 Architectural Overview: What, Where, When, Why & How

* **What**: Language-level keywords (`async def` and `await`) that demarcate asynchronous function definitions and non-blocking suspension points.
* **Where**: Applied in any code path where execution must pause for an external operation without freezing the OS thread.
* **When**: Used when calling an awaitable (a sub-coroutine, a scheduled `Task`, or an I/O `Future`).
* **Why**: Provides intuitive sequential control flow syntax while maintaining non-blocking cooperative multitasking under the hood.
* **How**: CPython evaluates `await target` by calling `target.__await__()`, obtaining an iterator, and yielding execution frames back to the event loop until the iterator completes.

---

## 📖 Theoretical Deep Dive

### 1. What is an Awaitable?

An object is an **Awaitable** if it can be passed to an `await` expression. In CPython, an object is awaitable if it implements the `__await__()` dunder method, which returns an iterator.

```text
                        THE 3 TYPES OF AWAITABLES
                                    |
    +-------------------------------+-------------------------------+
    |                               |                               |
1. Native Coroutines           2. Tasks                        3. Futures
 (Returned by `async def`)   (Created by `create_task`)     (Low-level I/O handles)
```

1. **Native Coroutines**: Created by invoking an `async def` function. Execution is lazy; code inside the function does not run until awaited or scheduled.
2. **Tasks (`asyncio.Task`)**: Wrappers created via `asyncio.create_task()` that schedule coroutines on the loop concurrently. A subclass of `Future`.
3. **Futures (`asyncio.Future`)**: Low-level objects representing an eventual result of an asynchronous operation (e.g., socket read completion or timer callbacks).

---

## 🔬 Under the Hood: `await` Execution Mechanics

When CPython encounters `result = await target`:
1. It verifies that `target` is awaitable (implements `__await__()`).
2. It pauses execution of the current coroutine frame, saving stack variables.
3. It passes control back to the **Event Loop** dispatcher.
4. The Event Loop executes other ready tasks.
5. When `target` completes, the Event Loop resumes the paused coroutine, injecting the return value into `result`.

### Interleaved Timeline Example (`01_await_mechanics.py`)

```text
Timeline (Seconds):
0.0s -------------> 0.1s -------------> 0.2s -------------> 0.3s -------------> 0.5s
 |                   |                   |                   |                   |
 Alpha starts (0.2s) |                   Alpha resumes (L25) |                   Alpha finishes (L29)
 Beta starts (0.1s)  Beta resumes (L37)                      Beta finishes (L41)
                     Beta starts 0.2s                         
```

---

## 💻 Script-by-Script Breakdown & Line-by-Line Guide

### 1. [`01_await_mechanics.py`](01_await_mechanics.py)
* **Goal**: Step-by-step trace showing control flow yielding back and forth between two awaiting coroutines on a single thread.
* **Key Concept**: Cooperative context-switching interleaves execution without multiple OS threads.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L21-L31** | `async def task_alpha()` | Coroutine alpha yielding at `await asyncio.sleep(0.2)` (L24) and `await asyncio.sleep(0.3)` (L28). |
| **L33-L43** | `async def task_beta()` | Coroutine beta yielding at `await asyncio.sleep(0.1)` (L36) and `await asyncio.sleep(0.2)` (L40). |
| **L49-L50** | `asyncio.create_task(...)` | Schedules `task_alpha` and `task_beta` concurrently on the event loop. |
| **L53-L54** | `await t1`, `await t2` | `main()` awaits `t1` and `t2`, resuming after both complete. |

---

### 2. [`02_awaitables_coroutines_tasks_futures.py`](02_awaitables_coroutines_tasks_futures.py)
* **Goal**: Demonstrate awaiting all 3 types of awaitables: Coroutine objects, Tasks, and low-level Futures.
* **Key Concept**: Type hierarchy distinction between Coroutine, Task, and Future objects.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L36-L40** | `coro = sample_coroutine(); await coro` | Directly awaits a raw native coroutine object (`<class 'coroutine'>`). |
| **L42-L45** | `task = asyncio.create_task(...); await task` | Wraps coroutine in a scheduled Task (`<class '_asyncio.Task'>`) and awaits it. |
| **L47-L56** | `fut = loop.create_future(); await fut` | Creates a low-level Future (`<class '_asyncio.Future'>`), schedules a `call_later` timer callback to set result, and awaits future resolution. |

---

### 3. [`03_common_pitfalls.py`](03_common_pitfalls.py)
* **Goal**: Demonstrate common async errors: unawaited coroutines, awaiting non-awaitables (`TypeError`), and synchronous blocking anti-patterns.
* **Key Concept**: Catching and avoiding common async bugs during development.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L28-L34** | `coro_ref = unawaited_demo()` | Calling coroutine without `await` stores an unstarted coroutine object without running function body. |
| **L37-L39** | `await unawaited_demo()` | Correct usage: `await` runs function body and returns result. |
| **L42-L50** | `await 42` (inside helper) | Attempting to `await` primitive `42` raises `TypeError: object int can't be used in 'await' expression`. |
| **L53-L57** | Blocking anti-pattern | Clarifies why `time.sleep()` blocks the loop and recommends `await asyncio.sleep()` or `asyncio.to_thread()`. |

---

## 🏃 Console Outputs & Benchmarks

### Running `01_await_mechanics.py`:
```text
=== Visualizing Interleaved Await Control Flow ===
[Alpha 1] Starting Task Alpha...
  [Beta 1] Starting Task Beta...
  [Beta 2] Resumed Task Beta after 0.1s pause!
[Alpha 2] Resumed Task Alpha after 0.2s pause!
  [Beta 3] Finished Task Beta!
[Alpha 3] Finished Task Alpha!

Final Returned Results: 'Alpha Output Result', 'Beta Output Result'
```

### Running `02_awaitables_coroutines_tasks_futures.py`:
```text
=== Exploring the 3 Types of Awaitables in Python ===
1a. Created coroutine object type : <class 'coroutine'>
1b. Awaited Native Coroutine Result : 'Coroutine Output Payload'

2a. Created task object type      : <class '_asyncio.Task'>
2b. Awaited Scheduled Task Result   : 'Coroutine Output Payload'

3a. Created Future object type    : <class '_asyncio.Future'>
  [Main] Awaiting unresolved Future object...
  [Callback] Timer triggered! Fulfilling low-level Future object...
3b. Awaited Low-Level Future Result : 'Future Resolved Payload'
```

### Running `03_common_pitfalls.py`:
```text
=== Common Async/Await Pitfalls & Anti-Patterns Demo ===

1. Calling unawaited_demo() WITHOUT 'await':
   Stored variable type: <class 'coroutine'>
   Value of coro_ref  : <coroutine object unawaited_demo at 0x...>
   [Fix] Now calling WITH 'await':
  [Coro Body] This print statement ONLY runs if the coroutine is awaited!
   Result when awaited: 'Hidden Result'

2. Attempting to await a non-awaitable integer primitive (await 42):
   [ERROR] Caught Expected TypeError: object int can't be used in 'await' expression
   [Fix] Only await Coroutines, Tasks, Futures, or objects with __await__().

3. Blocking the Event Loop (Conceptual Anti-Pattern):
   [Rule] Never call time.sleep(N) inside async code! Use `await asyncio.sleep(N)` instead.
   [Rule] For CPU-bound or blocking synchronous I/O, use `await asyncio.to_thread(func)`.
```

---

## ❓ Exercises & Practical Knowledge Checks

1. **Question**: Can you `await` a standard function defined with `def` (without `async`)?
   - **Answer**: No! A standard function does not return an awaitable object. Attempting to `await` it raises a `TypeError: object ... can't be used in 'await' expression`.

2. **Question**: What is the difference between awaiting a raw coroutine vs awaiting an `asyncio.Task`?
   - **Answer**: Awaiting a raw coroutine (`await coro()`) executes that coroutine sequentially within the current task. Awaiting an `asyncio.Task` (`t = asyncio.create_task(coro()); await t`) schedules `coro()` to run concurrently on the event loop background queue immediately when created.

3. **Practice Task**: Write a program that creates an `asyncio.Future()`, schedules a `call_later` callback to resolve it after 1 second using `fut.set_result("Done")`, and `await`s the future.


