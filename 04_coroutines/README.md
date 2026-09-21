# Module 04: Python Coroutines

## 📌 Executive Summary
Coroutines are the foundational building blocks of asynchronous programming in Python. A **Coroutine** is a specialized function whose execution can be paused at specific yield points (`await`), preserving its internal stack frame variables and instruction pointer, and resumed later by the event loop. This module explores the historical evolution of coroutines, native `async def` mechanics, valid `await` expressions, and low-level frame state transitions using CPython's `inspect` module.

---

## 💡 Architectural Overview: What, Where, When, Why & How

* **What**: First-class asynchronous code blocks that yield execution control to the event loop without terminating their execution context.
* **Where**: Defines the body of every asynchronous task, API handler, database operation, and background worker in Python.
* **When**: Used whenever an operation needs to pause for external I/O or wait for another sub-task without blocking the thread.
* **Why**: Native coroutines eliminate OS thread context-switching overhead, reduce RAM usage from megabytes per thread to kilobytes per coroutine frame, and provide clean, readable code.
* **How**: Python compiles `async def` functions into `PyCoroutineObject` frames. The event loop drives them by calling `.send(None)` to advance to the next `await` expression.

---

## 📖 Theoretical Deep Dive

### 1. Historical Evolution of Coroutines in Python

```text
                       EVOLUTION OF PYTHON COROUTINES
                       
   Python 2.5: Generator Functions
   - Used `yield` to return data to caller.
   - Introduced `generator.send(value)` to pass data back into generator frame.
                |
                v
   Python 3.4: Generator-Based Coroutines (PEP 3156)
   - Decorator: `@asyncio.coroutine`
   - Syntax: `yield from coroutine()` to delegate sub-generator execution.
                |
                v
   Python 3.5+: Native Coroutines (PEP 492)
   - Keywords: `async def` and `await`
   - First-class native language primitives with strict type checking.
```

### 2. Coroutine Execution Lifecycle States

At the CPython interpreter level, a coroutine object transitions through 4 distinct frame states (`inspect.getcoroutinestate`):

```text
       [CORO_CREATED] ---- (First step/await) ----> [CORO_RUNNING]
             |                                             |
             |                                    (Yields at await)
             |                                             v
       [CORO_CLOSED] <---- (Return / Exception) ---- [CORO_SUSPENDED]
```

1. **`CORO_CREATED`**: Coroutine object instantiated via `my_coro()`, but execution has not started yet (unstarted frame).
2. **`CORO_RUNNING`**: Currently being evaluated on the CPU by the event loop (active frame on execution stack).
3. **`CORO_SUSPENDED`**: Suspended at an `await` expression. Local stack frame variables are saved on the heap while yielding control to the event loop.
4. **`CORO_CLOSED`**: Execution completed (returned a value or raised an unhandled exception) or closed via `.close()`.

---

## 💻 Script-by-Script Breakdown & Line-by-Line Guide

### 1. [`01_generator_to_coroutine.py`](01_generator_to_coroutine.py)
* **Goal**: Demonstrate historical generator-based coroutines using `yield` and `gen.send(val)` to understand state preservation across execution pauses.
* **Key Concept**: Generator frame preservation before native `async def` was introduced in PEP 492.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L23-L33** | `def generator_coro()` | Generator function using `val = yield` to receive data from caller via `.send()`. |
| **L36** | `gen = generator_coro()` | Instantiates generator object in un-started state. |
| **L39** | `next(gen)` | Advances generator frame to the first `yield` expression (priming the generator). |
| **L42** | `gen.send("Data")` | Resumes generator, injecting `"Data"` into `val`, and continues execution. |

---

### 2. [`02_native_coroutines.py`](02_native_coroutines.py)
* **Goal**: Demonstrate native `async def` coroutines, lazy evaluation, and `await` mechanics.
* **Key Concept**: Invoking an `async def` function creates a dormant coroutine object without running any code inside the function body until driven by an event loop.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L22-L26** | `async def greet(name: str)` | Native coroutine definition returning a formatted string after `await asyncio.sleep(5.0)`. |
| **L33** | `coro_obj = greet("Alice")` | Calling `greet("Alice")` creates a `<coroutine object>` in `CORO_CREATED` state. No prints execute yet! |
| **L36-L37** | `asyncio.iscoroutine(coro_obj)` | Validates object type returns `True` and inspects type metadata. |
| **L41** | `asyncio.run(coro_obj)` | Binds coroutine object to event loop, driving execution of function body to completion. |

---

### 3. [`03_coroutine_states.py`](03_coroutine_states.py)
* **Goal**: Track coroutine frame state transitions programmatically using `inspect.getcoroutinestate()`.
* **Key Concept**: Demonstrates transition sequence `CORO_CREATED` -> `CORO_SUSPENDED` -> `CORO_CLOSED` and event loop yield mechanics.

#### Line-by-Line Execution Flow:
| Line Range | Code Element | Architectural Purpose & Execution Behavior |
| :--- | :--- | :--- |
| **L21-L26** | `async def stateful_coroutine()` | Sample coroutine pausing at `await asyncio.sleep(0.5)`. |
| **L32** | `coro = stateful_coroutine()` | Instantiates coroutine object without executing body. |
| **L35-L36** | `inspect.getcoroutinestate(coro)` | Verifies initial state is `CORO_CREATED`. |
| **L39** | `task = asyncio.create_task(coro)` | Schedules coroutine on event loop for next iteration (does NOT run immediately). |
| **L42** | `await asyncio.sleep(0.1)` | Pauses `main()`, yielding control to event loop so `task` starts and reaches its 0.5s sleep. |
| **L45-L46** | `inspect.getcoroutinestate(coro)` | Verifies active state is `CORO_SUSPENDED` (paused at sleep point). |
| **L49** | `await task` | Awaits completion of `task`. |
| **L52-L53** | `inspect.getcoroutinestate(coro)` | Verifies final state is `CORO_CLOSED` after execution ends. |

---

## 🏃 Console Outputs & Benchmarks

### Running `02_native_coroutines.py`:
```text
=== Native Coroutine Invocation & Lazy Evaluation ===
Type of returned object : <class 'coroutine'>
Is it a coroutine object?: True
Inspect iscoroutine()    : True
Notice: 'Inside greet()' has NOT been printed yet!

Now executing coroutine object with asyncio.run()...
Inside greet(): Hello, Alice!
Execution output: 'Greeting to Alice complete.'
```

### Running `03_coroutine_states.py`:
```text
=== Tracking Coroutine Lifecycle States ===
1. Initial State (Created, unstarted) : CORO_CREATED
  [Coro Body] Started execution! Reached `await asyncio.sleep(0.5)` pause point...
2. Active State (Paused at await sleep): CORO_SUSPENDED
  [Coro Body] Resumed execution! Returning final result...
   Task return result                : 'SUCCESS_RESULT'
3. Final State (Execution Closed)     : CORO_CLOSED
```

---

## ❓ Exercises & Practical Knowledge Checks

1. **Question**: What can be used with the `await` keyword? Can any function be awaited?
   - **Answer**: You can only `await` **awaitable** objects:
     - **Coroutine objects** (produced by invoking an `async def` function).
     - **`asyncio.Task`** objects (created via `asyncio.create_task()`).
     - **`asyncio.Future`** objects (e.g. from `asyncio.to_thread()`).
     - **Objects with `__await__()`** (from async libraries like `httpx`, `asyncpg`, `aiofiles`).
     - You *cannot* await standard synchronous functions directly (`await print()` or `await time.sleep()` will raise a `TypeError`).

2. **Question**: Is it mandatory for an `async def` coroutine function to contain the `await` keyword?
   - **Answer**: **No.** Using `async def` defines a function as a native coroutine function regardless of whether `await` is used. If it contains no `await`, it simply runs synchronously from start to finish when executed by the event loop.

3. **Question**: What happens if you call an `async def` function directly without `await` or `asyncio.run()`?
   - **Answer**: It returns an unstarted `<coroutine object>` in `CORO_CREATED` state without executing any code in the body. If un-awaited and garbage collected, CPython emits a `RuntimeWarning: coroutine '...' was never awaited`.

4. **Practice Task**: Use `inspect.getcoroutinestate()` to print the state of a coroutine before, during, and after executing it via `asyncio.run()`.


