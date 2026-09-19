"""
===============================================================================
Module 01: Asynchronous Execution Demo (Concurrent & Non-Blocking)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Native Coroutines (`async def`).
2. Non-blocking await points (`await asyncio.sleep`).
3. Event Loop control transfer.
4. Concurrent aggregation with `asyncio.gather()`.

HOW THIS CODE WORKS:
- `fetch_user_profile(user_id)` is defined with `async def`, making it a coroutine function.
- Inside the coroutine, `await asyncio.sleep(1.0)` is called instead of `time.sleep()`.
- The `await` keyword signals to the Event Loop: "I am waiting for I/O! Pause me,
  and run another ready task in the meantime."
- `asyncio.gather(*tasks)` schedules all 3 coroutines concurrently on the loop.

EXPECTED OUTPUT:
- All 3 user fetch requests start almost simultaneously at t=0.0s.
- All 3 network requests wait for 1 second concurrently.
- All 3 user fetch requests finish almost simultaneously at t=1.0s.
- Total execution time: ~1.0 second (3x speedup over synchronous!).
===============================================================================
"""

import asyncio
import time


async def fetch_user_profile(user_id: int) -> dict:
    """Simulates fetching a user profile from a remote API asynchronously.
    
    Args:
        user_id (int): Unique identifier of the user to fetch.

    Returns:
        dict: A dictionary containing the fetched user data.
    """
    print(f"[ASYNC] Step 1: Initiating request for User {user_id}...")
    
    # CRITICAL POINT: await asyncio.sleep(1.0) is NON-BLOCKING.
    # The 'await' keyword yields control back to the event loop dispatcher.
    # The event loop can now execute User 2 and User 3 while User 1 is waiting.
    await asyncio.sleep(1.0)
    
    print(f"[ASYNC] Step 2: Received network response for User {user_id}")
    return {"user_id": user_id, "name": f"User_{user_id}", "status": "active"}


async def main():
    """Main asynchronous coroutine entry point."""
    print("=== Starting Asynchronous (Concurrent Non-Blocking) Demo ===")
    start_time = time.perf_counter()
    
    # Create coroutine objects for 3 users (does not execute them yet!)
    tasks = [fetch_user_profile(user_id) for user_id in range(1, 4)]
    
    # asyncio.gather schedules all 3 coroutines concurrently on the event loop and waits for all to finish
    users = await asyncio.gather(*tasks)
    
    elapsed_time = time.perf_counter() - start_time
    
    print("\n--- Asynchronous Execution Summary ---")
    print(f"Fetched Users Count : {len(users)}")
    print(f"Total Execution Time: {elapsed_time:.2f} seconds")
    print("Notice: Time is ~1.0s because all 3 requests waited for network I/O CONCURRENTLY!")


if __name__ == "__main__":
    # Launch the event loop and execute the main coroutine
    asyncio.run(main())
