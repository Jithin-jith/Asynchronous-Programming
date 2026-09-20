"""
===============================================================================
Module 02: I/O-Bound Workload Asynchronous Demo
===============================================================================

CONCEPTS DEMONSTRATED:
1. I/O-Bound Workloads:
   - I/O (Input/Output)-bound operations spend >99% of their total wall-clock time 
     waiting for external hardware or remote systems (network sockets, disk drives, databases).
   - The CPU is almost entirely idle during this wait period.

2. Non-Blocking Asynchronous Sleep (`asyncio.sleep`):
   - Unlike `time.sleep()` which freezes the OS thread, `await asyncio.sleep()` registers 
     a timer with the event loop and yields control back immediately.
   - While one request waits for its timer/socket, the event loop runs other coroutines.

3. Concurrency Latency Mathematics:
   - Sequential Total Duration = sum(t_1, t_2, ..., t_n) = 1.0 + 0.8 + 1.2 + 0.5 + 1.5 = 5.0s.
   - Concurrent Total Duration = max(t_1, t_2, ..., t_n) = max(1.0, 0.8, 1.2, 0.5, 1.5) = ~1.5s.

HOW THIS CODE WORKS:
- `simulate_io_request(request_id, duration)` simulates a non-blocking network API call.
- We launch 5 concurrent requests with varying latencies using `asyncio.gather()`.
- OBSERVED RESULT: All 5 requests run concurrently on a SINGLE OS thread, finishing in ~1.5s!
===============================================================================
"""

import asyncio  # Standard library async I/O framework providing event loop & coroutine tools
import time     # High-resolution performance timer module for accurate duration measuring


async def simulate_io_request(request_id: int, duration: float) -> str:
    """Simulates an asynchronous HTTP API network call or database query.

    In real-world applications, this represents sending a request packet over TCP/IP
    and waiting for the remote server's response packet to return.

    Args:
        request_id (int): Unique numeric identifier for tracking request logs.
        duration (float): Simulated network latency time in seconds.

    Returns:
        str: Formatted mock JSON/string response payload.
    """
    # Line 1: Log request dispatch with request identifier and expected latency
    print(f"[I/O Task] Request #{request_id} sent to remote server (latency: {duration}s)...")
    
    # Line 2: NON-BLOCKING COOPERATIVE YIELD POINT
    # 'await asyncio.sleep(duration)' instructs the event loop to pause this coroutine for 'duration' seconds,
    # yield execution control back to the event loop thread, and switch to another ready task.
    # The OS thread remains 100% active and available during this pause!
    await asyncio.sleep(duration)
    
    # Line 3: Log response arrival once the event loop resumes this coroutine after timer expiration
    print(f"[I/O Task] Request #{request_id} response received after {duration}s!")
    
    # Line 4: Return synthesized response payload to the caller
    return f"Response_Payload_For_Request_{request_id}"


async def main():
    """Main coroutine orchestrator for scheduling concurrent I/O operations."""
    
    # Line 1: Output test header banner to standard output
    print("=== Simulating 5 Concurrent I/O Network Requests ===")
    
    # Line 2: Record high-resolution start timestamp (in fractional seconds)
    start_time = time.perf_counter()
    
    # Line 3: Instantiate 5 coroutine objects with varying latency parameters
    # NOTE: Calling an 'async def' function creates a coroutine object; it does NOT execute code yet.
    tasks = [
        simulate_io_request(1, 1.0),  # Task 1: 1.0 second delay
        simulate_io_request(2, 0.8),  # Task 2: 0.8 second delay
        simulate_io_request(3, 1.2),  # Task 3: 1.2 seconds delay
        simulate_io_request(4, 0.5),  # Task 4: 0.5 second delay (will finish first!)
        simulate_io_request(5, 1.5),  # Task 5: 1.5 seconds delay (determines total max duration)
    ]
    
    # Line 4: Schedule and execute all 5 coroutines concurrently using asyncio.gather()
    # 'await asyncio.gather(*tasks)' wraps coroutines into tasks, schedules them on the event loop,
    # overlaps their waiting periods, and suspends main() until ALL tasks return results.
    results = await asyncio.gather(*tasks)
    
    # Line 5: Calculate total elapsed wall-clock execution time
    elapsed = time.perf_counter() - start_time
    
    # Line 6: Output execution metrics and educational summary
    print(f"\n[SUMMARY] Successfully processed {len(results)} I/O requests!")
    print(f"[SUMMARY] Total Wall-Clock Time : {elapsed:.2f} seconds")
    print(f"[SUMMARY] Max Single Delay      : 1.50 seconds")
    print(f"[SUMMARY] Sum of All Delays     : 5.00 seconds")
    print("-" * 75)
    print("TAKEAWAY: Execution completed in ~1.5s (the maximum single delay) instead of")
    print("5.0s (the sum) because asyncio overlapped all network waiting times concurrently!")
    print("-" * 75)


if __name__ == "__main__":
    # Line 1: Bootstrap the asyncio event loop, execute main(), and perform clean event loop tear-down
    asyncio.run(main())

