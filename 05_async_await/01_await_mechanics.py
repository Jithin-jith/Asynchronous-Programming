"""
===============================================================================
Module 05: Interleaved Await Mechanics & Cooperative Multitasking
===============================================================================

CONCEPTS DEMONSTRATED:
1. Cooperative Context-Switching: How the `await` keyword yields execution control 
   back to the asyncio event loop.
2. Interleaved Execution: How two concurrent tasks (`task_alpha` and `task_beta`) 
   run concurrently on a single OS thread without thread switches.
3. Event Loop Scheduling: How timer expirations determine the order of task resume points.

HOW THIS CODE WORKS:
- `main()` creates two tasks using `asyncio.create_task()`:
    * Task Alpha pauses at `await asyncio.sleep(0.2)`, then later at `await asyncio.sleep(0.3)`.
    * Task Beta pauses at `await asyncio.sleep(0.1)`, then later at `await asyncio.sleep(0.2)`.
- Timeline breakdown:
    - T=0.0s: Both tasks start. Both hit their first `await asyncio.sleep()`. Control yields to event loop.
    - T=0.1s: Beta's 0.1s sleep expires first -> Beta resumes and logs `[Beta 2]`, then starts 0.2s sleep.
    - T=0.2s: Alpha's 0.2s sleep expires -> Alpha resumes and logs `[Alpha 2]`, then starts 0.3s sleep.
    - T=0.3s: Beta's second sleep (0.1 + 0.2 = 0.3s total) expires -> Beta finishes and logs `[Beta 3]`.
    - T=0.5s: Alpha's second sleep (0.2 + 0.3 = 0.5s total) expires -> Alpha finishes and logs `[Alpha 3]`.
===============================================================================
"""

import asyncio


async def task_alpha() -> str:
    """
    Task Alpha: Pauses for 0.2s, resumes, pauses for 0.3s, then completes.
    Total execution duration: 0.5 seconds.
    """
    print("[Alpha 1] Starting Task Alpha...")
    
    # -------------------------------------------------------------------------
    # YIELD POINT 1 (0.2s):
    # `await` pauses task_alpha and yields control to the event loop.
    # The event loop looks for other ready tasks (Task Beta is ready to run).
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.2)
    print("[Alpha 2] Resumed Task Alpha after 0.2s pause!")
    
    # -------------------------------------------------------------------------
    # YIELD POINT 2 (0.3s):
    # Pauses task_alpha again. Control returns to event loop until T=0.5s.
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.3)
    print("[Alpha 3] Finished Task Alpha!")
    return "Alpha Output Result"


async def task_beta() -> str:
    """
    Task Beta: Pauses for 0.1s, resumes, pauses for 0.2s, then completes.
    Total execution duration: 0.3 seconds.
    """
    print("  [Beta 1] Starting Task Beta...")
    
    # -------------------------------------------------------------------------
    # YIELD POINT 1 (0.1s):
    # Yields control to event loop. Since Beta's sleep (0.1s) is shorter than 
    # Alpha's (0.2s), the event loop will resume Beta BEFORE resuming Alpha!
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.1)
    print("  [Beta 2] Resumed Task Beta after 0.1s pause!")
    
    # -------------------------------------------------------------------------
    # YIELD POINT 2 (0.2s):
    # Yields control again until T=0.3s total time.
    # -------------------------------------------------------------------------
    await asyncio.sleep(0.2)
    print("  [Beta 3] Finished Task Beta!")
    return "Beta Output Result"


async def main():
    print("=== Visualizing Interleaved Await Control Flow ===")
    
    # Schedule both coroutines concurrently on the event loop as Tasks
    t1 = asyncio.create_task(task_alpha())
    t2 = asyncio.create_task(task_beta())
    
    # -------------------------------------------------------------------------
    # AWAITING TASK RESULTS:
    # Awaiting `t1` pauses `main()` until `t1` (Task Alpha) completes.
    # Meanwhile, `t2` (Task Beta) continues running concurrently on the loop!
    # -------------------------------------------------------------------------
    res1 = await t1
    res2 = await t2
    
    print(f"\nFinal Returned Results: '{res1}', '{res2}'")


if __name__ == "__main__":
    asyncio.run(main())

