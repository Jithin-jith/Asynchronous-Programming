"""
===============================================================================
Module 04: Coroutine Frame State Machine & Lifecycle Tracking
===============================================================================

CONCEPTS DEMONSTRATED:
1. `inspect.getcoroutinestate(coro)`: Inspecting the internal state of a Python
   native coroutine object.
2. The 4 Coroutine States defined by CPython `inspect` module:
   - `CORO_CREATED`   : Coroutine object instantiated, but execution has not started.
   - `CORO_RUNNING`   : Coroutine is currently executing (active frame on stack).
   - `CORO_SUSPENDED` : Coroutine is paused at an `await` (yield) point.
   - `CORO_CLOSED`    : Coroutine has completed execution or was explicitly closed.
3. Event Loop Scheduling Mechanics:
   - How `asyncio.create_task()` schedules a coroutine without immediately executing it.
   - How yielding control via `await asyncio.sleep()` allows scheduled tasks to run.

HOW THIS CODE WORKS:
- Step 1: `stateful_coroutine()` is instantiated, creating an unstarted coroutine (`CORO_CREATED`).
- Step 2: The coroutine is wrapped in `asyncio.create_task()`. `main()` yields control
  via `await asyncio.sleep(0.1)`. The event loop starts `stateful_coroutine()`, which
  executes until `await asyncio.sleep(0.5)`, suspending itself (`CORO_SUSPENDED`).
- Step 3: `main()` resumes from its 0.1s sleep, verifies the coroutine state (`CORO_SUSPENDED`),
  and then awaits the task completion (`await task`).
- Step 4: After `stateful_coroutine()` finishes, its state becomes `CORO_CLOSED`.
===============================================================================
"""

import asyncio
import inspect


async def stateful_coroutine() -> str:
    """
    A sample coroutine function that pauses midway through execution to demonstrate 
    frame suspension and state transitions.
    """
    print("  [Coro Body] Started execution! Reached `await asyncio.sleep(0.5)` pause point...")
    # Yields control back to event loop; coroutine enters CORO_SUSPENDED state
    await asyncio.sleep(0.5)
    print("  [Coro Body] Resumed execution! Returning final result...")
    return "SUCCESS_RESULT"


async def main():
    print("=== Tracking Coroutine Lifecycle States ===")
    
    # Instantiate the coroutine object (Lazy evaluation: code inside function has NOT run yet)
    coro = stateful_coroutine()
    
    # -------------------------------------------------------------------------
    # STATE 1: CORO_CREATED
    # The coroutine object exists in memory, but execution has never stepped into it.
    # -------------------------------------------------------------------------
    state1 = inspect.getcoroutinestate(coro)
    print(f"1. Initial State (Created, unstarted) : {state1}")
    assert state1 == inspect.CORO_CREATED, "Expected state: CORO_CREATED"
    
    # Wrap coroutine in an asyncio.Task to schedule it on the event loop.
    # Note: create_task() schedules execution for the NEXT event loop iteration;
    # it does NOT synchronously run the coroutine body immediately.
    task = asyncio.create_task(coro)
    
    # -------------------------------------------------------------------------
    # YIELD CONTROL TO EVENT LOOP:
    # `main()` pauses here for 0.1s. This gives control back to the event loop,
    # which executes `task`. `task` runs until line 24 of stateful_coroutine()
    # where it hits `await asyncio.sleep(0.5)` and suspends.
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.1)
    
    # -------------------------------------------------------------------------
    # STATE 2: CORO_SUSPENDED
    # `stateful_coroutine` is now waiting on its 0.5s sleep to expire.
    # Its execution stack frame is suspended at the `await` keyword.
    # -------------------------------------------------------------------------
    state2 = inspect.getcoroutinestate(coro)
    print(f"2. Active State (Paused at await sleep): {state2}")
    assert state2 == inspect.CORO_SUSPENDED, "Expected state: CORO_SUSPENDED"
    
    # -------------------------------------------------------------------------
    # WAIT FOR TASK COMPLETION:
    # `main()` waits until `task` (and thus `stateful_coroutine`) completes.
    # -------------------------------------------------------------------------
    result = await task
    print(f"   Task return result                : '{result}'")
    
    # -------------------------------------------------------------------------
    # STATE 3: CORO_CLOSED
    # The coroutine body has executed to completion and returned a value.
    # Its frame is cleaned up and execution state is closed.
    # -------------------------------------------------------------------------
    state3 = inspect.getcoroutinestate(coro)
    print(f"3. Final State (Execution Closed)     : {state3}")
    assert state3 == inspect.CORO_CLOSED, "Expected state: CORO_CLOSED"


if __name__ == "__main__":
    asyncio.run(main())

