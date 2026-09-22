"""
===============================================================================
Module 06: Loop Lifecycle Under the Hood & Concurrent Task Execution
===============================================================================

CONCEPTS DEMONSTRATED:
1. Low-level Event Loop Management: `asyncio.new_event_loop()`, `set_event_loop()`.
2. Synchronous-to-Asynchronous Execution Bridge: `loop.run_until_complete()`.
3. Resource Cleanup & Teardown: `loop.close()`.
4. Concurrent Task Scheduling: `asyncio.create_task()` running alongside long waits.
5. Parameterized Coroutines: Passing dynamic duration variables to async tasks.

EXECUTION WORKFLOW:
1. Entry Point Execution:
   - `main_manual()` is invoked when the script runs directly.
2. Event Loop Instantiation & Attachment:
   - `asyncio.new_event_loop()` instantiates a fresh OS-level event loop instance.
   - `asyncio.set_event_loop(loop)` assigns this instance as the current thread's loop.
3. Root Coroutine Execution:
   - `loop.run_until_complete(worker(wait_seconds))` blocks the synchronous thread until
     the `worker` coroutine (and its internal sub-tasks) finishes.
4. Concurrent Coroutine Spawning:
   - `worker` receives `wait_seconds` (10s) as a variable parameter.
   - Inside `worker`, `asyncio.create_task(print_seconds(seconds))` schedules `print_seconds`
     on the running event loop as a background task.
   - `worker` then yields execution to the event loop via `await asyncio.sleep(seconds)`.
5. Interleaved Event Loop Ticking:
   - Every second, `print_seconds()` yields control during `await asyncio.sleep(1.0)`,
     allowing the event loop to manage both the worker timer and the ticker output concurrently.
6. Graceful Teardown:
   - A `try...finally` block guarantees that `loop.close()` runs even if an exception occurs,
     releasing open handlers and preventing memory/socket leaks.
===============================================================================
"""

import asyncio


async def print_seconds(seconds: int):
    """
    Concurrent Ticker Coroutine.
    
    Prints elapsed time second-by-second while another task is executing.
    
    Workflow:
    - Iterates from 1 up to `seconds`.
    - `await asyncio.sleep(1.0)` suspends this coroutine for 1 second, yielding control
      back to the event loop so other tasks can execute concurrently.
    - Prints the progress update upon resuming each second.
    """
    for sec in range(1, seconds + 1):
        # Yield execution back to the event loop for 1.0 second interval
        await asyncio.sleep(1.0)
        print(f"  [Timer] Elapsed: {sec}/{seconds} second(s)")


async def worker(seconds: int = 10):
    """
    Primary Worker Coroutine.
    
    Demonstrates running a main coroutine while concurrently invoking a ticker task.
    
    Workflow:
    1. Receives the `seconds` delay as a variable parameter.
    2. Spawns `print_seconds` as a concurrent asyncio.Task via `asyncio.create_task()`.
    3. Suspends itself for `seconds` via `await asyncio.sleep(seconds)`.
    4. Awaits `ticker_task` to ensure the background task completes cleanly before exiting.
    """
    print(f"  [Worker] Executing inside manual event loop (waiting {seconds} seconds)...")
    
    # 1. Schedule print_seconds as a concurrent task on the active event loop
    ticker_task = asyncio.create_task(print_seconds(seconds))
    
    # 2. Worker performs its primary wait (yields control to event loop)
    await asyncio.sleep(seconds)
    
    # 3. Explicitly await the ticker task to ensure complete execution and error propagation
    await ticker_task
    
    print("  [Worker] Worker task completed.")


def main_manual():
    """
    Manual Event Loop Lifecycle Manager.
    
    Replicates the internal behavior of `asyncio.run()` by manually orchestrating:
    Creation -> Attachment -> Execution -> Cleanup.
    """
    print("=== Manual Event Loop Lifecycle Management ===")
    
    # STEP 1: Instantiate a new low-level event loop instance
    loop = asyncio.new_event_loop()
    
    # STEP 2: Set the newly created loop as the active loop for the current OS thread
    asyncio.set_event_loop(loop)
    print(f"1. Created Loop Instance: {loop}")
    
    # STEP 3: Define duration variable to pass into async coroutine
    wait_seconds = 10  # Seconds parameter passed dynamically
    
    try:
        # STEP 4: Run the event loop until worker(wait_seconds) completes.
        # This blocks synchronous execution of main_manual() while running async tasks inside loop.
        print("2. Running coroutine until complete...")
        loop.run_until_complete(worker(wait_seconds))
    finally:
        # STEP 5: Guarantee event loop cleanup and closure inside finally block
        # Prevents unclosed event loop warnings and socket leaks.
        print("3. Closing Event Loop instance...")
        loop.close()
        print(f"Is Loop Closed? {loop.is_closed()}")


if __name__ == "__main__":
    main_manual()

