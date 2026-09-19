"""
===============================================================================
Module 01: Synchronous Execution Demo (Sequential & Blocking)
===============================================================================

CONCEPTS DEMONSTRATED:
1. Sequential execution flow (Line-by-line processing).
2. Thread blocking during I/O simulation (time.sleep).
3. Cumulative total latency calculation: Total Time = sum(Individual Latencies).

HOW THIS CODE WORKS:
- The function `fetch_user_profile(user_id)` simulates a synchronous network request
  to fetch a database record or REST API profile.
- `time.sleep(1)` forces the CPython thread to pause for 1 full second.
- During this pause, the CPU/thread CANNOT do any other work.
- The `main()` loop calls `fetch_user_profile` 3 times sequentially.

EXPECTED OUTPUT:
- User 1 starts -> waits 1s -> completes
- User 2 starts -> waits 1s -> completes
- User 3 starts -> waits 1s -> completes
- Total execution time: ~3.0 seconds.
===============================================================================
"""

import time


def fetch_user_profile(user_id: int) -> dict:
    """Simulates fetching a user profile from a remote API synchronously.
    
    Args:
        user_id (int): Unique identifier of the user to fetch.

    Returns:
        dict: A dictionary containing the fetched user data.
    """
    print(f"[SYNC] Step 1: Initiating request for User {user_id}...")
    
    # CRITICAL POINT: time.sleep() is a BLOCKING call.
    # It halts the current OS thread execution. No other Python code can execute.
    time.sleep(1.0)
    
    print(f"[SYNC] Step 2: Received network response for User {user_id}")
    return {"user_id": user_id, "name": f"User_{user_id}", "status": "active"}


def main():
    """Main execution entry point for synchronous execution benchmark."""
    print("=== Starting Synchronous (Sequential Blocking) Demo ===")
    start_time = time.perf_counter()
    
    users = []
    # Sequential Loop: Each iteration MUST complete before the next iteration can start.
    for user_id in range(1, 4):
        user_data = fetch_user_profile(user_id)
        users.append(user_data)
        
    elapsed_time = time.perf_counter() - start_time
    
    print("\n--- Synchronous Execution Summary ---")
    print(f"Fetched Users Count : {len(users)}")
    print(f"Total Execution Time: {elapsed_time:.2f} seconds")
    print("Notice: Time is ~3.0s because 3 requests ran one after another sequentially.")


if __name__ == "__main__":
    main()
