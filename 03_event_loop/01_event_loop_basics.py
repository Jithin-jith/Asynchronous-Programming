"""
===============================================================================
Module 03: Event Loop Basics & Clock Inspection
===============================================================================

CONCEPTS DEMONSTRATED:
1. Event Loop Retrieval (`asyncio.get_running_loop()`):
   - Safely retrieves the active event loop running on the current OS thread.
   - Raises `RuntimeError` if called outside an active coroutine execution context.

2. Event Loop Operational State:
   - `loop.is_running()`: Returns `True` if the loop iteration cycle is currently executing tasks.
   - `loop.is_closed()`: Returns `True` if the event loop instance has been destroyed/shut down.

3. Internal Monotonic Clock (`loop.time()`):
   - Uses a monotonic clock source (`time.monotonic()`) that is guaranteed never to jump backwards.
   - Independent of system wall-clock time changes (e.g. NTP updates, daylight savings adjustments).
   - Used internally by asyncio to calculate relative timer delays (`call_later`, `call_at`).

HOW THIS CODE WORKS:
- `inspect_event_loop()` retrieves the current loop instance using `asyncio.get_running_loop()`.
- Inspects `loop.is_running()` and `loop.is_closed()`.
- Measures monotonic time before and after `await asyncio.sleep(0.5)` to track clock progression.
===============================================================================
"""

import asyncio  # Standard library async framework providing loop management & scheduling
import time     # System timer module for performance timing comparisons


async def inspect_event_loop():
    """Retrieves and prints properties of the active event loop instance."""
    
    # Line 1: Obtain reference to the event loop instance currently running on the main OS thread.
    # Note: 'get_running_loop()' is the preferred modern method inside coroutines.
    loop = asyncio.get_running_loop()
    
    # Line 2: Output string representation of the active event loop class instance
    print(f"Running Event Loop Instance: {loop}")
    
    # Line 3: Check if the loop is actively executing its event dispatch cycle (Returns True)
    print(f"Is Loop Running?           : {loop.is_running()}")
    
    # Line 4: Check if the event loop has been permanently closed (Returns False)
    print(f"Is Loop Closed?            : {loop.is_closed()}")
    
    # Line 5: Read the event loop's internal monotonic time (in fractional seconds)
    start_loop_time = loop.time()
    
    # Line 6: Read system high-resolution performance counter timestamp for comparison
    start_perf = time.perf_counter()
    
    # Line 7: Print initial loop clock timestamp
    print(f"Loop Monotonic Clock Time  : {start_loop_time:.4f}")
    
    # Line 8: Print system performance counter timestamp
    print(f"System Perf Counter        : {start_perf:.4f}")
    
    # Line 9: NON-BLOCKING YIELD POINT
    # Suspend 'inspect_event_loop' for 0.5s, allowing the event loop timer queue to advance.
    await asyncio.sleep(0.5)
    
    # Line 10: Read loop monotonic timestamp after timer expiration
    end_loop_time = loop.time()
    
    # Line 11: Calculate and output loop clock progression delta (~0.500s)
    print(f"Loop Clock after 0.5s sleep: {end_loop_time:.4f} (Delta: {end_loop_time - start_loop_time:.4f}s)")


def main():
    """Main execution wrapper to initialize the event loop and launch coroutine."""
    
    # Line 1: Print section header banner to standard output
    print("=== Inspecting Event Loop Instance & Clock ===")
    
    # Line 2: Create a new event loop, run 'inspect_event_loop()', and close loop on exit
    asyncio.run(inspect_event_loop())


if __name__ == "__main__":
    # Line 1: Program entry point when script is executed directly from shell
    main()

