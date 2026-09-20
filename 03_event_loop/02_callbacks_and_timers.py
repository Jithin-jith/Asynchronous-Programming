"""
===============================================================================
Module 03: Scheduling Callbacks & Timers on the Event Loop
===============================================================================

CONCEPTS DEMONSTRATED:
1. `loop.call_soon(callback, *args)`:
   - Schedules a synchronous callback function to be executed on the VERY NEXT 
     iteration tick of the event loop.
   - Pushes callback to the event loop's internal `_ready` FIFO queue.

2. `loop.call_later(delay, callback, *args)`:
   - Schedules a synchronous callback to run after `delay` relative seconds.
   - Pushes callback to the event loop's min-heap timer queue (`_scheduled`).

3. `loop.call_at(when, callback, *args)`:
   - Schedules a synchronous callback targeting an absolute monotonic timestamp `when` (`loop.time() + offset`).
   - Also inserts the callback into the event loop's min-heap timer queue (`_scheduled`).

HOW THIS CODE WORKS:
- Non-async synchronous functions (`def sync_callback(...)`) can be scheduled directly onto loop queues.
- `call_soon` executes immediately after the current step completes.
- `call_later(0.5, ...)` executes when `loop.time()` advances by 0.5 seconds.
- `call_later(1.0, ...)` executes at +1.0 second.
- `call_at(target, ...)` executes at absolute target clock timestamp (+1.5 seconds).
===============================================================================
"""

import asyncio  # Asynchronous I/O framework providing event loop callback APIs


def sync_callback(name: str, start_timestamp: float, loop):
    """Synchronous callback function invoked directly by the Event Loop during execution phases.

    Notice that this function is defined with standard 'def' (not 'async def').
    The event loop can invoke ordinary synchronous functions directly from its queues.

    Args:
        name (str): Describing label of the scheduled callback type.
        start_timestamp (float): Initial loop clock timestamp recorded at main start.
        loop: Active event loop instance used for checking current loop time.
    """
    # Line 1: Read current monotonic loop timestamp
    now = loop.time()
    
    # Line 2: Calculate elapsed wall-clock seconds since program initiation
    elapsed = now - start_timestamp
    
    # Line 3: Output callback execution metric to standard output
    print(f" -> Callback '{name}' executed at +{elapsed:.3f}s from start!")


async def main():
    """Main coroutine orchestrating callback registration across different loop queues."""
    
    # Line 1: Obtain reference to currently running event loop on main thread
    loop = asyncio.get_running_loop()
    
    # Line 2: Record initial monotonic loop clock timestamp
    start_time = loop.time()
    
    # Line 3: Print section header banner
    print("=== Direct Callback Scheduling on Event Loop ===")
    
    # Line 4: REGISTRATION 1: call_soon
    # Pushes 'sync_callback' to loop._ready queue.
    # Executes on the next iteration tick of the event loop (before any delayed timers).
    loop.call_soon(sync_callback, "Immediate (call_soon)", start_time, loop)
    
    # Line 5: REGISTRATION 2: call_later (1.0 second delay)
    # Inserts 'sync_callback' into loop._scheduled timer heap targeting (start_time + 1.0s).
    loop.call_later(1.0, sync_callback, "Delayed 1.0s (call_later)", start_time, loop)
    
    # Line 6: REGISTRATION 3: call_later (0.5 second delay)
    # Inserts 'sync_callback' into loop._scheduled timer heap targeting (start_time + 0.5s).
    loop.call_later(0.5, sync_callback, "Delayed 0.5s (call_later)", start_time, loop)
    
    # Line 7: REGISTRATION 4: call_at (Absolute monotonic timestamp)
    # Calculate target timestamp: 1.5 seconds in the future on loop monotonic clock
    target_timestamp = start_time + 1.5
    
    # Line 8: Insert 'sync_callback' into timer heap targeting exact monotonic timestamp 'target_timestamp'
    loop.call_at(target_timestamp, sync_callback, "Absolute 1.5s (call_at)", start_time, loop)
    
    # Line 9: Output registration status notification
    print("All callbacks registered on event loop queues. Keeping loop alive for 2.0s...")
    
    # Line 10: NON-BLOCKING YIELD POINT
    # Keep the event loop running for 2.0 seconds so all scheduled timers can expire and trigger!
    await asyncio.sleep(2.0)
    
    # Line 11: Print completion status message
    print("Execution complete!")


if __name__ == "__main__":
    # Line 1: Bootstrap event loop, execute main(), and perform clean shutdown
    asyncio.run(main())
