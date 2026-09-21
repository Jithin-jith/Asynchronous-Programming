"""
===============================================================================
Module 05: Awaiting Coroutines, Tasks, and Futures (The 3 Awaitables)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Native Coroutines: `async def` function objects that execute lazily when awaited.
2. `asyncio.Task` Objects: Wrappers created via `asyncio.create_task()` that schedule 
   coroutines for execution on the event loop concurrently.
3. `asyncio.Future` Objects: Low-level result containers representing an eventual outcome
   resolved asynchronously (e.g. by network callbacks or worker threads).

HOW THIS CODE WORKS:
- Section 1: Awaits a raw coroutine object directly (`coro = sample_coroutine(); await coro`).
- Section 2: Wraps a coroutine into a Task (`task = asyncio.create_task(...)`) and awaits it.
- Section 3: Creates a low-level Future (`fut = loop.create_future()`), registers a timer callback
  using `loop.call_later(0.2, ...)`, and awaits the Future until the callback calls `fut.set_result()`.
===============================================================================
"""

import asyncio


async def sample_coroutine() -> str:
    """
    A simple native coroutine yielding control for 0.1s before returning a string payload.
    """
    await asyncio.sleep(0.1)
    return "Coroutine Output Payload"


def set_future_result(fut: asyncio.Future, result_value: str):
    """
    A synchronous callback function executed by the event loop timer to manually 
    fulfill a low-level Future object by calling `fut.set_result(...)`.
    """
    print("  [Callback] Timer triggered! Fulfilling low-level Future object...")
    fut.set_result(result_value)


async def main():
    print("=== Exploring the 3 Types of Awaitables in Python ===")
    
    # -------------------------------------------------------------------------
    # 1. AWAITING A NATIVE COROUTINE OBJECT
    # - Calling `sample_coroutine()` returns a coroutine object.
    # - Direct `await coro` evaluates the coroutine directly within the current task context.
    # -------------------------------------------------------------------------
    coro = sample_coroutine()
    print(f"1a. Created coroutine object type : {type(coro)}")
    res1 = await coro
    print(f"1b. Awaited Native Coroutine Result : '{res1}'\n")
    
    # -------------------------------------------------------------------------
    # 2. AWAITING AN asyncio.Task OBJECT
    # - `asyncio.create_task()` wraps the coroutine into an asyncio.Task (a subclass of Future).
    # - It immediately schedules the coroutine for execution on the event loop queue.
    # - `await task` waits for the scheduled task to complete and retrieves its return value.
    # -------------------------------------------------------------------------
    task = asyncio.create_task(sample_coroutine())
    print(f"2a. Created task object type      : {type(task)}")
    res2 = await task
    print(f"2b. Awaited Scheduled Task Result   : '{res2}'\n")
    
    # -------------------------------------------------------------------------
    # 3. AWAITING AN asyncio.Future OBJECT
    # - A Future is a low-level object representing an asynchronous result that is NOT yet available.
    # - The caller `await fut` pauses execution until another component calls `fut.set_result(val)`.
    # -------------------------------------------------------------------------
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    print(f"3a. Created Future object type    : {type(fut)}")
    
    # Schedule our synchronous callback to resolve the Future after 0.2s delay
    loop.call_later(0.2, set_future_result, fut, "Future Resolved Payload")
    
    print("  [Main] Awaiting unresolved Future object...")
    res3 = await fut
    print(f"3b. Awaited Low-Level Future Result : '{res3}'")


if __name__ == "__main__":
    asyncio.run(main())

