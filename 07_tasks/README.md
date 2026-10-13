# Module 07: Asynchronous Tasks (`asyncio.create_task`)

## 📌 Executive Summary
An `asyncio.Task` wraps a coroutine and immediately schedules it on the event loop for concurrent execution. This module demonstrates creating background tasks, assigning human-readable names for observability, preventing Garbage Collection (GC) drops, and shielding critical **SQLite database transactions** from cancellation using `asyncio.shield()`.

> **Note for Users & GitHub Visitors:**  
> If an LLM subscription or API key is not available, the user can use `asyncio.sleep()` to execute code. All scripts include automatic, graceful fallbacks to sleep simulation so the code runs seamlessly in any environment.

---

## 💻 Script-by-Script Breakdown

| Script | Real-World Workload | Key Learning Point |
|---|---|---|
| `01_creating_tasks.py` | Concurrent SQLite user analytics + Gemini LLM pitch + inventory lookup | Demonstrates background execution while the main coroutine performs local processing. |
| `02_task_lifecycle_and_naming.py` | Named SQLite order analytics & Gemini observability tasks | Shows `task.get_name()`, `task.done()`, `task.result()`, and loop-wide `asyncio.all_tasks()`. |
| `03_background_tasks_shielding.py` | Shielded SQLite order transaction commit | Uses `asyncio.shield()` to guarantee critical database writes complete even when client requests abort. |

---

## 🏃 Expected Console Outputs

### Running `01_creating_tasks.py`:
```text
=================================================================
  MODULE 07: CONCURRENT TASKS WITH REAL SQLITE & GEMINI WORKLOADS
=================================================================
  [Task 1 - DB] Starting customer analytics lookup for User #1...
  [Task 2 - LLM] Generating Gemini promotional pitch for 'Cloud AI Solutions'...
  [Task 3 - DB] Starting inventory stock check...

[Main] Tasks dispatched to event loop! Doing local processing...
[Main] Intermediate calculation done (333283335000). Now awaiting task results...
...
Notice: All 3 tasks executed concurrently in the background!
```

---

## ❓ Exercises & Knowledge Checks

1. **Question**: Why should you store a reference in a `set` (e.g. `background_tasks.add(task)`) when spawning fire-and-forget background tasks?
   - *Answer*: In Python, if a task reference is not held anywhere, CPython's garbage collector can collect and destroy the task frame mid-execution, raising `Task was destroyed but it is pending!`.
